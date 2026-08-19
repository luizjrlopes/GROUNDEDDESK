# GroundedDesk

[English](README.md) | [Português](README.pt-BR.md)

**GroundedDesk** is a multi-tenant B2B support platform with governed knowledge management and evidence-grounded RAG. It combines tickets, queues, SLAs, knowledge operations, hybrid search, AI-assisted responses and auditing in one operational flow.

The architecture keeps critical decisions under application control: AI can assist with drafting responses, but it does not control ticket transitions, authorization, message delivery or business rules.

## Overview

Core capabilities include:

- multi-tenant support with organization-level isolation;
- JWT authentication, RBAC and tenant-scoped data access;
- tickets, queues, priorities, SLAs and explicit state transitions;
- comments, agent responses and attachment metadata;
- versioned knowledge base with reprocessing;
- asynchronous document ingestion;
- chunking and embeddings for semantic retrieval;
- hybrid lexical + vector search;
- result fusion through Reciprocal Rank Fusion (RRF);
- AI-assisted responses with citations and groundedness scoring;
- mandatory human review before assisted responses are sent;
- deterministic fallback when the AI provider is unavailable;
- audit trail for domain, retrieval and AI events.

## Architecture

```text
Browser / Next.js
        │ JWT
        ▼
FastAPI API
  │
  ├── authentication and authorization
  ├── tickets and SLA
  ├── knowledge base
  ├── hybrid search / RAG
  ├── AI assistance
  └── auditing
        │
        ▼
PostgreSQL + pgvector
  │
  ├── transactional data
  ├── documents and chunks
  ├── embeddings
  ├── audit events
  └── transactional ingestion queue
        ▲
        │
   Python Worker
```

PostgreSQL acts as both transactional and vector storage, reducing infrastructure requirements while preserving relational integrity across tickets, documents, chunks, citations and audit events.

## Stack

### Frontend
- Next.js 16
- React 19
- TypeScript
- App Router

### Backend
- Python 3.13
- FastAPI
- SQLAlchemy 2
- Pydantic
- JWT

### Data and search
- PostgreSQL 18
- pgvector
- lexical and vector retrieval
- Reciprocal Rank Fusion

### Asynchronous processing
- Python worker
- transactional PostgreSQL queue
- `FOR UPDATE SKIP LOCKED`

### Local infrastructure
- Docker
- Docker Compose

## Evidence-grounded RAG

```text
Question / ticket context
        │
        ▼
Authorized retrieval
        │
        ├── lexical score
        └── vector score
                │
                ▼
        Reciprocal Rank Fusion
                │
                ▼
        Evidence + citations
                │
                ▼
           AI assistance
                │
                ▼
           Human review
                │
                ▼
               Send
```

The AI layer is provider-agnostic and uses a deterministic local implementation by default, allowing the environment to run without paid external services.

## Security and governance

- authorization enforced server-side;
- tenant isolation at the data layer;
- separate roles for operations, management, knowledge administration and auditing;
- AI-assisted responses require human review;
- relevant events are recorded for auditability;
- AI-provider failures do not interrupt the primary ticket workflow.

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

- Web: `http://localhost:3000`
- API / OpenAPI: `http://localhost:8000/docs`

The API initializes the required schema and local data. The worker processes ingestion jobs stored in PostgreSQL.

## Repository structure

```text
GroundedDesk/
├── apps/
│   ├── api/              # FastAPI, domain, persistence, worker and tests
│   └── web/              # Next.js user interface
├── docs/                 # Architecture, RAG, security and technical docs
├── scripts/              # Deterministic repository validation
├── docker-compose.yml
└── .github/workflows/
```

## Validation

```bash
python scripts/validate_repo.py
pip install ./apps/api
python -m unittest discover apps/api/tests -v
cd apps/web
npm ci
npm run typecheck
npm run build
```

CI runs backend and frontend checks on pushes to `main` and pull requests.

## Technical documentation

- `docs/architecture.md`
- `docs/rag.md`
- `docs/security.md`
- `docs/demo.md`

## License

This project is distributed under the terms defined in `LICENSE`.
