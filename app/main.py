from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from app.rag.ingestor import ingest_zip, ingest_github
from app.rag.embedder import embed_query
from app.rag.store import query_chunks
import tempfile, os
from agent.loop import run
from agent.reporter import generate_report , build_html , Mode
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import Query




load_dotenv()
app = FastAPI()

class GithubIngestRequest(BaseModel):
    github_url: str

class QueryRequest(BaseModel):
    repo_id: str
    query : str
    n_results : int = 5

@app.post("/ingest/github")
def ingest_github_endpoint(request : GithubIngestRequest):
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
        os.remove(tmp_path)


@app.post("/query")
async def query_endpoint(request : QueryRequest):
    try:
        embedding = embed_query(request.query)
        chunks = query_chunks(request.repo_id , embedding , request.n_results)
        return chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/audit")
def audit_repo(
    repo_path: str,
    mode: Mode = Query(default="autopilot", description="'autopilot' or 'manual'"),
):
    """
    Run the full Pragma agent loop on a local repo path.
    Returns the AuditResults as JSON and writes reports to ./output/.
    """
    results = run(repo_path)
 
    repo_name = os.path.basename(repo_path.rstrip("/"))
    html_path = generate_report(results, mode=mode, repo_name=repo_name, output_dir="output")
 
    return {
        "repo": repo_name,
        "mode": mode,
        "total_findings": len(results),
        "report_html": str(html_path),
        "results": [
            {
                "check_id":    r.finding.check_id,
                "path":        r.finding.path,
                "line":        r.finding.stLine,
                "severity":    r.finding.severity,
                "message":     r.finding.msg,
                "explanation": r.explanation,
                "fix":         r.fix,
            }
            for r in results
        ],
    }

@app.get("/audit/report/html", response_class=HTMLResponse)
def get_html_report(repo_path: str, mode: Mode = Query(default="autopilot")):
    """
    Run audit and return the HTML report inline (viewable in browser).
    """
    results = run(repo_path)
    repo_name = os.path.basename(repo_path.rstrip("/"))
    return build_html(results, mode=mode, repo_name=repo_name)
 
 
@app.get("/audit/report/download")
def download_report(
    repo_path: str,
    mode: Mode = Query(default="autopilot"),
    fmt: str  = Query(default="html", description="'html' or 'md'"),
):
    """
    Run audit and return the report file as a download.
    """
    results = run(repo_path)
    repo_name = os.path.basename(repo_path.rstrip("/"))
    html_path = generate_report(results, mode=mode, repo_name=repo_name, output_dir="output")
    return FileResponse(html_path, media_type="text/html", filename=html_path.name)