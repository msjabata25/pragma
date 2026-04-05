from scanner import scan
from parser import parse
from models import Finding
from models import AuditResult
from google import genai
import os
import json
from dotenv import load_dotenv
from ..rag.embedder import embed_query
from ..rag.store import query_chunks
from knowledge import query_knowledge


load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def run(repo_path: str):
    repo_id = os.path.basename(repo_path)
    results = []
    scannedDict = scan(repo_path)
    findings = parse(scannedDict)

    for finding in findings:
        # 1. Gen RAG query with Flash
        query_prompt = f"""You are a security code analysis assistant.

Given this vulnerability:
- Rule: {finding.check_id}
- Message: {finding.msg}
- Severity: {finding.severity}

Generate a single semantic search query to retrieve the most relevant code chunks 
from a codebase. Return ONLY the query string, nothing else."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",  # better model and doesnt crash like 2.0 (Trust me, I tried)
            contents=query_prompt
        )
        rag_query = response.text.strip()

        # 2. Retrieve code chunks from ChromaDB
        query_vector = embed_query(rag_query)
        chunks = query_chunks(repo_id, query_vector)
        chunks_text = "\n\n".join([c["content"] for c in chunks])

        # 3. Retrieve relevant knowledge chunks (OWASP, CWE, etc.)
        #    Falls back to [] gracefully if KB hasn't been built yet
        knowledge_chunks = query_knowledge(rag_query)
        knowledge_text = "\n\n".join(
            f"[{k['source']} — {k['heading']}]\n{k['content']}"
            for k in knowledge_chunks
        ) if knowledge_chunks else ""

        # 4. Ask Flash to explain vuln + generate fix
        knowledge_section = f"""
Relevant security knowledge:
{knowledge_text}
""" if knowledge_text else ""

        audit_prompt = f"""You are a security code consultant.

Given this vulnerability:
- Rule: {finding.check_id}
- Message: {finding.msg}
- Severity: {finding.severity}

Relevant code from the repository:
{chunks_text}
{knowledge_section}
Respond ONLY with a JSON object with exactly these two fields:
{{
    "explanation": "simple, clear explanation of the vulnerability",
    "fix": "the corrected code or fix instructions"
}}
No preamble, no markdown, just the JSON."""

        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=audit_prompt
        )
        clean = res.text.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(clean)

        # 5. Wrap into AuditResult
        results.append(AuditResult(
            finding=finding,
            relevant_chunks=[c["content"] for c in chunks],
            explanation=data["explanation"],
            fix=data["fix"]
        ))

    return results