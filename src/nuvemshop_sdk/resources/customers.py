# src/nuvemshop_sdk/resources/customers.py
"""CustomersResource — Nuvemshop Customer API."""

from __future__ import annotations

from .base import ResourceCRUD


class CustomersResource(ResourceCRUD):
    """Manage customers on the Nuvemshop API."""

    endpoint = "customers"
