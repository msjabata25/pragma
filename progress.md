# Pragma — Progress

## Current Project Structure
```
pragma/
  app/
    agent/
      __init__.py
      loop.py             ✅ done (updated — knowledge base integration)
      models.py           ✅ done
      parser.py           ✅ done
      reporter.py         ✅ done (new)
      scanner.py          ✅ done
    rag/
      __init__.py
      chunker.py          ✅ done
      embedder.py         ✅ done
      ingestor.py         ✅ done
      store.py            ✅ done
    knowledge/
      __init__.py         ✅ done
      md_chunker.py       ✅ done
      ingest.py           ✅ done
      query.py            ✅ done
      fetch_sources.py    ✅ done (one-time, already run)
      sources/
        owasp/            ✅ 31 curated cheat sheets fetched
        cwe/              ✅ 15 CWE definitions fetched
    main.py
  chroma_db/
    pragma_code           ✅ (code chunks per repo)
    pragma_knowledge      ✅ 635 chunks ingested (sentence-transformers/all-MiniLM-L6-v2)
  pyproject.toml
  README.md
```

---

## What Was Recently Built

### Async Audit Loop (`agent/loop.py`) ✅
- **Parallel Processing**: Uses `asyncio.gather` with semaphores to process multiple vulnerabilities simultaneously without hitting Gemini rate limits.
- **Persona-Aware Logic**: Generates distinct `technical`, `ceo`, and `public` analysis for every finding.
- **Dynamic Routing**: Integration with `get_chunk_count` ensures the model scales (Flash vs Pro) based on repo size.

### Persona-Based Reporting (`agent/reporter.py`) ✅
- **Dynamic HTML**: Supports three viewing modes (CEO Executive Summary, Public, Technical Auditor).
- **CEO Accordion**: Intelligently hides technical code blocks behind details tags for executive views.
- **Embedded Downloads**: Inlines base64 Markdown data so users can download reports without extra server hits.

### Robust Ingestion (`rag/ingestor.py`) ✅
- **Windows Compatibility**: Implemented `force_rmtree` with `os.chmod` to handle read-only `.git` pack files that previously caused `Access Denied` errors on Windows.

---

## Key Technical Decisions
- **Strict Data Modeling**: Moved from a flat `AuditResult` to a nested structure (`technical`, `ceo`, `public` objects) to maintain data integrity across the RAG pipeline.
- **Security-First Scanning**: Updated `scanner.py` to use `p/security-audit` instead of `auto` config to ensure "vibe coded" vulnerabilities are detected.
- **Absolute Imports**: Shifted all internal calls to `app.<module>` format to support running the server from the root directory.

---

## Key Technical Decisions
- **Two separate ChromaDB collections**: `pragma_code` (Gemini embeddings, 768-dim) and `pragma_knowledge` (MiniLM, 384-dim) — queried independently, no dimension conflict
- **Local embeddings for knowledge base**: `all-MiniLM-L6-v2` via sentence-transformers — no rate limits, offline, ~90MB cached model
- **Static knowledge base**: curated once, committed to repo, never re-fetched
- **Python pinned to `>=3.12,<3.13`** — 3.14 breaks ChromaDB + pydantic

---

## FastAPI Endpoints

### Existing (wired, working)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest/github` | Ingest a GitHub repo by URL |
| POST | `/ingest/zip` | Ingest a repo from uploaded ZIP file |
| POST | `/query` | Query ChromaDB with a natural language string |
| POST | `/audit` | Runs full persona audit, returns JSON, writes HTML |
| GET | `/audit/report/html` | Streams persona-specific HTML directly to browser |
| GET | `/audit/report/download` | Serves persona-specific HTML as a file download |



---

## What's Left

### Future
- **Snyk integration** for dependency-level vulnerability scanning.
- **Frontend Dashboard**: Transition from raw HTML reports to a React-based interface.
- **Multi-Repo Comparison**: Allowing users to see security trends across multiple audited projects.