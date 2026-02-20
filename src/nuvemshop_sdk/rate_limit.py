# src/nuvemshop_sdk/rate_limit.py
"""
Thread-safe, per-store rate-limit manager for the Nuvemshop SDK.

Strategy
--------
The Nuvemshop API controls its own leaky-bucket.  The SDK does **not**
simulate a local bucket.  Instead it:

1. **Reads** ``X-RateLimit-Remaining`` and ``X-RateLimit-Reset`` from every
   response.
2. **Preemptively blocks** when ``remaining == 0`` (before sending the next
   request) by sleeping until the ``reset`` timestamp.
3. **Reactively blocks** when an unexpected HTTP 429 is received, parsing
   the headers and sleeping.

Rate-limit state is indexed by ``store_id`` only, so that token rotation
does not create orphaned buckets.  Multiple stores sharing the same process
never interfere with each other.

All public methods are thread-safe.

Backward compatibility
----------------------
Public method signatures still accept a ``token`` parameter for backward
compatibility, but the parameter is **ignored** for bucket lookup purposes.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("nuvemshop_sdk.rate_limit")


# ---------------------------------------------------------------------------
# Per-store bucket state
# ---------------------------------------------------------------------------

@dataclass
class _BucketState:
    """Internal mutable state for a single store."""

    remaining: Optional[int] = None
    reset_timestamp: float = 0.0
    total_requests: int = 0
    blocked_threads: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)


# ---------------------------------------------------------------------------
# Public metrics DTO
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RateLimitStatus:
    """Snapshot of the current rate-limit state for a store."""

    remaining: Optional[int]
    reset_timestamp: float
    blocked_threads: int
    total_requests: int


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class RateLimitManager:
    """Thread-safe rate-limit controller indexed by ``store_id``.

    Token rotation is safe: swapping the access_token for a store
    does NOT create a new bucket.

    Usage (inside ``HttpClient``)::

        rl = RateLimitManager()

        # Before sending a request:
        rl.wait_if_needed(store_id, token)

        # After receiving a response:
        rl.update_from_headers(store_id, token, response.headers)
    """

    def __init__(self) -> None:
        self._buckets: dict[int, _BucketState] = {}
        self._global_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Bucket access  (keyed by store_id only)
    # ------------------------------------------------------------------

    def _get_bucket(self, store_id: int) -> _BucketState:
        if store_id not in self._buckets:
            with self._global_lock:
                # Double-checked locking
                if store_id not in self._buckets:
                    self._buckets[store_id] = _BucketState()
        return self._buckets[store_id]

    # ------------------------------------------------------------------
    # Pre-request: preemptive wait
    # ------------------------------------------------------------------

    def wait_if_needed(self, store_id: int, token: str = "") -> None:
        """Block the calling thread if the bucket for this store is empty.

        This is called **before** every HTTP request.

        Args:
            store_id: The Nuvemshop store ID.
            token: Kept for backward compatibility; ignored for lookup.
        """
        bucket = self._get_bucket(store_id)
        with bucket.lock:
            if bucket.remaining is not None and bucket.remaining <= 0:
                wait_seconds = max(0.0, bucket.reset_timestamp - time.time())
                if wait_seconds > 0:
                    bucket.blocked_threads += 1
                    logger.info(
                        "Rate limit preemptive wait",
                        extra={
                            "store_id": store_id,
                            "wait_seconds": round(wait_seconds, 2),
                            "reset_timestamp": bucket.reset_timestamp,
                        },
                    )

        # Sleep outside the lock so other threads can also compute their
        # wait time without being blocked.
        if bucket.remaining is not None and bucket.remaining <= 0:
            wait_seconds = max(0.0, bucket.reset_timestamp - time.time())
            if wait_seconds > 0:
                time.sleep(wait_seconds)
            with bucket.lock:
                bucket.blocked_threads = max(0, bucket.blocked_threads - 1)

    # ------------------------------------------------------------------
    # Post-response: update state from headers
    # ------------------------------------------------------------------

    def update_from_headers(
        self,
        store_id: int,
        token: str,
        headers: dict[str, str],
    ) -> None:
        """Parse ``X-RateLimit-*`` headers and update the bucket state.

        Expected headers (case-insensitive lookup):
          - ``X-RateLimit-Remaining``
          - ``X-RateLimit-Reset``

        Args:
            store_id: The Nuvemshop store ID.
            token: Kept for backward compatibility; ignored for lookup.
            headers: Response headers dict.
        """
        bucket = self._get_bucket(store_id)

        # Case-insensitive header lookup
        lower_headers = {k.lower(): v for k, v in headers.items()}

        raw_remaining = lower_headers.get("x-ratelimit-remaining")
        raw_reset = lower_headers.get("x-ratelimit-reset")

        with bucket.lock:
            bucket.total_requests += 1

            if raw_remaining is not None:
                try:
                    bucket.remaining = int(raw_remaining)
                except (ValueError, TypeError):
                    pass

            if raw_reset is not None:
                try:
                    bucket.reset_timestamp = float(raw_reset)
                except (ValueError, TypeError):
                    pass

        logger.debug(
            "Rate limit headers updated",
            extra={
                "store_id": store_id,
                "remaining": bucket.remaining,
                "reset_timestamp": bucket.reset_timestamp,
            },
        )

    # ------------------------------------------------------------------
    # Reactive: called when 429 is received
    # ------------------------------------------------------------------

    def handle_429(
        self,
        store_id: int,
        token: str,
        headers: dict[str, str],
    ) -> float:
        """Update state from a 429 response and return seconds to wait.

        The caller (``HttpClient``) should sleep for the returned duration
        before retrying.

        Args:
            store_id: The Nuvemshop store ID.
            token: Kept for backward compatibility; ignored for lookup.
            headers: Response headers dict.
        """
        self.update_from_headers(store_id, token, headers)
        bucket = self._get_bucket(store_id)

        with bucket.lock:
            bucket.remaining = 0
            wait_seconds = max(0.0, bucket.reset_timestamp - time.time())

        # Fallback: if the server didn't send a reset header, wait 2 s.
        if wait_seconds <= 0:
            wait_seconds = 2.0

        logger.warning(
            "Rate limit 429 received — reactive wait",
            extra={
                "store_id": store_id,
                "wait_seconds": round(wait_seconds, 2),
            },
        )
        return wait_seconds

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def get_status(self, store_id: int, token: str = "") -> RateLimitStatus:
        """Return a read-only snapshot of the rate-limit state.

        Args:
            store_id: The Nuvemshop store ID.
            token: Kept for backward compatibility; ignored for lookup.
        """
        bucket = self._get_bucket(store_id)
        with bucket.lock:
            return RateLimitStatus(
                remaining=bucket.remaining,
                reset_timestamp=bucket.reset_timestamp,
                blocked_threads=bucket.blocked_threads,
                total_requests=bucket.total_requests,
            )
