"""프로필 CRUD — 사주 입력 저장/조회/삭제."""

from datetime import date, time as time_type

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Profile, User
from dependencies.auth import get_current_user
from dependencies.db import get_db
from schemas.profile import ProfileCreate, ProfileResponse

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
    dup = await db.execute(
        select(Profile).where(
            Profile.user_id == user.id,
            Profile.birth_date == birth_date,
            Profile.birth_time == birth_time,
            Profile.calendar == body.calendar,
            Profile.gender == body.gender,
        )
    )
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 저장된 프로필입니다.")

    profile = Profile(
        user_id=user.id,
        birth_date=birth_date,
        birth_time=birth_time,
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
        .order_by(Profile.created_at.desc())
    )
    return result.scalars().all()


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
    return profile


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
