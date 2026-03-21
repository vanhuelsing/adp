"""ADP SDK exceptions."""

from __future__ import annotations


class ADPError(Exception):
    """Base exception for all ADP SDK errors."""


class ADPValidationError(ADPError):
    """Raised when an ADP message fails schema validation."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


class ADPConnectionError(ADPError):
    """Raised when a network/connection error occurs."""


class ADPHTTPError(ADPError):
    """Raised when the server returns a non-2xx HTTP response."""

    def __init__(self, message: str, status_code: int, response_body: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
