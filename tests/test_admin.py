"""admin-api 冒烟测试"""

from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

AUTH = {"Authorization": f"Bearer {settings.ADMIN_TOKEN}"}


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "ok"


def test_auth_required():
    resp = client.get("/v1/knowledge/status")
    assert resp.status_code == 401


def test_auth_valid():
    resp = client.get("/v1/knowledge/status", headers=AUTH)
    assert resp.status_code == 200


def test_knowledge_status():
    resp = client.get("/v1/knowledge/status", headers=AUTH)
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["documents"] == 2


def test_persona_get():
    resp = client.get("/v1/personas/P1", headers=AUTH)
    data = resp.json()
    assert data["data"]["name"] == "灵山小导游"


def test_persona_not_found():
    resp = client.get("/v1/personas/P99", headers=AUTH)
    assert resp.json()["code"] == 40400


def test_create_broadcast():
    resp = client.post("/v1/broadcasts", headers=AUTH, json={"text": "测试播报", "priority": "high"})
    data = resp.json()
    assert data["code"] == 0
    assert "broadcastId" in data["data"]


def test_analytics_overview():
    resp = client.get("/v1/analytics/overview", headers=AUTH)
    data = resp.json()
    assert data["data"]["activeSessions"] >= 0


def test_runtime_status():
    resp = client.get("/v1/runtime/status", headers=AUTH)
    data = resp.json()
    assert data["data"]["fayOnline"] is True


def test_trace_header():
    resp = client.get("/health")
    assert "x-trace-id" in resp.headers

# ── Round 2 新增 P0 测试 ──

def test_auth_login():
    resp = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "token" in data
    assert data["user"]["role"] == "super_admin"

def test_auth_login_fail():
    resp = client.post("/v1/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.json()["code"] == 40100

def test_auth_me():
    resp = client.get("/v1/auth/me", headers=AUTH)
    assert resp.status_code == 200

def test_auth_users():
    resp = client.get("/v1/auth/users", headers=AUTH)
    assert resp.status_code == 200
    assert len(resp.json()["data"]["items"]) >= 2

def test_auth_roles():
    resp = client.get("/v1/auth/roles", headers=AUTH)
    assert resp.status_code == 200
    assert len(resp.json()["data"]["items"]) >= 2

def test_ops_snapshot():
    resp = client.get("/v1/admin/ops/snapshot", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "visitors" in data
    assert "alerts" in data
    assert "todos" in data

def test_content_create_spot():
    resp = client.post("/v1/content/spots", headers=AUTH, json={
        "name": "测试景点", "lat": 29.5, "lng": 106.5, "description": "测试"
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "draft"
    assert data["id"].startswith("SPOT-")

def test_content_list_spots():
    resp = client.get("/v1/content/spots", headers=AUTH)
    assert resp.status_code == 200
    assert len(resp.json()["data"]["items"]) >= 1

def test_content_publish_spot():
    # create first
    r = client.post("/v1/content/spots", headers=AUTH, json={
        "name": "发布测试", "lat": 29.6, "lng": 106.6
    })
    spot_id = r.json()["data"]["id"]
    resp = client.post(f"/v1/content/spots/{spot_id}/publish", headers=AUTH)
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "published"

def test_content_withdraw_spot():
    r = client.post("/v1/content/spots", headers=AUTH, json={
        "name": "撤回测试", "lat": 29.7, "lng": 106.7
    })
    spot_id = r.json()["data"]["id"]
    client.post(f"/v1/content/spots/{spot_id}/publish", headers=AUTH)
    resp = client.post(f"/v1/content/spots/{spot_id}/withdraw", headers=AUTH)
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "draft"

def test_content_notice_create_and_publish():
    resp = client.post("/v1/content/notices", headers=AUTH, json={
        "title": "闭园通知", "content": "6月15日闭园维护", "priority": "high"
    })
    nid = resp.json()["data"]["id"]
    resp2 = client.post(f"/v1/content/notices/{nid}/publish", headers=AUTH)
    assert resp2.json()["data"]["status"] == "published"

def test_content_event_create():
    resp = client.post("/v1/content/events", headers=AUTH, json={
        "name": "灯光秀", "time": "19:30", "location": "朝天门", "capacity": 200
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "draft"

def test_content_ticket_product():
    resp = client.post("/v1/content/ticket-products", headers=AUTH, json={
        "name": "VIP票", "price": 100.0, "applicableCrowd": "成人", "officialUrl": "https://buy.example.com/vip"
    })
    assert resp.status_code == 200
    resp2 = client.get("/v1/content/ticket-products", headers=AUTH)
    assert len(resp2.json()["data"]["items"]) >= 1

def test_config_get():
    resp = client.get("/v1/admin/config", headers=AUTH)
    assert resp.status_code == 200
    assert "featureFlags" in resp.json()["data"]

def test_config_feature_flags():
    resp = client.patch("/v1/admin/config/feature-flags", headers=AUTH, json={
        "flags": {"voiceGuide": True}
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["voiceGuide"] == True

def test_work_orders_admin():
    resp = client.get("/v1/admin/work-orders", headers=AUTH)
    assert resp.status_code == 200
    assert "items" in resp.json()["data"]

def test_approval_flow():
    """完整审批流: draft → submit → approve → published"""
    # 创建
    r = client.post("/v1/content/spots", headers=AUTH, json={"name": "审批测试", "lat": 30.0, "lng": 106.0})
    spot_id = r.json()["data"]["id"]
    assert r.json()["data"]["status"] == "draft"
    # 提交审核
    r2 = client.post(f"/v1/content/spots/{spot_id}/submit-review", headers=AUTH)
    assert r2.json()["data"]["status"] == "pending_review"
    # 检查待审列表
    r3 = client.get("/v1/content/pending-review", headers=AUTH)
    assert any(i["id"] == spot_id for i in r3.json()["data"]["items"])
    # 审核通过
    r4 = client.post(f"/v1/content/spots/{spot_id}/approve", headers=AUTH)
    assert r4.json()["data"]["status"] == "published"
    assert "approvedAt" in r4.json()["data"]

def test_approval_reject():
    """驳回流程"""
    r = client.post("/v1/content/notices", headers=AUTH, json={"title": "驳回测试", "content": "test", "priority": "low"})
    nid = r.json()["data"]["id"]
    client.post(f"/v1/content/notices/{nid}/submit-review", headers=AUTH)
    r2 = client.post(f"/v1/content/notices/{nid}/reject?reason=内容不完整", headers=AUTH)
    assert r2.json()["data"]["status"] == "draft"
    assert r2.json()["data"]["rejectionReason"] == "内容不完整"

def test_content_negative_price():
    """票价不能为负"""
    resp = client.post("/v1/content/ticket-products", headers=AUTH, json={
        "name": "负价票", "price": -50.0, "applicableCrowd": "成人", "officialUrl": "https://test.com"
    })
    assert resp.status_code == 422


def test_content_invalid_coordinates():
    """坐标范围校验"""
    resp = client.post("/v1/content/spots", headers=AUTH, json={
        "name": "无效坐标", "lat": 999.0, "lng": 0
    })
    assert resp.status_code == 422

def test_login_then_access():
    """登录获取token后能用该token访问受保护接口"""
    # 登录
    r = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    token = r.json()["data"]["token"]
    # 用动态token访问受保护接口
    resp = client.get("/v1/admin/config", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["code"] == 0

def test_dynamic_token_expiry():
    """过期token被拒绝（手动篡改时间）"""
    r = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["data"]["token"]
    # 直接篡改 token 存储，模拟过期
    from app.auth import _TOKENS
    for t in list(_TOKENS.keys()):
        if t == token:
            _TOKENS[t]["expiresAt"] = "2020-01-01T00:00:00Z"
    resp = client.get("/v1/admin/config", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
