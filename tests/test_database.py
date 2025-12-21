from interview_system.data.database import get_database
from interview_system.services.session_manager import get_session_manager


def test_delete_last_conversation_logs_deletes_exact_n(isolated_runtime):
    sm = get_session_manager()
    db = get_database()

    session = sm.create_session("tester")
    sid = session.session_id

    sm.add_conversation_log(
        sid,
        {
            "timestamp": "2025-01-01 00:00:00",
            "topic": "学校-德育",
            "question_type": "核心问题",
            "question": "Q1",
            "answer": "A1",
            "depth_score": 1,
        },
    )
    sm.add_conversation_log(
        sid,
        {
            "timestamp": "2025-01-01 00:00:01",
            "topic": "学校-德育",
            "question_type": "追问回答",
            "question": "Q2",
            "answer": "A2",
            "depth_score": 1,
            "is_ai_generated": True,
        },
    )
    sm.add_conversation_log(
        sid,
        {
            "timestamp": "2025-01-01 00:00:02",
            "topic": "学校-德育",
            "question_type": "追问跳过",
            "question": "Q3",
            "answer": "A3",
            "depth_score": 0,
        },
    )

    assert len(db.get_conversation_logs(sid)) == 3

    ok = db.delete_last_conversation_logs(sid, 2)
    assert ok is True

    remaining = db.get_conversation_logs(sid)
    assert len(remaining) == 1
    assert remaining[0]["answer"] == "A1"


def test_rollback_session_state_is_atomic(isolated_runtime):
    sm = get_session_manager()
    db = get_database()

    session = sm.create_session("tester")
    sid = session.session_id

    sm.add_conversation_log(
        sid,
        {
            "timestamp": "2025-01-01 00:00:00",
            "topic": "学校-德育",
            "question_type": "核心问题",
            "question": "Q1",
            "answer": "A1",
            "depth_score": 1,
        },
    )
    sm.add_conversation_log(
        sid,
        {
            "timestamp": "2025-01-01 00:00:01",
            "topic": "学校-德育",
            "question_type": "核心问题",
            "question": "Q2",
            "answer": "A2",
            "depth_score": 1,
        },
    )

    # 正常回滚：删除 1 条，并更新会话状态
    ok = db.rollback_session_state(
        sid,
        delete_log_count=1,
        session_update={
            "current_question_idx": 0,
            "is_finished": False,
            "end_time": None,
            "is_followup": False,
            "current_followup_is_ai": False,
            "current_followup_count": 0,
            "current_followup_question": "",
        },
    )
    assert ok is True
    assert len(db.get_conversation_logs(sid)) == 1
