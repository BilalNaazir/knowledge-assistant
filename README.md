# Knowledge Assistant

A multi-tenant AI knowledge assistant: upload documents, connect structured data,
ask questions, get cited answers.

## Repository layout

| Path        | Purpose                                   |
|-------------|-------------------------------------------|
| `backend/`  | Python / FastAPI service and workers      |
| `frontend/` | TypeScript / Next.js web app              |
| `infra/`    | Terraform, Kubernetes manifests           |
| `evals/`    | RAG and agent evaluation harness          |
| `docs/adr/` | Architecture Decision Records             |
