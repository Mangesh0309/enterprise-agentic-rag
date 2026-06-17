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

