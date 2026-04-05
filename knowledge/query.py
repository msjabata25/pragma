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

COLLECTION_NAME = "pragma_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Load once, reuse across all calls in the same process."""
    return SentenceTransformer(EMBEDDING_MODEL)


def query_knowledge(
    query_text: str,
    db_path: str | Path = "chroma_db",
    n_results: int = 3,
) -> list[dict]:
    """
    Embed query_text locally and retrieve the top-n most relevant knowledge chunks.

    Returns a list of dicts:
        [{"source": "owasp/injection", "heading": "Parameterized Queries", "content": "..."}]

    Returns [] gracefully if the collection doesn't exist yet.
    """
    chroma = chromadb.PersistentClient(path=str(db_path))

    existing = [c.name for c in chroma.list_collections()]
    if COLLECTION_NAME not in existing:
        return []

    collection = chroma.get_collection(COLLECTION_NAME)
    if collection.count() == 0:
        return []

    model        = _get_model()
    query_vector = model.encode([query_text], convert_to_numpy=True)[0].tolist()

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas"],
    )

    chunks = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append({
            "source":  meta.get("source", ""),
            "heading": meta.get("heading", ""),
            "content": doc,
        })

    return chunks