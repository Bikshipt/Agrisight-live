"""
Tests for Offline Sync API.
"""
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_offline_sync_accepts_scans():
  payload = {"scans": [{"scan_image": "base64", "local_prediction": "Leaf spot"}]}
  resp = client.post("/api/offline-sync", json=payload)
  assert resp.status_code == 200
  data = resp.json()
  assert data["status"] == "accepted"
  assert data["count"] == 1

