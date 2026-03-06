"""
Tests for Microclimate Risk Engine.
Expected env vars: MOCK_WEATHER=true for deterministic behavior.
"""
from app.services.microclimate_risk_engine import (
    MicroclimateInput,
    predict_microclimate_risk,
)
import anyio


def test_microclimate_risk_basic():
    forecast = [
        {"date": "2026-03-05", "temperature_c": 22.0, "humidity": 0.85, "rainfall_mm": 2.0}
    ]
    payload = MicroclimateInput(
        crop_type="tomato",
        lat=23.0,
        lon=81.0,
        temperature=22.0,
        humidity=0.85,
        rainfall=2.0,
        wind_speed=1.0,
        recent_disease_history=[],
    )

    result = anyio.run(lambda: predict_microclimate_risk(payload, forecast))
    assert "probability" in result
    assert 0.0 <= result["probability"] <= 1.0

