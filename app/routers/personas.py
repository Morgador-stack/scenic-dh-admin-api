"""人设与提示词策略"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok, err

router = APIRouter(tags=["Personas"])

_PERSONAS = {
    "P1": {
        "id": "P1",
        "name": "灵山小导游",
        "description": "热情活泼，面向普通游客的导览数字人。用通俗易懂的语言讲解佛教文化和景点故事。",
        "tone": "friendly",
        "fallbackPolicy": {
            "maxRetries": 2,
            "lowConfidenceThreshold": 0.4,
            "timeoutMs": 8000,
            "defaultFallback": "抱歉，这个问题我需要问一下景区工作人员，请稍等。",
        },
    },
    "P2": {
        "id": "P2",
        "name": "灵山文化导览",
        "description": "专业庄重，面向文化深度游游客。引用经典文献深入讲解佛教艺术和历史。",
        "tone": "professional",
        "fallbackPolicy": {
            "maxRetries": 3,
            "lowConfidenceThreshold": 0.5,
            "timeoutMs": 12000,
            "defaultFallback": "关于这个问题，目前资料尚不充分，建议查阅景区官方文献以获取更准确的信息。",
        },
    },
}


class PersonaUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    tone: str | None = None
    fallbackPolicy: dict | None = None


@router.get("/personas/{persona_id}")
def get_persona(persona_id: str, request: Request):
    trace_id = request.state.trace_id
    persona = _PERSONAS.get(persona_id)
    if not persona:
        return err(40400, f"人设 {persona_id} 不存在", trace_id)
    return ok(persona, trace_id=trace_id)


@router.put("/personas/{persona_id}")
def update_persona(persona_id: str, body: PersonaUpdateRequest, request: Request):
    trace_id = request.state.trace_id
    persona = _PERSONAS.get(persona_id)
    if not persona:
        return err(40400, f"人设 {persona_id} 不存在", trace_id)
    if body.name is not None:
        persona["name"] = body.name
    if body.description is not None:
        persona["description"] = body.description
    if body.tone is not None:
        persona["tone"] = body.tone
    if body.fallbackPolicy is not None:
        persona["fallbackPolicy"] = body.fallbackPolicy
    _PERSONAS[persona_id] = persona
    return ok(persona, trace_id=trace_id)
