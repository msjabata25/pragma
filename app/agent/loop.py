from scanner import scan
from parser import parse
from models import Finding
from models import AuditResult
from google import genai
import os
from dotenv import load_dotenv
from ..rag.embedder import embed_query
from ..rag.store import query_chunks
import json


load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])



def run(repo_path  : str):
    repo_id = os.path.basename(repo_path)
    results = []
    scannedDict  = scan(repo_path)
    findings = parse(scannedDict)

    for finding in findings :
        # 1. Gen RAG query with flash
        query_prompt = f"""You are a security code analysis assistant.

Given this vulnerability:
- Rule: {finding.check_id}
- Message: {finding.msg}
- Severity: {finding.severity}

Generate a single semantic search query to retrieve the most relevant code chunks 
from a codebase. Return ONLY the query string, nothing else."""
        

        response  = client.models.generate_content(
            model= "gemini-2.5-flash" #better model and doesnt crash like 2.0 (Trust me, I tried)
            , contents= query_prompt
        )
        rag_query = response.text
        # 2. retirive those chunks from chromaDB

        query_vector = embed_query(rag_query)
        chunks = query_chunks(repo_id , query_vector)
        chunks_text = "\n\n".join([c["content"] for c in chunks])
        # 3. ask Flash to explain vul + generate fix 
        audit_prompt = f"""You are a security code consultant.

Given this vulnerability:
- Rule: {finding.check_id}
- Message: {finding.msg}
- Severity: {finding.severity}

Relevant code:
{chunks_text}

Respond ONLY with a JSON object with exactly these two fields:
{{
    "explanation": "simple, clear explanation of the vulnerability",
    "fix": "the corrected code or fix instructions"
}}
No preamble, no markdown, just the JSON."""
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents= audit_prompt
        )
        clean = res.text.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(clean)
        exp = data["explanation"]
        fix = data["fix"]
        # 4. wrap into AuditResult
        results.append( AuditResult(
            finding= finding,
            relevant_chunks=[c["content"] for c in chunks],
            explanation= exp,
            fix = fix
        )
        )

    return results