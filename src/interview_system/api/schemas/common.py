"""通用 Schema。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="错误码", examples=["SESSION_NOT_FOUND"])
    message: str = Field(..., description="错误信息", examples=["Session not found"])
    details: dict[str, Any] | None = Field(default=None, description="错误详情")


class ErrorResponse(BaseModel):
    error: ErrorDetail
