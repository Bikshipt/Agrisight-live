"""
Tests for the Disease Progression Engine.
Expected env vars: None
Testing tips: Run with pytest.
"""
from app.services.disease_progression_engine import (
    DiseaseProgressionInput,
    simulate_disease_progression,
)


def test_progression_monotonic_growth():
    payload = DiseaseProgressionInput(
        disease_name="Early Blight",
        crop_type="tomato",
        severity_score=0.2,
        humidity=0.85,
        temperature=24.0,
        rainfall=0.0,
        days_since_detection=0,
    )
    result = simulate_disease_progression(payload)
    probs = [p["infection_probability"] for p in result["spread_forecast"]]
    assert probs[0] <= probs[1] <= probs[2]

