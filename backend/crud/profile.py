"""Profile CRUD 헬퍼 — DB 조회 + 일주 enrichment."""

import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Profile
from schemas.profile import ProfileResponse
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
