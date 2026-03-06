"""
Mock Outbreak Data Generator.

Provides synthetic crop scan events for local demo mode and testing the
outbreak intelligence engine without requiring Firestore.

Expected env vars: None
Testing tips:
- Use a fixed 'now' timestamp and assert that generated events cluster
  tightly around the configured coordinates.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List


@dataclass
class MockScan:
  disease: str
  timestamp: datetime
  geo_lat: float
  geo_long: float
  crop_type: str


def generate_mock_outbreak_events(now: datetime | None = None) -> List[MockScan]:
  """
  Generate a small cluster of events for a single disease.
  """
  now = now or datetime.now(timezone.utc)
  base_lat, base_long = 23.233, 81.12
  disease = "Brown Planthopper"

  events: List[MockScan] = []
  for i in range(10):
    dt = now - timedelta(minutes=10 * i)
    lat_jitter = (i % 3 - 1) * 0.01
    long_jitter = (i % 4 - 1.5) * 0.01
    events.append(
      MockScan(
        disease=disease,
        timestamp=dt,
        geo_lat=base_lat + lat_jitter,
        geo_long=base_long + long_jitter,
        crop_type="rice",
      )
    )
  return events

