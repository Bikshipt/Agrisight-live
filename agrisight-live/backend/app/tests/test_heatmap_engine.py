"""
Tests for Outbreak Heatmap Engine.
"""
from app.services.outbreak_heatmap_engine import _kernel_density


def test_kernel_density_non_negative():
    points = [(23.0, 81.0), (23.01, 81.02)]
    density = _kernel_density(points, 23.0, 81.0, bandwidth_km=10.0)
    assert density >= 0.0

