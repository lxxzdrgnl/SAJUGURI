"""Profile CRUD 헬퍼 — DB 조회 + 일주 enrichment."""

from __future__ import annotations
import logging
from datetime import date, time as time_type

from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Profile
from schemas.profile import ProfileCreate, ProfileResponse
from engine.calc.saju import calculate_saju

logger = logging.getLogger(__name__)


async def get_profile_or_404(db: AsyncSession, profile_id: int, user_id: int) -> Profile:
    """
    Profile을 user_id 소유권과 함께 조회한다.

    존재하지 않거나 다른 사용자 소유이면 404를 반환한다.
    """
    result = await db.execute(
        select(Profile).where(Profile.id == profile_id, Profile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="프로필을 찾을 수 없습니다.")
    return profile


async def find_duplicate_profile(
    db: AsyncSession,
    user_id: int,
    birth_date: date,
    birth_time: time_type | None,
    calendar: str,
    gender: str,
) -> Profile | None:
    """동일 조건의 프로필이 이미 있는지 조회한다."""
    time_cond = (
        Profile.birth_time.is_(None)
        if birth_time is None
        else Profile.birth_time == birth_time
    )
    result = await db.execute(
        select(Profile).where(
            and_(
                Profile.user_id == user_id,
                Profile.birth_date == birth_date,
                time_cond,
                Profile.calendar == calendar,
                Profile.gender == gender,
            )
        ).limit(1)
    )
    return result.scalar_one_or_none()


async def has_any_profile(db: AsyncSession, user_id: int) -> bool:
    """유저가 기존에 저장한 프로필이 하나라도 있는지 확인한다."""
    result = await db.execute(
        select(Profile).where(Profile.user_id == user_id).limit(1)
    )
    return result.scalar_one_or_none() is not None


async def create_profile(
    db: AsyncSession,
    user_id: int,
    birth_date: date,
    birth_time: time_type | None,
    is_representative: bool,
    body: ProfileCreate,
) -> Profile:
    """Profile 레코드를 생성하고 flush한다. commit은 호출자 책임."""
    profile = Profile(
        user_id=user_id,
        birth_date=birth_date,
        birth_time=birth_time,
        is_representative=is_representative,
        **{k: v for k, v in body.model_dump().items() if k not in ("birth_date", "birth_time")},
    )
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


def attach_ilju(profile: Profile) -> ProfileResponse:
    """ProfileResponse에 동적으로 계산한 일주를 추가한다."""
    resp = ProfileResponse.model_validate(profile)
    try:
        saju = calculate_saju(
            birth_date=resp.birth_date,
            birth_time=resp.birth_time,
            gender=resp.gender,
            calendar=resp.calendar,
            is_leap_month=resp.is_leap_month,
        )
        dp = saju["day_pillar"]
        resp.day_stem = dp["stem"]
        resp.day_branch = dp["branch"]
        resp.day_stem_element = dp["stem_element"]
    except Exception as exc:
        logger.warning("일주 계산 실패 (profile_id=%s): %s", profile.id, exc)
    return resp
