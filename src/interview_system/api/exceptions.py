"""API 异常与统一错误响应。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from interview_system.application.exceptions import (
    NothingToUndoError,
    SessionAlreadyCompletedError,
    SessionNotFoundError,
)


@dataclass(frozen=True, slots=True)
class APIError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: dict[str, Any] | None = None


def _error_payload(
    *, code: str, message: str, details: dict[str, Any] | None
) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def _handle_api_error(_request: Request, exc: APIError):  # noqa: ANN001
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                code=exc.code, message=exc.message, details=exc.details
            ),
        )

    @app.exception_handler(SessionNotFoundError)
    async def _handle_session_not_found(_request: Request, exc: SessionNotFoundError):  # noqa: ANN001
        return JSONResponse(
            status_code=404,
            content=_error_payload(
                code="SESSION_NOT_FOUND",
                message="Session not found",
                details={"session_id": str(exc.session_id)},
            ),
        )

    @app.exception_handler(SessionAlreadyCompletedError)
    async def _handle_session_completed(
        _request: Request, exc: SessionAlreadyCompletedError
    ):  # noqa: ANN001
        return JSONResponse(
            status_code=400,
            content=_error_payload(
                code="SESSION_COMPLETED",
                message="Session already completed",
                details={"session_id": str(exc.session_id)},
            ),
        )

    @app.exception_handler(NothingToUndoError)
    async def _handle_nothing_to_undo(_request: Request, exc: NothingToUndoError):  # noqa: ANN001
        return JSONResponse(
            status_code=400,
            content=_error_payload(
                code="NO_MESSAGES_TO_UNDO",
                message="No messages to undo",
                details={"session_id": str(exc.session_id)},
            ),
        )
