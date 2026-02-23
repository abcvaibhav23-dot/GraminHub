"""Shared service-layer exceptions."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ServiceError(Exception):
    message: str
    status_code: int = 400

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


class ValidationError(ServiceError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)


class UnauthorizedError(ServiceError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=401)


class ForbiddenError(ServiceError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=403)


class NotFoundError(ServiceError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=404)


class ConflictError(ServiceError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=409)


class TooManyRequestsError(ServiceError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=429)
