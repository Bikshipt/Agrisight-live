"""
Tests for Satellite Vegetation Intelligence Engine.
"""
import anyio

from app.services.satellite_analysis_engine import analyze_satellite_health


def test_satellite_engine_returns_structure():
    result = anyio.run(lambda: analyze_satellite_health(23.0, 81.0))
    assert "vegetation_health" in result
    assert "ndvi_current" in result
    assert "stress_alert" in result

