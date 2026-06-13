"""scenic-dh-admin-api — 运营管理接口"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware import TraceMiddleware, admin_auth_middleware

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='{"time":"%(asctime)s","level":"%(levelname)s","service":"%(name)s","message":"%(message)s"}',
    stream=sys.stdout,
)
logger = logging.getLogger("admin-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.SERVICE_NAME} v{settings.SERVICE_VERSION} starting on port {settings.PORT}")
    yield
    logger.info(f"{settings.SERVICE_NAME} shutting down")


app = FastAPI(
    title="scenic-dh-admin-api",
    version=settings.SERVICE_VERSION,
    description="运营管理接口 — 知识库、人设、播报、审计、分析、运行控制、内容配置、工单、IAM",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(TraceMiddleware)
app.middleware("http")(admin_auth_middleware)


@app.get("/health", tags=["Health"])
def health():
    from app.schemas.common import ok
    trace_id = "startup-check"
    return ok(
        {"status": "ok", "version": settings.SERVICE_VERSION, "dependencies": {"business_api": settings.BUSINESS_API_URL}},
        trace_id,
    )


# Routers — 原有
from app.routers import knowledge, personas, broadcasts, audit, analytics, runtime, data_gaps, audit_logs  # noqa: E402
# Routers — 新增
from app.routers import ops, content, work_orders as wo_router, config as config_router  # noqa: E402
from app import auth  # noqa: E402

app.include_router(knowledge.router, prefix="/v1")
app.include_router(personas.router, prefix="/v1")
app.include_router(broadcasts.router, prefix="/v1")
app.include_router(audit.router, prefix="/v1")
app.include_router(analytics.router, prefix="/v1")
app.include_router(runtime.router, prefix="/v1")
app.include_router(data_gaps.router, prefix="/v1")
app.include_router(audit_logs.router, prefix="/v1")

app.include_router(ops.router, prefix="/v1")
app.include_router(content.router, prefix="/v1")
app.include_router(wo_router.router, prefix="/v1")
app.include_router(config_router.router, prefix="/v1")
app.include_router(auth.router, prefix="/v1")
