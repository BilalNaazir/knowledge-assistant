"""Application errors and the one JSON error shape the API returns."""

from typing import Any

from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str  # stable, machine-readable, e.g. "not_found"
    message: str  # human-readable
    request_id: str | None = None
    details: list[dict[str, Any]] | None = None  # used for validation errors


class ErrorResponse(BaseModel):
    error: ErrorBody


class AppError(Exception):
    """Base class for errors we raise on purpose. Subclasses set the HTTP mapping."""

    status_code: int = 500
    code: str = "internal_error"
    default_message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    default_message = "Resource not found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
    default_message = "The request conflicts with the current state"


class PermissionDeniedError(AppError):
    status_code = 403
    code = "permission_denied"
    default_message = "You do not have permission to do that"
