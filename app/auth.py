"""IAM / RBAC — 管理员登录、token管理、用户角色权限"""

import hashlib
import secrets
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok, err

router = APIRouter(tags=["Auth"])

# ── 种子管理员 ──
_USERS: dict[str, dict] = {
    "admin": {
        "id": "ADM-001",
        "username": "admin",
        "passwordHash": hashlib.sha256("admin123".encode()).hexdigest(),
        "displayName": "超级管理员",
        "role": "super_admin",
        "status": "active",
    },
    "operator": {
        "id": "ADM-002",
        "username": "operator",
        "passwordHash": hashlib.sha256("oper123".encode()).hexdigest(),
        "displayName": "运营人员",
        "role": "operator",
        "status": "active",
    },
}

_ROLES: dict[str, dict] = {
    "super_admin": {"name": "super_admin", "label": "超级管理员", "permissions": ["*"]},
    "operator": {"name": "operator", "label": "运营人员", "permissions": ["content:read", "content:write", "work_order:read", "work_order:write", "broadcasts:write", "knowledge:read"]},
    "viewer": {"name": "viewer", "label": "只读用户", "permissions": ["content:read", "analytics:read"]},
}

_TOKENS: dict[str, dict] = {}  # token -> {username, expiresAt, scope}


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    token: str


@router.post("/auth/login")
def login(body: LoginRequest, request: Request):
    trace_id = request.state.trace_id
    user = _USERS.get(body.username)
    if not user:
        return err(40100, "用户名或密码错误", trace_id)

    pw_hash = hashlib.sha256(body.password.encode()).hexdigest()
    if pw_hash != user["passwordHash"]:
        return err(40100, "用户名或密码错误", trace_id)

    if user["status"] != "active":
        return err(40300, "该账号已被停用", trace_id)

    token = f"adm_{secrets.token_hex(32)}"
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _TOKENS[token] = {"username": body.username, "expiresAt": expires_at, "scope": user["role"]}

    return ok({
        "token": token,
        "expiresAt": expires_at,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "displayName": user["displayName"],
            "role": user["role"],
        },
    }, trace_id)


@router.post("/auth/refresh")
def refresh_token(body: RefreshTokenRequest, request: Request):
    trace_id = request.state.trace_id
    token_info = _TOKENS.get(body.token)
    if not token_info:
        return err(40101, "token 无效或已过期", trace_id)

    new_token = f"adm_{secrets.token_hex(32)}"
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _TOKENS[new_token] = {"username": token_info["username"], "expiresAt": expires_at, "scope": token_info["scope"]}
    del _TOKENS[body.token]

    return ok({"token": new_token, "expiresAt": expires_at}, trace_id)


@router.get("/auth/me")
def get_current_user(request: Request):
    trace_id = request.state.trace_id
    username = getattr(request.state, "admin_username", None)
    if not username or username not in _USERS:
        return err(40101, "未登录", trace_id)
    user = _USERS[username]
    role = _ROLES.get(user["role"], {"permissions": []})
    return ok({
        "id": user["id"],
        "username": user["username"],
        "displayName": user["displayName"],
        "role": user["role"],
        "permissions": role["permissions"],
    }, trace_id)


@router.get("/auth/users")
def list_users(request: Request):
    trace_id = request.state.trace_id
    users = [{"id": u["id"], "username": u["username"], "displayName": u["displayName"], "role": u["role"], "status": u["status"]} for u in _USERS.values()]
    return ok({"items": users, "total": len(users)}, trace_id)


@router.get("/auth/roles")
def list_roles(request: Request):
    trace_id = request.state.trace_id
    roles = list(_ROLES.values())
    return ok({"items": roles, "total": len(roles)}, trace_id)
