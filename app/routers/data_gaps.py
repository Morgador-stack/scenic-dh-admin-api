"""资料缺口管理 — 维护缺失数据的清单和补充状态"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok

router = APIRouter(tags=["Data Gaps"])

# 当前已知缺口
_GAPS = [
    {
        "id": "GAP-001",
        "dataType": "gps_coordinates",
        "description": "16 个景点的精确经纬度坐标",
        "impact": "地图 POI 标记、附近设施查询、到达触发精度",
        "status": "mock",
        "mockStrategy": "手工指定模拟坐标",
        "priority": "P0",
        "owner": "接口负责人",
    },
    {
        "id": "GAP-002",
        "dataType": "realtime_weather",
        "description": "景区实时天气数据",
        "impact": "首页天气展示、出行提醒、数字人天气提示",
        "status": "mock",
        "mockStrategy": "demo-mock-service 固定返回",
        "priority": "P0",
        "owner": "接口负责人",
    },
    {
        "id": "GAP-003",
        "dataType": "realtime_crowd",
        "description": "实时客流和景点排队时长",
        "impact": "运营看板实时数据、路线避堵建议",
        "status": "mock",
        "mockStrategy": "demo-mock-service 固定返回",
        "priority": "P0",
        "owner": "接口负责人",
    },
    {
        "id": "GAP-004",
        "dataType": "current_announcements",
        "description": "当前有效公告、临时闭园、演出调整通知",
        "impact": "公告列表、主动播报内容",
        "status": "manual_seed",
        "mockStrategy": "后台手工 seed 维护",
        "priority": "P0",
        "owner": "接口负责人",
    },
    {
        "id": "GAP-005",
        "dataType": "ticket_inventory",
        "description": "真实票务库存、订单、支付状态",
        "impact": "票务预约功能",
        "status": "not_applicable",
        "mockStrategy": "仅做票务信息展示和跳转占位，不做交易",
        "priority": "P0",
        "owner": "接口负责人",
    },
    {
        "id": "GAP-006",
        "dataType": "complaint_workflow",
        "description": "投诉工单流程（类型、处理人、流转记录）",
        "impact": "投诉反馈完整闭环",
        "status": "simplified",
        "mockStrategy": "使用 feedback 接口简化状态流替代",
        "priority": "P0",
        "owner": "接口负责人",
    },
    {
        "id": "GAP-007",
        "dataType": "lost_found_records",
        "description": "失物招领记录",
        "impact": "失物登记、认领查询",
        "status": "manual_seed",
        "mockStrategy": "手工构建演示 seed 数据",
        "priority": "P1",
        "owner": "接口负责人",
    },
    {
        "id": "GAP-008",
        "dataType": "emergency_contacts",
        "description": "客服热线、应急电话、医疗救助联系方式",
        "impact": "服务指南、数字人兜底引导",
        "status": "pending",
        "mockStrategy": "需人工补充，确认前不强答",
        "priority": "P1",
        "owner": "接口负责人 + RAG负责人",
    },
    {
        "id": "GAP-009",
        "dataType": "user_accounts",
        "description": "真实用户账号体系、收藏、浏览记录",
        "impact": "个性化推荐、游客中心",
        "status": "not_applicable",
        "mockStrategy": "使用匿名 session 和演示行为",
        "priority": "P0",
        "owner": "接口负责人",
    },
    {
        "id": "GAP-010",
        "dataType": "route_topology",
        "description": "路网拓扑、精确导航路径",
        "impact": "地图导航、路线规划算法",
        "status": "mock",
        "mockStrategy": "使用手工路线顺序 + 模拟坐标",
        "priority": "P0",
        "owner": "接口负责人",
    },
]


class GapUpdateRequest(BaseModel):
    status: str | None = None
    mockStrategy: str | None = None
    note: str | None = None


@router.get("/data-gaps")
def list_data_gaps(priority: str = None, status: str = None, request: Request = None):
    trace_id = request.state.trace_id
    gaps = _GAPS
    if priority:
        gaps = [g for g in gaps if g["priority"] == priority]
    if status:
        gaps = [g for g in gaps if g["status"] == status]
    return ok(
        data={
            "items": gaps,
            "total": len(gaps),
            "summary": {
                "total": len(_GAPS),
                "p0": len([g for g in _GAPS if g["priority"] == "P0"]),
                "p1": len([g for g in _GAPS if g["priority"] == "P1"]),
                "resolved": len([g for g in _GAPS if g["status"] in ("resolved", "not_applicable")]),
                "pending": len([g for g in _GAPS if g["status"] in ("pending", "mock", "manual_seed")]),
            },
        },
        trace_id=trace_id,
    )


@router.patch("/data-gaps/{gap_id}")
def update_gap(gap_id: str, body: GapUpdateRequest, request: Request):
    trace_id = request.state.trace_id
    for g in _GAPS:
        if g["id"] == gap_id:
            if body.status is not None:
                g["status"] = body.status
            if body.mockStrategy is not None:
                g["mockStrategy"] = body.mockStrategy
            return ok(data=g, trace_id=trace_id)
    from app.schemas.common import err
    return err("NOT_FOUND", "NOT_FOUND", f"缺口 {gap_id} 不存在", trace_id)
