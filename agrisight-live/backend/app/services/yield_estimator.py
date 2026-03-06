"""
Yield Impact Estimator.

Converts disease detection probabilities into simple economic impact
estimates for the farmer, using configurable yield loss curves.

Expected env vars: None (all configuration via JSON parameters file).
Testing tips:
- Feed known probabilities and ensure yield_loss_percent increases
  monotonically, and that net_savings_if_treated is never negative.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

PARAMS_PATH = Path(__file__).resolve().parent.parent / "data" / "yield_models.json"


@dataclass
class YieldEstimatorInput:
  disease: str
  infection_probability: float
  crop_type: str
  field_area: float  # in acres
  market_price_per_ton: float  # in local currency


_YIELD_PARAMS_CACHE: Dict[str, Dict[str, Dict[str, float]]] | None = None


def _load_params() -> Dict[str, Dict[str, Dict[str, float]]]:
  with PARAMS_PATH.open("r", encoding="utf-8") as f:
    return json.load(f)


def _get_params(crop_type: str, disease: str) -> Dict[str, float]:
  global _YIELD_PARAMS_CACHE
  if _YIELD_PARAMS_CACHE is None:
    _YIELD_PARAMS_CACHE = _load_params()

  crop_key = crop_type.lower()
  disease_key = disease.replace(" ", "_").lower()

  crop_block = _YIELD_PARAMS_CACHE.get(crop_key) or _YIELD_PARAMS_CACHE.get("generic", {})
  return crop_block.get(disease_key) or crop_block.get("default") or {
    "max_loss_percent": 0.3,
    "alpha": 0.6,
    "baseline_yield_ton_per_acre": 1.0,
    "avg_treatment_cost_per_acre": 800.0,
  }


def estimate_yield_impact(payload: YieldEstimatorInput) -> Dict[str, float]:
  """
  Estimate yield and financial impact.
  """
  params = _get_params(payload.crop_type, payload.disease)
  p = max(0.0, min(1.0, payload.infection_probability))
  max_loss = float(params["max_loss_percent"])
  alpha = float(params["alpha"])

  yield_loss_percent = min(max_loss, alpha * p)

  baseline_yield = float(params["baseline_yield_ton_per_acre"])
  expected_yield_loss_tons = yield_loss_percent * baseline_yield * payload.field_area
  expected_loss_rupees = expected_yield_loss_tons * payload.market_price_per_ton

  treatment_cost_per_acre = float(params["avg_treatment_cost_per_acre"])
  treatment_cost = treatment_cost_per_acre * payload.field_area
  net_savings_if_treated = max(0.0, expected_loss_rupees - treatment_cost)

  return {
    "yield_loss_percent": round(yield_loss_percent, 2),
    "expected_loss_rupees": round(expected_loss_rupees, 0),
    "treatment_cost": round(treatment_cost, 0),
    "net_savings_if_treated": round(net_savings_if_treated, 0),
  }

