from __future__ import annotations

from interview_system.domain.services.answer_processor import AnswerProcessor


def test_answer_processor_scores_depth_and_returns_result():
    processor = AnswerProcessor(
        depth_keywords=["具体", "经历"],
        common_keywords=["时间"],
        max_depth_score=4,
    )
    topic = {"name": "学校-德育", "questions": ["Q1"]}

    result = processor.process_core_answer(answer="我有一次具体经历", topic=topic)
    assert result.topic == "学校-德育"
    assert result.question == "Q1"
    assert result.depth_score >= 1
