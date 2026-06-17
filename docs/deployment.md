# Deployment

## Local Docker Compose

```powershell
copy .env.example .env
docker compose up --build
docker compose exec ollama ollama pull llama3
```

Services:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- ChromaDB: `http://localhost:8001`
- PostgreSQL: `localhost:5432`

## Production Considerations

- Replace `JWT_SECRET_KEY` with a strong secret.
- Move uploaded source files to object storage if retention is required.
- Run Alembic migrations rather than `create_all` startup initialization.
- Put backend and frontend behind HTTPS.
- Restrict CORS to approved domains.
- Use managed PostgreSQL with backups.
- Run ChromaDB with persistent storage or a managed vector backend.
- Configure centralized logs and metrics for agent traces, latency, feedback, and tool failures.

## GitHub And Demo Video

Initialize the repository, push it to a public GitHub remote, then record a demo that covers:

- Admin registration and workspace creation.
- Document upload and indexing.
- Streaming chat answer with citations.
- Feedback submission.
- Analytics dashboard.
- API docs and architecture diagram.
