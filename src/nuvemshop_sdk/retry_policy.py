# src/nuvemshop_sdk/retry_policy.py
"""
Retry policy for the Nuvemshop SDK.

Backoff strategy::

    sleep = base * 2^attempt + random_jitter

Retry ONLY for:
  - NetworkError (connection / DNS / timeout)
  - 5xx (server errors)
  - 429 (rate limit — after RateLimitManager handles the wait)

NEVER retry:
  - 401 (Unauthorized)
  - 402 (Store Inactive)
  - 403 (Forbidden)
  - 422 (Validation)

This prevents masking business-logic errors.
"""

from __future__ import annotations

import logging
import random
import time
from typing import Optional

logger = logging.getLogger("nuvemshop_sdk.retry")


# Status codes that must NEVER be retried
_NO_RETRY_STATUSES = frozenset({401, 402, 403, 422})

# Status codes eligible for retry
_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


class RetryPolicy:
    """Configurable retry policy with exponential backoff and jitter.

    Args:
        max_retries: Maximum number of retry attempts.  ``0`` disables retries.
        base_delay: Base delay in seconds for the backoff calculation.
        max_delay: Upper-bound cap for the computed delay.
        jitter_range: Maximum random jitter added to each delay (in seconds).
    """

    def __init__(
        self,
        *,
        max_retries: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 30.0,
        jitter_range: float = 0.5,
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter_range = jitter_range

    # ------------------------------------------------------------------
    # Decision helpers
    # ------------------------------------------------------------------

    @staticmethod
    def is_retryable_status(status_code: int) -> bool:
        """Return ``True`` if the status code is eligible for retry."""
        return status_code in _RETRYABLE_STATUSES

    @staticmethod
    def is_non_retryable_status(status_code: int) -> bool:
        """Return ``True`` if the status code must **never** be retried."""
        return status_code in _NO_RETRY_STATUSES

    def should_retry(
        self,
        attempt: int,
        *,
        status_code: Optional[int] = None,
        is_network_error: bool = False,
    ) -> bool:
        """Decide whether to retry.

        Args:
            attempt: Zero-based attempt index (0 = first try).
            status_code: The HTTP status code, if available.
            is_network_error: ``True`` if the failure was a network error.

        Returns:
            ``True`` if the request should be retried.
        """
        if attempt >= self.max_retries:
            return False

        if is_network_error:
            return True

        if status_code is not None:
            if self.is_non_retryable_status(status_code):
                return False
            return self.is_retryable_status(status_code)

        return False

    # ------------------------------------------------------------------
    # Delay computation
    # ------------------------------------------------------------------

    def compute_delay(self, attempt: int) -> float:
        """Return the backoff delay (in seconds) for the given attempt.

        Formula::

            delay = min(base * 2^attempt + jitter, max_delay)
        """
        exp_delay = self.base_delay * (2 ** attempt)
        jitter = random.uniform(0, self.jitter_range)  # noqa: S311
        return min(exp_delay + jitter, self.max_delay)

    def wait(self, attempt: int) -> float:
        """Sleep for the computed delay and return the duration slept."""
        delay = self.compute_delay(attempt)
        logger.info(
            "Retry backoff",
            extra={
                "attempt": attempt + 1,
                "max_retries": self.max_retries,
                "delay_seconds": round(delay, 3),
            },
        )
        time.sleep(delay)
        return delay
