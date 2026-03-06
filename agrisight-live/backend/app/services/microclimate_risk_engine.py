"""
Microclimate Disease Risk Engine.

Uses short-term weather forecasts and disease-specific environmental rules
to proactively estimate the risk of disease outbreaks before symptoms
appear on leaves.

Expected env vars:
- MOCK_WEATHER: if "true", uses mocked weather data from weather_client.
Testing tips:
- Feed deterministic forecast data and assert that risk scores respond to
  humidity and temperature changes as expected.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


PARAMS_PATH = Path(__file__).resolve().parent.parent / "data" / "disease_environment_rules.json"


@dataclass
class MicroclimateInput:
    crop_type: str
    lat: float
    lon: float
    temperature: float
    humidity: float
    rainfall: float
    wind_speed: float
    recent_disease_history: List[str]


def _load_rules() -> Dict[str, Dict[str, Any]]:
    with PARAMS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


_RULES_CACHE: Dict[str, Dict[str, Any]] | None = None


def _get_rules() -> Dict[str, Dict[str, Any]]:
    global _RULES_CACHE
    if _RULES_CACHE is None:
        _RULES_CACHE = _load_rules()
    return _RULES_CACHE


def _score_env_for_disease(rule: Dict[str, Any], forecast: List[Dict[str, Any]]) -> float:
    """
    Compute an aggregate risk score in [0, 1] for a given disease rule and
    a multi-day forecast.
    """
    if not forecast:
        return 0.0

    wh, wt, wr = 0.4, 0.4, 0.2
    scores: List[float] = []
    for day in forecast:
        temp = float(day.get("temperature_c", 24.0))
        hum = float(day.get("humidity", 0.8)) * 100.0  # to %
        rain = float(day.get("rainfall_mm", 0.0))

        # Humidity score: 0 if below minimum, 1 if comfortably above.
        h_min = float(rule.get("humidity_min", 0.0))
        if hum < h_min:
            h_score = 0.0
        else:
            h_score = min(1.0, (hum - h_min) / 20.0)

        # Temperature score: triangular within specified range.
        t_low, t_high = rule.get("temperature_range", [10.0, 35.0])
        if temp <= t_low or temp >= t_high:
            t_score = 0.0
        else:
            mid = (t_low + t_high) / 2.0
            t_score = 1.0 - abs(temp - mid) / ((t_high - t_low) / 2.0)

        # Rainfall score: between min and max, favouring diseases that like wet / dry.
        r_min = float(rule.get("rainfall_min", 0.0))
        r_max = float(rule.get("rainfall_max", 100.0))
        if rain < r_min or rain > r_max:
            r_score = 0.0
        else:
            # Closer to mid of [r_min, r_max] -> higher.
            mid_r = (r_min + r_max) / 2.0
            if r_max == r_min:
                r_score = 1.0
            else:
                r_score = 1.0 - abs(rain - mid_r) / ((r_max - r_min) / 2.0)

        risk = max(0.0, min(1.0, wh * h_score + wt * t_score + wr * r_score))
        scores.append(risk)

    # Aggregate across forecast horizon using max as a simple heuristic.
    return max(scores) if scores else 0.0


async def predict_microclimate_risk(
    payload: MicroclimateInput,
    forecast: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Produce a high-level microclimate risk summary based on forecast.
    """
    rules = _get_rules()
    best_disease = None
    best_score = 0.0

    for disease_name, rule in rules.items():
        score = _score_env_for_disease(rule, forecast)
        if score > best_score:
            best_score = score
            best_disease = disease_name

    if best_disease is None:
        return {
            "risk_alert": False,
            "disease": None,
            "probability": 0.0,
            "prediction_window_days": len(forecast),
            "recommended_prevention": None,
        }

    # Nudge risk slightly if the disease appears in recent history.
    if best_disease.replace("_", " ") in (d.lower() for d in payload.recent_disease_history):
        best_score = min(1.0, best_score + 0.1)

    return {
        "risk_alert": best_score >= 0.4,
        "disease": best_disease.replace("_", " ").title(),
        "probability": round(best_score, 2),
        "prediction_window_days": len(forecast),
        "recommended_prevention": "Apply preventive fungicide and monitor leaf surfaces daily.",
    }

