from .models import Finding

_SEVERITY_RANK = {"CRITICAL": 4, "ERROR": 3, "WARNING": 2, "INFO": 1}

def parse(semgrep_output: dict) -> list[Finding]:
    seen: dict[tuple, Finding] = {}

    for result in semgrep_output["results"]:
        finding = Finding(
            check_id=result["check_id"],
            path=result["path"],
            stLine=result["start"]["line"],
            msg=result["extra"]["message"],
            severity=result["extra"]["severity"],
        )
        key = (finding.path, finding.check_id)
        if key not in seen:
            seen[key] = finding
        else:
            existing = seen[key]
            if _SEVERITY_RANK.get(finding.severity.upper(), 0) > _SEVERITY_RANK.get(existing.severity.upper(), 0):
                seen[key] = finding

    return list(seen.values())