"""프로필 CRUD — 사주 입력 저장/조회/삭제."""

from datetime import date, time as time_type

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Profile, User
from dependencies.auth import get_current_user
from dependencies.db import get_db
from schemas.profile import ProfileCreate, ProfileResponse
from engine.calc.saju import calculate_saju


def _attach_ilju(profile: Profile) -> ProfileResponse:
    """ProfileResponse에 동적으로 계산한 일주를 추가."""
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
    except Exception:
        pass
    return resp

router = APIRouter(prefix="/api/profiles", tags=["프로필"])


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED, summary="프로필 저장")
async def create_profile(
    body: ProfileCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    birth_date = date.fromisoformat(body.birth_date)
    birth_time = time_type.fromisoformat(body.birth_time) if body.birth_time else None

    # 동일 생년월일+생시+음양력+성별 중복 체크
    time_cond = Profile.birth_time.is_(None) if birth_time is None else Profile.birth_time == birth_time
    dup = await db.execute(
        select(Profile).where(
            and_(
                Profile.user_id == user.id,
                Profile.birth_date == birth_date,
                time_cond,
                Profile.calendar == body.calendar,
                Profile.gender == body.gender,
            )
        ).limit(1)
    )
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 저장된 프로필입니다.")

    # 첫 프로필이면 자동으로 대표 설정
    existing = await db.execute(select(Profile).where(Profile.user_id == user.id).limit(1))
    is_first = existing.scalar_one_or_none() is None

    profile = Profile(
        user_id=user.id,
        birth_date=birth_date,
        birth_time=birth_time,
        is_representative=is_first,
        **{k: v for k, v in body.model_dump().items() if k not in ("birth_date", "birth_time")},
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("", response_model=list[ProfileResponse], summary="내 프로필 목록")
async def list_profiles(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Profile)
        .where(Profile.user_id == user.id)
        .order_by(Profile.is_representative.desc(), Profile.created_at.desc())
    )
    return [_attach_ilju(p) for p in result.scalars().all()]


@router.get("/representative", response_model=ProfileResponse, summary="대표 프로필 조회")
async def get_representative_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Profile).where(Profile.user_id == user.id, Profile.is_representative == True)  # noqa: E712
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="대표 프로필이 없습니다.")
    return _attach_ilju(profile)


@router.patch("/{profile_id}/representative", response_model=ProfileResponse, summary="대표 프로필 설정")
async def set_representative(
    profile_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 기존 대표 해제
    await db.execute(
        update(Profile)
        .where(Profile.user_id == user.id, Profile.is_representative == True)  # noqa: E712
        .values(is_representative=False)
    )
    # 새 대표 설정
    result = await db.execute(
        select(Profile).where(Profile.id == profile_id, Profile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="프로필을 찾을 수 없습니다.")
    profile.is_representative = True
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=ProfileResponse, summary="프로필 단건 조회")
async def get_profile(
    profile_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Profile).where(Profile.id == profile_id, Profile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="프로필을 찾을 수 없습니다.")
    return _attach_ilju(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, summary="프로필 삭제")
async def delete_profile(
    profile_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Profile).where(Profile.id == profile_id, Profile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="프로필을 찾을 수 없습니다.")
    await db.delete(profile)
    await db.commit()
