"""상품 열람 기록 스키마."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProductViewRequest(BaseModel):
    product_id: str = Field(pattern=r"^[a-z_]{1,40}$")
    day_stem: Literal["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"] | None = None
    age_band: str | None = Field(None, pattern=r"^\d{1,3}-\d{1,3}$")
    gender: Literal["male", "female"] | None = None
