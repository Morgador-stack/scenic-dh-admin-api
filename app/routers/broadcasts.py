"""人工播报接口"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok

router = APIRouter(tags=["Broadcasts"])

_BROADCASTS: list[dict] = []


class BroadcastRequest(BaseModel):
    text: str
    target: str = "all"
    targetId: str | None = None
    priority: str = "normal"


@router.post("/broadcasts")
def create_broadcast(body: BroadcastRequest, request: Request):
    trace_id = request.state.trace_id
    broadcast_id = str(uuid.uuid4())[:8]
    bc = {
        "id": broadcast_id,
        "text": body.text,
        "priority": body.priority,
        "target": body.target,
        "targetId": body.targetId,
        "expiresAt": datetime.now(timezone.utc).replace(hour=18).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "queued",
    }
    _BROADCASTS.append(bc)
    return ok(data={"broadcastId": broadcast_id, "queueState": "queued"}, trace_id=trace_id)


@router.get("/broadcasts")
def list_broadcasts(request: Request):
    trace_id = request.state.trace_id
    return ok(data={"items": _BROADCASTS}, trace_id=trace_id)
