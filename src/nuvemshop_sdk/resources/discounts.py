# src/nuvemshop_sdk/resources/discounts.py
"""
DiscountsResource — Nuvemshop Discounts API.
"""

from __future__ import annotations

from .base import ResourceCRUD


class DiscountsResource(ResourceCRUD):
    """Manage discounts on the Nuvemshop API.
    """

    endpoint = "discounts"
