"""知识库管理代理 — 管理端触发 RAG 入库与状态查询"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok
from app.config import settings

router = APIRouter(tags=["Knowledge"])

# 模拟的知识库状态
_knowledge_state = {
    "scenicId": "SA-001",
    "documents": 2,
    "chunks": 415,
    "updatedAt": "2026-06-02T10:00:00Z",
}


class SourceRequest(BaseModel):
    scenicId: str
    sourceName: str
    sourceType: str
    filePath: str | None = None


class ReindexRequest(BaseModel):
    scenicId: str
    reason: str = "manual"


@router.get("/knowledge/status")
def get_knowledge_status(scenic_id: str = None, request: Request = None):
    trace_id = request.state.trace_id
    return ok(data=_knowledge_state, trace_id=trace_id)


@router.post("/knowledge/sources")
def register_source(body: SourceRequest, request: Request):
    trace_id = request.state.trace_id
    return ok(data={"sourceId": f"SRC-{body.scenicId}-{body.sourceName}", "status": "registered"}, trace_id=trace_id)


@router.post("/knowledge/reindex")
def trigger_reindex(body: ReindexRequest, request: Request):
    trace_id = request.state.trace_id
    return ok(data={"jobId": f"REINDEX-{body.scenicId}-1", "status": "started"}, trace_id=trace_id)
