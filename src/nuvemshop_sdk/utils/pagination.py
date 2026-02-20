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


def paginate(
    fetcher: Callable[..., list[dict[str, Any]]],
    *,
    per_page: int = 50,
    start_page: int = 1,
    **filters: Any,
) -> Generator[dict[str, Any], None, None]:
    """Yield items one by one, fetching pages lazily.

    Args:
        fetcher: A callable that accepts ``page``, ``per_page``, and
            arbitrary keyword filters, and returns a list of dicts.
        per_page: Items per page (Nuvemshop max is typically 200).
        start_page: First page number (1-based).
        **filters: Extra query-string parameters forwarded to ``fetcher``.

    Yields:
        Individual resource dicts.
    """
    page = start_page
    while True:
        items = fetcher(page=page, per_page=per_page, **filters)
        if not items:
            break
        yield from items
        # If we received fewer items than requested, we're on the last page
        if len(items) < per_page:
            break
        page += 1


def paginate_collect(
    fetcher: Callable[..., list[dict[str, Any]]],
    *,
    per_page: int = 50,
    start_page: int = 1,
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
        **filters,
    ))
