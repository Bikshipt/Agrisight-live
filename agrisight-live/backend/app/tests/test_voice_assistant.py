"""
Tests for Voice Assistant API.
"""
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_voice_query_basic_response():
    resp = client.post("/api/voice-query", json={"text": "Why are my rice leaves turning brown?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data

