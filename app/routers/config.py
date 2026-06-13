"""配置中心 — 服务URL、token、功能开关、环境矩阵"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok
from app.config import settings

router = APIRouter(tags=["Config Center"])

# ── 可动态修改的配置 ──
_DYNAMIC_CONFIG: dict = {
    "serviceUrls": {
        "businessApi": settings.BUSINESS_API_URL,
        "ragService": settings.RAG_SERVICE_URL,
        "fayRuntime": settings.FAY_RUNTIME_URL,
    },
    "featureFlags": {
        "mockMode": True,
        "offlineAvailable": True,
        "voiceGuide": False,
        "photoRecognition": False,
        "arImmersive": False,
        "ticketPayment": False,
        "multiLanguage": False,
    },
    "limits": {
        "maxSessionsPerUser": 3,
        "maxQueuesPerResource": 200,
        "maxWorkOrdersPerDay": 500,
        "feedbackCooldownMinutes": 5,
    },
    "environments": {
        "current": "dev",
        "available": ["dev", "staging", "prod"],
        "dev": {"debug": True, "logLevel": "DEBUG"},
        "staging": {"debug": False, "logLevel": "INFO"},
        "prod": {"debug": False, "logLevel": "WARNING"},
    },
}


class UpdateFeatureFlagsRequest(BaseModel):
    flags: dict


class UpdateConfigRequest(BaseModel):
    serviceUrls: dict | None = None
    limits: dict | None = None


@router.get("/admin/config")
def get_config(request: Request):
    trace_id = request.state.trace_id
    return ok(_DYNAMIC_CONFIG, trace_id)


@router.get("/admin/config/feature-flags")
def get_feature_flags(request: Request):
    trace_id = request.state.trace_id
    return ok(_DYNAMIC_CONFIG["featureFlags"], trace_id)


@router.patch("/admin/config/feature-flags")
def update_feature_flags(body: UpdateFeatureFlagsRequest, request: Request):
    trace_id = request.state.trace_id
    _DYNAMIC_CONFIG["featureFlags"].update(body.flags)
    return ok(_DYNAMIC_CONFIG["featureFlags"], trace_id)


@router.patch("/admin/config")
def update_config(body: UpdateConfigRequest, request: Request):
    trace_id = request.state.trace_id
    if body.serviceUrls:
        _DYNAMIC_CONFIG["serviceUrls"].update(body.serviceUrls)
    if body.limits:
        _DYNAMIC_CONFIG["limits"].update(body.limits)
    return ok(_DYNAMIC_CONFIG, trace_id)
