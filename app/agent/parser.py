from .models import Finding


def parse(semgrep_output : dict) -> list[Finding]:
    findings = []
    for result in semgrep_output["results"]:
        #Parsing the output into the dataclass Finding
        finding = Finding(
            check_id  = result["check_id"],
            path      = result["path"],
            stLine    = result["start"]["line"],
            msg       = result["extra"]["message"],
            severity  = result["extra"]["severity"]
        )
        findings.append(finding)
    
    return findings

        