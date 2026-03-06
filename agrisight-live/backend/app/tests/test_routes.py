"""
Tests for API Routes.
Expected env vars: MOCK_GEMINI=true
Testing tips: Run with pytest.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_start_session():
    response = client.post("/api/start-session")
    assert response.status_code == 200
    assert "session_id" in response.json()


def test_live_websocket_mock_stream():
    # Ensure we can open a session and connect to live WS in mock mode.
    session_resp = client.post("/api/start-session")
    session_id = session_resp.json()["session_id"]

    with client.websocket_connect(f"/api/ws/live/{session_id}") as websocket:
        websocket.send_json(
            {
                "type": "video_frame",
                "timestamp": 123,
                "image_base64": "dummy",
            }
        )
        message = websocket.receive_text()
        assert "diagnosis" in message or "annotation" in message

