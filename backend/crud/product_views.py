"""product_views DB 접근. 단발 쓰기라 내부에서 commit."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ProductView


async def record_view(
    db: AsyncSession,
    *,
    product_id: str,
    user_id: int | None,
    day_stem: str | None,
    age_band: str | None,
    gender: str | None,
) -> None:
    db.add(ProductView(
        product_id=product_id, user_id=user_id,
        day_stem=day_stem, age_band=age_band, gender=gender,
    ))
    await db.commit()
