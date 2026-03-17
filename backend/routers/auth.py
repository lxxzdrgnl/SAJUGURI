"""Google OAuth Authorization Code Flow + Refresh Token 인증.

authlib — OAuth 클라이언트 관리 (Google, Kakao 등 멀티 프로바이더 대응)
CSRF state는 Starlette SessionMiddleware 쿠키로 관리.
"""

from datetime import datetime, timezone

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.config import Config

from core.config import settings
from core.exceptions import (
    DatabaseException,
    OAuthFailedException,
    TokenExpiredException,
    UnauthorizedException,
)
from core.security import hash_token
from crud.auth import create_token_pair, get_or_create_user
from db.models import RefreshToken, User
from dependencies.auth import get_current_user
from dependencies.db import get_db

router = APIRouter(prefix="/api/auth", tags=["인증"])

# ─── OAuth 클라이언트 ──────────────────────────────────────────────────────────

_config = Config(
    environ={
        "GOOGLE_CLIENT_ID": settings.google_client_id,
        "GOOGLE_CLIENT_SECRET": settings.google_client_secret,
    }
)
oauth = OAuth(_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
# 추후 추가 예시:
# oauth.register(name="kakao", ...)


# ─── Pydantic 스키마 ───────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


# ─── 엔드포인트 ────────────────────────────────────────────────────────────────

@router.get("/google", summary="Google OAuth 로그인 시작")
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(request, settings.google_redirect_uri)


@router.get("/google/callback", summary="Google OAuth 콜백")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise OAuthFailedException(str(e))

    user_info = token.get("userinfo")
    if not user_info:
        raise OAuthFailedException("userinfo를 가져올 수 없습니다.")

    email = user_info.get("email")
    social_id = user_info.get("sub")
    if not email:
        raise OAuthFailedException("이메일 정보가 없습니다.")

    try:
        user = await get_or_create_user(db, email, social_id)
        access_token, refresh_token = await create_token_pair(db, user)
    except OAuthFailedException:
        raise
    except Exception as e:
        raise DatabaseException(str(e))

    redirect_url = (
        f"{settings.frontend_url}/auth/callback"
        f"?access_token={access_token}"
        f"&refresh_token={refresh_token}"
    )
    return RedirectResponse(url=redirect_url, status_code=302)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh Token으로 새 토큰 발급")
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_token(body.refresh_token)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,  # noqa: E712
        )
    )
    stored = result.scalar_one_or_none()

    if not stored:
        raise UnauthorizedException()

    if stored.expires_at < datetime.now(timezone.utc):
        stored.revoked = True
        await db.commit()
        raise TokenExpiredException()

    stored.revoked = True
    await db.commit()

    user_result = await db.execute(select(User).where(User.id == stored.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise UnauthorizedException()

    access_token, new_refresh_token = await create_token_pair(db, user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.jwt_expire_minutes * 60,
    )


@router.post("/logout", summary="로그아웃 — 모든 Refresh Token 폐기")
async def logout(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked == False,  # noqa: E712
        )
    )
    tokens = result.scalars().all()
    for t in tokens:
        t.revoked = True
    await db.commit()
    return {"message": "로그아웃되었습니다.", "revoked_tokens": len(tokens)}


@router.get("/me", summary="현재 로그인 유저 정보")
async def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "provider": user.provider,
    }
