# src/nuvemshop_sdk/models/variant.py
"""
Variant model — the fundamental unit of inventory in Nuvemshop.

🧠 Nuvemshop Model Rule:
  - Inventory (stock) exists ONLY at the variant level.
  - SKU is per variant.
  - Price is per variant.
  - A product ALWAYS has at least one variant.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from .base import NuvemshopBaseModel


class Variant(NuvemshopBaseModel):
    """A product variant in Nuvemshop.

    All inventory, price, and SKU data lives here — never at the
    product root.
    """

    id: Optional[int] = None
    product_id: Optional[int] = None
    sku: Optional[str] = None
    name: Optional[str] = None
    price: Optional[str] = None
    compare_at_price: Optional[str] = None
    promotional_price: Optional[str] = None
    stock: Optional[int] = None
    stock_management: Optional[bool] = None
    weight: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    depth: Optional[str] = None
    position: Optional[int] = None
    image_id: Optional[int] = None
    barcode: Optional[str] = None
    values: Optional[list[dict[str, Any]]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
