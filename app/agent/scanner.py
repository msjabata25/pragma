import subprocess
import json

def scan(repo_path : str) -> dict:
    try:
        result = subprocess.run(
    ["uv" , "run" , "semgrep", "scan", "--config", "auto", "--json", repo_path],
    capture_output=True,
    encoding="utf-8",
    errors="ignore",
    env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}
)
        
        
    except Exception as e:
        return {"Error" : str(e) }

    else:
        return json.loads(result.stdout)
    