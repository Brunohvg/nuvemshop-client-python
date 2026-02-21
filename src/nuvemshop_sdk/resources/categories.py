# src/nuvemshop_sdk/resources/categories.py
"""
CategoriesResource — Nuvemshop Category API.
"""

from __future__ import annotations

from .base import ResourceCRUD


class CategoriesResource(ResourceCRUD):
    """Manage categories on the Nuvemshop API.

    Usage::

        # List
        categories = client.categories.list()

        # Create
        client.categories.create({
            "name": {"pt": "Novidades"},
            "description": {"pt": "Produtos recém-chegados"}
        })
    """

    endpoint = "categories"
