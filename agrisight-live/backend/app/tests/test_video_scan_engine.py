"""
Tests for the Autonomous Field Video Scan Engine.
Expected env vars: None
"""
from app.services.video_field_scan_engine import analyze_field_video


def test_video_scan_engine_handles_invalid_bytes():
    # Passing random bytes should still yield a valid summary structure.
    summary = analyze_field_video(b"not-a-real-video")
    assert "plants_analyzed" in summary
    assert "healthy_percent" in summary
    assert "mild_infection_percent" in summary
    assert "severe_infection_percent" in summary
    assert "hotspot_regions" in summary

