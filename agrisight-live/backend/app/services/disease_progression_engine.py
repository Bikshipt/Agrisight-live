"""
Disease Progression Engine.

Uses a simple exponential growth model to forecast how a detected disease
is likely to spread over the coming days based on environmental factors.

Expected env vars: None (all configuration via JSON parameters file).
Testing tips:
- Use deterministic inputs and assert that infection probabilities grow
  monotonically with time and with increasing humidity/temperature closeness
  to the optimal values defined in the parameters file.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

PARAMS_PATH = Path(__file__).resolve().parent.parent / "data" / "disease_growth_parameters.json"


@dataclass
class DiseaseProgressionInput:
  disease_name: str
  crop_type: str
  severity_score: float
  humidity: float
  temperature: float
  rainfall: float
  days_since_detection: int


def _load_params() -> Dict[str, Dict[str, float]]:
  with PARAMS_PATH.open("r", encoding="utf-8") as f:
    raw = json.load(f)
  return raw


_PARAMS_CACHE: Dict[str, Dict[str, Dict[str, float]]] | None = None


def _get_params(crop_type: str, disease_name: str) -> Dict[str, float]:
  global _PARAMS_CACHE
  if _PARAMS_CACHE is None:
    _PARAMS_CACHE = _load_params()

  crop_key = crop_type.lower()
  disease_key = disease_name.replace(" ", "_").lower()

  crop_block = _PARAMS_CACHE.get(crop_key) or _PARAMS_CACHE.get("generic", {})
  return crop_block.get(disease_key) or crop_block.get("default") or {
    "base_growth_rate": 0.08,
    "optimal_temperature_c": 26,
    "optimal_humidity": 0.8,
  }


def _growth_rate(params: Dict[str, float], humidity: float, temperature_c: float) -> float:
  base = params["base_growth_rate"]
  # Humidity factor: closer to optimal -> closer to 1.3x, far -> 0.7x.
  h_opt = params["optimal_humidity"]
  h_delta = min(1.0, abs(humidity - h_opt))
  humidity_factor = 1.3 - 0.6 * h_delta

  # Temperature factor: within +/-5C of optimal is ideal.
  t_opt = params["optimal_temperature_c"]
  t_delta = min(10.0, abs(temperature_c - t_opt))
  temperature_factor = 1.25 - 0.05 * t_delta

  rainfall_factor = 1.0  # reserved for future use

  return max(0.01, base * humidity_factor * temperature_factor * rainfall_factor)


def simulate_disease_progression(
  payload: DiseaseProgressionInput,
) -> Dict[str, object]:
  """
  Compute a small forecast horizon for infection probability using:
  I(t) = I0 * e^(r * t)
  where r depends on environment and disease parameters.
  """
  params = _get_params(payload.crop_type, payload.disease_name)
  r = _growth_rate(params, payload.humidity, payload.temperature)

  # Ensure initial severity is in [0, 1].
  i0 = max(0.0, min(1.0, payload.severity_score))

  forecast_days: List[int] = [3, 7, 10]
  spread_forecast: List[Dict[str, float]] = []
  for day in forecast_days:
    t = max(0, day - payload.days_since_detection)
    p = i0 * math.exp(r * t)
    spread_forecast.append({"day": day, "infection_probability": float(min(1.0, p))})

  # Rough yield loss band derived from final day probability.
  terminal_p = spread_forecast[-1]["infection_probability"]
  yield_min = max(0.0, min(0.9, terminal_p * 0.6))
  yield_max = max(yield_min, min(0.95, terminal_p * 0.8))

  return {
    "spread_forecast": spread_forecast,
    "yield_loss_estimate": {"min": round(yield_min, 2), "max": round(yield_max, 2)},
    "intervention_window_hours": 48,
  }

