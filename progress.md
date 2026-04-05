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

## What Was Built

### `agent/reporter.py` ✅
- Input: `list[AuditResult]` + mode (`autopilot` / `manual`)
- Output: self-contained HTML report with embedded MD download button (no server round-trip)
- Autopilot mode: severity, file/line, plain-English explanation, fix
- Manual mode: adds Semgrep rule ID, raw AST chunks, fix as diff block
- `generate_report()` returns a single `Path` (HTML only — MD is embedded inside)

### `knowledge/` ✅
- `fetch_sources.py` — one-time fetcher, 46 sources (31 OWASP + 15 CWE), saves as .md files
- `md_chunker.py` — splits docs by `##` / `###` headings into `KnowledgeChunk` objects
- `ingest.py` — CLI (`python -m knowledge.ingest`), local embeddings via `sentence-transformers/all-MiniLM-L6-v2`, resumable, no API calls
- `query.py` — queries `pragma_knowledge` collection, model cached via `lru_cache`, graceful `[]` fallback

### `agent/loop.py` updated ✅
- After code chunk retrieval, calls `query_knowledge(rag_query)` — reuses Flash's generated query, no extra LLM call
- Knowledge chunks injected into audit prompt as separate section: `[source — heading]\ncontent`
- Fully graceful — if KB not built, audit still runs normally

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

### New (built, not yet wired into main.py)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/audit` | Run full agent loop, return JSON + write HTML report |
| GET | `/audit/report/html` | Run audit, return HTML inline |
| GET | `/audit/report/download` | Run audit, serve HTML file as download |

---

## What's Left

### Next Session
- **Dynamic model routing** — Flash → Gemini 2.5 Pro → Claude Opus by repo size
- **Wire `/audit` endpoints** into `main.py`
- **Async loop** — parallel finding processing

### Future
- Snyk integration