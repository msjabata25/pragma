# Pragma — Agent Loop Progress

## Session Summary
Built the full agent loop (`loop.py`) connecting all existing Pragma modules into a working pipeline.

---

## Files Built This Session

### `agent/models.py`
Defines the two core data structures:
- `Finding` — raw Semgrep output (check_id, path, stLine, msg, severity)
- `AuditResult` — Finding + agent output (finding, relevant_chunks, explanation, fix)

### `agent/parser.py`
- Function: `parse(semgrep_output: dict) -> list[Finding]`
- Loops through `semgrep_output["results"]` and maps each result to a `Finding`
- Handles nested fields: `result["start"]["line"]`, `result["extra"]["message"]` etc.

### `scanner.py` (refactored)
- Function: `scan(repo_path: str) -> dict`
- Runs Semgrep via subprocess, returns parsed JSON
- Uses `json.loads(result.stdout)`, try/except/else pattern
- Model used: `gemini-2.5-flash` (2.0 was crashing)

### `agent/loop.py` ✅ COMPLETE
The main agent loop. Full pipeline:

```
scan() → parse() → [per finding]:
  1. Flash generates RAG query (query_prompt)
  2. embed_query() → query_vector
  3. query_chunks() → chunks
  4. Flash explains vuln + generates fix (audit_prompt) → JSON
  5. AuditResult appended to results
→ return list[AuditResult]
```

Key implementation details:
- `repo_id = os.path.basename(repo_path)` — derived from path
- `client` initialized once outside the loop
- `chunks_text = "\n\n".join([c["content"] for c in chunks])` — for prompt injection
- JSON stripping safety net before parsing Flash response:
  ```python
  clean = res.text.strip().removeprefix("```json").removesuffix("```").strip()
  data = json.loads(clean)
  ```
- `relevant_chunks=[c["content"] for c in chunks]` — list[str] not joined string

---

## Current Project Structure
```
pragma/
  app/
    agent/
      __init__.py
      loop.py             ✅ done
      models.py           ✅ done
      parser.py           ✅ done
      scanner.py          ✅ done
    rag/
      __init__.py
      chunker.py          ✅ done (prev session)
      embedder.py         ✅ done (prev session)
      ingestor.py         ✅ done (prev session)
      store.py            ✅ done (prev session)
    main.py
  chroma_db/
  output.json
  progress.md
  pyproject.toml
  README.md
  test_chunker.py
```

---

## `app/main.py` — Existing FastAPI Endpoints
Already wired up and working:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest/github` | Ingest a GitHub repo by URL |
| POST | `/ingest/zip` | Ingest a repo from uploaded ZIP file |
| POST | `/query` | Query ChromaDB with a natural language string |

Not yet wired: the agent loop (`run()`) has no endpoint yet — next session.

---

## What's Left

### Next Session — Report Builder
- Input: `list[AuditResult]`
- Output: human-readable report (format TBD — markdown or HTML)
- Should work for both Autopilot mode (vibe coders) and Manual mode (experienced devs)

### Future
- Snyk integration (not installed yet — Semgrep only for now)
- Dynamic model routing: Flash → Gemini 2.5 Pro → Claude Opus by repo size
- FastAPI endpoints wiring `run()` to the REST layer
- Async loop for parallel finding processing