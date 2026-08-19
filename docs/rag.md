# RAG design

The retrieval path is explicit and inspectable.

1. Normalize the query.
2. Generate a deterministic local embedding (default demo provider).
3. Load authorized PostgreSQL-backed chunks and score them lexically in the application layer.
4. Read their pgvector embeddings and compute vector similarity in the application layer.
5. Fuse candidate ranks with reciprocal-rank fusion.
6. Keep the top evidence set.
7. Produce an answer draft only from that evidence.
8. Return citations, per-channel scores and groundedness.
9. Require a human action before the draft can become a ticket reply.

The local provider is intentionally deterministic so a clone can run offline. A real model provider can implement the same `AIProvider` interface later.
