"""会话审计、消息审计、问答采纳"""

from fastapi import APIRouter, Request, Query

from app.schemas.common import ok, err

router = APIRouter(tags=["Audit"])

# 管理端共享 business-api 的内存存储（实际部署时通过 HTTP 代理查询 business-api）
# MVP 阶段这里返回模拟数据


@router.get("/sessions")
def list_sessions(date_range: str = Query(None), status: str = Query(None), request: Request = None):
    trace_id = request.state.trace_id
    return ok(
        data={
            "items": [
                {"id": "550e8400-...", "profile": {"language": "zh"}, "source": "miniprogram", "status": "active", "createdAt": "2026-06-02T09:00:00Z"},
            ],
            "total": 1,
        },
        trace_id=trace_id,
    )


@router.get("/sessions/{session_id}")
def get_session_detail(session_id: str, request: Request):
    trace_id = request.state.trace_id
    return ok(
        data={
            "id": session_id,
            "profile": {"language": "zh", "interests": ["佛教文化"]},
            "status": "active",
            "messages": [
                {"id": "MSG-001", "role": "user", "text": "灵山大佛有多高？", "fallback": False, "confidence": 0.95},
                {"id": "MSG-002", "role": "assistant", "text": "灵山大佛高88米...", "citations": [], "fallback": False, "confidence": 0.95},
            ],
            "events": [],
            "feedback": [],
        },
        trace_id=trace_id,
    )


@router.get("/messages")
def list_messages(date_range: str = Query(None), fallback: bool = Query(None), request: Request = None):
    trace_id = request.state.trace_id
    return ok(
        data={
            "items": [
                {"id": "MSG-001", "sessionId": "550e8400-...", "role": "user", "text": "灵山大佛有多高？", "fallback": False, "createdAt": "2026-06-02T10:00:00Z"},
                {"id": "MSG-002", "sessionId": "550e8400-...", "role": "assistant", "text": "灵山大佛高88米...", "fallback": False, "createdAt": "2026-06-02T10:00:01Z"},
            ],
            "total": 2,
        },
        trace_id=trace_id,
    )


@router.post("/messages/{message_id}/adopt")
def adopt_message(message_id: str, request: Request):
    trace_id = request.state.trace_id
    return ok(data={"messageId": message_id, "adopted": True, "category": "faq_candidate"}, trace_id=trace_id)
