"""Shared error types for v2 domains."""
from __future__ import annotations


class AppError(Exception):
    """Base class for business-rule and application errors."""


class NotFound(AppError):
    pass


class Forbidden(AppError):
    pass


class Conflict(AppError):
    pass


class ValidationError(AppError):
    pass

