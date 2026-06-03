"""审计日志模块 — 记录所有管理操作"""

import time
import uuid
from typing import Optional

# 内存审计日志（MVP 阶段；后续换持久化存储）
_audit_logs: list[dict] = []


def log_action(
    action: str,
    operator: str = "admin",
    target: str = "",
    detail: Optional[dict] = None,
    trace_id: str = "",
) -> dict:
    """记录一条审计日志"""
    entry = {
        "id": str(uuid.uuid4())[:12],
        "action": action,
        "operator": operator,
        "target": target,
        "detail": detail or {},
        "trace_id": trace_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _audit_logs.append(entry)
    return entry


def get_logs(limit: int = 50, action: Optional[str] = None) -> list[dict]:
    """查询审计日志"""
    logs = _audit_logs
    if action:
        logs = [l for l in logs if l["action"] == action]
    return logs[-limit:]


# 预定义操作类型
ACTION_KNOWLEDGE_REINDEX = "knowledge.reindex"
ACTION_KNOWLEDGE_SOURCE_REGISTER = "knowledge.source.register"
ACTION_PERSONA_UPDATE = "persona.update"
ACTION_BROADCAST_CREATE = "broadcast.create"
ACTION_MESSAGE_ADOPT = "message.adopt"
ACTION_RUNTIME_CLEAR_QUEUE = "runtime.clear_queue"
ACTION_RUNTIME_MIC_TOGGLE = "runtime.microphone.toggle"
