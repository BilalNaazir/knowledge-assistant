# 1. Use a monorepo

Date: 2026-09-21
Status: Accepted

## Context

The project has a Python backend, a TypeScript frontend, infrastructure code and an
evaluation harness. Changes often span several of these, for example a new API field
plus the UI that uses it.

## Decision

Keep everything in one Git repository, in top-level folders: `backend/`, `frontend/`,
`infra/`, `evals/` and `docs/`.

## Consequences

- A cross-cutting change lands in one pull request, and CI can test it as a whole.
- One place for issues, history and access control.
- CI must be path-aware so a docs-only change doesn't rebuild everything.
- The repository grows over time. This is acceptable at this project's size.
