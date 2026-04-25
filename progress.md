# Pragma — Progress

## Current Project Structure
```
pragma/
  app/
    agent/
      __init__.py
      loop.py             ✅ done (async, per-loop semaphores, Groq)
      models.py           ✅ done
      parser.py           ✅ done
      reporter.py         ✅ done (persona-based HTML + embedded MD download)
      router.py           ✅ done (dynamic model routing by chunk count)
      scanner.py          ✅ done (p/security-audit ruleset)
    rag/
      __init__.py
      chunker.py          ✅ done
      embedder.py         ✅ done
      ingestor.py         ✅ done (Windows-safe force_rmtree)
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
    pragma_code           ✅ (code chunks per repo, Gemini embeddings, 768-dim)
    pragma_knowledge      ✅ 635 chunks ingested (sentence-transformers/all-MiniLM-L6-v2, 384-dim)
  pyproject.toml
  README.md
```

---

## ✅ Alpha Complete

Pragma's alpha version is fully functional end-to-end. All core modules are wired and working.

---

## What Was Built

### Async Audit Loop (`agent/loop.py`) ✅
- **Parallel Processing**: Uses `asyncio.gather` with per-loop semaphores (created inside `run_async`, not at module level) to process multiple vulnerabilities simultaneously without hitting rate limits.
- **Persona-Aware Logic**: Generates distinct `technical`, `ceo`, and `public` analysis for every finding.
- **Dynamic Routing**: Integration with `get_chunk_count` and `router.py` ensures the model scales (Flash vs Pro) based on repo size.
- **Groq backend**: Switched to `AsyncGroq` for fast inference.

### Persona-Based Reporting (`agent/reporter.py`) ✅
- **Dynamic HTML**: Supports three viewing modes (CEO Executive Summary, Public, Technical Auditor).
- **CEO Accordion**: Hides technical code blocks behind `<details>` tags for executive views.
- **Embedded Downloads**: Inlines base64 Markdown data so users can download reports without extra server hits.
- `build_html()` returns HTML string directly (used by the streaming endpoint).
- `generate_report()` writes HTML to disk (used by the download endpoint).

### Robust Ingestion (`rag/ingestor.py`) ✅
- **Windows Compatibility**: `force_rmtree` with `os.chmod` handles read-only `.git` pack files that caused `Access Denied` errors on Windows.

---

## Key Technical Decisions

- **Two separate ChromaDB collections**: `pragma_code` (Gemini embeddings, 768-dim) and `pragma_knowledge` (MiniLM, 384-dim) — queried independently, no dimension conflict.
- **Local embeddings for knowledge base**: `all-MiniLM-L6-v2` via sentence-transformers — no rate limits, fully offline, ~90MB cached model.
- **Static knowledge base**: curated once, committed to repo, never re-fetched.
- **Python pinned to `>=3.12,<3.13`** — 3.14 breaks ChromaDB + pydantic.
- **Semaphores created inside `run_async`** — module-level semaphores caused `KeyError: '_type'` due to cross-loop lifecycle issues with ChromaDB's internal config deserialization.
- **`p/security-audit` ruleset** — targets AI-generated / "vibe coded" patterns more precisely than the generic `auto` config.

---

## FastAPI Endpoints

### Wired and Working
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest/github` | Ingest a GitHub repo by URL |
| POST | `/ingest/zip` | Ingest a repo from uploaded ZIP file |
| POST | `/query` | Query ChromaDB with a natural language string |
| POST | `/audit` | Runs Semgrep scan + parse, returns findings JSON (no LLM) |
| GET | `/audit/report/html` | Streams persona-specific HTML directly to browser |
| GET | `/audit/report/download` | Serves persona-specific HTML as a file download |

### ⚠️ Frontend Note
`/audit/report/html` and `/audit/report/download` are placeholder endpoints for the MVP.
Once the React frontend is built, these will likely be replaced or removed entirely —
the frontend will consume raw JSON from `/audit` and render its own UI.
Revisit both endpoints when starting the frontend phase.

---

## Known Issues / Minor TODOs
- ChromaDB telemetry warnings (`capture() takes 1 positional argument but 3 were given`) — harmless version mismatch, safe to ignore.
- LLM occasionally returns malformed JSON (unescaped apostrophes in values) — one finding per run may silently fail. Fix: tighten prompt to explicitly ban apostrophes in values, or add a JSON repair step.
- `n_results` auto-capped by ChromaDB when a repo has fewer chunks than requested — harmless warning, expected on small repos.

---

## What's Next (Post-Alpha)

### Near-term
- **Fix JSON robustness**: Prompt hardening + fallback repair for malformed LLM responses.
- **React Frontend**: Replace HTML report endpoints with a proper dashboard that consumes `/audit` JSON directly.

### Future
- **Snyk integration**: Dependency-level vulnerability scanning.
- **Multi-Repo Comparison**: Security trends across multiple audited projects.
- **Dynamic model routing refinement**: Better thresholds for Flash vs Pro vs Opus selection.