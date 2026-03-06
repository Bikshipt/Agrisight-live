"""
Outbreak Intelligence Engine.

Detects emerging disease clusters based on recent scan events stored in
Firestore and/or local mock data. Uses a lightweight spatial clustering
algorithm inspired by DBSCAN for geo coordinates.

Expected env vars:
- GOOGLE_CLOUD_PROJECT (optional): Firestore project id.
- GOOGLE_APPLICATION_CREDENTIALS (optional): path to service account JSON.

Testing tips:
- Use the mock outbreak data generator to feed synthetic clusters and
  assert that outbreak_alert toggles as expected.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
  from google.cloud import firestore  # type: ignore[import]
except Exception:  # noqa: BLE001
  firestore = None  # type: ignore[assignment]


from app.dev.mock_outbreak_data import generate_mock_outbreak_events


@dataclass
class ScanEvent:
  disease: str
  timestamp: datetime
  geo_lat: float
  geo_long: float
  crop_type: str


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
  r = 6371.0
  phi1, phi2 = math.radians(lat1), math.radians(lat2)
  dphi = math.radians(lat2 - lat1)
  dlambda = math.radians(lon2 - lon1)
  a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  return r * c


def _fetch_recent_scans_from_firestore(hours: int = 24) -> List[ScanEvent]:
  if firestore is None:
    return []

  project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
  if not project_id:
    return []

  client = firestore.Client(project=project_id)
  since = datetime.now(timezone.utc) - timedelta(hours=hours)

  docs = (
    client.collection("crop_scans")
    .where("timestamp", ">=", since.isoformat())
    .stream()
  )
  events: List[ScanEvent] = []
  for d in docs:
    data = d.to_dict()
    try:
      events.append(
        ScanEvent(
          disease=data.get("disease", ""),
          timestamp=datetime.fromisoformat(data.get("timestamp")),
          geo_lat=float(data.get("geo_lat") or 0.0),
          geo_long=float(data.get("geo_long") or 0.0),
          crop_type=data.get("crop_type", ""),
        )
      )
    except Exception:
      continue
  return events


def _cluster_events(events: Iterable[ScanEvent], eps_km: float, min_pts: int) -> List[List[ScanEvent]]:
  """
  Very small DBSCAN-like clustering tuned for the expected small datasets.
  """
  events_list = list(events)
  clusters: List[List[ScanEvent]] = []
  visited: set[int] = set()

  for i, ev in enumerate(events_list):
    if i in visited:
      continue
    visited.add(i)
    neighbors = [j for j, other in enumerate(events_list) if _haversine_km(ev.geo_lat, ev.geo_long, other.geo_lat, other.geo_long) <= eps_km]
    if len(neighbors) < min_pts:
      continue
    cluster: List[ScanEvent] = []
    queue = neighbors[:]
    while queue:
      idx = queue.pop()
      if idx not in visited:
        visited.add(idx)
        ev_j = events_list[idx]
        neighbors_j = [
          k
          for k, other in enumerate(events_list)
          if _haversine_km(ev_j.geo_lat, ev_j.geo_long, other.geo_lat, other.geo_long) <= eps_km
        ]
        if len(neighbors_j) >= min_pts:
          queue.extend(neighbors_j)
      cluster.append(events_list[idx])
    clusters.append(cluster)

  return clusters


def analyze_outbreak_probability(now: Optional[datetime] = None) -> Dict[str, Any]:
  """
  Analyze recent events and return an outbreak alert payload.
  """
  now = now or datetime.now(timezone.utc)
  events = _fetch_recent_scans_from_firestore()
  if not events:
    events = generate_mock_outbreak_events(now=now)

  if not events:
    return {
      "outbreak_alert": False,
      "disease": None,
      "cluster_center": None,
      "radius_km": 0,
      "spread_probability": 0.0,
    }

  # Group by disease and cluster each disease separately.
  best_cluster: Optional[Tuple[str, List[ScanEvent]]] = None
  for disease in {e.disease for e in events if e.disease}:
    disease_events = [e for e in events if e.disease == disease]
    clusters = _cluster_events(disease_events, eps_km=15.0, min_pts=3)
    for c in clusters:
      if not best_cluster or len(c) > len(best_cluster[1]):
        best_cluster = (disease, c)

  if not best_cluster:
    return {
      "outbreak_alert": False,
      "disease": None,
      "cluster_center": None,
      "radius_km": 0,
      "spread_probability": 0.0,
    }

  disease, cluster = best_cluster
  lats = [e.geo_lat for e in cluster]
  longs = [e.geo_long for e in cluster]
  center_lat = sum(lats) / len(lats)
  center_long = sum(longs) / len(longs)
  radius_km = max(
    1.0,
    max(_haversine_km(center_lat, center_long, e.geo_lat, e.geo_long) for e in cluster),
  )

  # Simple density-based probability proxy: more points in smaller radius -> higher.
  density = len(cluster) / (radius_km ** 2)
  spread_probability = max(0.0, min(0.99, 1 - math.exp(-density)))

  return {
    "outbreak_alert": spread_probability > 0.4,
    "disease": disease,
    "cluster_center": [round(center_lat, 3), round(center_long, 3)],
    "radius_km": round(radius_km, 1),
    "spread_probability": round(spread_probability, 2),
  }

