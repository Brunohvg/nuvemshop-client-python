# src/nuvemshop_sdk/resources/inventory.py
"""
InventoryResource — Safe inventory management for the Nuvemshop SDK.

🧠 This is a **wrapper** around :class:`VariantsResource`.

Its sole purpose is to:
  1. Provide a clear ``client.inventory`` entry point for stock operations.
  2. Enforce that stock is ALWAYS updated at the variant level.
  3. Prevent misuse of product-level inventory updates.
"""

from __future__ import annotations

from typing import Any

from ..exceptions import ValidationError
from .base import BaseResource
from .variants import VariantsResource


class InventoryResource(BaseResource):
    """Inventory management — variant-level only.

    Usage::

        # Correct: update stock on a variant
        client.inventory.set_stock(
            product_id=123, variant_id=456, stock=50
        )

        # This resource exists to make the mental model explicit.
    """

    def __init__(self, variants: VariantsResource) -> None:
        self._variants = variants

    def set_stock(
        self,
        product_id: int,
        variant_id: int,
        stock: int,
    ) -> dict[str, Any]:
        """Set the stock quantity for a specific variant.

        Args:
            product_id: The product that owns the variant.
            variant_id: The variant to update.
            stock: New stock quantity (>= 0).

        Raises:
            ValidationError: If ``stock`` is negative.
        """
        if stock < 0:
            raise ValidationError(
                "Stock cannot be negative.",
                status_code=422,
                error_code="INVALID_STOCK",
                error_description="Stock value must be >= 0.",
            )
        return self._variants.update_stock(product_id, variant_id, stock)

    def get_stock(
        self,
        product_id: int,
        variant_id: int,
    ) -> int | None:
        """Read the current stock level for a variant.

        Returns:
            The stock value, or ``None`` if stock management is disabled.
        """
        variant = self._variants.get(product_id, variant_id)
        return variant.get("stock")

    def list_stock(
        self,
        product_id: int,
    ) -> list[dict[str, Any]]:
        """Return a summary of stock for all variants of a product.

        Returns a list of dicts::

            [
                {"variant_id": 1, "sku": "ABC-S", "stock": 42},
                {"variant_id": 2, "sku": "ABC-M", "stock": 0},
            ]
        """
        variants = self._variants.get_all(product_id)
        return [
            {
                "variant_id": v.get("id"),
                "sku": v.get("sku"),
                "stock": v.get("stock"),
            }
            for v in variants
        ]
