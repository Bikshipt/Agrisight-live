"""
API Routes for AgriSight Live.

This module exposes REST endpoints and a low-latency WebSocket endpoint
used by the frontend PWA to stream camera frames and audio chunks to the
backend, which in turn orchestrates Gemini Live sessions.

Expected env vars:
- MOCK_GEMINI: when true, the Gemini client returns deterministic mock
  responses for offline development and tests.

Testing tips:
- Use FastAPI's TestClient / WebSocketTestSession to simulate a frontend.
- Run with MOCK_GEMINI=true to avoid external dependencies.
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File

from app.api.schema import FeedbackRequest, SessionCreateResponse
from app.services.outbreak_heatmap_engine import generate_outbreak_heatmap
from app.services.satellite_analysis_engine import analyze_satellite_health
from app.services.session_manager import session_manager
from app.services.video_field_scan_engine import analyze_field_video

logger = logging.getLogger("agrisight.api")

router = APIRouter()


def _log_event(event_type: str, **fields: Any) -> None:
    """
    Emit a structured JSON log to stdout for observability.
    """
    payload: Dict[str, Any] = {"event": event_type, "ts": datetime.now(timezone.utc).isoformat()}
    payload.update(fields)
    logger.info(json.dumps(payload))


@router.post("/start-session", response_model=SessionCreateResponse)
async def start_session() -> Dict[str, str]:
    """
    Create a new analysis session and return its identifier.
    """
    session_id = str(uuid.uuid4())
    state = session_manager.create_session(session_id)
    _log_event("session_start", session_id=session_id, created_at=state.created_at)
    return {"session_id": session_id}


@router.websocket("/ws/live/{session_id}")
async def websocket_live(websocket: WebSocket, session_id: str) -> None:
    """
    WebSocket endpoint for low-latency multimodal streaming.

    Incoming messages from the frontend are JSON objects of the form:
    - {"type": "video_frame", "timestamp": ..., "image_base64": "..."}
    - {"type": "audio_chunk", "timestamp": ..., "audio_base64": "..."}
    - {"type": "user_interrupt"}

    Outgoing messages are high-level events:
    - {"type": "annotation", "boxes": [...]}
    - {"type": "transcript", "text": "..."}
    - {"type": "diagnosis", "disease": "...", ...}
    - {"type": "session_log_update", ...}
    """
    state = session_manager.get_session(session_id)
    if state is None:
        await websocket.close(code=4404)
        return

    await websocket.accept()
    agent = session_manager.get_or_create_agent(session_id)
    await agent.start_session()

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                _log_event("frame_received_invalid", session_id=session_id, raw=raw)
                continue

            msg_type = message.get("type")
            timestamp = message.get("timestamp")

            if msg_type == "video_frame":
                image_b64 = message.get("image_base64")
                if not image_b64:
                    continue
                session_manager.append_frame(session_id, message)
                _log_event("frame_received", session_id=session_id, timestamp=timestamp)
                events = await agent.stream_frame(image_b64, timestamp)
            elif msg_type == "audio_chunk":
                audio_b64 = message.get("audio_base64")
                if not audio_b64:
                    continue
                session_manager.append_audio_chunk(session_id, message)
                _log_event("audio_received", session_id=session_id, timestamp=timestamp)
                events = await agent.stream_audio(audio_b64, timestamp)
            elif msg_type == "user_interrupt":
                await agent.interrupt()
                _log_event("session_interrupt", session_id=session_id)
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "session_log_update",
                            "session_id": session_id,
                            "status": "interrupted",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                )
                continue
            elif msg_type == "heartbeat":
                # Keep-alive ping from client; respond with a small pong.
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "heartbeat_ack",
                            "session_id": session_id,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                )
                continue
            else:
                _log_event("unknown_message_type", session_id=session_id, msg_type=msg_type)
                continue

            for event in events:
                if not isinstance(event, dict):
                    continue
                etype = event.get("type")
                if etype == "diagnosis":
                    _log_event(
                        "diagnosis_generated",
                        session_id=session_id,
                        disease=event.get("disease"),
                        confidence=event.get("confidence"),
                    )
                    # Trigger downstream predictive reasoning pipeline.
                    combined = session_manager.run_reasoning_pipeline(session_id, event)
                    await websocket.send_text(json.dumps({"type": "combined_result", **combined}))
                elif etype == "annotation":
                    _log_event("gemini_response", session_id=session_id, kind="annotation")
                elif etype == "transcript":
                    _log_event("gemini_response", session_id=session_id, kind="transcript")
                await websocket.send_text(json.dumps(event))
    except WebSocketDisconnect:
        _log_event("session_disconnected", session_id=session_id)
    except Exception as exc:  # noqa: BLE001
        _log_event("session_error", session_id=session_id, error=str(exc))
        await websocket.close(code=1011)


@router.post("/feedback/{session_id}")
async def submit_feedback(session_id: str, feedback: FeedbackRequest) -> Dict[str, str]:
    """
    Store user confirmation / correction for a session in memory.
    """
    state = session_manager.get_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")
    state.logs.append({"type": "feedback", "payload": feedback.dict()})
    _log_event("feedback_received", session_id=session_id)
    return {"status": "success"}


@router.get("/session/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    """
    Get the in-memory session log and latest structured result snapshot.
    """
    state = session_manager.get_session(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": state.session_id,
        "status": state.status,
        "created_at": state.created_at,
        "last_updated_at": state.last_updated_at,
        "frames": state.frames,
        "audio_chunks": state.audio_chunks,
        "logs": state.logs,
    }


@router.post("/field-scan")
async def field_scan(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze a short field walkthrough video and return a health summary.
    """
    content = await file.read()
    summary = analyze_field_video(content)
    _log_event("field_scan_completed", plants_analyzed=summary.get("plants_analyzed", 0))
    return summary


@router.post("/offline-sync")
async def offline_sync(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accept offline-captured scans from rural devices and enqueue them for full analysis.
    """
    scans = payload.get("scans", [])
    _log_event("offline_sync_received", count=len(scans))
    # In a full implementation we would persist and trigger analysis here.
    return {"status": "accepted", "count": len(scans)}


@router.get("/satellite-health")
async def satellite_health(lat: float, lon: float) -> Dict[str, Any]:
    """
    Summarize vegetation health using satellite NDVI time series.
    """
    result = await analyze_satellite_health(lat, lon)
    _log_event("satellite_health_checked", lat=lat, lon=lon, stress_alert=result.get("stress_alert"))
    return result


@router.get("/outbreak-heatmap")
async def outbreak_heatmap() -> Dict[str, Any]:
    """
    Return a regional disease heatmap grid for map visualization.
    """
    grid = generate_outbreak_heatmap()
    _log_event("outbreak_heatmap_generated", cells=len(grid.get("grid", [])))
    return grid


@router.post("/voice-query")
async def voice_query(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Basic text-based voice assistant endpoint. In mock mode this simply
    echoes a templated response.
    """
    question = str(payload.get("text") or "")
    language = str(payload.get("language") or "en")

    if not question:
        raise HTTPException(status_code=400, detail="Missing text")

    # For now, return a deterministic answer; this can be wired to Gemini Live.
    if "rice" in question.lower() and "brown" in question.lower():
        answer = "Possible early stage rice blast detected. Spray a recommended fungicide within 48 hours."
    else:
        answer = "Based on your description, monitor the leaves closely and consider sending a clear photo for precise diagnosis."

    _log_event("voice_query_handled", language=language)
    return {"answer": answer}

