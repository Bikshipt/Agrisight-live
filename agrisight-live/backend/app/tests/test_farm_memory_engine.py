"""
Tests for Farm Memory Intelligence Engine.
Expected env vars: None
"""
from app.services.farm_memory_engine import FarmMemoryInput, analyze_farm_memory


def test_farm_memory_detects_pattern_structure():
    disease_history = [
        {"disease": "Nitrogen deficiency", "timestamp": "2026-07-01T00:00:00"},
        {"disease": "Nitrogen deficiency", "timestamp": "2026-07-10T00:00:00"},
        {"disease": "Nitrogen deficiency", "timestamp": "2026-07-20T00:00:00"},
    ]
    payload = FarmMemoryInput(
        farm_id="farm-123",
        scan_history=[],
        disease_history=disease_history,
        treatment_history=[],
    )
    result = analyze_farm_memory(payload)
    assert "pattern_detected" in result
    assert "pattern" in result
    assert "recommendation" in result

