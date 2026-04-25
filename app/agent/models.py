from dataclasses import dataclass, field
from typing import Literal

Persona = Literal["ceo", "public", "technical"]

@dataclass
class PersonaContent:
    explanation: str
    fix: str
    fixed_code: str | None = None  

@dataclass
class Finding:
    path: str
    stLine: int
    msg: str
    severity: str
    check_id: str

@dataclass
class AuditResult:
    finding: Finding
    relevant_chunks: list[str]
    technical: PersonaContent
    ceo: PersonaContent
    public: PersonaContent