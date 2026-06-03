"""审计日志查询接口"""

from fastapi import APIRouter, Request, Query

from app.schemas.common import ok
from app.audit import get_logs

router = APIRouter(tags=["Audit Logs"])


@router.get("/audit-logs")
def list_audit_logs(action: str = Query(None), limit: int = Query(50, ge=1, le=200), request: Request = None):
    trace_id = request.state.trace_id
    logs = get_logs(limit=limit, action=action)
    return ok({"items": logs, "total": len(logs)}, trace_id)
