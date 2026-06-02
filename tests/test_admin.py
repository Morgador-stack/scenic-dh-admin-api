"""admin-api 冒烟测试"""

from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

AUTH = {"x-admin-token": settings.ADMIN_TOKEN}


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
    assert data["success"]
    assert data["data"]["documents"] == 2


def test_persona_get():
    resp = client.get("/v1/personas/P1", headers=AUTH)
    data = resp.json()
    assert data["data"]["name"] == "灵山小导游"


def test_persona_not_found():
    resp = client.get("/v1/personas/P99", headers=AUTH)
    assert resp.json()["code"] == "NOT_FOUND"


def test_create_broadcast():
    resp = client.post("/v1/broadcasts", headers=AUTH, json={"text": "测试播报", "priority": "high"})
    data = resp.json()
    assert data["success"]
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
