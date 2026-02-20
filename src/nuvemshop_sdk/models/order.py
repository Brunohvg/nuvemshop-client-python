# src/nuvemshop_sdk/models/order.py
"""
Order model for Nuvemshop.

🧠 Nuvemshop Model Rule:
  - Orders are webhook-driven.
  - Polling should be avoided in favour of event-based processing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from .base import NuvemshopBaseModel


class OrderItem(NuvemshopBaseModel):
    """A line item inside an order."""

    id: Optional[int] = None
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    name: Optional[str] = None
    price: Optional[str] = None
    quantity: Optional[int] = None
    sku: Optional[str] = None
    weight: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    depth: Optional[str] = None
    free_shipping: Optional[bool] = None


class Order(NuvemshopBaseModel):
    """An order in Nuvemshop."""

    id: Optional[int] = None
    number: Optional[int] = None
    token: Optional[str] = None
    store_id: Optional[int] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None
    shipping_status: Optional[str] = None
    gateway: Optional[str] = None
    gateway_id: Optional[str] = None
    currency: Optional[str] = None
    language: Optional[str] = None
    subtotal: Optional[str] = None
    discount: Optional[str] = None
    shipping: Optional[str] = None
    shipping_option: Optional[str] = None
    total: Optional[str] = None
    total_usd: Optional[str] = None
    weight: Optional[str] = None
    note: Optional[str] = None
    customer: Optional[dict[str, Any]] = None
    products: Optional[list[OrderItem]] = None
    shipping_address: Optional[dict[str, Any]] = None
    billing_address: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None
