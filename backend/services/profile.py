"""Profile 서비스 — 프로필 생성 비즈니스 규칙 제어."""

from __future__ import annotations
from datetime import date, time as time_type

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.profile import (
    attach_ilju,
    create_profile,
    find_duplicate_profile,
    has_any_profile,
)
from schemas.profile import ProfileCreate, ProfileResponse


async def create_profile_for_user(
    db: AsyncSession,
    user_id: int,
    body: ProfileCreate,
) -> ProfileResponse:
    """
    프로필 생성 흐름을 제어한다.

    비즈니스 규칙:
    - 동일 생년월일·생시·음양력·성별 중복 불허
    - 첫 번째 프로필은 자동으로 대표 설정

    Returns:
        일주가 enriched된 ProfileResponse
    """
    birth_date = date.fromisoformat(body.birth_date)
    birth_time = time_type.fromisoformat(body.birth_time) if body.birth_time else None

    if await find_duplicate_profile(db, user_id, birth_date, birth_time, body.calendar, body.gender):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 저장된 프로필입니다.")

    is_first = not await has_any_profile(db, user_id)

    profile = await create_profile(db, user_id, birth_date, birth_time, is_first, body)
    await db.commit()
    await db.refresh(profile)
    return attach_ilju(profile)
