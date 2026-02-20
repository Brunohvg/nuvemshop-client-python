# src/nuvemshop_sdk/models/customer.py
"""Customer model for Nuvemshop."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from .base import NuvemshopBaseModel


class Customer(NuvemshopBaseModel):
    """A customer in Nuvemshop."""

    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    identification: Optional[str] = None
    note: Optional[str] = None
    default_address: Optional[dict[str, Any]] = None
    addresses: Optional[list[dict[str, Any]]] = None
    billing_name: Optional[str] = None
    billing_phone: Optional[str] = None
    billing_address: Optional[str] = None
    billing_number: Optional[str] = None
    billing_floor: Optional[str] = None
    billing_locality: Optional[str] = None
    billing_city: Optional[str] = None
    billing_province: Optional[str] = None
    billing_zipcode: Optional[str] = None
    billing_country: Optional[str] = None
    total_spent: Optional[str] = None
    total_spent_currency: Optional[str] = None
    orders_count: Optional[int] = None
    last_order_id: Optional[int] = None
    active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
