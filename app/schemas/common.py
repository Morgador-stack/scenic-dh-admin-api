"""统一响应信封"""

from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel
from datetime import datetime, timezone


class Pagination(BaseModel):
    page: int = 1
    limit: int = 20
    total: int
    totalPages: int


class ErrorDetail(BaseModel):
    type: str
    message: str
    detail: Optional[Any] = None


class ResponseMeta(BaseModel):
    pagination: Optional[Pagination] = None


T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    code: Optional[str] = None
    error: Optional[ErrorDetail] = None
    traceId: str
    timestamp: str
    meta: Optional[ResponseMeta] = None


def ok(data: T, trace_id: str, pagination: Optional[Pagination] = None) -> ResponseEnvelope[T]:
    return ResponseEnvelope(
        success=True,
        data=data,
        traceId=trace_id,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        meta=ResponseMeta(pagination=pagination) if pagination else None,
    )


def err(code: str, error_type: str, message: str, trace_id: str, detail: Any = None) -> ResponseEnvelope:
    return ResponseEnvelope(
        success=False,
        code=code,
        error=ErrorDetail(type=error_type, message=message, detail=detail),
        traceId=trace_id,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
