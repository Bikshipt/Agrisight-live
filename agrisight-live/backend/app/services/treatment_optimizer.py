"""
Treatment Optimization Engine.

Recommends an intervention plan (product and dosage) for a detected
disease and crop type based on a lightweight knowledge base.

Expected env vars: None (all configuration via JSON parameters file).
Testing tips:
- Verify that total_required_ml scales linearly with field area.
- Verify that application_window_hours shrinks slightly as severity grows.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

PARAMS_PATH = Path(__file__).resolve().parent.parent / "data" / "treatment_knowledge_base.json"


@dataclass
class TreatmentOptimizerInput:
  disease: str
  crop_type: str
  field_area: float  # in acres
  severity: float  # 0-1


_TREATMENT_CACHE: Dict[str, Dict[str, Dict[str, float]]] | None = None


def _load_params() -> Dict[str, Dict[str, Dict[str, float]]]:
  with PARAMS_PATH.open("r", encoding="utf-8") as f:
    return json.load(f)


def _get_treatment(crop_type: str, disease: str) -> Dict[str, float | str]:
  global _TREATMENT_CACHE
  if _TREATMENT_CACHE is None:
    _TREATMENT_CACHE = _load_params()

  crop_key = crop_type.lower()
  disease_key = disease.replace(" ", "_").lower()

  crop_block = _TREATMENT_CACHE.get(crop_key) or _TREATMENT_CACHE.get("generic", {})
  return crop_block.get(disease_key) or crop_block.get("default") or {
    "recommended_treatment": "Broad-spectrum fungicide",
    "dosage_ml_per_acre": 100,
    "application_window_hours": 48,
  }


def optimize_treatment(payload: TreatmentOptimizerInput) -> Dict[str, float | str]:
  """
  Recommend an optimized treatment plan.
  """
  cfg = _get_treatment(payload.crop_type, payload.disease)
  dosage_per_acre = float(cfg["dosage_ml_per_acre"])
  base_window = float(cfg["application_window_hours"])
  severity = max(0.0, min(1.0, payload.severity))

  total_required_ml = dosage_per_acre * payload.field_area
  # Higher severity shortens the ideal application window slightly.
  application_window_hours = max(12.0, base_window * (1.0 - 0.3 * severity))

  return {
    "recommended_treatment": str(cfg["recommended_treatment"]),
    "dosage_ml_per_acre": round(dosage_per_acre, 1),
    "total_required_ml": round(total_required_ml, 1),
    "application_window_hours": round(application_window_hours, 1),
  }

