"""Auth CRUD 헬퍼 — 유저 upsert + 토큰 쌍 생성."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.security import create_access_token, generate_refresh_token, hash_token
from db.models import RefreshToken, User


async def get_or_create_user(db: AsyncSession, email: str, social_id: str) -> User:
    """이메일로 유저를 조회하고 없으면 생성한다."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        user = User(email=email, provider="google", social_id=social_id, role="user")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def create_token_pair(db: AsyncSession, user: User) -> tuple[str, str]:
    """액세스 토큰 + 리프레시 토큰 쌍을 발급하고 DB에 저장한다."""
    access_token = create_access_token(user.id)
    refresh_token = generate_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=expires_at,
    ))
    await db.commit()
    return access_token, refresh_token
