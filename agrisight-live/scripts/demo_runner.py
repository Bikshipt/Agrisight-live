"""
Demo Runner Script.

Simulates a farmer session end-to-end for recording hackathon demo videos.

Usage:
- Ensure backend is running (mock or demo mode).
- Run: `python scripts/demo_runner.py`
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict

import urllib.request

BASE_URL = "http://localhost:8000/api"


def _post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def _get(path: str) -> Dict[str, Any]:
    with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=10) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def run_demo():
    print("Starting AgriSight Live demo session...")
    # 1. Simulate starting a session
    start = _post("/start-session", {})
    session_id = start["session_id"]
    print(f"Session created: {session_id}")

    # 2. Simulate a diagnosis + prediction pipeline by calling session endpoint later.
    print("Waiting briefly for diagnosis and predictions to accumulate...")
    time.sleep(2.0)

    # 3. Fetch combined session data if available
    session = _get(f"/session/{session_id}")
    print("Session snapshot:", json.dumps(session, indent=2)[:800], "...\n")

    # 4. Fetch outbreak heatmap & satellite health for context
    heatmap = _get("/outbreak-heatmap")
    print("Outbreak heatmap cells:", len(heatmap.get("grid", [])))

    sat = _get("/satellite-health?lat=23.233&lon=81.12")
    print("Satellite vegetation health:", sat)

    print("Demo sequence complete.")


if __name__ == "__main__":
    run_demo()

