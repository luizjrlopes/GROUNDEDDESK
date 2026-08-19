# Architecture

GroundedDesk is split into a browser application, an HTTP API, a PostgreSQL database and a background worker. PostgreSQL is deliberately both the transactional store and the vector store: it keeps the portfolio deployment small while preserving relational integrity between knowledge documents, chunks, citations, tickets and audit events.

```text
Browser / Next.js
       | JWT
       v
FastAPI API ------------------------------+
  | tickets / auth / audit                |
  | knowledge / search / AI draft         |
  v                                       |
PostgreSQL 18 + pgvector                  |
  |                                       |
  +-- transactional domain tables         |
  +-- knowledge chunks + embeddings       |
  +-- ingestion_jobs <--- Python worker --+
```

The API owns authorization, tenant filtering, state transitions and audit creation. The worker only claims and processes ingestion jobs. The AI provider never owns ticket transitions or message delivery.
