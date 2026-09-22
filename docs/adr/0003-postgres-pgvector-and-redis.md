# 3. PostgreSQL with pgvector for data, Redis for ephemeral state

Date: 2026-09-21
Status: Accepted

## Context

The system stores relational data (tenants, users, documents, conversations, tickets)
and vector embeddings for retrieval. It also needs fast ephemeral state such as rate
limits and caches.

## Decision

- Use PostgreSQL with the pgvector extension for both relational and vector data.
- Use Redis for rate limiting and caching only. Anything that must survive lives in
  Postgres.
- Local development runs both in Docker Compose. Production uses RDS and ElastiCache.
- Object storage is deferred to the ingestion phase. MinIO's community edition was
  archived in April 2026, so an S3-compatible replacement will be chosen then, behind
  our own storage interface. Production uses AWS S3.

## Consequences

- One database to operate, back up and secure. Row-Level Security can cover
  embeddings too, and hybrid queries can mix SQL filters with vector search.
- pgvector is less specialised than a dedicated vector database. We accept that at
  this scale and can revisit it if benchmarks show a bottleneck.
- Readiness probes check only the dependencies the service actually uses.
