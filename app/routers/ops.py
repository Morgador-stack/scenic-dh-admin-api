"""运营首页聚合 — 今日游客、会话、排队、活动、告警、待办快照"""

from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.schemas.common import ok

router = APIRouter(tags=["Ops Snapshot"])


@router.get("/admin/ops/snapshot")
def get_ops_snapshot(request: Request):
    trace_id = request.state.trace_id
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return ok({
        "generatedAt": now,
        "visitors": {
            "today": 1247,
            "currentOnSite": 358,
            "trend": "+12%",
            "peakHours": ["10:00", "14:00"],
        },
        "sessions": {
            "active": 203,
            "totalToday": 892,
            "avgDurationMinutes": 45,
        },
        "queues": {
            "activeResources": 2,
            "totalWaiting": 23,
            "avgWaitMinutes": 15,
            "alerts": ["灵山大佛等待时间超过 20 分钟"],
        },
        "events": {
            "activeToday": 3,
            "nextEvent": {"name": "夜景灯光秀", "time": "19:30", "resource": "QP-002"},
            "upcoming": 2,
        },
        "notices": {
            "active": 5,
            "latest": "东门入口临时限流通知",
        },
        "workOrders": {
            "pending": 12,
            "critical": 1,
            "overdueSLA": 2,
        },
        "alerts": [
            {"level": "warning", "message": "灵山大佛排队超 20 分钟", "timestamp": now},
            {"level": "info", "message": "夜景灯光秀今晚 19:30 场次已满", "timestamp": now},
        ],
        "todos": [
            "处理 2 个超时工单",
            "审核 3 条待发布公告",
            "夜景灯光秀场次确认",
        ],
    }, trace_id)
