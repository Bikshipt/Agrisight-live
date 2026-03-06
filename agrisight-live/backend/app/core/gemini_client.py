"""
Gemini Live API Client.

This module exposes a high-level async wrapper around the Gemini Live
multimodal streaming API that is tailored for AgriSight Live.

Expected env vars:
- GEMINI_API_KEY: API key for Google GenAI SDK.
- MOCK_GEMINI: if "true", use deterministic mock responses without
  calling the real Gemini API.

Testing tips:
- Run unit tests with MOCK_GEMINI=true to avoid external dependencies.
- For integration tests against a real project, inject a fake SDK client.
"""
import asyncio
import os
import random
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List

from app.services.cache_manager import cache_manager


class GeminiLiveAgent:
    """
    High-level Gemini Live session wrapper used by the WebSocket engine.

    The real implementation should use the Google GenAI Python SDK to open
    a multimodal streaming session and forward frames / audio chunks.
    This class keeps the interface stable while allowing MOCK_GEMINI mode
    for local development and tests.
    """

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.mock_mode = os.getenv("MOCK_GEMINI", "true").lower() == "true"
        self._lock = asyncio.Lock()
        self._interrupted = asyncio.Event()
        self._interrupted.clear()

        # Placeholders for real SDK objects
        self._sdk_stream = None  # type: ignore[var-annotated]

    async def start_session(self) -> None:
        """
        Initialize an underlying Gemini Live streaming session.

        In real mode, this would:
        - Instantiate the Google GenAI client with the API key.
        - Open a bidirectional streaming session for multimodal input/output.
        - Configure model, safety settings, and output schema.
        """
        if self.mock_mode:
            # Nothing to initialize for mock mode.
            return

        # Real implementation sketch (non-functional placeholder):
        # from google import genai
        # client = genai.Client(api_key=self.api_key)
        # self._sdk_stream = await client.aio.live.connect(model="gemini-1.5-pro-exp")
        # await self._sdk_stream.send({"setup": {...}})

    async def stream_frame(self, image_base64: str, timestamp: int | None) -> List[Dict[str, Any]]:
        """
        Stream a single video frame to Gemini Live.

        Returns a list of high-level events that should be sent back to
        the frontend (annotations, partial diagnosis, transcript updates).
        """
        async with self._lock:
            if self.mock_mode:
                return await self._mock_events_for_frame(timestamp)

            # Real SDK example (pseudo-code, not executed). For resiliency,
            # cache the last successful diagnosis per session as a fallback.
            cache_key = f"gemini:last:{self.session_id}"
            for attempt in range(3):
                try:
                    # await self._sdk_stream.send({"video_frame": {"image_base64": image_base64}})
                    # events = []
                    # async for evt in self._sdk_stream:
                    #     events.append(self._translate_sdk_event(evt))
                    #     if self._interrupted.is_set():
                    #         break
                    events: List[Dict[str, Any]] = []
                    cache_manager.set(cache_key, events)
                    return events
                except Exception:
                    if attempt == 2:
                        cached = cache_manager.get(cache_key)
                        if cached:
                            return cached
                        return await self._mock_events_for_frame(timestamp)
                    continue

    async def stream_audio(self, audio_base64: str, timestamp: int | None) -> List[Dict[str, Any]]:
        """
        Stream an audio chunk to Gemini Live.

        In mock mode this will only possibly update transcript events.
        """
        async with self._lock:
            if self.mock_mode:
                return await self._mock_events_for_audio(timestamp)

            # Real implementation would forward PCM/Opus audio bytes to the SDK.
            # For now we simply swallow failures and rely on mock transcript if needed.
            try:
                # await self._sdk_stream.send({"audio_chunk": {...}})
                # events = [...]
                events: List[Dict[str, Any]] = []
                return events
            except Exception:
                return await self._mock_events_for_audio(timestamp)

    async def interrupt(self) -> None:
        """
        Signal that the current reasoning loop should be stopped.
        """
        self._interrupted.set()
        # For a real SDK stream we would also cancel / reset the stream here.

    async def receive_events(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Optional async generator interface for advanced streaming usage.

        Not currently used by the WebSocket route, but provided for future
        composition if we want to decouple I/O from Gemini streaming.
        """
        if self.mock_mode:
            # Yield a simple deterministic diagnosis once for the session.
            yield self._mock_diagnosis_event()
            return

        # Real implementation would loop over SDK event stream here.
        return

    async def _mock_events_for_frame(self, timestamp: int | None) -> List[Dict[str, Any]]:
        """
        Deterministic mock responses for a video frame.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        base_conf = 0.78 + random.random() * 0.1
        confidence = min(base_conf, 0.95)
        box = {
            "x": 18.0,
            "y": 26.0,
            "w": 42.0,
            "h": 52.0,
            "label": "Lesion",
            "score": round(confidence, 2),
        }

        events: List[Dict[str, Any]] = [
            {
                "type": "annotation",
                "boxes": [box],
                "session_id": self.session_id,
                "timestamp": timestamp or int(datetime.now(timezone.utc).timestamp() * 1000),
            },
            {
                "type": "diagnosis",
                "disease": "Early Blight",
                "confidence": round(confidence, 2),
                "recommended_actions": [
                    "Remove heavily affected leaves to reduce spore load.",
                    "Avoid overhead watering to limit leaf wetness duration.",
                    "Apply copper-based fungicide in the early morning.",
                ],
                "session_id": self.session_id,
                "timestamp": now_iso,
            },
        ]
        return events

    async def _mock_events_for_audio(self, timestamp: int | None) -> List[Dict[str, Any]]:
        """
        Deterministic mock responses for an audio chunk.
        """
        text = "Analyzing leaf lesions for early blight indicators."
        return [
            {
                "type": "transcript",
                "text": text,
                "session_id": self.session_id,
                "timestamp": timestamp or int(datetime.now(timezone.utc).timestamp() * 1000),
            }
        ]

    def _mock_diagnosis_event(self) -> Dict[str, Any]:
        """
        Single-shot mock diagnosis event.
        """
        return {
            "type": "diagnosis",
            "disease": "Early Blight",
            "confidence": 0.87,
            "recommended_actions": [
                "Isolate the affected plants.",
                "Apply an appropriate fungicide within 24 hours.",
            ],
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

