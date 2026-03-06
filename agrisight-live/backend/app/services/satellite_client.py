"""
Satellite Client Service.

Provides simple helpers to fetch NDVI-like vegetation metrics from public
APIs. For this scaffold we primarily support a MOCK mode; real
integration with Sentinel-2 / MODIS / GEE can be added later.

Expected env vars:
- MOCK_SATELLITE: if "true", returns deterministic fake NDVI values.

Testing tips:
- Use MOCK_SATELLITE=true to avoid external calls.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

try:
    import httpx  # type: ignore[import]
except Exception:  # noqa: BLE001
    httpx = None  # type: ignore[assignment]

from app.services.cache_manager import cache_manager


async def _mock_ndvi(lat: float, lon: float) -> float:
    return 0.54


async def _mock_ndvi_history(lat: float, lon: float, days: int) -> List[Dict[str, Any]]:
    now = datetime.now(timezone.utc)
    base = 0.7
    history: List[Dict[str, Any]] = []
    for i in range(days):
        dt = now - timedelta(days=i)
        ndvi = base - 0.02 * i
        history.append({"date": dt.date().isoformat(), "ndvi": round(ndvi, 2)})
    return list(reversed(history))


async def fetch_ndvi(lat: float, lon: float) -> float:
    """
    Fetch a current NDVI estimate for a given location.
    """
    if os.getenv("MOCK_SATELLITE", "true").lower() == "true" or httpx is None:
        return await _mock_ndvi(lat, lon)

    cache_key = f"ndvi:current:{lat:.3f}:{lon:.3f}"
    cached = cache_manager.get(cache_key)
    if cached is not None:
        return float(cached)

    # Placeholder for real satellite API integration.
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Example URL to a hypothetical NDVI endpoint; replace with real.
        url = f"https://example-ndvi-api.com/ndvi?lat={lat}&lon={lon}"
        for attempt in range(3):
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                ndvi = float(data.get("ndvi", 0.5))
                cache_manager.set(cache_key, ndvi)
                return ndvi
            except Exception:
                if attempt == 2:
                    return await _mock_ndvi(lat, lon)
                continue


async def fetch_ndvi_history(lat: float, lon: float, days: int = 7) -> List[Dict[str, Any]]:
    """
    Fetch a short NDVI history time series.
    """
    if os.getenv("MOCK_SATELLITE", "true").lower() == "true" or httpx is None:
        return await _mock_ndvi_history(lat, lon, days)

    cache_key = f"ndvi:history:{lat:.3f}:{lon:.3f}:{days}"
    cached = cache_manager.get(cache_key)
    if cached:
        return cached

    async with httpx.AsyncClient(timeout=5.0) as client:
        url = f"https://example-ndvi-api.com/ndvi/history?lat={lat}&lon={lon}&days={days}"
        for attempt in range(3):
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                history = data.get("history", [])
                cache_manager.set(cache_key, history)
                return history
            except Exception:
                if attempt == 2:
                    return await _mock_ndvi_history(lat, lon, days)
                continue

