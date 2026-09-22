# 4. Testcontainers for database integration tests

Date: 2026-09-21
Status: Accepted

## Context

Unit tests use fake dependency checks so they run fast and need no infrastructure.
That proves our logic is correct but never proves our actual SQL, connection
settings, or Postgres-specific behavior (like the pgvector extension) work for real.

## Decision

Add a separate `integration` test suite that starts a real, throwaway Postgres
(the same `pgvector/pgvector:pg17` image used in Compose and production) via
Testcontainers, scoped to one container per test session. Mark these tests with
`@pytest.mark.integration` and exclude them from the default `pytest` / pre-commit
run; run them explicitly via `make test-integration`.

## Consequences

- Fast day-to-day feedback loop (unit tests only) stays fast.
- Integration tests need Docker running locally and in CI.
- Confidence that real SQL and the pgvector extension actually work, not just that
  our code calls the right functions.
- The test container starts once per session (a few seconds), not once per test.
