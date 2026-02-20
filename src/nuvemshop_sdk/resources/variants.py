# src/nuvemshop_sdk/resources/variants.py
"""
VariantsResource — Nuvemshop Variant API.

🧠 The variant is the FUNDAMENTAL unit of inventory in Nuvemshop.
All stock, SKU, and price operations MUST happen here.

Endpoints follow the pattern:
  ``products/{product_id}/variants``
  ``products/{product_id}/variants/{variant_id}``
"""

from __future__ import annotations

from typing import Any, Generator, Optional

from ..utils.pagination import paginate, paginate_collect
from .base import BaseResource


class VariantsResource(BaseResource):
    """Manage product variants (the authoritative source for stock, SKU,
    and price).

    Usage::

        # List all variants for a product
        variants = client.variants.list(product_id=123)

        # Update stock (variant-level only!)
        client.variants.update_stock(product_id=123, variant_id=456, stock=50)

        # Update price
        client.variants.update_price(
            product_id=123, variant_id=456, price="79.90"
        )
    """

    # ------------------------------------------------------------------
    # Endpoint helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _endpoint(product_id: int, variant_id: Optional[int] = None) -> str:
        base = f"products/{product_id}/variants"
        if variant_id is not None:
            return f"{base}/{variant_id}"
        return base

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def list(
        self,
        product_id: int,
        *,
        page: int = 1,
        per_page: int = 50,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """List variants for a product."""
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        params.update(filters)
        result = self._http.get(self._endpoint(product_id), params=params)
        if isinstance(result, list):
            return result
        return result  # type: ignore[return-value]

    def get(self, product_id: int, variant_id: int) -> dict[str, Any]:
        """Fetch a single variant."""
        return self._http.get(self._endpoint(product_id, variant_id))

    def create(
        self,
        product_id: int,
        data: dict[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new variant for a product."""
        return self._http.post(
            self._endpoint(product_id),
            data=data,
            idempotency_key=idempotency_key,
        )

    def update(
        self,
        product_id: int,
        variant_id: int,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Full update (PUT) of a variant."""
        return self._http.put(
            self._endpoint(product_id, variant_id),
            data=data,
        )

    def patch(
        self,
        product_id: int,
        variant_id: int,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Partial update (PATCH) of a variant."""
        return self._http.patch(
            self._endpoint(product_id, variant_id),
            data=data,
        )

    def delete(self, product_id: int, variant_id: int) -> dict[str, Any]:
        """Delete a variant."""
        return self._http.delete(self._endpoint(product_id, variant_id))

    # ------------------------------------------------------------------
    # Domain-specific convenience methods
    # ------------------------------------------------------------------

    def update_stock(
        self,
        product_id: int,
        variant_id: int,
        stock: int,
    ) -> dict[str, Any]:
        """Update the stock quantity for a specific variant.

        This is the ONLY correct way to update inventory in Nuvemshop.
        """
        return self.patch(product_id, variant_id, {"stock": stock})

    def update_price(
        self,
        product_id: int,
        variant_id: int,
        price: str,
        *,
        compare_at_price: Optional[str] = None,
        promotional_price: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update the price of a specific variant."""
        payload: dict[str, Any] = {"price": price}
        if compare_at_price is not None:
            payload["compare_at_price"] = compare_at_price
        if promotional_price is not None:
            payload["promotional_price"] = promotional_price
        return self.patch(product_id, variant_id, payload)

    def update_sku(
        self,
        product_id: int,
        variant_id: int,
        sku: str,
    ) -> dict[str, Any]:
        """Update the SKU of a specific variant."""
        return self.patch(product_id, variant_id, {"sku": sku})

    # ------------------------------------------------------------------
    # Pagination
    # ------------------------------------------------------------------

    def iter_all(
        self,
        product_id: int,
        *,
        per_page: int = 50,
        **filters: Any,
    ) -> Generator[dict[str, Any], None, None]:
        """Lazy generator — yields all variants for a product."""

        def _fetcher(
            *, page: int = 1, per_page: int = 50, **kw: Any,
        ) -> list[dict[str, Any]]:
            return self.list(product_id, page=page, per_page=per_page, **kw)

        yield from paginate(_fetcher, per_page=per_page, **filters)

    def get_all(
        self,
        product_id: int,
        *,
        per_page: int = 50,
        **filters: Any,
    ) -> list[dict[str, Any]]:
        """Collect all variants for a product into a list."""

        def _fetcher(
            *, page: int = 1, per_page: int = 50, **kw: Any,
        ) -> list[dict[str, Any]]:
            return self.list(product_id, page=page, per_page=per_page, **kw)

        return paginate_collect(_fetcher, per_page=per_page, **filters)
