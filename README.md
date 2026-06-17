# Enterprise Agentic RAG

A production-style Enterprise Agentic RAG platform for organizational knowledge assistance. It combines FastAPI, LangGraph, LlamaIndex, ChromaDB, PostgreSQL, Ollama/Llama 3, Tavily web search, and a React/Tailwind dashboard.

## What Is Included

- Multi-workspace document ingestion for PDF, DOCX, TXT, CSV, and Markdown.
- Hybrid retrieval with Chroma dense vectors and BM25 keyword ranking.
- Agent workflow with routing, retrieval, Tavily web search, response generation, verification, and reflection.
- Ollama-backed response generation with `llama3`.
- Hugging Face embeddings with `BAAI/bge-small-en-v1.5`.
- JWT auth, role-based access, resumable conversations, feedback, analytics, and evaluation report scaffolding.
- Docker Compose stack for PostgreSQL, ChromaDB, Ollama, backend, and frontend.

## Quick Start

1. Copy `.env.example` to `.env` and set `TAVILY_API_KEY`.
2. Start the stack:

```powershell
docker compose up --build
```

3. Pull the Llama 3 model if your Ollama volume does not already have it:

```powershell
docker compose exec ollama ollama pull llama3
```

4. Open the app at `http://localhost:5173`.
5. Register the first account. The first registered account becomes an admin.

Backend API docs are available at `http://localhost:8000/docs`.

## Local Checks

```powershell
./scripts/check.ps1
```

This runs backend tests and the frontend production build.

## Project Layout

```text
backend/app
  agents/       LangGraph-oriented multi-agent workflow
  api/          FastAPI routers
  auth/         JWT and role dependencies
  db/           SQLAlchemy models and sessions
  ingestion/    parsing and chunking
  retrieval/    Chroma, BM25, hybrid ranking
  services/     application use cases
frontend/src
  features/     chat, document management, analytics
  components/   reusable UI elements
docs/           architecture, API, deployment notes
```

## Notes

- This repository is ready to be initialized and pushed to GitHub with `git init`, `git add .`, and your normal remote workflow.
- Demo video recording is an external deliverable; the app and docs are structured so a demo can show upload, indexing, chat, citations, feedback, and analytics.
