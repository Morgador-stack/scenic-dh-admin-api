"""运行控制接口"""

from fastapi import APIRouter, Request

from app.schemas.common import ok

router = APIRouter(tags=["Runtime"])

_runtime_state = {
    "fayOnline": True,
    "ttsOnline": True,
    "speaking": False,
    "queueLength": 0,
    "lastError": None,
}


@router.get("/runtime/status")
def get_runtime_status(request: Request):
    trace_id = request.state.trace_id
    return ok(data=_runtime_state, trace_id=trace_id)


@router.post("/runtime/microphone/toggle")
def toggle_microphone(request: Request):
    trace_id = request.state.trace_id
    return ok(data={"microphone": "toggled", "status": "ok"}, trace_id=trace_id)


@router.post("/runtime/clear-queue")
def clear_queue(request: Request):
    trace_id = request.state.trace_id
    _runtime_state["queueLength"] = 0
    return ok(data={"queue": "cleared", "queueLength": 0}, trace_id=trace_id)
