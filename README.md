# Pragma 🔍
> *Your code is cooked. Pragma knows it. And now, so do you.*

---

## What is this?

Maybe you vibed your way through a project. Maybe you paid someone to build 
your business website. Maybe ChatGPT wrote 80% of it and it works — kinda — 
and you're not asking questions.

**The problem?** That code is probably a security nightmare. Hardcoded secrets,
SQL injection waiting to happen, auth that breaks if you look at it wrong.
Nobody checked it. And honestly, neither did the AI that generated it.

**Pragma fixes that.**

Pragma is an agentic code auditor that scans your repo, finds the issues, and
actually explains what's wrong — in plain English, not in "refer to CWE-89 for
further details." It then tells you exactly how to fix it.

No security degree required. No dev on speed dial required.

---

## Who is this for?

**If you can't read code:**
- You own a restaurant, a shop, a startup — someone built you a website and 
  you just... hope it's fine
- You hired a freelancer and have no way to verify their work is secure
- You're about to launch something and the words "data breach" keep you up

**If you can:**
- Vibe coders who ship first and ask questions never
- Beginners using Cursor, Copilot, or any AI tool to build projects
- Anyone who's looked at their own codebase and thought *"I hope nobody 
  checks this"*

If you've ever deployed something and immediately closed the tab out of fear —
this is for you.

---

## How it works

1. **Drop your repo in.** Pragma accepts a ZIP upload or a GitHub URL and 
   ingests it automatically.
2. **Issues get flagged.** Semgrep scans your code deterministically — not 
   guessing, actually finding.
3. **The agent kicks in.** For each finding, it retrieves the exact relevant 
   code chunks from a RAG pipeline and hands them to a judge model.
4. **You get a clean report.** Plain English. Concrete fixes. Ready to act on.

No noise. No "potential vulnerability detected in 47 files good luck."
Just what's wrong and how to make it not wrong.

---

## Stack
*(for the devs)*

- **FastAPI** — backend
- **ChromaDB + gemini-embedding-001** — RAG pipeline with AST-aware code 
  chunking
- **Semgrep** — deterministic vulnerability scanning
- **Gemini 2.5 Flash** — RAG query generation + judge model
- **Gemini 2.5 Pro / Claude Opus** — larger model routing for bigger repos 
  (coming soon)

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

Because `#pragma` is a compiler directive — it tells the compiler what to do
*before* it starts running.

Pragma tells *you* what to do before your code goes live.

---

## Follow the build

Shipping in public. Progress, demos, and the occasional existential crisis.

[![Instagram](https://img.shields.io/badge/Instagram-@p__rag__ma-E1306C?style=flat&logo=instagram&logoColor=white)](https://www.instagram.com/p_rag_ma?)

---
*Built by a robotics freshman who got tired of watching people deploy broken 
code and call it a feature.*
