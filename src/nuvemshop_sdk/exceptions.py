# src/nuvemshop_sdk/exceptions.py
"""
Exceptions layer for the Nuvemshop SDK.

Every exception parses `error_code` and `error_description` from the API
JSON response body so callers never receive raw text blobs.

Status → Exception mapping:
    401 → UnauthorizedError
    402 → StoreInactiveError
    403 → ForbiddenError
    422 → ValidationError
    429 → RateLimitError
    5xx → ServerError

Network / connection failures → NetworkError
"""

from __future__ import annotations

from typing import Any, Optional


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class NuvemshopError(Exception):
    """Base exception for every SDK error."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        error_description: Optional[str] = None,
        response_body: Optional[Any] = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.error_description = error_description
        self.response_body = response_body
        super().__init__(message)

    def __repr__(self) -> str:
        parts = [f"status_code={self.status_code}"]
        if self.error_code:
            parts.append(f"error_code={self.error_code!r}")
        if self.error_description:
            parts.append(f"error_description={self.error_description!r}")
        return f"{self.__class__.__name__}({', '.join(parts)})"


# ---------------------------------------------------------------------------
# HTTP mapped exceptions (never retried for business errors)
# ---------------------------------------------------------------------------

class UnauthorizedError(NuvemshopError):
    """401 — Invalid or expired access token."""


class StoreInactiveError(NuvemshopError):
    """402 — The store subscription is inactive / unpaid."""


class ForbiddenError(NuvemshopError):
    """403 — The token lacks the required scope."""


class ValidationError(NuvemshopError):
    """422 — The request payload failed server-side validation."""


class RateLimitError(NuvemshopError):
    """429 — Rate limit exceeded. Check `retry_after` attribute."""

    def __init__(
        self,
        message: str,
        *,
        retry_after: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


class ServerError(NuvemshopError):
    """5xx — An unexpected error on the Nuvemshop side."""


# ---------------------------------------------------------------------------
# Network / transport
# ---------------------------------------------------------------------------

class NetworkError(NuvemshopError):
    """Connection timeout, DNS failure, or any transport-level error."""


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_STATUS_MAP: dict[int, type[NuvemshopError]] = {
    401: UnauthorizedError,
    402: StoreInactiveError,
    403: ForbiddenError,
    422: ValidationError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: ServerError,
}


def raise_for_status(status_code: int, body: Any, headers: dict[str, str] | None = None) -> None:
    """Parse the API response and raise the appropriate exception.

    This function is the ONLY place where HTTP status codes are converted to
    SDK exceptions. It guarantees that ``error_code`` and
    ``error_description`` are always extracted from the JSON body when
    available.
    """
    error_code: Optional[str] = None
    error_description: Optional[str] = None
    message_parts: list[str] = []

    # Try to extract structured error fields from JSON body
    if isinstance(body, dict):
        error_code = body.get("code") or body.get("error") or body.get("error_code")
        error_description = (
            body.get("description")
            or body.get("error_description")
            or body.get("message")
        )
    elif isinstance(body, str):
        error_description = body

    if error_code:
        message_parts.append(f"[{error_code}]")
    if error_description:
        message_parts.append(str(error_description))
    if not message_parts:
        message_parts.append(f"HTTP {status_code}")

    message = " ".join(message_parts)

    # Build common kwargs
    kwargs: dict[str, Any] = dict(
        status_code=status_code,
        error_code=error_code,
        error_description=error_description,
        response_body=body,
    )

    # Special-case 429: attach retry_after
    if status_code == 429:
        retry_after: Optional[float] = None
        if headers:
            raw = headers.get("x-ratelimit-reset") or headers.get("retry-after")
            if raw:
                try:
                    retry_after = float(raw)
                except (ValueError, TypeError):
                    pass
        raise RateLimitError(message, retry_after=retry_after, **kwargs)

    # Lookup the mapped exception class
    exc_cls = _STATUS_MAP.get(status_code)
    if exc_cls is None and 500 <= status_code < 600:
        exc_cls = ServerError

    if exc_cls is None:
        exc_cls = NuvemshopError

    raise exc_cls(message, **kwargs)
