"""Dependency injection for FastAPI。"""

from __future__ import annotations

from fastapi import Request

from interview_system.application.services.interview_service import InterviewService
from interview_system.application.services.session_service import SessionService
from interview_system.config.settings import Settings
from interview_system.domain.services.answer_processor import AnswerProcessor
from interview_system.domain.services.followup_generator import FollowupGenerator
from interview_system.infrastructure.cache.memory_cache import SessionCache
from interview_system.infrastructure.database.connection import AsyncDatabase
from interview_system.infrastructure.database.repositories.session_repository_impl import (
    SessionRepositoryImpl,
)


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_database(request: Request) -> AsyncDatabase:
    return request.app.state.db


def get_session_cache(request: Request) -> SessionCache:
    return request.app.state.session_cache


def get_session_repository(request: Request) -> SessionRepositoryImpl:
    db = get_database(request)
    cache = get_session_cache(request)
    return SessionRepositoryImpl(db, cache=cache)


def get_session_service(request: Request) -> SessionService:
    repo = get_session_repository(request)
    return SessionService(repo)


def get_interview_service(request: Request) -> InterviewService:
    from interview_system.common.config import INTERVIEW_CONFIG
    from interview_system.core.questions import EDU_TYPES, SCENES, TOPICS
    from interview_system.integrations.api_helpers import generate_followup

    class _LLM:
        def generate_followup(self, answer: str, topic: dict, conversation_log=None):
            try:
                return generate_followup(answer, topic, conversation_log)
            except Exception:
                return None

    repo = get_session_repository(request)

    processor = AnswerProcessor(
        depth_keywords=INTERVIEW_CONFIG.depth_keywords,
        common_keywords=INTERVIEW_CONFIG.common_keywords,
        max_depth_score=INTERVIEW_CONFIG.max_depth_score,
    )

    followup = FollowupGenerator(
        llm=_LLM(),
        min_answer_length=INTERVIEW_CONFIG.min_answer_length,
        max_followups_per_question=INTERVIEW_CONFIG.max_followups_per_question,
        max_depth_score=INTERVIEW_CONFIG.max_depth_score,
    )

    return InterviewService(
        repository=repo,
        answer_processor=processor,
        followup_generator=followup,
        topics_source={"TOPICS": TOPICS, "SCENES": SCENES, "EDU_TYPES": EDU_TYPES},
        total_questions=INTERVIEW_CONFIG.total_questions,
    )
