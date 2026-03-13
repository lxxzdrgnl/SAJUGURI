"""공유 링크 생성/조회 — 비로그인 접근 가능."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.models import Profile, SharedResult, User
from dependencies.auth import get_optional_user
from dependencies.db import get_db
from schemas.share import ShareCreate, ShareResponse, SharedResultResponse

router = APIRouter(prefix="/api/share", tags=["공유"])


@router.post("", response_model=ShareResponse, status_code=status.HTTP_201_CREATED, summary="공유 링크 생성")
async def create_share(
    request: Request,
    body: ShareCreate,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    # 로그인 사용자가 profile_id를 지정한 경우 소유권 확인
    if body.profile_id is not None:
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.")
        result = await db.execute(
            select(Profile).where(Profile.id == body.profile_id, Profile.user_id == user.id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="프로필을 찾을 수 없습니다.")

    # profile_id도 없고 birth_input도 없으면 거부
    if body.profile_id is None and not body.birth_input:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="profile_id 또는 birth_input 중 하나는 필수입니다.")

    shared = SharedResult(
        profile_id=body.profile_id,
        birth_input=body.birth_input,
        calc_snapshot=body.calc_snapshot,
    )
    db.add(shared)
    await db.commit()
    await db.refresh(shared)

    share_url = f"{settings.frontend_url}/share/{shared.share_token}"
    return ShareResponse(
        share_token=shared.share_token,
        share_url=share_url,
        created_at=shared.created_at,
    )


@router.get("/{token}", response_model=SharedResultResponse, summary="공유 결과 조회 (비로그인 가능)")
async def get_share(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SharedResult).where(SharedResult.share_token == token)
    )
    shared = result.scalar_one_or_none()
    if not shared:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="공유 링크를 찾을 수 없습니다.")
    return shared
