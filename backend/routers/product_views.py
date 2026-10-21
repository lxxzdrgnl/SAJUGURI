"""상품 열람 기록 — 게스트 허용."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud import product_views as pv_crud
from db.models import User
from dependencies.auth import get_optional_user
from dependencies.db import get_db
from schemas.product_views import ProductViewRequest

router = APIRouter(prefix="/api/products", tags=["상품"])


@router.post("/views", status_code=status.HTTP_204_NO_CONTENT, summary="상품 열람 기록")
async def record_product_view(
    body: ProductViewRequest,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await pv_crud.record_view(
        db,
        product_id=body.product_id,
        user_id=user.id if user else None,
        day_stem=body.day_stem,
        age_band=body.age_band,
        gender=body.gender,
    )
