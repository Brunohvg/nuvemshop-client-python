# src/nuvemshop_sdk/utils/webhook.py
"""
Webhook security utilities for the Nuvemshop SDK.

Features:
  - HMAC SHA-256 signature validation
  - Timing-safe comparison via ``hmac.compare_digest()``
  - Timestamp replay-attack protection (configurable window, default 5 min)

Usage::

    from nuvemshop_sdk.utils.webhook import verify_webhook_signature

    is_valid = verify_webhook_signature(
        body=request.data,
        signature=request.headers["X-Linkedstore-HMAC-SHA256"],
        secret="your_client_secret",
    )
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Optional


def verify_webhook_signature(
    body: bytes | str,
    signature: str,
    secret: str,
    *,
    timestamp: Optional[float] = None,
    max_age_seconds: float = 300.0,  # 5 minutes
) -> bool:
    """Validate a Nuvemshop webhook request.

    Args:
        body: The raw request body (bytes or UTF-8 string).
        signature: The HMAC signature sent in the webhook header.
        secret: Your application's client secret.
        timestamp: Unix timestamp from the webhook (optional).
            If provided, replay protection is enforced.
        max_age_seconds: Maximum age in seconds for replay protection.

    Returns:
        ``True`` if the signature is valid and the timestamp (if given)
        is within the acceptable window.

    Security:
        - Uses ``hmac.compare_digest()`` to prevent timing attacks.
        - Rejects expired timestamps to prevent replay attacks.
    """
    # 1. Replay protection
    if timestamp is not None:
        age = abs(time.time() - timestamp)
        if age > max_age_seconds:
            return False

    # 2. Normalize body to bytes
    if isinstance(body, str):
        body = body.encode("utf-8")

    # 3. Compute expected HMAC
    expected = hmac.new(
        key=secret.encode("utf-8"),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # 4. Timing-safe comparison
    return hmac.compare_digest(expected, signature)
