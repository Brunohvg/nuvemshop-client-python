# src/nuvemshop_sdk/resources/stores.py
"""StoresResource — Nuvemshop Store API."""

from __future__ import annotations

from typing import Any

from .base import BaseResource


class StoresResource(BaseResource):
    """Read store information.

    Usage::

        info = client.stores.get()
    """

    def get(self) -> dict[str, Any]:
        """Fetch the current store's information."""
        return self._http.get("store")
