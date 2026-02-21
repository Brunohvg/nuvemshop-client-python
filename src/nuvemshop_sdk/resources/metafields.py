# src/nuvemshop_sdk/resources/metafields.py
"""
MetafieldsResource — Nuvemshop Metafields API.
"""

from __future__ import annotations

from typing import Any, Optional

from .base import BaseResource


class MetafieldsResource(BaseResource):
    """Manage metafields for products, variants, or orders.

    Endpoints:
      - /products/{product_id}/metafields
      - /orders/{order_id}/metafields
    """

    def list_for_product(self, product_id: int) -> list[dict[str, Any]]:
        """List metafields for a product."""
        return self._http.get(f"products/{product_id}/metafields")

    def create_for_product(self, product_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Create a metafield for a product."""
        return self._http.post(f"products/{product_id}/metafields", data=data)

    def list_for_order(self, order_id: int) -> list[dict[str, Any]]:
        """List metafields for an order."""
        return self._http.get(f"orders/{order_id}/metafields")

    def create_for_order(self, order_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Create a metafield for an order."""
        return self._http.post(f"orders/{order_id}/metafields", data=data)
