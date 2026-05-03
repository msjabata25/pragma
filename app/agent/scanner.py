import subprocess
import json

def scan(repo_path: str) -> dict:
    try:
        result = subprocess.run(
            ["uv", "run", "semgrep", "scan",
 "--config", "p/security-audit",
 "--config", "p/python",
 "--config", "p/secrets",
 "--no-git-ignore", "--json", repo_path],
            capture_output=True,
            encoding="utf-8",
            errors="ignore",
            env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8", "SEMGREP_RULES_CACHE": "/tmp/semgrep_cache"}
        )
        print(f"[DEBUG] semgrep returncode: {result.returncode}")
        print(f"[DEBUG] semgrep stderr: {result.stderr[:500]}")
        print(f"[DEBUG] semgrep stdout preview: {result.stdout[:300]}")
        
        if result.returncode not in (0, 1):
            raise RuntimeError(f"Semgrep failed:\n{result.stderr}")
        return json.loads(result.stdout)
    except Exception as e:
        return {"results": [], "errors": [str(e)]}
