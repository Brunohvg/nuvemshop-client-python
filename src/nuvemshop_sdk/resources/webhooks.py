# src/nuvemshop_sdk/resources/webhooks.py
"""
WebhooksResource — Nuvemshop Webhook API.

Provides CRUD for webhook subscriptions and re-exports the
``verify_webhook_signature`` utility for convenience.
"""

from __future__ import annotations

from .base import ResourceCRUD

# Re-export for convenience: client.webhooks.verify_signature(...)
from ..utils.webhook import verify_webhook_signature


class WebhooksResource(ResourceCRUD):
    """Manage webhook subscriptions on the Nuvemshop API.

    Usage::

        # Subscribe to order events
        client.webhooks.create({
            "event": "order/created",
            "url": "https://myapp.example.com/hooks/orders",
        })

        # Verify incoming webhook signature
        is_valid = client.webhooks.verify_signature(
            body=request.data,
            signature=request.headers["X-Linkedstore-HMAC-SHA256"],
            secret="your_client_secret",
        )
    """

    endpoint = "webhooks"

    @staticmethod
    def verify_signature(
        body: bytes | str,
        signature: str,
        secret: str,
        *,
        timestamp: float | None = None,
        max_age_seconds: float = 300.0,
    ) -> bool:
        """Verify a Nuvemshop webhook signature.

        Delegates to :func:`~nuvemshop_sdk.utils.webhook.verify_webhook_signature`.
        """
        return verify_webhook_signature(
            body=body,
            signature=signature,
            secret=secret,
            timestamp=timestamp,
            max_age_seconds=max_age_seconds,
        )
