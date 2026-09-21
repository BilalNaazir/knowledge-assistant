"""Aggregates every v1 router under the /api/v1 prefix."""

from fastapi import APIRouter

from assistant.api.v1 import meta

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(meta.router)
