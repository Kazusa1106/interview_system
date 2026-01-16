from __future__ import annotations

from interview_system.domain.services.followup_generator import FollowupGenerator


class FakeLLM:
    def __init__(self, reply: str | None):
        self._reply = reply

    def generate_followup(self, answer: str, topic: dict, conversation_log=None):  # type: ignore[override]
        return self._reply


def test_followup_generator_uses_llm_when_available():
    gen = FollowupGenerator(
        llm=FakeLLM("AI追问?"),
        min_answer_length=10,
        max_followups_per_question=3,
        max_depth_score=4,
    )
    r = gen.should_followup(
        answer="回答不够长",
        topic={"followups": ["预设"]},
        conversation_log=[],
        current_followup_count=0,
        depth_score=0,
        seed=1,
    )
    assert r.need_followup is True
    assert r.is_ai_generated is True


def test_followup_generator_falls_back_to_preset_when_forced():
    gen = FollowupGenerator(
        llm=FakeLLM(None),
        min_answer_length=10,
        max_followups_per_question=3,
        max_depth_score=4,
    )
    r = gen.should_followup(
        answer="短",
        topic={"followups": ["预设1", "预设2"]},
        conversation_log=[],
        current_followup_count=0,
        depth_score=0,
        seed=1,
    )
    assert r.need_followup is True
    assert r.is_ai_generated is False
    assert r.followup_question in {"预设1", "预设2"}
