"""Liveness and readiness probes, used by Docker and Kubernetes."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus(BaseModel):
    status: Literal["ok"] = "ok"


@router.get("/live", summary="Liveness probe")
async def live() -> HealthStatus:
    """The process is running."""
    return HealthStatus()


@router.get("/ready", summary="Readiness probe")
async def ready() -> HealthStatus:
    """The service can take traffic. Dependency checks (Postgres, Redis) come later."""
    return HealthStatus()
