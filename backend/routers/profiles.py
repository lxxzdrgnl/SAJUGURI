"""프로필 CRUD — 사주 입력 저장/조회/삭제."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from crud.profile import attach_ilju, get_profile_or_404
from db.models import Profile, User
from dependencies.auth import get_current_user
from dependencies.db import get_db
from schemas.profile import ProfileCreate, ProfileResponse
from services.profile import create_profile_for_user

router = APIRouter(prefix="/api/profiles", tags=["프로필"])


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED, summary="프로필 저장")
async def create_profile(
    body: ProfileCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_profile_for_user(db, user.id, body)


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
    return [attach_ilju(p) for p in result.scalars().all()]


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
    return attach_ilju(profile)


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
    profile = await get_profile_or_404(db, profile_id, user.id)
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
    profile = await get_profile_or_404(db, profile_id, user.id)
    return attach_ilju(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, summary="프로필 삭제")
async def delete_profile(
    profile_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_profile_or_404(db, profile_id, user.id)
    await db.delete(profile)
    await db.commit()
