# 2. Structured JSON logging and a single error shape

Date: 2026-09-21
Status: Accepted

## Context

The service will run as many pods behind a load balancer, and a single user action
will later cross the API, a queue, a worker and an LLM call. We need to find all logs
for one request, and clients need predictable error responses.

## Decision

- Log to stdout as one JSON object per line, using the standard library `logging`.
- Assign each request a correlation ID (`X-Request-ID`), store it in a `ContextVar`,
  and include it in every log line and every error response.
- Return every failure as `{"error": {"code", "message", "request_id", "details?"}}`.
  Unhandled exceptions return a generic message; the traceback goes only to the logs.

## Consequences

- Logs are directly filterable in Loki/Grafana with no parsing rules.
- Clients branch on the stable `code`, not on message text.
- Standard-library logging keeps dependencies low and works with OpenTelemetry later.
  The trade-off is slightly more hand-written code than a library such as structlog.
- A crash produces two log entries: ours (with the request ID) and uvicorn's.
