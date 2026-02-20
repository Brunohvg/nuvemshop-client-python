# src/nuvemshop_sdk/resources/orders.py
"""
OrdersResource — Nuvemshop Order API.

🧠 Nuvemshop Model Rule:
  Orders should be processed via webhooks (event-driven).
  Polling-based order sync should be avoided.
"""

from __future__ import annotations

from .base import ResourceCRUD


class OrdersResource(ResourceCRUD):
    """Manage orders on the Nuvemshop API.

    Usage::

        # Get a single order
        order = client.orders.get(order_id=789)

        # List recent orders (but prefer webhooks for real-time processing)
        orders = client.orders.list(per_page=50, status="open")

        # Iterate all orders lazily
        for order in client.orders.iter_all(status="closed"):
            archive(order)
    """

    endpoint = "orders"
