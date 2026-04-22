from __future__ import annotations
import asyncio
import json
import os
from dotenv import load_dotenv
from groq import AsyncGroq

from .scanner import scan
from .parser import parse
from .models import Finding, AuditResult, PersonaContent
from .router import resolve_model, Model
from ..rag.embedder import embed_query
from ..rag.store import query_chunks, get_chunk_count
from ..knowledge.query import query_knowledge

load_dotenv()

_SEMAPHORES: dict[Model, asyncio.Semaphore] = {
    Model.SMALL:  asyncio.Semaphore(5),
    Model.MEDIUM: asyncio.Semaphore(3),
    Model.LARGE:  asyncio.Semaphore(2),
}

async def _process_finding(
    finding: Finding,
    repo_id: str,
    model: Model,
    client: AsyncGroq,
) -> AuditResult:
    sem = _SEMAPHORES[model]

    async with sem:
        # 1. Generate RAG query
        query_prompt = f"Generate a single semantic search query for vulnerability: {finding.check_id}. Return ONLY the query."
        query_response = await client.chat.completions.create(
            model=Model.SMALL.value,
            messages=[{"role": "user", "content": query_prompt}],
        )
        rag_query = query_response.choices[0].message.content.strip()

        # 2. Retrieve code and knowledge
        query_vector, knowledge_chunks = await asyncio.gather(
            asyncio.to_thread(embed_query, rag_query),
            asyncio.to_thread(query_knowledge, rag_query),
        )
        chunks = query_chunks(repo_id, query_vector)
        chunks_text = "\n\n".join([c["content"] for c in chunks])
        knowledge_text = "\n\n".join(f"[{k['source']}] {k['content']}" for k in knowledge_chunks)

        # 3. Persona-Aware Audit Prompt
        audit_prompt = f"""You are a security code consultant.
Vulnerability: {finding.check_id} ({finding.msg})
Code Context:
{chunks_text}
Security Knowledge:
{knowledge_text}

Respond ONLY with a JSON object with exactly these fields:
{{
    "technical": {{ "explanation": "Dev-focused root cause", "fix": "Technical fix" }},
    "ceo": {{ "explanation": "Non-technical business risk", "fix": "High-level action" }},
    "public": {{ "explanation": "Simple analogy/educational summary", "fix": "Approachable fix description" }}
}}"""

        audit_response = await client.chat.completions.create(
            model=model.value,
            messages=[{"role": "user", "content": audit_prompt}],
        )
        clean = audit_response.choices[0].message.content.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(clean)

    return AuditResult(
        finding=finding,
        relevant_chunks=[c["content"] for c in chunks],
        technical=PersonaContent(**data["technical"]),
        ceo=PersonaContent(**data["ceo"]),
        public=PersonaContent(**data["public"])
    )

async def run_async(repo_path: str) -> list[AuditResult]:
    client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

    repo_id = os.path.basename(repo_path)

    chunk_count = await asyncio.to_thread(get_chunk_count, repo_id)
    decision = resolve_model(repo_id)

    scanned_dict = await asyncio.to_thread(scan, repo_path)
    findings = parse(scanned_dict)
    print(f"[DEBUG] findings count: {len(findings)}")

    if not findings:
        return []

    tasks = [_process_finding(f, repo_id, decision.model, client) for f in findings]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for r in results:
        if isinstance(r, Exception):
            print(f"[DEBUG] task failed: {type(r).__name__}: {r}")

    return [r for r in results if not isinstance(r, Exception)]

def run(repo_path: str) -> list[AuditResult]:
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(run_async(repo_path))
    except RuntimeError:
        return asyncio.run(run_async(repo_path))