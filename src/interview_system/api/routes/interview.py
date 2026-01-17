"""访谈交互相关路由（薄层）。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from interview_system.api.deps import get_interview_service
from interview_system.api.mappers import to_message_response, to_message_responses
from interview_system.api.schemas.message import MessageCreate, MessageResponse
from interview_system.application.services.interview_service import InterviewService

router = APIRouter(prefix="/session/{session_id}", tags=["interview"])


@router.get("/messages", response_model=list[MessageResponse])
async def get_messages(
    session_id: UUID, service: InterviewService = Depends(get_interview_service)
):
    messages = await service.get_messages(session_id)
    return to_message_responses(messages)


@router.post("/message", response_model=MessageResponse)
async def send_message(
    session_id: UUID,
    data: MessageCreate,
    service: InterviewService = Depends(get_interview_service),
):
    result = await service.process_answer(session_id=session_id, answer=data.text)
    return to_message_response("assistant", result.assistant_message)


@router.post("/undo", response_model=list[MessageResponse])
async def undo_last(
    session_id: UUID, service: InterviewService = Depends(get_interview_service)
):
    await service.undo_last(session_id=session_id)
    messages = await service.get_messages(session_id)
    return to_message_responses(messages)


@router.post("/skip", response_model=MessageResponse)
async def skip_question(
    session_id: UUID, service: InterviewService = Depends(get_interview_service)
):
    result = await service.skip_question(session_id=session_id)
    return to_message_response("assistant", result.assistant_message)
