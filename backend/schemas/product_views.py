"""상품 열람 기록 스키마."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ProductViewRequest(BaseModel):
    product_id: str = Field(pattern=r"^[a-z_]{1,40}$")
    day_stem: str | None = Field(None, max_length=2)
    age_band: str | None = Field(None, pattern=r"^\d{1,3}-\d{1,3}$")
    gender: str | None = Field(None, max_length=10)
