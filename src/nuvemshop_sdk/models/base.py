# src/nuvemshop_sdk/models/base.py
"""
Base Pydantic model for all Nuvemshop SDK data objects.

``extra="allow"`` ensures forward compatibility: if the Nuvemshop API
adds new fields, the SDK will accept them silently instead of raising
validation errors.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class NuvemshopBaseModel(BaseModel):
    """Base model used by every Nuvemshop entity.

    - ``extra="allow"`` — unknown fields are stored, never rejected.
    - ``populate_by_name=True`` — fields can be set by alias or name.
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
