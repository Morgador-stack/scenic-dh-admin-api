"""中间件：trace_id、admin 鉴权、审计日志"""

import uuid
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings

logger = logging.getLogger("admin-api")


class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("x-trace-id", f"trace_{uuid.uuid4().hex}")
        span_id = str(uuid.uuid4())[:8]

        request.state.trace_id = trace_id
        request.state.span_id = span_id

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        response.headers["x-trace-id"] = trace_id
        response.headers["x-span-id"] = span_id
        response.headers["x-service"] = settings.SERVICE_NAME
        response.headers["x-elapsed-ms"] = f"{elapsed_ms:.1f}"

        logger.info(
            "request",
            extra={
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "elapsed_ms": round(elapsed_ms, 2),
            },
        )
        return response


async def admin_auth_middleware(request: Request, call_next):
    """管理端鉴权。接受硬编码 ADMIN_TOKEN 或 /auth/login 签发的动态 token。"""
    PUBLIC_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}
    PUBLIC_PREFIXES = ("/v1/auth/login", "/v1/auth/refresh")
    path = request.url.path.rstrip("/")
    if path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES):
        return await call_next(request)

    from app.schemas.common import err
    trace_id = getattr(request.state, "trace_id", "unknown")

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JSONResponse(status_code=401, content=err(40100, "管理 token 无效", trace_id))

    token = auth[7:]

    # 硬编码 dev token（向后兼容 + 测试用）
    if token == settings.ADMIN_TOKEN:
        return await call_next(request)

    # 动态 token（/auth/login 签发）
    try:
        from app.auth import _TOKENS
        from datetime import datetime, timezone
        token_info = _TOKENS.get(token)
        if token_info:
            expires = datetime.strptime(token_info["expiresAt"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) < expires:
                request.state.admin_username = token_info["username"]
                return await call_next(request)
    except Exception:
        pass

    return JSONResponse(status_code=401, content=err(40101, "token 无效或已过期", trace_id))
