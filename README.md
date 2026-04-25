# `pragma` 🔍
> *Your code is cooked. Pragma knows it. And now, so do you.*

---

## What is this?

Maybe you vibed your way through a project. Maybe you paid someone to build your business website. Maybe ChatGPT wrote 80% of it and it works — kinda — and you're not asking questions.

**The problem?** That code is probably a security nightmare. Hardcoded secrets, SQL injection waiting to happen, auth that breaks if you look at it wrong. Nobody checked it. And honestly, neither did the AI that generated it.

**Pragma fixes that.**

Pragma is an agentic security auditor that scans your repo, finds the vulnerabilities, and explains what's wrong — in plain English, not in *"refer to CWE-89 for further details."* Then it tells you exactly how to fix it, with a working code snippet you can paste in directly.

No security degree required. No dev on speed dial required.

---

## Who is this for?

**If you can't read code:**
- You own a restaurant, a shop, a startup — someone built you a website and you just... hope it's fine
- You hired a freelancer and have no way to verify their work is secure
- You're about to launch something and the words *"data breach"* keep you up at night

**If you can:**
- Vibe coders who ship first and ask questions never
- Beginners using Cursor, Copilot, or any AI tool to build real projects
- Anyone who's looked at their own codebase and thought *"I hope nobody checks this"*

If you've ever deployed something and immediately closed the tab out of fear — this is for you.

---

## How it works

```
your repo
    │
    ▼
[ Semgrep ]  ──────────────────────────────────────────  deterministic scan
    │                                                     no hallucinations,
    │                                                     actual findings only
    ▼
[ RAG Pipeline ]  ─────────────────────────────────────  pulls the exact
    │              ChromaDB · AST-aware chunking          code chunks relevant
    │              OWASP + CWE knowledge base             to each finding
    ▼
[ Judge Model ]  ──────────────────────────────────────  explains the bug,
    │              Groq · Flash / Pro routing             gives you the fix,
    │                                                     writes the fixed code
    ▼
[ Report ]  ────────────────────────────────────────────  3 modes:
                                                          CEO · Public · Technical
```

1. **Drop your repo in** via ZIP upload or GitHub URL
2. **Semgrep scans it** deterministically — not guessing, actually finding
3. **The agent kicks in** — for each finding, retrieves relevant code + security knowledge and hands it to the judge
4. **You get a clean report** — plain English, concrete fixes, copy-paste code snippets

No noise. No *"potential vulnerability detected in 47 files, good luck."*
Just what's wrong, why it matters, and how to fix it.

---

## Report Modes

Pragma generates three personas for every finding so the right person gets the right information:

| Mode | Audience | What you get |
|------|----------|--------------|
| 🛠 **Technical** | Developers | Root cause, exact fix, corrected code block |
| 💼 **CEO** | Non-technical founders | Business risk in plain English, high-level action, code snippet to hand off |
| 🌍 **Public** | Everyone else | Simple analogy, approachable explanation, beginner-friendly fix |

---

## Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI |
| Scanning | Semgrep (`p/security-audit` · `p/python` · `p/secrets`) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (knowledge) · `gemini-embedding-001` (code) |
| Vector DB | ChromaDB — two collections, no dimension conflicts |
| Knowledge Base | 46 OWASP cheat sheets · 15 CWE definitions (635 chunks, static) |
| LLM | Groq — Flash for small repos, Pro routing for larger ones |
| Chunking | AST-aware — functions and classes as atomic units, not arbitrary token windows |

---

## Endpoints

| Method | Endpoint | What it does |
|--------|----------|--------------|
| `POST` | `/ingest/github` | Ingest a repo by GitHub URL |
| `POST` | `/ingest/zip` | Ingest a repo from a ZIP upload |
| `POST` | `/query` | Query the RAG pipeline directly |
| `POST` | `/audit` | Scan + parse, returns raw findings JSON |
| `GET` | `/audit/report/html` | Full agent loop → persona report in browser |
| `GET` | `/audit/report/download` | Full agent loop → persona report as file download |

---

## Status

🟢 **Alpha complete. Frontend next.**

| Module | Status |
|--------|--------|
| AST-aware code chunker | ✅ |
| Embedding + ChromaDB storage | ✅ |
| GitHub + ZIP ingestion | ✅ |
| Semgrep scanner (multi-ruleset) | ✅ |
| OWASP + CWE static knowledge base | ✅ |
| Agent loop — scan → RAG → explain → fix | ✅ |
| Persona-based HTML reports + MD download | ✅ |
| Finding deduplication (highest severity per line) | ✅ |
| Frontend dashboard | 🚧 |
| Snyk dependency scanning | 🚧 |

This is not production-ready. But the core pipeline is real, it runs, and it works.

---

## Setup

```bash
# Clone and install
git clone https://github.com/yourhandle/pragma
cd pragma
uv sync

# Add your keys
cp .env.example .env
# Fill in GROQ_API_KEY and GEMINI_API_KEY

# Ingest the knowledge base (one-time)
uv run python app/knowledge/ingest.py

# Start the server
uv run fastapi dev app/main.py
```

> **Python version:** `>=3.12,<3.13` — 3.14 breaks ChromaDB + Pydantic. Pin it.

---

## Why "Pragma"?

`#pragma` is a compiler directive — it tells the compiler what to do *before* it starts running.

Pragma tells *you* what to do before your code goes live.

---

## Follow the build

Shipping in public. Progress, demos, and the occasional existential crisis.

[![Instagram](https://img.shields.io/badge/Instagram-@p__rag__ma-E1306C?style=flat&logo=instagram&logoColor=white)](https://www.instagram.com/p_rag_ma?)

---

*Built by a robotics freshman who got tired of watching people deploy broken code and call it a feature.*