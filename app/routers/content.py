"""内容配置中心 — 景点、路线、公告、活动、服务设施、票务口径 CRUD"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Request, Query
from pydantic import BaseModel, Field

from app.schemas.common import ok, err

router = APIRouter(tags=["Content Management"])

# ── 内存存储 ──
_SPOTS: dict[str, dict] = {}
_ROUTES: dict[str, dict] = {}
_NOTICES: dict[str, dict] = {}
_EVENTS: dict[str, dict] = {}
_SERVICES: dict[str, dict] = {}
_TICKET_PRODUCTS: dict[str, dict] = {}
_COUNTERS = {"spot": 0, "route": 0, "notice": 0, "event": 0, "service": 0, "ticket": 0}


# ═══ 通用 CRUD 辅助 ═══

def _create(store: dict, item_id: str, data: dict, prefix: str, counter_key: str) -> dict:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    item = {"id": item_id, **data, "status": "draft", "version": 1, "createdAt": now, "updatedAt": now}
    store[item_id] = item
    return item


def _update(store: dict, item_id: str, data: dict) -> dict:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    item = store[item_id]
    item.update(data)
    item["version"] = item.get("version", 1) + 1
    item["updatedAt"] = now
    store[item_id] = item
    return item


def _publish(store: dict, item_id: str) -> dict:
    item = store[item_id]
    item["status"] = "published"
    item["publishedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return item


def _withdraw(store: dict, item_id: str) -> dict:
    item = store[item_id]
    item["status"] = "draft"
    return item


# ═══ 通用请求体 ═══

class SpotData(BaseModel):
    name: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    category: str = "景点"
    description: str | None = None
    guideText: str | None = None
    labels: list[str] | None = []
    scenicId: str = "SA-001"

class NoticeData(BaseModel):
    title: str
    content: str
    priority: str = "normal"
    targetAudience: str = "all"

class EventData(BaseModel):
    name: str
    time: str
    location: str
    description: str | None = None
    capacity: int = Field(default=100, ge=1, le=100000)

class ServiceData(BaseModel):
    name: str
    type: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    hours: str = "08:00-18:00"
    phone: str | None = None

class TicketProductData(BaseModel):
    name: str
    price: float = Field(ge=0)
    applicableCrowd: str
    officialUrl: str

class PublishRequest(BaseModel):
    status: str  # "published" or "draft"


# ═══ 景点 ═══

@router.get("/content/spots")
def list_spots(request: Request, status: str | None = None, q: str | None = None):
    trace_id = request.state.trace_id
    items = list(_SPOTS.values())
    if status:
        items = [i for i in items if i["status"] == status]
    if q:
        items = [i for i in items if q in i.get("name", "") or q in i.get("description", "")]
    return ok({"items": items, "total": len(items)}, trace_id)

@router.post("/content/spots")
def create_spot(data: SpotData, request: Request):
    trace_id = request.state.trace_id
    _COUNTERS["spot"] += 1
    spot_id = f"SPOT-{_COUNTERS['spot']:03d}"
    item = _create(_SPOTS, spot_id, data.model_dump(), "SPOT", "spot")
    return ok(item, trace_id)

@router.put("/content/spots/{spot_id}")
def update_spot(spot_id: str, data: SpotData, request: Request):
    trace_id = request.state.trace_id
    if spot_id not in _SPOTS:
        return err(40404, f"景点 {spot_id} 不存在", trace_id)
    return ok(_update(_SPOTS, spot_id, data.model_dump()), trace_id)

@router.post("/content/spots/{spot_id}/publish")
def publish_spot(spot_id: str, request: Request):
    trace_id = request.state.trace_id
    if spot_id not in _SPOTS:
        return err(40404, f"景点 {spot_id} 不存在", trace_id)
    return ok(_publish(_SPOTS, spot_id), trace_id)

@router.post("/content/spots/{spot_id}/withdraw")
def withdraw_spot(spot_id: str, request: Request):
    trace_id = request.state.trace_id
    if spot_id not in _SPOTS:
        return err(40404, f"景点 {spot_id} 不存在", trace_id)
    return ok(_withdraw(_SPOTS, spot_id), trace_id)

@router.delete("/content/spots/{spot_id}")
def delete_spot(spot_id: str, request: Request):
    trace_id = request.state.trace_id
    if spot_id not in _SPOTS: return err(40404, f"景点 {spot_id} 不存在", trace_id)
    del _SPOTS[spot_id]
    return ok({"deleted": spot_id}, trace_id)


# ═══ 公告 ═══

@router.get("/content/notices")
def list_notices(request: Request, status: str | None = None):
    trace_id = request.state.trace_id
    items = list(_NOTICES.values())
    if status:
        items = [i for i in items if i["status"] == status]
    return ok({"items": items, "total": len(items)}, trace_id)

@router.post("/content/notices")
def create_notice(data: NoticeData, request: Request):
    trace_id = request.state.trace_id
    _COUNTERS["notice"] += 1
    nid = f"NOTICE-{_COUNTERS['notice']:03d}"
    return ok(_create(_NOTICES, nid, data.model_dump(), "NOTICE", "notice"), trace_id)

@router.put("/content/notices/{notice_id}")
def update_notice(notice_id: str, data: NoticeData, request: Request):
    trace_id = request.state.trace_id
    if notice_id not in _NOTICES:
        return err(40404, f"公告 {notice_id} 不存在", trace_id)
    return ok(_update(_NOTICES, notice_id, data.model_dump()), trace_id)

@router.post("/content/notices/{notice_id}/publish")
def publish_notice(notice_id: str, request: Request):
    trace_id = request.state.trace_id
    if notice_id not in _NOTICES:
        return err(40404, f"公告 {notice_id} 不存在", trace_id)
    return ok(_publish(_NOTICES, notice_id), trace_id)

@router.post("/content/notices/{notice_id}/withdraw")
def withdraw_notice(notice_id: str, request: Request):
    trace_id = request.state.trace_id
    if notice_id not in _NOTICES:
        return err(40404, f"公告 {notice_id} 不存在", trace_id)
    return ok(_withdraw(_NOTICES, notice_id), trace_id)


# ═══ 活动 ═══

@router.get("/content/events")
def list_events(request: Request, status: str | None = None):
    trace_id = request.state.trace_id
    items = list(_EVENTS.values())
    if status:
        items = [i for i in items if i["status"] == status]
    return ok({"items": items, "total": len(items)}, trace_id)

@router.post("/content/events")
def create_event(data: EventData, request: Request):
    trace_id = request.state.trace_id
    _COUNTERS["event"] += 1
    eid = f"EVENT-{_COUNTERS['event']:03d}"
    return ok(_create(_EVENTS, eid, data.model_dump(), "EVENT", "event"), trace_id)

@router.put("/content/events/{event_id}")
def update_event(event_id: str, data: EventData, request: Request):
    trace_id = request.state.trace_id
    if event_id not in _EVENTS:
        return err(40404, f"活动 {event_id} 不存在", trace_id)
    return ok(_update(_EVENTS, event_id, data.model_dump()), trace_id)

@router.post("/content/events/{event_id}/publish")
def publish_event(event_id: str, request: Request):
    trace_id = request.state.trace_id
    if event_id not in _EVENTS:
        return err(40404, f"活动 {event_id} 不存在", trace_id)
    return ok(_publish(_EVENTS, event_id), trace_id)

@router.post("/content/events/{event_id}/withdraw")
def withdraw_event(event_id: str, request: Request):
    trace_id = request.state.trace_id
    if event_id not in _EVENTS:
        return err(40404, f"活动 {event_id} 不存在", trace_id)
    return ok(_withdraw(_EVENTS, event_id), trace_id)


# ═══ 服务设施 ═══

@router.get("/content/services")
def list_services(request: Request, status: str | None = None):
    trace_id = request.state.trace_id
    items = list(_SERVICES.values())
    if status:
        items = [i for i in items if i["status"] == status]
    return ok({"items": items, "total": len(items)}, trace_id)

@router.post("/content/services")
def create_service(data: ServiceData, request: Request):
    trace_id = request.state.trace_id
    _COUNTERS["service"] += 1
    sid = f"SVC-{_COUNTERS['service']:03d}"
    return ok(_create(_SERVICES, sid, data.model_dump(), "SVC", "service"), trace_id)

@router.put("/content/services/{service_id}")
def update_service(service_id: str, data: ServiceData, request: Request):
    trace_id = request.state.trace_id
    if service_id not in _SERVICES:
        return err(40404, f"服务设施 {service_id} 不存在", trace_id)
    return ok(_update(_SERVICES, service_id, data.model_dump()), trace_id)

@router.post("/content/services/{service_id}/publish")
def publish_service(service_id: str, request: Request):
    trace_id = request.state.trace_id
    if service_id not in _SERVICES:
        return err(40404, f"服务设施 {service_id} 不存在", trace_id)
    return ok(_publish(_SERVICES, service_id), trace_id)


# ═══ 票务口径 ═══

@router.get("/content/ticket-products")
def list_ticket_products(request: Request, status: str | None = None):
    trace_id = request.state.trace_id
    items = list(_TICKET_PRODUCTS.values())
    if status:
        items = [i for i in items if i["status"] == status]
    return ok({"items": items, "total": len(items)}, trace_id)

@router.post("/content/ticket-products")
def create_ticket_product(data: TicketProductData, request: Request):
    trace_id = request.state.trace_id
    _COUNTERS["ticket"] += 1
    tid = f"TP-{_COUNTERS['ticket']:03d}"
    return ok(_create(_TICKET_PRODUCTS, tid, data.model_dump(), "TP", "ticket"), trace_id)

@router.put("/content/ticket-products/{product_id}")
def update_ticket_product(product_id: str, data: TicketProductData, request: Request):
    trace_id = request.state.trace_id
    if product_id not in _TICKET_PRODUCTS:
        return err(40404, f"票务产品 {product_id} 不存在", trace_id)
    return ok(_update(_TICKET_PRODUCTS, product_id, data.model_dump()), trace_id)

@router.post("/content/ticket-products/{product_id}/publish")
def publish_ticket_product(product_id: str, request: Request):
    trace_id = request.state.trace_id
    if product_id not in _TICKET_PRODUCTS:
        return err(40404, f"票务产品 {product_id} 不存在", trace_id)
    return ok(_publish(_TICKET_PRODUCTS, product_id), trace_id)

# ═══ 路线配置 ═══

class RouteData(BaseModel):
    name: str
    type: str = "casual"
    duration: str = "4小时"
    nodes: list[str] | None = []
    difficulty: str = "easy"
    tags: list[str] | None = []
    description: str | None = None


@router.get("/content/routes")
def list_routes(request: Request, status: str | None = None):
    trace_id = request.state.trace_id
    items = list(_ROUTES.values())
    if status: items = [i for i in items if i["status"] == status]
    return ok({"items": items, "total": len(items)}, trace_id)


@router.post("/content/routes")
def create_route(data: RouteData, request: Request):
    trace_id = request.state.trace_id
    _COUNTERS["route"] += 1
    rid = f"ROUTE-{_COUNTERS['route']:03d}"
    return ok(_create(_ROUTES, rid, data.model_dump(), "ROUTE", "route"), trace_id)


@router.put("/content/routes/{route_id}")
def update_route(route_id: str, data: RouteData, request: Request):
    trace_id = request.state.trace_id
    if route_id not in _ROUTES: return err(40404, f"路线 {route_id} 不存在", trace_id)
    return ok(_update(_ROUTES, route_id, data.model_dump()), trace_id)


@router.post("/content/routes/{route_id}/publish")
def publish_route(route_id: str, request: Request):
    trace_id = request.state.trace_id
    if route_id not in _ROUTES: return err(40404, f"路线 {route_id} 不存在", trace_id)
    return ok(_publish(_ROUTES, route_id), trace_id)


# ═══ 审批流（通用，覆盖 6 类内容） ═══

@router.get("/content/pending-review")
def list_pending_review(request: Request):
    """所有待审核内容"""
    trace_id = request.state.trace_id
    pending = []
    for store, label in [(_SPOTS, "景点"), (_ROUTES, "路线"), (_NOTICES, "公告"), (_EVENTS, "活动"), (_SERVICES, "服务"), (_TICKET_PRODUCTS, "票务")]:
        for item in store.values():
            if item.get("status") == "pending_review":
                pending.append({"type": label, "id": item["id"], "name": item.get("name") or item.get("title") or "", "status": "pending_review", "updatedAt": item.get("updatedAt", "")})
    return ok({"items": pending, "total": len(pending)}, trace_id)


_store_map = {"spots": _SPOTS, "routes": _ROUTES, "notices": _NOTICES, "events": _EVENTS, "services": _SERVICES, "ticket-products": _TICKET_PRODUCTS}


@router.post("/content/{content_type}/{item_id}/submit-review")
def submit_review(content_type: str, item_id: str, request: Request):
    """提交审核"""
    trace_id = request.state.trace_id
    store = _store_map.get(content_type)
    if not store:
        return err(40001, f"无效内容类型: {content_type}", trace_id)
    item = store.get(item_id)
    if not item:
        return err(40404, f"{item_id} 不存在", trace_id)
    if item["status"] != "draft":
        return err(40001, f"只有草稿可提交审核，当前: {item['status']}", trace_id)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    item["status"] = "pending_review"; item["submittedAt"] = now; item["updatedAt"] = now
    return ok(item, trace_id)


@router.post("/content/{content_type}/{item_id}/approve")
def approve_content(content_type: str, item_id: str, request: Request):
    """审核通过"""
    trace_id = request.state.trace_id
    store = _store_map.get(content_type)
    if not store: return err(40001, f"无效内容类型: {content_type}", trace_id)
    item = store.get(item_id)
    if not item: return err(40404, f"{item_id} 不存在", trace_id)
    if item["status"] != "pending_review":
        return err(40001, f"只有待审核可批准，当前: {item['status']}", trace_id)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    item["status"] = "published"; item["approvedAt"] = now; item["publishedAt"] = now; item["updatedAt"] = now
    return ok(item, trace_id)


@router.post("/content/{content_type}/{item_id}/reject")
def reject_content(content_type: str, item_id: str, reason: str = "", request: Request = None):
    """审核驳回"""
    trace_id = request.state.trace_id
    store = _store_map.get(content_type)
    if not store: return err(40001, f"无效内容类型: {content_type}", trace_id)
    item = store.get(item_id)
    if not item: return err(40404, f"{item_id} 不存在", trace_id)
    if item["status"] != "pending_review":
        return err(40001, f"只有待审核可驳回，当前: {item['status']}", trace_id)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    item["status"] = "draft"; item["rejectedAt"] = now; item["rejectionReason"] = reason; item["updatedAt"] = now
    return ok(item, trace_id)

# ═══ 排队叫号（运营端控制队列状态） ═══

@router.post("/content/queues/{ticket_id}/call")
def call_queue_number(ticket_id: str, request: Request):
    """后台叫号 — 将排队票状态改为 called，模拟真实叫号"""
    trace_id = request.state.trace_id
    from app.schemas.common import err
    # 通过 business-api 的共享内存无法直连，此处用本地模拟队列状态
    return err(50100, "需要连接 business-api 队列数据库。MVP 阶段请通过 business-api 直接操作。", trace_id)


# 实际实现：admin-api 通过 HTTP 调用 business-api 的队列取消/状态变更
# 详细见 H-06 交接文档中的服务间调用规范

@router.delete("/content/{content_type}/{item_id}")
def delete_content(content_type: str, item_id: str, request: Request):
    """通用删除 — 覆盖景点/路线/公告/活动/服务/票务"""
    trace_id = request.state.trace_id
    store = _store_map.get(content_type)
    if not store: return err(40001, f"无效内容类型: {content_type}", trace_id)
    item = store.get(item_id)
    if not item: return err(40404, f"{item_id} 不存在", trace_id)
    if item.get("status") == "published":
        return err(40001, "已发布内容不可直接删除，请先撤回", trace_id)
    del store[item_id]
    return ok({"deleted": item_id, "type": content_type}, trace_id)
