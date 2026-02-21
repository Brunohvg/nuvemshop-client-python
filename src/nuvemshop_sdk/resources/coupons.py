# src/nuvemshop_sdk/resources/coupons.py
"""
CouponsResource — Nuvemshop Coupons API.
"""

from __future__ import annotations

from .base import ResourceCRUD


class CouponsResource(ResourceCRUD):
    """Manage discount coupons on the Nuvemshop API.

    Usage::

        # List
        coupons = client.coupons.list()

        # Create
        client.coupons.create({
            "code": "NATAL10",
            "type": "percentage",
            "value": "10.00"
        })
    """

    endpoint = "coupons"
