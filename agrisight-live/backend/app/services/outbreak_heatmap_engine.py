"""
Outbreak Heatmap Engine.

Generates a simple regional disease density heatmap grid from historical
crop scan events stored in Firestore.

Expected env vars:
- GOOGLE_CLOUD_PROJECT / GOOGLE_APPLICATION_CREDENTIALS (optional).
Testing tips:
- In tests, monkeypatch Firestore or call the density function directly
  with synthetic points.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

try:
    from google.cloud import firestore  # type: ignore[import]
except Exception:  # noqa: BLE001
    firestore = None  # type: ignore[assignment]


def _firestore_client():
    if firestore is None:
        return None
    return firestore.Client()


def _kernel_density(points: List[Tuple[float, float]], lat: float, lon: float, bandwidth_km: float) -> float:
    """
    Gaussian kernel density estimate at a given grid point.
    """
    if not points:
        return 0.0
    bw2 = bandwidth_km ** 2

    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    density = 0.0
    for plat, plon in points:
        d = haversine_km(lat, lon, plat, plon)
        density += math.exp(-0.5 * (d ** 2) / bw2)
    return density


def generate_outbreak_heatmap() -> Dict[str, Any]:
    """
    Build a coarse grid of disease density values.
    """
    client = _firestore_client()
    if client is None:
        return {"grid": []}

    docs = client.collection("crop_scans").stream()
    points: List[Tuple[float, float]] = []
    for d in docs:
        data = d.to_dict()
        try:
            lat = float(data.get("geo_lat") or 0.0)
            lon = float(data.get("geo_long") or 0.0)
        except Exception:
            continue
        if lat and lon:
            points.append((lat, lon))

    if not points:
        return {"grid": []}

    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    # Simple 6x6 grid.
    steps = 6
    lat_step = (max_lat - min_lat) / max(steps - 1, 1) or 0.01
    lon_step = (max_lon - min_lon) / max(steps - 1, 1) or 0.01

    grid: List[Dict[str, Any]] = []
    for i in range(steps):
        for j in range(steps):
            glat = min_lat + i * lat_step
            glon = min_lon + j * lon_step
            density = _kernel_density(points, glat, glon, bandwidth_km=10.0)
            grid.append({"lat": round(glat, 3), "lon": round(glon, 3), "density": round(float(density), 2)})

    return {"grid": grid}

