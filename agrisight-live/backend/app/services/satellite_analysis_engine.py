"""
Satellite Vegetation Intelligence Engine.

Uses NDVI time series to detect crop stress at field scale.

Expected env vars:
- MOCK_SATELLITE: if "true", uses deterministic NDVI history.
Testing tips:
- Call analyze_satellite_health with a known NDVI history and assert that
  stress_alert toggles when NDVI drops by > 0.1 within 5 days.
"""
from __future__ import annotations

from typing import Any, Dict, List

from app.services.satellite_client import fetch_ndvi, fetch_ndvi_history


async def analyze_satellite_health(lat: float, lon: float) -> Dict[str, Any]:
    """
    Compute a vegetation health summary using NDVI history.
    """
    history: List[Dict[str, Any]] = await fetch_ndvi_history(lat, lon, days=7)
    if not history:
        ndvi_current = await fetch_ndvi(lat, lon)
        return {
            "vegetation_health": "unknown",
            "ndvi_current": ndvi_current,
            "ndvi_previous": None,
            "stress_alert": False,
        }

    ndvi_current = float(history[-1]["ndvi"])
    ndvi_previous = float(history[0]["ndvi"])

    drop = ndvi_previous - ndvi_current
    stress_alert = drop > 0.1

    if stress_alert:
        health = "declining"
    elif ndvi_current > 0.6:
        health = "healthy"
    else:
        health = "stable"

    return {
        "vegetation_health": health,
        "ndvi_current": round(ndvi_current, 2),
        "ndvi_previous": round(ndvi_previous, 2),
        "stress_alert": stress_alert,
    }

