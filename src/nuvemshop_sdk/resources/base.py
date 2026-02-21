# src/nuvemshop_sdk/resources/base.py
"""
Base resource class for the Nuvemshop SDK.

Provides standard CRUD methods (``list``, ``get``, ``create``, ``update``,
``delete``) and pagination helpers (``iter_all``, ``get_all``).

Every concrete resource inherits from :class:`ResourceCRUD` and only
needs to set its ``endpoint`` (and optionally override methods to enforce
Nuvemshop model rules).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator, Optional

from ..utils.pagination import paginate, paginate_collect

if TYPE_CHECKING:
    from ..http_client import HttpClient


class BaseResource:
    """Minimal base that holds a reference to the HTTP client."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http


class ResourceCRUD(BaseResource):
    """
    Recurso genérico com suporte a operações CRUD e paginação integrada.

    As subclasses devem definir o atributo ``endpoint`` (ex: ``"products"``).
    """

    endpoint: str = ""

    # ------------------------------------------------------------------
    # Basic CRUD
    # ------------------------------------------------------------------

    def list(
        self,
        *,
        page: int = 1,
        per_page: int = 50,
        next_url: Optional[str] = None,
        **filters: Any,
    ) -> list[dict[str, Any]] | tuple[list[dict[str, Any]], dict[str, str]]:
        """List resources with support for page/per_page or next_url."""
        # Use next_url if provided (standard 2025-03 practice)
        if next_url:
            result, headers = self._http.get_with_headers(next_url)
        else:
            params: dict[str, Any] = {"page": page, "per_page": per_page}
            params.update(filters)
            result, headers = self._http.get_with_headers(self.endpoint, params=params)

        # Unwrapping logic (ensure list)
        items = []
        if isinstance(result, list):
            items = result
        elif isinstance(result, dict):
            for value in result.values():
                if isinstance(value, list):
                    items = value
                    break

        # If called internally by paginate(), we return headers.
        # Otherwise, for backward compatibility, we return just the list.
        # But wait, how do we know? Let's check if the caller expects it?
        # A better approach: always return a list but allow a different method or flag.
        # Actually, for the SDK to be modern, let's make it return just headers if next_url is set?
        # For simplicity, if next_url is NO-None, we return (list, headers).
        if next_url is not None:
             return items, headers
        return items

    def get(self, resource_id: int) -> dict[str, Any]:
        """Fetch a single resource by ID."""
        return self._http.get(f"{self.endpoint}/{resource_id}")

    def create(
        self,
        data: dict[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new resource."""
        return self._http.post(
            self.endpoint, data=data, idempotency_key=idempotency_key,
        )

    def update(self, resource_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Full update (PUT) of a resource."""
        return self._http.put(f"{self.endpoint}/{resource_id}", data=data)

    def patch(self, resource_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Partial update (PATCH) of a resource."""
        return self._http.patch(f"{self.endpoint}/{resource_id}", data=data)

    def delete(self, resource_id: int) -> dict[str, Any]:
        """Delete a resource."""
        return self._http.delete(f"{self.endpoint}/{resource_id}")

    # ------------------------------------------------------------------
    # Pagination helpers
    # ------------------------------------------------------------------

    def iter_all(
        self, *, per_page: int = 50, **filters: Any,
    ) -> Generator[dict[str, Any], None, None]:
        """Lazy generator — yields items one by one, fetching pages on demand.

        Memory-safe for stores with 50 k+ resources::

            for product in client.products.iter_all():
                process(product)
        """
        yield from paginate(
            self._fetch_page,
            per_page=per_page,
            **filters,
        )

    def get_all(
        self, *, per_page: int = 50, **filters: Any,
    ) -> list[dict[str, Any]]:
        """Collect all pages into a single list.

        ⚠️  Prefer ``iter_all()`` for large datasets.
        """
        return paginate_collect(
            self._fetch_page,
            per_page=per_page,
            **filters,
        )

    def _fetch_page(
        self,
        *,
        page: int = 1,
        per_page: int = 50,
        next_url: Optional[str] = None,
        **kw: Any,
    ) -> list[dict[str, Any]] | tuple[list[dict[str, Any]], dict[str, str]]:
        """Internal fetcher compatible with the pagination utility."""
        return self.list(
            page=page, per_page=per_page, next_url=next_url, **kw
        )
