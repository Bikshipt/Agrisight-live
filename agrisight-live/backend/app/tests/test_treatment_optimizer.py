"""
Tests for the Treatment Optimization Engine.
Expected env vars: None
Testing tips: Run with pytest.
"""
from app.services.treatment_optimizer import (
    TreatmentOptimizerInput,
    optimize_treatment,
)


def test_treatment_optimizer_scales_with_area():
    payload_small = TreatmentOptimizerInput(
        disease="Early Blight",
        crop_type="tomato",
        field_area=1.0,
        severity=0.5,
    )
    payload_large = TreatmentOptimizerInput(
        disease="Early Blight",
        crop_type="tomato",
        field_area=3.0,
        severity=0.5,
    )
    res_small = optimize_treatment(payload_small)
    res_large = optimize_treatment(payload_large)
    assert res_large["total_required_ml"] > res_small["total_required_ml"]

