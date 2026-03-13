"""SQLAlchemy 모델."""

from __future__ import annotations
import uuid
from datetime import date, time, datetime, timezone
from sqlalchemy import String, DateTime, Date, Time, Integer, Boolean, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]        = mapped_column(Integer, primary_key=True)
    email:           Mapped[str]        = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider:        Mapped[str]        = mapped_column(String(20), default="local")
    social_id:       Mapped[str | None] = mapped_column(String(255), nullable=True)
    role:            Mapped[str]        = mapped_column(String(20), default="user")
    created_at:      Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=_utcnow)


class Profile(Base):
    __tablename__ = "profiles"

    id:            Mapped[int]         = mapped_column(Integer, primary_key=True)
    user_id:       Mapped[int]         = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name:          Mapped[str]         = mapped_column(String(50))
    birth_date:    Mapped[date]         = mapped_column(Date)
    birth_time:    Mapped[time | None] = mapped_column(Time, nullable=True)
    calendar:      Mapped[str]         = mapped_column(String(10), default="solar")
    gender:        Mapped[str]         = mapped_column(String(10))
    is_leap_month: Mapped[bool]        = mapped_column(Boolean, default=False)
    city:               Mapped[str | None]  = mapped_column(String(100), nullable=True)
    longitude:          Mapped[float | None] = mapped_column(Numeric(7, 4), nullable=True)
    is_representative:  Mapped[bool]         = mapped_column(Boolean, default=False, nullable=False)
    day_stem:           Mapped[str | None]   = mapped_column(String(5), nullable=True)
    day_branch:         Mapped[str | None]   = mapped_column(String(5), nullable=True)
    day_stem_element:   Mapped[str | None]   = mapped_column(String(5), nullable=True)
    created_at:         Mapped[datetime]     = mapped_column(DateTime(timezone=True), default=_utcnow)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True)
    user_id:    Mapped[int]      = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str]      = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked:    Mapped[bool]     = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class SharedResult(Base):
    __tablename__ = "shared_results"

    id:            Mapped[int]         = mapped_column(Integer, primary_key=True)
    profile_id:    Mapped[int | None]  = mapped_column(Integer, ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    birth_input:   Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    share_token:   Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    calc_snapshot: Mapped[dict]        = mapped_column(JSONB)
    created_at:    Mapped[datetime]    = mapped_column(DateTime(timezone=True), default=_utcnow)
