# src/nuvemshop_sdk/resources/products.py
"""
ProductsResource — Nuvemshop Product API.

🧠 Nuvemshop Model Enforcement:
  1. If ``stock`` is detected at the product root in ``create()`` or
     ``update()`` → raise ``ValidationError``.
  2. If no variants are provided in ``create()`` → auto-create a default
     variant so the product is never variantless.
"""

from __future__ import annotations

from typing import Any, Optional

from ..exceptions import ValidationError
from .base import ResourceCRUD


# Fields that MUST NOT appear at the product root because they only
# exist on variants in the real Nuvemshop model.
_VARIANT_ONLY_FIELDS = frozenset({"stock", "inventory_quantity"})


class ProductsResource(ResourceCRUD):
    """Manage products on the Nuvemshop API.

    Usage::

        # List
        products = client.products.list(per_page=50)

        # Lazy iterate all
        for p in client.products.iter_all():
            print(p["name"])

        # Create (variants are required or auto-generated)
        client.products.create({
            "name": {"pt": "Camiseta"},
            "variants": [{"price": "49.90", "stock": 10}]
        })
    """

    endpoint = "products"

    # ------------------------------------------------------------------
    # Overrides with model enforcement
    # ------------------------------------------------------------------

    def create(
        self,
        data: dict[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a product.

        Raises:
            ValidationError: If stock-related fields are set at the
                product root (they must be on variants).
        """
        self._block_root_stock(data)
        self._ensure_variants(data)
        return super().create(data, idempotency_key=idempotency_key)

    def update(self, resource_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Update a product (PUT).

        Raises:
            ValidationError: If stock-related fields are set at the
                product root.
        """
        self._block_root_stock(data)
        return super().update(resource_id, data)

    def patch(self, resource_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Partially update a product (PATCH).

        Raises:
            ValidationError: If stock-related fields are set at the
                product root.
        """
        self._block_root_stock(data)
        return super().patch(resource_id, data)

    # ------------------------------------------------------------------
    # Enforcement helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _block_root_stock(data: dict[str, Any]) -> None:
        """Raise if any variant-only field appears at the product root."""
        offending = _VARIANT_ONLY_FIELDS & data.keys()
        if offending:
            raise ValidationError(
                f"Stock/inventory fields {offending} must be set on "
                f"variants, not at the product root.  Use "
                f"client.variants.update_stock() instead.",
                status_code=422,
                error_code="INVALID_PRODUCT_STOCK",
                error_description=(
                    "Nuvemshop model rule: inventory exists only at "
                    "the variant level."
                ),
            )

    @staticmethod
    def _ensure_variants(data: dict[str, Any]) -> None:
        """Auto-create a default variant if none are provided.

        The Nuvemshop API requires every product to have at least one
        variant.  If the caller omits variants entirely, we inject a
        minimal default to keep the payload valid.
        """
        if "variants" not in data or not data["variants"]:
            data["variants"] = [{}]
