"""요청/응답 요약 로깅 미들웨어."""

from __future__ import annotations
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("sajubon.access")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    요청/응답 요약 로그.
    형식: METHOD PATH  status=200  time=123ms  ip=1.2.3.4
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000)

        logger.info(
            "%s %s  status=%d  time=%dms  ip=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            request.client.host if request.client else "-",
        )
        return response
