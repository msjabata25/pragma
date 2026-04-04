# Pragma 🔍

> *Your code is cooked. Pragma knows it. And now, so do you.*

---

## What is this?

You vibed your way through a project. ChatGPT wrote 80% of it. It works. Kinda. You're not totally sure why, but it does, and you're not asking questions.

**The problem?** That code is probably a security nightmare. Hardcoded secrets, SQL injection waiting to happen, auth that breaks if you look at it wrong. You didn't write it, so you don't know. And honestly, neither does the AI that generated it.

**Pragma fixes that.**

Pragma is an agentic code auditor that scans your repo, finds the issues, and actually explains what's wrong — in plain English, not in "refer to CWE-89 for further details." It then tells you exactly how to fix it. No security degree required.

---

## How it works

1. **Drop your repo in.** Pragma accepts a ZIP upload or a GitHub URL and ingests it automatically.
2. **Issues get flagged.** Semgrep scans your code deterministically — not guessing, actually finding.
3. **The agent kicks in.** For each finding, it retrieves the exact relevant code chunks from a RAG pipeline and hands them to a judge model.
4. **You get a clean report.** Plain English. Concrete fixes. Ready to copy-paste.

No noise. No "potential vulnerability detected in 47 files good luck." Just the thing that's wrong and how to make it not wrong.

---

## Who is this for?

- Vibe coders who ship first and ask questions never
- Beginners using Cursor, Copilot, or any AI tool to build projects
- Anyone who's looked at their own code and thought *"I hope nobody checks this"*

If you've ever deployed something and immediately closed the tab out of fear — this is for you.

---

## Stack

- **FastAPI** — backend
- **ChromaDB + gemini-embedding-001** — RAG pipeline with AST-aware code chunking
- **Semgrep** — deterministic vulnerability scanning
- **Gemini 2.5 Flash** — RAG query generation + judge model
- **Gemini 2.5 Pro / Claude Opus** — larger model routing (coming soon)

---

## Current Endpoints

| Method | Endpoint | What it does |
|--------|----------|--------------|
| POST | `/ingest/github` | Ingest a repo by GitHub URL |
| POST | `/ingest/zip` | Ingest a repo from a ZIP upload |
| POST | `/query` | Query the RAG pipeline directly |
| POST | `/audit` | Run the full agent loop on a repo *(in progress)* |

---

## Status

🟡 **Core pipeline complete. Report generation in progress.**

- ✅ AST-aware code chunker
- ✅ Embedding + ChromaDB storage
- ✅ GitHub + ZIP ingestion
- ✅ Semgrep scanner
- ✅ Agent loop (scan → RAG → explain → fix)
- 🚧 Report builder
- 🚧 Frontend

This is not production-ready yet. But it will be.

---

## Why "Pragma"?

Because `#pragma` is a compiler directive. It tells the compiler what to do before it starts.

Pragma tells *you* what to do before your code goes live.

---

*Built by a robotics freshman who got tired of watching people deploy broken code and call it a feature.*