# API

The backend exposes OpenAPI documentation at `/docs` when running locally.

## Auth

- `POST /api/auth/register` creates an account. The first account becomes admin.
- `POST /api/auth/login` returns a bearer token.
- `GET /api/auth/me` returns the current user.

## Workspaces

- `GET /api/workspaces` lists accessible workspaces.
- `POST /api/workspaces` creates a workspace for admins.
- `DELETE /api/workspaces/{workspace_id}` deletes a workspace for admins.
- `POST /api/workspaces/{workspace_id}/members/{user_id}` grants workspace access.

## Documents

- `POST /api/documents/upload` ingests a file into a workspace.
- `GET /api/documents` lists documents, optionally filtered by `workspace_id`.
- `DELETE /api/documents/{document_id}` removes metadata, chunks, and vectors.

## Chat

- `POST /api/chat` returns a complete answer.
- `POST /api/chat/stream` streams Server-Sent Events:
  - `token` events contain incremental answer text.
  - `done` contains the final answer, citations, confidence, route, and reflection count.
  - `error` contains failure details.

## Feedback, Analytics, Evaluation

- `POST /api/feedback` stores a 1-5 rating for an assistant message.
- `GET /api/analytics/summary` returns query, latency, retrieval, feedback, and document totals.
- `GET /api/analytics/documents` returns the most cited documents.
- `POST /api/evaluations/run` creates a RAGAS report placeholder until a labeled dataset is supplied.
