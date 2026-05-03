from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import tempfile
import os
from pathlib import Path
import asyncio

from app.agent.loop import run_async
from app.agent.models import Persona
from app.rag.ingestor import ingest_zip, ingest_github
from app.rag.embedder import embed_query
from app.rag.store import query_chunks

load_dotenv()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Pragma AI Code Auditor")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://msjabata25.github.io",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- Schemas ---

class GithubIngestRequest(BaseModel):
    github_url: str

class QueryRequest(BaseModel):
    repo_id: str
    query: str
    n_results: int = 5

class AuditRequest(BaseModel):
    repo_id: str


# --- Helpers ---

def _get_repo_path(repo_id: str) -> Path:
    path = Path("repos") / repo_id
    if not path.exists():
        path = Path(repo_id)
    return path


# --- Endpoints ---

@app.post("/ingest/github")
@limiter.limit("10/hour")
def ingest_github_endpoint(request: Request, body: GithubIngestRequest):
    try:
        return ingest_github(body.github_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/zip")
@limiter.limit("10/hour")
async def ingest_zip_endpoint(request: Request, file: UploadFile = File(...)):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        return await asyncio.to_thread(ingest_zip, tmp_path)  # ← wrap it
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/query")
@limiter.limit("30/minute")
async def query_endpoint(request: Request, body: QueryRequest):
    try:
        embedding = embed_query(body.query)
        chunks = query_chunks(body.repo_id, embedding, body.n_results)
        return chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/audit")
@limiter.limit("5/hour")
async def audit_endpoint(request: Request, body: AuditRequest):
    """
    Run a full audit on an already-ingested repo.
    Returns raw findings JSON — the frontend owns rendering.
    """
    repo_path = _get_repo_path(body.repo_id)
    if not repo_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Repo '{body.repo_id}' not found. Ingest it first."
        )
    try:
        results = await run_async(str(repo_path))
        return {
            "repo_id": body.repo_id,
            "findings": [
                {
                    "finding": {
                        "check_id":  r.finding.check_id,
                        "msg":       r.finding.msg,
                        "path":      r.finding.path,
                        "stLine":    r.finding.stLine,
                        "severity":  r.finding.severity,
                    },
                    "technical": {
                        "explanation": r.technical.explanation,
                        "fix":         r.technical.fix,
                        "fixed_code":  r.technical.fixed_code,
                    },
                    "ceo": {
                        "explanation": r.ceo.explanation,
                        "fix":         r.ceo.fix,
                        "fixed_code":  r.ceo.fixed_code,
                    },
                    "public": {
                        "explanation": r.public.explanation,
                        "fix":         r.public.fix,
                        "fixed_code":  r.public.fixed_code,
                    },
                }
                for r in results
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))