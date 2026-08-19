# GroundedDesk

GroundedDesk is a multi-tenant support desk with a governed knowledge base and evidence-first RAG. The final repository turns the validated HTML prototype into a locally runnable product: tickets and SLA remain deterministic, AI drafts require human review, retrieval exposes its evidence, and every material action is auditable.

## Final stack

- **Web:** Next.js 16.2.x, React 19.2, TypeScript, App Router
- **API:** Python 3.13, FastAPI 0.140.x, SQLAlchemy 2.0
- **Database/search:** PostgreSQL 18 + pgvector 0.8.6
- **Background processing:** transactional PostgreSQL job queue + Python worker (`FOR UPDATE SKIP LOCKED`)
- **RAG:** PostgreSQL full-text + pgvector candidate retrieval, reciprocal-rank fusion, deterministic local embedding/generation provider by default
- **Auth:** signed JWT demo sessions with server-side RBAC and tenant scoping
- **Local runtime:** Docker Compose

No paid service is required for the demo path. The AI boundary is provider-based, so a real provider can be added without changing ticket, retrieval, or audit contracts.

## Product capabilities

- demo login with Cliente, Atendente, Gestor, Admin KB and Auditor roles;
- organization-scoped data access;
- tickets, queues, priority, SLA and explicit state transitions;
- requester comments and agent replies;
- AI-assisted draft with citations and groundedness score;
- mandatory human review before sending an AI-assisted answer;
- Markdown/PDF/DOCX knowledge-document metadata and version history;
- asynchronous ingestion/reprocessing;
- chunking and deterministic local embeddings;
- hybrid lexical/vector search with visible scores and reranking;
- AI-provider failure simulation and deterministic fallback;
- immutable-style audit trail for domain, retrieval and AI events;
- repeatable seed and demo reset.

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Web: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

The API container initializes the schema and seeds demo data automatically. The worker consumes document-ingestion jobs from PostgreSQL.

## Demo flow

1. Login as **Rafael Lima / Atendente**.
2. Open ticket `GD-1842`.
3. Generate/inspect the grounded draft and citations.
4. Click **Usar como base**, review the text, and send it.
5. Open **Busca RAG** to inspect lexical/vector/RRF scores.
6. Login as **Ana Martins / Admin KB** to publish or reprocess a document.
7. Toggle **Simular falha de IA** and confirm tickets remain operable.
8. Login as **Otávio Faria / Auditor** and inspect the audit trail.

## Repository layout

```text
apps/
  api/      FastAPI API, domain services, DB models, worker and tests
  web/      Next.js application preserving the prototype interaction model
scripts/    deterministic repository validation
```

## Validation

The repository contains lightweight static/domain checks that do not require dependency installation:

```bash
python scripts/validate_repo.py
python -m unittest discover apps/api/tests -v
```

Full runtime validation, after dependencies are available:

```bash
docker compose up --build
```

## Architecture

See `docs/architecture.md`, `docs/rag.md`, `docs/security.md`, and `docs/demo.md`.
