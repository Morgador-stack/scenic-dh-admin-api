"""工单中心 — 分配、处理、状态流转、SLA追踪"""

from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok, err

router = APIRouter(tags=["Work Orders Admin"])

# ── 模拟工单数据 ──
_WO_DATA: dict[str, dict] = {}


class AssignWorkOrderRequest(BaseModel):
    assignee: str


class ProcessWorkOrderRequest(BaseModel):
    action: str  # "accept", "resolve", "close"
    resolution: str | None = None


# ═══ 工单管理 ═══

@router.get("/admin/work-orders")
def list_work_orders(
    request: Request,
    status: str | None = None,
    priority: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    trace_id = request.state.trace_id
    items = list(_WO_DATA.values())
    if status:
        items = [w for w in items if w["status"] == status]
    if priority:
        items = [w for w in items if w.get("priority") == priority]
    items.sort(key=lambda w: w.get("createdAt", ""), reverse=True)

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = items[start:end]

    return ok({
        "items": page_items,
        "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": max(1, (total + page_size - 1) // page_size)},
    }, trace_id)


@router.get("/admin/work-orders/{wo_id}")
def get_work_order(wo_id: str, request: Request):
    trace_id = request.state.trace_id
    wo = _WO_DATA.get(wo_id)
    if not wo:
        return err(40404, f"工单 {wo_id} 不存在", trace_id)
    return ok(wo, trace_id)


@router.patch("/admin/work-orders/{wo_id}")
def update_work_order(wo_id: str, body: ProcessWorkOrderRequest, request: Request):
    trace_id = request.state.trace_id
    wo = _WO_DATA.get(wo_id)
    if not wo:
        return err(40404, f"工单 {wo_id} 不存在", trace_id)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if body.action == "accept":
        wo["status"] = "processing"
        wo["acceptedAt"] = now
    elif body.action == "resolve":
        wo["status"] = "resolved"
        wo["resolution"] = body.resolution or ""
        wo["resolvedAt"] = now
    elif body.action == "close":
        wo["status"] = "closed"
        if body.resolution:
            wo["resolution"] = body.resolution
        wo["closedAt"] = now
    else:
        return err(40001, f"无效操作: {body.action}，有效操作: accept, resolve, close", trace_id)

    wo["updatedAt"] = now
    return ok(wo, trace_id)


@router.post("/admin/work-orders/{wo_id}/assign")
def assign_work_order(wo_id: str, body: AssignWorkOrderRequest, request: Request):
    trace_id = request.state.trace_id
    wo = _WO_DATA.get(wo_id)
    if not wo:
        return err(40404, f"工单 {wo_id} 不存在", trace_id)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    wo["assignedTo"] = body.assignee
    wo["assignedAt"] = now
    wo["updatedAt"] = now
    return ok(wo, trace_id)


# ═══ 工单数据注入（供 business-api 提交的工单同步展示） ═══

class SyncWorkOrderRequest(BaseModel):
    id: str
    type: str
    title: str
    category: str = "general"
    sessionId: str | None = None
    description: str | None = None
    priority: str = "medium"
    lat: float | None = None
    lng: float | None = None
    contactPhone: str | None = None
    status: str = "pending"


@router.post("/admin/work-orders/sync")
def sync_work_order(body: SyncWorkOrderRequest, request: Request):
    """business-api 提交工单后同步到 admin-api 存储"""
    trace_id = request.state.trace_id
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    wo = body.model_dump()
    wo["createdAt"] = now
    wo["updatedAt"] = now
    _WO_DATA[body.id] = wo
    return ok({"id": body.id, "synced": True}, trace_id)
