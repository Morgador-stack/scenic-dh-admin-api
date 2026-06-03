"""运营分析接口"""

from fastapi import APIRouter, Request, Query

from app.schemas.common import ok

router = APIRouter(tags=["Analytics"])


@router.get("/analytics/overview")
def get_overview(date_range: str = Query(None), request: Request = None):
    trace_id = request.state.trace_id
    return ok(
        {
            "activeSessions": 42,
            "totalMessages": 1280,
            "avgRating": 4.3,
            "fallbackRate": 0.12,
            "ragHitRate": 0.88,
            "avatarUptime": 0.997,
        },
        trace_id,
    )


@router.get("/analytics/hot-questions")
def get_hot_questions(date_range: str = Query(None), request: Request = None):
    trace_id = request.state.trace_id
    return ok(
        {
            "items": [
                {"question": "灵山大佛有多高", "count": 145, "avgConfidence": 0.92},
                {"question": "九龙灌浴表演时间", "count": 98, "avgConfidence": 0.88},
                {"question": "梵宫里面有什么", "count": 87, "avgConfidence": 0.85},
                {"question": "灵山的门票多少钱", "count": 72, "avgConfidence": 0.78},
                {"question": "怎么从无锡市区到灵山", "count": 65, "avgConfidence": 0.45},
            ]
        },
        trace_id,
    )


@router.get("/analytics/rag")
def get_rag_analytics(date_range: str = Query(None), request: Request = None):
    trace_id = request.state.trace_id
    return ok(
        {
            "hitRate": 0.88,
            "fallbackRate": 0.12,
            "avgLatencyMs": 320,
            "p95LatencyMs": 850,
            "topFallbackReasons": [
                {"reason": "no_citation", "count": 42},
                {"reason": "low_confidence", "count": 28},
                {"reason": "timeout", "count": 8},
            ],
        },
        trace_id,
    )


@router.get("/analytics/avatar")
def get_avatar_analytics(date_range: str = Query(None), request: Request = None):
    trace_id = request.state.trace_id
    return ok(
        {
            "speechCount": 1150,
            "failures": 15,
            "avgSpeechDurationMs": 8000,
            "avgQueueLength": 2.1,
            "uptime": "99.7%",
        },
        trace_id,
    )
