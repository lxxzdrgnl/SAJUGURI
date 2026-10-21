"""상품 열람 기록 — 게스트 허용."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud import product_views as pv_crud
from db.models import User
from dependencies.auth import get_optional_user
from dependencies.db import get_db
from schemas.product_views import ProductViewRequest
from services import rate_limit

router = APIRouter(prefix="/api/products", tags=["상품"])

VIEWS_PER_MINUTE = 60  # IP당 분당 기록 상한


@router.post("/views", status_code=status.HTTP_204_NO_CONTENT, summary="상품 열람 기록")
async def record_product_view(
    request: Request,
    body: ProductViewRequest,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not await rate_limit.allow(request, "product_views", limit=VIEWS_PER_MINUTE):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="요청이 너무 많습니다.")
    await pv_crud.record_view(
        db,
        product_id=body.product_id,
        user_id=user.id if user else None,
        day_stem=body.day_stem,
        age_band=body.age_band,
        gender=body.gender,
    )
