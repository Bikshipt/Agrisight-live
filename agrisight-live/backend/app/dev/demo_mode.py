"""
Demo Mode Utilities.

Provides deterministic simulated scans, outbreaks, and weather alerts for
hackathon demos when DEMO_MODE=true.

Expected env vars:
- DEMO_MODE: if "true", callers should rely on these helpers instead of live APIs.
Testing tips:
- Import and call these functions directly in unit tests; no external services required.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List


def simulated_scan_events() -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc)
    return [
        {
            "session_id": f"demo-{i}",
            "disease": "Early Blight" if i % 2 == 0 else "Leaf Spot",
            "confidence": 0.8,
            "timestamp": (now - timedelta(minutes=5 * i)).isoformat(),
            "geo_lat": 23.233 + 0.01 * (i % 3),
            "geo_long": 81.12 + 0.01 * (i % 4),
        }
        for i in range(6)
    ]


def simulated_outbreak_alert() -> Dict[str, Any]:
    return {
        "outbreak_alert": True,
        "disease": "Brown Planthopper",
        "cluster_center": [23.233, 81.12],
        "radius_km": 12,
        "spread_probability": 0.61,
    }


def simulated_weather_alert() -> Dict[str, Any]:
    return {
        "risk_alert": True,
        "disease": "Powdery Mildew",
        "probability": 0.7,
        "prediction_window_days": 4,
        "recommended_prevention": "Apply preventive fungicide in the next 48 hours.",
    }

