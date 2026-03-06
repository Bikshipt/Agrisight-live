"""
Tests for the Yield Impact Estimator.
Expected env vars: None
Testing tips: Run with pytest.
"""
from app.services.yield_estimator import YieldEstimatorInput, estimate_yield_impact


def test_yield_estimator_basic():
    payload = YieldEstimatorInput(
        disease="Early Blight",
        infection_probability=0.5,
        crop_type="tomato",
        field_area=1.0,
        market_price_per_ton=10000.0,
    )
    result = estimate_yield_impact(payload)
    assert 0.0 <= result["yield_loss_percent"] <= 0.4
    assert result["expected_loss_rupees"] >= 0
    assert result["net_savings_if_treated"] >= 0

