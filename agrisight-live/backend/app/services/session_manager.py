"""
Session Manager Service.
Handles state for active analysis sessions, their streaming buffers, and
chained reasoning pipelines that enrich raw diagnoses with predictions.

Expected env vars:
- GOOGLE_CLOUD_PROJECT / GOOGLE_APPLICATION_CREDENTIALS (optional) for Firestore.
Testing tips:
- Unit test session lifecycle methods and the reasoning pipeline with
  MOCK_GEMINI=true and Firestore disabled.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from google.cloud import firestore  # type: ignore[import]
except Exception:  # noqa: BLE001
    firestore = None  # type: ignore[assignment]

from app.core.gemini_client import GeminiLiveAgent
from app.services.disease_progression_engine import (
    DiseaseProgressionInput,
    simulate_disease_progression,
)
from app.services.farm_memory_engine import FarmMemoryInput, analyze_farm_memory
from app.services.microclimate_risk_engine import (
    MicroclimateInput,
    predict_microclimate_risk,
)
from app.services.outbreak_intelligence_engine import analyze_outbreak_probability
from app.services.treatment_optimizer import TreatmentOptimizerInput, optimize_treatment
from app.services.weather_client import get_forecast_weather
from app.services.yield_estimator import YieldEstimatorInput, estimate_yield_impact


class SessionState:
    """
    In-memory representation of an active session.

    This keeps lightweight metadata only – durable storage to Firestore / GCS
    should be implemented in a separate persistence layer.
    """

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.status: str = "active"
        self.created_at: str = datetime.now(timezone.utc).isoformat()
        self.last_updated_at: str = self.created_at
        self.frames: List[Dict[str, Any]] = []
        self.audio_chunks: List[Dict[str, Any]] = []
        self.logs: List[Dict[str, Any]] = []
        self.agent: Optional[GeminiLiveAgent] = None
        self.combined_result: Optional[Dict[str, Any]] = None

    def touch(self) -> None:
        self.last_updated_at = datetime.now(timezone.utc).isoformat()


class SessionManager:
    """
    Manages active analysis sessions and their associated GeminiLiveAgent.
    """

    def __init__(self) -> None:
        self.active_sessions: Dict[str, SessionState] = {}

    def create_session(self, session_id: str) -> SessionState:
        state = SessionState(session_id=session_id)
        self.active_sessions[session_id] = state
        return state

    def get_session(self, session_id: str) -> Optional[SessionState]:
        return self.active_sessions.get(session_id)

    def ensure_session(self, session_id: str) -> SessionState:
        existing = self.get_session(session_id)
        if existing:
            return existing
        return self.create_session(session_id)

    def end_session(self, session_id: str) -> None:
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

    def get_or_create_agent(self, session_id: str) -> GeminiLiveAgent:
        state = self.ensure_session(session_id)
        if state.agent is None:
            state.agent = GeminiLiveAgent(session_id=session_id)
        return state.agent

    def append_frame(self, session_id: str, frame: Dict[str, Any]) -> None:
        state = self.ensure_session(session_id)
        state.frames.append(frame)
        state.touch()

    def append_audio_chunk(self, session_id: str, chunk: Dict[str, Any]) -> None:
        state = self.ensure_session(session_id)
        state.audio_chunks.append(chunk)
        state.touch()

    def append_log(self, session_id: str, event: Dict[str, Any]) -> None:
        state = self.ensure_session(session_id)
        state.logs.append(event)
        state.touch()

    def _firestore_client(self):
        if firestore is None:
            return None
        return firestore.Client()

    def _persist_crop_scan(self, session_id: str, combined: Dict[str, Any]) -> None:
        client = self._firestore_client()
        if client is None:
            return
        diagnosis = combined.get("diagnosis") or {}
        spread = combined.get("spread_forecast") or {}
        yield_impact = combined.get("yield_impact") or {}
        treatment_plan = combined.get("treatment_plan") or {}

        doc = {
            "scan_id": session_id,
            "timestamp": diagnosis.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            "geo_lat": diagnosis.get("geo_lat"),
            "geo_long": diagnosis.get("geo_long"),
            "disease": diagnosis.get("disease"),
            "confidence": diagnosis.get("confidence"),
            "crop_type": diagnosis.get("crop_type"),
            "spread_forecast": spread,
            "yield_impact": yield_impact,
            "treatment_plan": treatment_plan,
        }
        client.collection("crop_scans").document(session_id).set(doc)

    def run_reasoning_pipeline(self, session_id: str, diagnosis_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a diagnosis event with predictive and economic reasoning.

        Pipeline:
        vision diagnosis
          -> disease progression
          -> microclimate risk forecast
          -> yield impact estimation
          -> treatment optimization
          -> outbreak intelligence
          -> farm memory learning
        """
        state = self.ensure_session(session_id)

        # Extract core diagnosis fields with fallbacks.
        disease = str(diagnosis_event.get("disease") or diagnosis_event.get("disease_name") or "")
        confidence = float(diagnosis_event.get("confidence") or 0.0)
        crop_type = str(diagnosis_event.get("crop_type") or "generic")

        # In a real system these would come from device sensors or user input.
        humidity = float(diagnosis_event.get("humidity") or 0.8)
        temperature = float(diagnosis_event.get("temperature_c") or 26.0)
        rainfall = float(diagnosis_event.get("rainfall_mm") or 0.0)
        days_since_detection = int(diagnosis_event.get("days_since_detection") or 0)
        field_area = float(diagnosis_event.get("field_area_acres") or 1.0)
        market_price_per_ton = float(diagnosis_event.get("market_price_per_ton") or 6800.0)
        severity_score = max(0.1, confidence)
        lat = float(diagnosis_event.get("geo_lat") or 0.0)
        lon = float(diagnosis_event.get("geo_long") or 0.0)
        farm_id = str(diagnosis_event.get("farm_id") or "demo-farm")

        # Disease progression.
        progression = simulate_disease_progression(
            DiseaseProgressionInput(
                disease_name=disease,
                crop_type=crop_type,
                severity_score=severity_score,
                humidity=humidity,
                temperature=temperature,
                rainfall=rainfall,
                days_since_detection=days_since_detection,
            )
        )

        # Microclimate risk forecast (uses short-term forecast weather).
        recent_diseases = [
            log.get("payload", {}).get("diagnosis", {}).get("disease")
            for log in state.logs
            if log.get("type") == "combined_result"
        ]
        forecast_weather = []
        if lat and lon:
            # Fire-and-forget style; errors will simply yield no risk.
            try:
                import anyio  # type: ignore[import]

                async def _fetch():
                    from app.services.weather_client import get_forecast_weather as gf

                    return await gf(lat, lon, 4)

                forecast_weather = anyio.run(_fetch)
            except Exception:
                forecast_weather = []

        from app.services.microclimate_risk_engine import MicroclimateInput as McInput, predict_microclimate_risk

        microclimate_risk = anyio.run(
            lambda: predict_microclimate_risk(
                McInput(
                    crop_type=crop_type,
                    lat=lat,
                    lon=lon,
                    temperature=temperature,
                    humidity=humidity,
                    rainfall=rainfall,
                    wind_speed=float(diagnosis_event.get("wind_speed_ms") or 1.0),
                    recent_disease_history=[d for d in recent_diseases if d],
                ),
                forecast_weather,
            )
        ) if forecast_weather else {
            "risk_alert": False,
            "disease": None,
            "probability": 0.0,
            "prediction_window_days": 0,
            "recommended_prevention": None,
        }

        yield_impact = estimate_yield_impact(
            YieldEstimatorInput(
                disease=disease,
                infection_probability=confidence,
                crop_type=crop_type,
                field_area=field_area,
                market_price_per_ton=market_price_per_ton,
            )
        )

        treatment_plan = optimize_treatment(
            TreatmentOptimizerInput(
                disease=disease,
                crop_type=crop_type,
                field_area=field_area,
                severity=severity_score,
            )
        )

        outbreak_alert = analyze_outbreak_probability()

        # Farm memory learning (pure analysis + optional Firestore profile update).
        farm_profile = analyze_farm_memory(
            FarmMemoryInput(
                farm_id=farm_id,
                scan_history=[],
                disease_history=[diagnosis_event],
                treatment_history=[],
            )
        )

        combined = {
            "diagnosis": diagnosis_event,
            "spread_forecast": progression,
            "microclimate_risk": microclimate_risk,
            "yield_impact": yield_impact,
            "treatment_plan": treatment_plan,
            "outbreak_alert": outbreak_alert,
            "farm_memory": farm_profile,
        }

        state.combined_result = combined
        self.append_log(session_id, {"type": "combined_result", "payload": combined})
        self._persist_crop_scan(session_id, combined)
        return combined


session_manager = SessionManager()


