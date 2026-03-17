"""Google OAuth Authorization Code Flow + Refresh Token 인증.

authlib — OAuth 클라이언트 관리 (Google, Kakao 등 멀티 프로바이더 대응)
CSRF state는 Starlette SessionMiddleware 쿠키로 관리.
"""

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.config import Config

from core.config import settings
from core.exceptions import (
    DatabaseException,
    OAuthFailedException,
)
from crud.auth import revoke_all_tokens
from db.models import User
from dependencies.auth import get_current_user
from dependencies.db import get_db
from services.auth import exchange_refresh_token, social_login

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
        access_token, refresh_token = await social_login(db, email, social_id)
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
    access_token, new_refresh_token = await exchange_refresh_token(db, body.refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.jwt_expire_minutes * 60,
    )


@router.post("/logout", summary="로그아웃 — 모든 Refresh Token 폐기")
async def logout(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    count = await revoke_all_tokens(db, user.id)
    return {"message": "로그아웃되었습니다.", "revoked_tokens": count}


@router.get("/me", summary="현재 로그인 유저 정보")
async def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "provider": user.provider,
    }
