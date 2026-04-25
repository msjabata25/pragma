from __future__ import annotations
import asyncio
import json
import os
from dotenv import load_dotenv
from groq import AsyncGroq
import traceback

from .scanner import scan
from .parser import parse
from .models import Finding, AuditResult, PersonaContent
from .router import resolve_model, Model
from ..rag.embedder import embed_query
from ..rag.store import query_chunks, get_chunk_count
from ..knowledge.query import query_knowledge

load_dotenv()

# ❌ REMOVED: module-level semaphores were causing cross-loop KeyError: '_type'
# They're now created fresh inside run_async per event loop lifecycle


async def _process_finding(
    finding: Finding,
    repo_id: str,
    model: Model,
    client: AsyncGroq,
    semaphores: dict[Model, asyncio.Semaphore],  # ✅ passed in, not global
) -> AuditResult:
    sem = semaphores[model]

    async with sem:
        query_prompt = (
            f"Generate a single semantic search query for vulnerability: "
            f"{finding.check_id}. Return ONLY the query string, no explanation."
        )
        query_response = await client.chat.completions.create(
            model=Model.SMALL.value,
            messages=[{"role": "user", "content": query_prompt}],
        )
        rag_query = query_response.choices[0].message.content.strip()

        query_vector, knowledge_chunks = await asyncio.gather(
            asyncio.to_thread(embed_query, rag_query),
            asyncio.to_thread(query_knowledge, rag_query),
        )
        chunks = query_chunks(repo_id, query_vector)
        chunks_text = "\n\n".join([c["content"] for c in chunks])
        knowledge_text = "\n\n".join(
            f"[{k['source']}] {k['content']}" for k in knowledge_chunks
        )

        audit_prompt = f"""You are a security code consultant.
Vulnerability: {finding.check_id} ({finding.msg})
Code Context:
{chunks_text}
Security Knowledge:
{knowledge_text}

Respond ONLY with a valid JSON object with exactly these fields, no markdown fences:
{{
    "technical": {{ "explanation": "Dev-focused root cause", "fix": "Technical fix description", "fixed_code": "The full corrected function or block, not just the changed line. Include enough surrounding context that a beginner can copy-paste it directly as a replacement." }},
    "ceo":       {{ "explanation": "Non-technical business risk", "fix": "High-level action", "fixed_code": "The full corrected function or block, not just the changed line. Include enough surrounding context that a beginner can copy-paste it directly as a replacement." }},
    "public":    {{ "explanation": "Simple analogy/educational summary", "fix": "Approachable fix description", "fixed_code": "The full corrected function or block, not just the changed line. Include enough surrounding context that a beginner can copy-paste it directly as a replacement." }}
}}"""

        audit_response = await client.chat.completions.create(
            model=model.value,
            messages=[{"role": "user", "content": audit_prompt}],
        )

        raw = audit_response.choices[0].message.content.strip()

        # ✅ More robust fence stripping — handles ```json, ```, or bare JSON
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]  # drop the ```json line
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
    # Strip any smart quotes and try again
            raw = raw.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    # Last resort: ask the model to fix it
            print(f"[DEBUG] JSON parse failed, raw was:\n{raw}")
            raise

    return AuditResult(
        finding=finding,
        relevant_chunks=[c["content"] for c in chunks],
        technical=PersonaContent(**data["technical"]),
        ceo=PersonaContent(**data["ceo"]),
        public=PersonaContent(**data["public"]),
    )


async def run_async(repo_path: str) -> list[AuditResult]:
    # ✅ Semaphores created here — bound to THIS event loop, not a stale one
    semaphores: dict[Model, asyncio.Semaphore] = {
        Model.SMALL:  asyncio.Semaphore(5),
        Model.MEDIUM: asyncio.Semaphore(3),
        Model.LARGE:  asyncio.Semaphore(2),
    }

    client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])
    repo_id = os.path.basename(repo_path)

    chunk_count = await asyncio.to_thread(get_chunk_count, repo_id)
    decision = resolve_model(repo_id)

    scanned_dict = await asyncio.to_thread(scan, repo_path)
    findings = parse(scanned_dict)
    print(f"[DEBUG] findings count: {len(findings)}")

    if not findings:
        return []

    tasks = [
        _process_finding(f, repo_id, decision.model, client, semaphores)
        for f in findings
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for r in results:
        if isinstance(r, Exception):
            print(f"[DEBUG] task failed: {type(r).__name__}: {r}")
            traceback.print_exception(type(r), r, r.__traceback__)

    return [r for r in results if not isinstance(r, Exception)]


def run(repo_path: str) -> list[AuditResult]:
    # ✅ Always use asyncio.run() — creates a clean loop every time.
    # The old try/except was masking the real issue (stale loop + stale semaphores).
    return asyncio.run(run_async(repo_path))