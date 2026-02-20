# src/nuvemshop_sdk/utils/pagination.py
"""
Lazy pagination utilities for the Nuvemshop SDK.

The Nuvemshop API returns paginated results.  These helpers provide:

- ``paginate()``:  A **lazy generator** that yields items one by one,
  fetching pages on demand.  Memory-safe for stores with 50 k+ products.

- ``paginate_collect()``:  Convenience wrapper that collects all items
  into a list.  Use with caution on very large data sets.

Both functions are used internally by :class:`ResourceCRUD.iter_all` and
:class:`ResourceCRUD.get_all`.
"""

from __future__ import annotations

from typing import Any, Callable, Generator

# Nuvemshop API enforces a maximum of 200 items per page.
MAX_PER_PAGE: int = 200

# Safety limit to prevent infinite loops caused by API misbehavior.
# 10_000 pages × 200 items = 2 million items — generous enough for
# any legitimate store, but guaranteed to terminate.
_MAX_PAGES: int = 10_000


def paginate(
    fetcher: Callable[..., list[dict[str, Any]]],
    *,
    per_page: int = 50,
    start_page: int = 1,
    max_pages: int | None = None,
    **filters: Any,
) -> Generator[dict[str, Any], None, None]:
    """Yield items one by one, fetching pages lazily.

    Args:
        fetcher: A callable that accepts ``page``, ``per_page``, and
            arbitrary keyword filters, and returns a list of dicts.
        per_page: Items per page (clamped to ``MAX_PER_PAGE = 200``).
        start_page: First page number (1-based).
        max_pages: Optional safety limit to prevent infinite loops.
            Defaults to ``_MAX_PAGES`` (10 000).
        **filters: Extra query-string parameters forwarded to ``fetcher``.

    Yields:
        Individual resource dicts.
    """
    # Defensive: clamp per_page to API maximum
    per_page = max(1, min(per_page, MAX_PER_PAGE))
    limit = max_pages if max_pages is not None else _MAX_PAGES

    page = start_page
    pages_fetched = 0

    while pages_fetched < limit:
        items = fetcher(page=page, per_page=per_page, **filters)

        # Stop on empty response
        if not items:
            break

        yield from items
        pages_fetched += 1

        # If we received fewer items than requested → last page
        if len(items) < per_page:
            break

        # Explicit page increment
        page += 1


def paginate_collect(
    fetcher: Callable[..., list[dict[str, Any]]],
    *,
    per_page: int = 50,
    start_page: int = 1,
    max_pages: int | None = None,
    **filters: Any,
) -> list[dict[str, Any]]:
    """Collect all pages into a single list.

    ⚠️  For stores with tens of thousands of resources, prefer
    ``paginate()`` (the lazy generator) to avoid memory spikes.
    """
    return list(paginate(
        fetcher,
        per_page=per_page,
        start_page=start_page,
        max_pages=max_pages,
        **filters,
    ))
