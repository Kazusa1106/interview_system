from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from interview_system.api.main import create_app
from interview_system.config.settings import Settings


def test_api_session_flow_and_errors():
    app = create_app(
        Settings(
            database_url="sqlite+aiosqlite:///:memory:",
            log_level="INFO",
            allowed_origins=[],
        )
    )

    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200

        r = client.post("/api/session/start", json={})
        assert r.status_code == 200
        payload = r.json()
        assert payload["status"] == "active"
        session_id = payload["id"]

        # uuid 格式
        UUID(session_id)

        msgs = client.get(f"/api/session/{session_id}/messages")
        assert msgs.status_code == 200
        messages = msgs.json()
        assert messages and messages[-1]["role"] == "assistant"

        send = client.post(f"/api/session/{session_id}/message", json={"text": "短"})
        assert send.status_code == 200
        assert send.json()["role"] == "assistant"

        undo = client.post(f"/api/session/{session_id}/undo")
        assert undo.status_code == 200

        # 空撤销应返回统一错误格式
        undo2 = client.post(f"/api/session/{session_id}/undo")
        assert undo2.status_code == 400
        err = undo2.json()
        assert err["error"]["code"] == "NO_MESSAGES_TO_UNDO"

        skip = client.post(f"/api/session/{session_id}/skip")
        assert skip.status_code == 200

        stats = client.get(f"/api/session/{session_id}/stats")
        assert stats.status_code == 200
        assert "total_messages" in stats.json()

        deleted = client.delete(f"/api/session/{session_id}")
        assert deleted.status_code == 200

        not_found = client.get(f"/api/session/{session_id}")
        assert not_found.status_code == 404
        assert not_found.json()["error"]["code"] == "SESSION_NOT_FOUND"
