from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import tempfile
import os
from pathlib import Path

from app.agent.loop import run_async
from app.agent.reporter import generate_report
from app.agent.models import Persona
from app.rag.ingestor import ingest_zip, ingest_github
from app.rag.embedder import embed_query
from app.rag.store import query_chunks

load_dotenv()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Pragma AI Code Auditor")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# --- Schemas ---

class GithubIngestRequest(BaseModel):
    github_url: str

class QueryRequest(BaseModel):
    repo_id: str
    query: str
    n_results: int = 5


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
        return ingest_zip(tmp_path)
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


@app.get("/audit/report/download")
@limiter.limit("5/hour")
async def download_report(
    request: Request,
    repo_id: str,
    mode: Persona = Query(default="technical"),
):
    repo_path = _get_repo_path(repo_id)
    results = await run_async(str(repo_path))
    repo_name = repo_path.name
    html_path = generate_report(results, mode=mode, repo_name=repo_name, output_dir="output")
    return FileResponse(
        path=html_path,
        media_type="text/html",
        filename=f"pragma_{mode}_{repo_name}.html",
    )