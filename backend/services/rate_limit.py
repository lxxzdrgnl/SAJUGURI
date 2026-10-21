"""간단한 고정 윈도우 레이트 리밋 — arq redis 풀 재사용, redis 장애 시 fail-open."""
from __future__ import annotations

import logging
import time

from fastapi import Request

logger = logging.getLogger(__name__)


def client_ip(request: Request) -> str:
    """프록시 뒤라면 X-Forwarded-For 첫 값, 아니면 소켓 peer."""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def allow(request: Request, scope: str, *, limit: int, window_sec: int = 60) -> bool:
    """scope+IP 기준 window 내 limit 초과 시 False. redis 없음/오류면 True(차단 안 함)."""
    redis = getattr(request.app.state, "arq", None)
    if redis is None:
        return True
    key = f"rl:{scope}:{client_ip(request)}:{int(time.time()) // window_sec}"
    try:
        n = await redis.incr(key)
        if n == 1:
            await redis.expire(key, window_sec * 2)
        return n <= limit
    except Exception:  # noqa: BLE001 — redis 다운 등: 추적이 페이지를 깨면 안 됨
        logger.warning("rate limit 확인 실패 — 허용 처리", exc_info=True)
        return True
