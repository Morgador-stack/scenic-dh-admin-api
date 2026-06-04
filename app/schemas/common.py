"""统一响应信封 — 对齐 RAG 服务 {code, message, data, trace_id}"""

from typing import Optional, Any
from pydantic import BaseModel


class Pagination(BaseModel):
    page: int = 1
    page_size: int = 20
    total: int
    total_pages: int


class ResponseEnvelope(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
    trace_id: str = ""


def ok(data: Any, trace_id: str, pagination: Optional[Pagination] = None) -> dict:
    """构造成功响应，可选分页"""
    result: dict = {
        "code": 0,
        "message": "success",
        "data": data,
        "trace_id": trace_id,
    }
    if pagination:
        result["data"] = {
            "items": data,
            "pagination": {
                "page": pagination.page,
                "page_size": pagination.page_size,
                "total": pagination.total,
                "total_pages": pagination.total_pages,
            },
        }
    return result


def err(code: int, message: str, trace_id: str) -> dict:
    """构造错误响应"""
    return {
        "code": code,
        "message": message,
        "data": None,
        "trace_id": trace_id,
    }
