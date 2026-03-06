"""
Tests for the Outbreak Intelligence Engine.
Expected env vars: None
Testing tips: Run with pytest.
"""
from datetime import datetime, timezone

from app.services.outbreak_intelligence_engine import analyze_outbreak_probability


def test_outbreak_mock_alert():
    # With no Firestore configured, the engine should fall back to mock data
    # and usually raise an alert for the synthetic cluster.
    now = datetime.now(timezone.utc)
    result = analyze_outbreak_probability(now=now)
    assert "outbreak_alert" in result
    assert "spread_probability" in result

