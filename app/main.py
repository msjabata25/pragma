from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv
import tempfile
import os
from pathlib import Path
from app.agent.scanner import scan
from app.agent.parser import parse
from app.agent.loop import run
from app.agent.reporter import generate_report, build_html
from app.agent.models import Persona
# (And make sure your rag imports also use the app. prefix)
from app.rag.ingestor import ingest_zip, ingest_github
from app.rag.embedder import embed_query
from app.rag.store import query_chunks
from fastapi.responses import FileResponse, HTMLResponse
from app.agent.loop import run, run_async
load_dotenv()
app = FastAPI(title="Pragma AI Code Auditor")

# --- Schemas ---

class GithubIngestRequest(BaseModel):
    github_url: str

class QueryRequest(BaseModel):
    repo_id: str
    query: str
    n_results: int = 5

# --- Helpers ---

def _get_repo_path(repo_id: str) -> str:
    """Helper to locate the local repo path from an ID/name."""
    # Assuming repos are stored in a standard 'repos' directory
    base_dir = Path("repos") 
    path = base_dir / repo_id
    if not path.exists():
        # Fallback for direct pathing if needed
        path = Path(repo_id)
    return str(path)

# --- Endpoints ---

@app.post("/ingest/github")
def ingest_github_endpoint(request: GithubIngestRequest):
    try:
        result = ingest_github(request.github_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest/zip")
async def ingest_zip_endpoint(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        result = ingest_zip(tmp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    try:
        embedding = embed_query(request.query)
        chunks = query_chunks(request.repo_id, embedding, request.n_results)
        return chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audit")
def audit_repo(
    repo_id: str,
    mode: Persona = Query(default="technical")
):
    repo_path = Path("repos") / repo_id
    print(f"[DEBUG] Looking for repo at: {repo_path.resolve()}")
    print(f"[DEBUG] Path exists: {repo_path.exists()}")

    # ✅ Only scan/parse here — run() is for the report endpoints
    scanned = scan(str(repo_path))
    findings = parse(scanned)
    print(f"[DEBUG] findings count: {len(findings)}")

    return {
        "repo": repo_id,
        "total_findings": len(findings),
        "findings": [
            {
                "check_id": f.check_id,
                "path": f.path,
                "line": f.stLine,
                "severity": f.severity,
                "message": f.msg,
            }
            for f in findings
        ],
    }
@app.get("/audit/report/html", response_class=HTMLResponse)
async def get_html_report(
    repo_id: str,
    mode: Persona = Query(default="ceo")
):
    repo_path = _get_repo_path(repo_id)
    results = await run_async(repo_path)  # ✅ await, not run()
    repo_name = os.path.basename(repo_path.rstrip("/"))
    return build_html(results, mode=mode, repo_name=repo_name)


@app.get("/audit/report/download")
async def download_report(
    repo_id: str,
    mode: Persona = Query(default="technical"),
):
    repo_path = _get_repo_path(repo_id)
    results = await run_async(repo_path)  # ✅ await, not run()
    repo_name = os.path.basename(repo_path.rstrip("/"))
    html_path = generate_report(results, mode=mode, repo_name=repo_name, output_dir="output")
    return FileResponse(
        path=html_path,
        media_type="text/html",
        filename=f"pragma_{mode}_{repo_name}.html"
    )


@app.get("/audit/report/download")
def download_report(
    repo_id: str,
    mode: Persona = Query(default="technical"),
):
    """
    Run audit and return the persona-based HTML report as a file download.
    """
    repo_path = _get_repo_path(repo_id)
    results = run(repo_path)
    repo_name = os.path.basename(repo_path.rstrip("/"))
    
    html_path = generate_report(results, mode=mode, repo_name=repo_name, output_dir="output")
    
    return FileResponse(
        path=html_path, 
        media_type="text/html", 
        filename=f"pragma_{mode}_{repo_name}.html"
    )