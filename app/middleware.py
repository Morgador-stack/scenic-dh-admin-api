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
    """管理端鉴权。MVP 阶段使用固定 token 占位。"""
    # health 端点不需要鉴权
    if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json") or request.url.path.startswith("/v1/auth/login") or request.url.path.startswith("/v1/auth/refresh"):
        return await call_next(request)

    from app.schemas.common import err

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or auth[7:] != settings.ADMIN_TOKEN:
        trace_id = getattr(request.state, "trace_id", "unknown")
        return JSONResponse(
            status_code=401,
            content=err(40100, "管理 token 无效", trace_id),
        )
    return await call_next(request)
