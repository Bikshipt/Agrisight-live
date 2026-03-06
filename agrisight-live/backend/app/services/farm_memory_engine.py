"""
Farm Memory Intelligence Engine.

Builds and maintains long-term knowledge about each farm by aggregating
scan, disease, and treatment histories into a Firestore-backed profile.

Expected env vars:
- GOOGLE_CLOUD_PROJECT / GOOGLE_APPLICATION_CREDENTIALS for Firestore (optional).
Testing tips:
- Call analyze_farm_memory with in-memory histories to verify pattern
  detection is deterministic without requiring Firestore.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from google.cloud import firestore  # type: ignore[import]
except Exception:  # noqa: BLE001
    firestore = None  # type: ignore[assignment]


@dataclass
class FarmMemoryInput:
    farm_id: str
    scan_history: List[Dict[str, Any]]
    disease_history: List[Dict[str, Any]]
    treatment_history: List[Dict[str, Any]]


def _season_for_timestamp(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts)
    except Exception:
        return "unknown"
    month = dt.month
    if month in (6, 7, 8, 9):
        return "monsoon"
    if month in (10, 11, 12, 1):
        return "winter"
    return "summer"


def _firestore_client():
    if firestore is None:
        return None
    return firestore.Client()


def analyze_farm_memory(payload: FarmMemoryInput) -> Dict[str, Any]:
    """
    Analyze historical patterns for a farm and optionally persist profile.
    """
    # Aggregate crop types and recurring diseases by season.
    crop_types = sorted({s.get("crop_type") for s in payload.scan_history if s.get("crop_type")})

    seasonal_diseases: Dict[str, Counter[str]] = {"monsoon": Counter(), "winter": Counter(), "summer": Counter()}
    for event in payload.disease_history:
        disease = str(event.get("disease") or "")
        ts = str(event.get("timestamp") or "")
        season = _season_for_timestamp(ts)
        seasonal_diseases.setdefault(season, Counter())
        if disease:
            seasonal_diseases[season][disease] += 1

    recurring_patterns: List[str] = []
    for season, counter in seasonal_diseases.items():
        for disease, count in counter.items():
            if count >= 3:
                recurring_patterns.append(f"{disease} recurring during {season}")

    pattern_detected = bool(recurring_patterns)
    pattern = recurring_patterns[0] if recurring_patterns else None
    recommendation: Optional[str] = None
    if pattern and "nitrogen" in pattern.lower():
        recommendation = "Apply nitrogen fertilizer 10 days earlier next season."
    elif pattern and "powdery mildew" in pattern.lower():
        recommendation = "Schedule preventive fungicide sprays before the usual onset window."
    elif pattern:
        recommendation = "Plan a targeted preventive treatment before the usual onset window."

    profile = {
        "farm_id": payload.farm_id,
        "crop_types": crop_types,
        "recurring_diseases": recurring_patterns,
        "seasonal_patterns": seasonal_diseases,
        "treatment_effectiveness": {},  # Placeholder for future detailed modeling.
    }

    client = _firestore_client()
    if client is not None:
        client.collection("farm_profiles").document(payload.farm_id).set(profile, merge=True)

    return {
        "pattern_detected": pattern_detected,
        "pattern": pattern,
        "recommendation": recommendation,
        "profile": profile,
    }

