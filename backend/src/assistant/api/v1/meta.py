"""Basic service metadata."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from assistant import __version__
from assistant.config import Settings, get_settings

router = APIRouter(tags=["meta"])


class MetaResponse(BaseModel):
    name: str
    version: str
    environment: str


@router.get("/meta", summary="Service metadata")
async def meta(settings: Annotated[Settings, Depends(get_settings)]) -> MetaResponse:
    return MetaResponse(
        name=settings.app_name,
        version=__version__,
        environment=settings.environment,
    )
