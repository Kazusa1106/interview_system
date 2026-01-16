from __future__ import annotations

from interview_system.domain.services.question_selector import select_questions


def test_select_questions_is_deterministic_with_seed():
    topics = [
        {"name": "t1", "scene": "学校", "edu_type": "德育"},
        {"name": "t2", "scene": "家庭", "edu_type": "智育"},
        {"name": "t3", "scene": "社区", "edu_type": "体育"},
        {"name": "t4", "scene": "学校", "edu_type": "美育"},
        {"name": "t5", "scene": "家庭", "edu_type": "劳育"},
        {"name": "t6", "scene": "社区", "edu_type": "德育"},
    ]
    scenes = ["学校", "家庭", "社区"]
    edu_types = ["德育", "智育", "体育", "美育", "劳育"]

    r1 = select_questions(
        topics=topics, scenes=scenes, edu_types=edu_types, total_questions=6, seed=42
    )
    r2 = select_questions(
        topics=topics, scenes=scenes, edu_types=edu_types, total_questions=6, seed=42
    )
    assert [t["name"] for t in r1] == [t["name"] for t in r2]


def test_select_questions_covers_all_scenes_and_edu_types():
    topics = [
        {"name": "t1", "scene": "学校", "edu_type": "德育"},
        {"name": "t2", "scene": "家庭", "edu_type": "智育"},
        {"name": "t3", "scene": "社区", "edu_type": "体育"},
        {"name": "t4", "scene": "学校", "edu_type": "美育"},
        {"name": "t5", "scene": "家庭", "edu_type": "劳育"},
        {"name": "t6", "scene": "社区", "edu_type": "德育"},
    ]
    scenes = ["学校", "家庭", "社区"]
    edu_types = ["德育", "智育", "体育", "美育", "劳育"]

    selected = select_questions(
        topics=topics, scenes=scenes, edu_types=edu_types, total_questions=6, seed=1
    )
    assert len(selected) == 6
    assert set(scenes).issubset({t["scene"] for t in selected})
    assert set(edu_types).issubset({t["edu_type"] for t in selected})
