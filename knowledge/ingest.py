"""
knowledge/ingest.py
CLI entry point — walks knowledge/sources/, chunks every .md file,
embeds each chunk using a local sentence-transformers model, and upserts
into the 'pragma_knowledge' ChromaDB collection.

No API calls, no rate limits, runs fully offline after first model download.

Usage:
    python -m knowledge.ingest
    python -m knowledge.ingest --sources-dir knowledge/sources --db-path chroma_db
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from knowledge.md_chunker import chunk_file, KnowledgeChunk

# ── Config ────────────────────────────────────────────────────
COLLECTION_NAME  = "pragma_knowledge"
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"  # 384-dim, fast, no API needed
BATCH_SIZE       = 64                   # local model — no rate limits, go fast


# ── Embedding ─────────────────────────────────────────────────

def embed_texts(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


# ── Ingest ────────────────────────────────────────────────────

def ingest(sources_dir: Path, db_path: Path) -> None:
    # ── Collect all .md files ──────────────────────────────
    md_files = sorted(sources_dir.rglob("*.md"))
    if not md_files:
        print(f"[pragma-knowledge] No .md files found in {sources_dir}")
        sys.exit(1)

    print(f"[pragma-knowledge] Found {len(md_files)} source file(s)")

    # ── Chunk all files ────────────────────────────────────
    all_chunks: list[KnowledgeChunk] = []
    for path in md_files:
        chunks = chunk_file(path, base_dir=sources_dir)
        print(f"  {path.relative_to(sources_dir)}  →  {len(chunks)} chunk(s)")
        all_chunks.extend(chunks)

    print(f"[pragma-knowledge] Total chunks: {len(all_chunks)}")

    # ── Load local embedding model ─────────────────────────
    print(f"[pragma-knowledge] Loading embedding model '{EMBEDDING_MODEL}'...")
    print(f"                   (downloads ~90MB on first run, cached after)")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print(f"[pragma-knowledge] Model loaded.")

    # ── ChromaDB setup ─────────────────────────────────────
    chroma     = chromadb.PersistentClient(path=str(db_path))
    collection = chroma.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # ── Skip already-ingested chunks ───────────────────────
    existing_ids: set[str] = set()
    try:
        existing_ids = set(collection.get(include=[])["ids"])
        if existing_ids:
            print(f"[pragma-knowledge] {len(existing_ids)} chunks already ingested — skipping those.")
    except Exception:
        pass

    # ── Embed + upsert in batches ──────────────────────────
    total    = len(all_chunks)
    upserted = 0
    skipped  = 0

    for batch_start in range(0, total, BATCH_SIZE):
        batch = all_chunks[batch_start : batch_start + BATCH_SIZE]
        ids   = [
            f"{c.source}::{hashlib.md5(c.content.encode()).hexdigest()[:12]}"
            for c in batch
        ]

        new_indices = [i for i, id_ in enumerate(ids) if id_ not in existing_ids]
        if not new_indices:
            skipped += len(batch)
            continue

        batch = [batch[i] for i in new_indices]
        ids   = [ids[i] for i in new_indices]
        texts = [c.content for c in batch]
        metas = [{"source": c.source, "heading": c.heading} for c in batch]

        embeddings = embed_texts(model, texts)

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metas,
        )

        upserted += len(batch)
        print(f"  Upserted {upserted}/{total} chunks...")

    print(f"[pragma-knowledge] ✅ Done. {upserted} new, {skipped} skipped. "
          f"Total in '{COLLECTION_NAME}': {collection.count()}.")


# ── CLI ───────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pragma-knowledge",
        description="Ingest curated security docs into the Pragma knowledge base.",
    )
    parser.add_argument(
        "--sources-dir",
        type=Path,
        default=Path("knowledge/sources"),
        help="Directory containing curated .md source files (default: knowledge/sources)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("chroma_db"),
        help="Path to the ChromaDB persistent store (default: chroma_db)",
    )
    args = parser.parse_args()

    if not args.sources_dir.exists():
        print(f"[pragma-knowledge] ERROR: sources dir not found: {args.sources_dir}")
        sys.exit(1)

    ingest(sources_dir=args.sources_dir, db_path=args.db_path)


if __name__ == "__main__":
    main()