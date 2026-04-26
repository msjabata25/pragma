"""
knowledge/query.py
Query the pragma_knowledge ChromaDB collection using a local embedding model.
Called by the agent loop to enrich the judge prompt.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME  = "pragma_knowledge"
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"

# MiniLM cosine distance: 0.0 = identical, 2.0 = opposite.
# Chunks above this threshold are noise — don't send them to the judge.
# Calibrate by logging distances on real queries; 0.45 is a safe starting point.
MAX_DISTANCE = 0.45


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Load once, reuse across all calls in the same process."""
    return SentenceTransformer(EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def _get_collection(db_path: str):
    """
    Instantiate the ChromaDB client and collection once per process.
    Avoids spinning up a new PersistentClient on every finding call.
    Returns None if the collection doesn't exist or is empty.
    """
    chroma   = chromadb.PersistentClient(path=db_path)
    existing = [c.name for c in chroma.list_collections()]
    if COLLECTION_NAME not in existing:
        return None
    collection = chroma.get_collection(COLLECTION_NAME)
    return collection if collection.count() > 0 else None


def query_knowledge(
    query_text: str,
    db_path: str | Path = "chroma_db",
    n_results: int = 3,
    max_distance: float = MAX_DISTANCE,
) -> list[dict]:
    """
    Embed query_text locally and retrieve the top-n most relevant knowledge chunks,
    filtered by cosine distance so only genuinely relevant chunks reach the judge.

    Returns a list of dicts:
        [{"source": "owasp/injection", "heading": "Parameterized Queries", "content": "..."}]

    Returns [] gracefully if the collection doesn't exist or no chunks pass the threshold.
    """
    collection = _get_collection(str(db_path))
    if collection is None:
        return []

    model        = _get_model()
    query_vector = model.encode([query_text], convert_to_numpy=True)[0].tolist()

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],  # ✅ request distances
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        if dist <= max_distance:  # ✅ drop irrelevant chunks before they hit the prompt
            chunks.append({
                "source":   meta.get("source", ""),
                "heading":  meta.get("heading", ""),
                "content":  doc,
                "distance": round(dist, 4),  # useful for debugging / calibration
            })

    return chunks