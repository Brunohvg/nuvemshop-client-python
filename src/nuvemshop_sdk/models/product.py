# src/nuvemshop_sdk/models/product.py
"""
Product model for Nuvemshop.

🧠 Nuvemshop Model Rule:
  - Products ALWAYS have variants.
  - Product-level stock updates are INVALID.
  - A product without explicit variants gets a single default variant.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from .base import NuvemshopBaseModel
from .variant import Variant


class ProductImage(NuvemshopBaseModel):
    """An image attached to a product."""

    id: Optional[int] = None
    product_id: Optional[int] = None
    src: Optional[str] = None
    position: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Product(NuvemshopBaseModel):
    """A product in Nuvemshop.

    Note: ``stock``, ``sku``, and ``price`` are authoritative **only** at
    the variant level.  The values that appear on the product root are
    informational copies of the *first* variant.
    """

    id: Optional[int] = None
    name: Optional[dict[str, str]] = None
    description: Optional[dict[str, str]] = None
    handle: Optional[dict[str, str]] = None
    categories: Optional[list[Any]] = None
    brand: Optional[str] = None
    published: Optional[bool] = None
    free_shipping: Optional[bool] = None
    seo_title: Optional[dict[str, str]] = None
    seo_description: Optional[dict[str, str]] = None
    tags: Optional[str] = None
    attributes: Optional[list[dict[str, Any]]] = None
    variants: Optional[list[Variant]] = None
    images: Optional[list[ProductImage]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
