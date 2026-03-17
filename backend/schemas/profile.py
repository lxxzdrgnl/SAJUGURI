"""프로필 API 요청/응답 Pydantic 스키마."""

from __future__ import annotations
from datetime import date, datetime, time
from pydantic import BaseModel, Field, field_validator


class ProfileCreate(BaseModel):
    name: str = Field(max_length=20, examples=["나"])
    birth_date: str = Field(description="YYYY-MM-DD", examples=["1990-03-15"])
    birth_time: str | None = Field(default=None, description="HH:MM", examples=["14:30"])
    calendar: str = Field(default="solar", pattern="^(solar|lunar)$")
    gender: str = Field(pattern="^(male|female)$")
    is_leap_month: bool = Field(default=False)
    city: str | None = Field(default=None, max_length=100)
    longitude: float | None = Field(default=None)


class ProfileResponse(BaseModel):
    id: int
    name: str
    birth_date: str
    birth_time: str | None
    calendar: str
    gender: str
    is_leap_month: bool
    city: str | None
    longitude: float | None
    is_representative: bool
    day_stem: str | None = None
    day_branch: str | None = None
    day_stem_element: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("birth_date", mode="before")
    @classmethod
    def coerce_date(cls, v: object) -> str:
        if isinstance(v, date):
            return v.isoformat()
        return str(v)

    @field_validator("birth_time", mode="before")
    @classmethod
    def coerce_time(cls, v: object) -> str | None:
        if isinstance(v, time):
            return v.strftime("%H:%M")
        return v  # type: ignore[return-value]

    @field_validator("longitude", mode="before")
    @classmethod
    def coerce_decimal(cls, v: object) -> float | None:
        if v is None:
            return None
        return float(v)
