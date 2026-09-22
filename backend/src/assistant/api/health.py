"""Liveness and readiness probes, used by Docker and Kubernetes."""

import asyncio
import logging
from collections.abc import Awaitable, Callable, Mapping
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel

from assistant.config import Settings, get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

# A readiness check is an async function that raises if its dependency is unhealthy.
ReadinessCheck = Callable[[], Awaitable[None]]


class HealthStatus(BaseModel):
    status: Literal["ok"] = "ok"


class ReadinessReport(BaseModel):
    status: Literal["ok", "unavailable"]
    checks: dict[str, str]  # dependency name -> "ok" or "failed"


def get_readiness_checks(request: Request) -> Mapping[str, ReadinessCheck]:
    """The dependency checks the app registered at startup (see main.py)."""
    checks: Mapping[str, ReadinessCheck] = request.app.state.readiness_checks
    return checks


async def _run_check(name: str, check: ReadinessCheck, timeout: float) -> bool:
    try:
        await asyncio.wait_for(check(), timeout=timeout)
    except Exception:
        # Log the reason for operators, but never return it to the caller.
        logger.warning("readiness check failed", extra={"dependency": name}, exc_info=True)
        return False
    return True


@router.get("/live", summary="Liveness probe")
async def live() -> HealthStatus:
    """The process is running. Deliberately checks nothing else."""
    return HealthStatus()


@router.get(
    "/ready",
    summary="Readiness probe",
    responses={503: {"model": ReadinessReport, "description": "A dependency is unavailable"}},
)
async def ready(
    response: Response,
    checks: Annotated[Mapping[str, ReadinessCheck], Depends(get_readiness_checks)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ReadinessReport:
    """Report whether the service can take traffic, by really talking to its dependencies."""
    names = list(checks)
    results = await asyncio.gather(
        *(_run_check(name, checks[name], settings.readiness_timeout_seconds) for name in names)
    )

    healthy = all(results)
    if not healthy:
        response.status_code = 503

    return ReadinessReport(
        status="ok" if healthy else "unavailable",
        checks={name: "ok" if ok else "failed" for name, ok in zip(names, results, strict=True)},
    )
