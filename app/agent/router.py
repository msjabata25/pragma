from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import chromadb

SMALL_REPO_MAX_CHUNKS  = 100
MEDIUM_REPO_MAX_CHUNKS = 500

class Model(str, Enum):
    SMALL  = "llama-3.3-70b-versatile"
    MEDIUM = "llama-3.3-70b-versatile"
    LARGE  = "llama-3.3-70b-versatile"

@dataclass(frozen=True)
class RoutingDecision:
    model:       Model
    chunk_count: int
    tier:        str
    provider:    str

    def __str__(self) -> str:
        return (
            f"[router] {self.tier} repo ({self.chunk_count} chunks) "
            f"→ {self.model.value} ({self.provider})"
        )

CHROMA_PATH = "./chroma_db"

def _chunk_count(repo_id: str) -> int:
    try:
        client     = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_collection(f"pragma_{repo_id}")
        return collection.count()
    except Exception:
        return 0

def resolve_model(repo_id: str) -> RoutingDecision:
    count = _chunk_count(repo_id)

    if count < SMALL_REPO_MAX_CHUNKS:
        return RoutingDecision(model=Model.SMALL, chunk_count=count, tier="small", provider="groq")
    elif count < MEDIUM_REPO_MAX_CHUNKS:
        return RoutingDecision(model=Model.MEDIUM, chunk_count=count, tier="medium", provider="groq")
    else:
        return RoutingDecision(model=Model.LARGE, chunk_count=count, tier="large", provider="groq")