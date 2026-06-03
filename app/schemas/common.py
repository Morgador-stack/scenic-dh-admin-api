"""统一响应信封 — 对齐 RAG 服务 {code, message, data, trace_id}"""

from typing import Optional, Any
from pydantic import BaseModel


class Pagination(BaseModel):
    page: int = 1
    page_size: int = 20
    total: int
    total_pages: int


def ok(data: Any, trace_id: str) -> dict:
    return {
        "code": 0,
        "message": "success",
        "data": data,
        "trace_id": trace_id,
    }


def err(code: int, message: str, trace_id: str) -> dict:
    return {
        "code": code,
        "message": message,
        "data": None,
        "trace_id": trace_id,
    }
