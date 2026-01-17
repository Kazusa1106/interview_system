from __future__ import annotations

import pytest

from interview_system.application.services.interview_service import InterviewService
from interview_system.domain.entities import Session
from interview_system.domain.services.answer_processor import AnswerProcessor
from interview_system.domain.services.followup_generator import FollowupGenerator
from interview_system.domain.value_objects.conversation_entry import ConversationEntry


class FakeRepo:
    def __init__(self):
        self.sessions: dict[str, Session] = {}
        self.logs: dict[str, list[ConversationEntry]] = {}

    async def get(self, session_id):  # type: ignore[override]
        return self.sessions.get(str(session_id))

    async def save(self, session: Session) -> None:  # type: ignore[override]
        self.sessions[str(session.id)] = session

    async def delete(self, session_id):  # type: ignore[override]
        self.sessions.pop(str(session_id), None)
        self.logs.pop(str(session_id), None)
        return True

    async def list_conversation_entries(self, session_id):  # type: ignore[override]
        return list(self.logs.get(str(session_id), []))

    async def append_conversation_entry(
        self, session_id, entry: ConversationEntry
    ) -> None:  # type: ignore[override]
        self.logs.setdefault(str(session_id), []).append(entry)

    async def delete_last_conversation_entry(self, session_id):  # type: ignore[override]
        items = self.logs.get(str(session_id), [])
        if not items:
            return None
        return items.pop()


def _service(repo: FakeRepo) -> InterviewService:
    processor = AnswerProcessor(
        depth_keywords=["具体"], common_keywords=[], max_depth_score=4
    )
    followup = FollowupGenerator(
        llm=None, min_answer_length=10, max_followups_per_question=3, max_depth_score=4
    )
    topics_source = {
        "TOPICS": [
            {
                "name": "学校-德育",
                "scene": "学校",
                "edu_type": "德育",
                "questions": ["Q1"],
                "followups": ["F1"],
            },
            {
                "name": "家庭-智育",
                "scene": "家庭",
                "edu_type": "智育",
                "questions": ["Q2"],
                "followups": ["F2"],
            },
            {
                "name": "社区-体育",
                "scene": "社区",
                "edu_type": "体育",
                "questions": ["Q3"],
                "followups": ["F3"],
            },
            {
                "name": "学校-美育",
                "scene": "学校",
                "edu_type": "美育",
                "questions": ["Q4"],
                "followups": ["F4"],
            },
            {
                "name": "家庭-劳育",
                "scene": "家庭",
                "edu_type": "劳育",
                "questions": ["Q5"],
                "followups": ["F5"],
            },
            {
                "name": "社区-德育",
                "scene": "社区",
                "edu_type": "德育",
                "questions": ["Q6"],
                "followups": ["F6"],
            },
        ],
        "SCENES": ["学校", "家庭", "社区"],
        "EDU_TYPES": ["德育", "智育", "体育", "美育", "劳育"],
    }
    return InterviewService(
        repository=repo,  # type: ignore[arg-type]
        answer_processor=processor,
        followup_generator=followup,
        topics_source=topics_source,
        total_questions=2,
    )


@pytest.mark.asyncio
async def test_interview_service_start_and_get_messages():
    repo = FakeRepo()
    service = _service(repo)

    session = await service.start_session(user_name="tester", topics=None)
    assert session.user_name == "tester"
    assert len(session.selected_topics) == 2

    messages = await service.get_messages(session.id)
    assert messages[-1]["role"] == "assistant"
    assert "第1/2题" in messages[-1]["content"]


@pytest.mark.asyncio
async def test_interview_service_followup_then_next_question():
    repo = FakeRepo()
    service = _service(repo)
    session = await service.start_session(user_name="tester", topics=None)

    # 短回答触发强制追问（预设）
    r1 = await service.process_answer(session_id=session.id, answer="短")
    assert r1.is_finished is False
    assert r1.assistant_message in {"F1", "F2", "F3", "F4", "F5", "F6"}

    # 追问回答足够长，结束追问并进入下一题
    r2 = await service.process_answer(
        session_id=session.id, answer="足够长的回答内容足够长"
    )
    assert r2.is_finished is False
    assert "第2/2题" in r2.assistant_message


@pytest.mark.asyncio
async def test_interview_service_undo_and_restart():
    repo = FakeRepo()
    service = _service(repo)
    session = await service.start_session(user_name="tester", topics=None)

    await service.process_answer(session_id=session.id, answer="短")
    assert await service.get_messages(session.id)

    await service.undo_last(session_id=session.id)
    messages = await service.get_messages(session.id)
    assert messages[-1]["role"] == "assistant"

    await service.restart(session_id=session.id)
    messages2 = await service.get_messages(session.id)
    assert len(messages2) == 1
