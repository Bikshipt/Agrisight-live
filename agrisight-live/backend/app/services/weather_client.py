"""
Weather Client Service.

Provides lightweight wrappers around external weather APIs for use by the
microclimate risk engine. For production use you should configure proper
timeouts, retries, and API keys if required.

Expected env vars:
- MOCK_WEATHER: if "true", returns deterministic fake data.

Testing tips:
- Set MOCK_WEATHER=true in tests to avoid external HTTP calls.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import json

try:
    import httpx  # type: ignore[import]
except Exception:  # noqa: BLE001
    httpx = None  # type: ignore[assignment]

from app.services.cache_manager import cache_manager


async def _mock_current(lat: float, lon: float) -> Dict[str, Any]:
    return {
        "temperature_c": 24.0,
        "humidity": 0.8,
        "rainfall_mm": 2.0,
        "wind_speed_ms": 1.5,
    }


async def _mock_forecast(lat: float, lon: float, days: int) -> List[Dict[str, Any]]:
    base = datetime.now(timezone.utc)
    out: List[Dict[str, Any]] = []
    for i in range(days):
        out.append(
            {
                "date": (base + timedelta(days=i)).date().isoformat(),
                "temperature_c": 22.0 + i,
                "humidity": 0.78,
                "rainfall_mm": 3.0 + i,
            }
        )
    return out


async def get_current_weather(lat: float, lon: float) -> Dict[str, Any]:
    """
    Retrieve a small set of current weather features for the given location.
    """
    if os.getenv("MOCK_WEATHER", "false").lower() == "true" or httpx is None:
        return await _mock_current(lat, lon)

    cache_key = f"weather:current:{lat:.3f}:{lon:.3f}"
    cached = cache_manager.get(cache_key)
    if cached:
        return cached

    async with httpx.AsyncClient(timeout=5.0) as client:
        # Open-Meteo current weather (temperature, windspeed) and simple humidity estimate
        om_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
        )
        for attempt in range(3):
            try:
                resp = await client.get(om_url)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception:
                if attempt == 2:
                    return await _mock_current(lat, lon)
                continue
        current = data.get("current", {})

        result = {
            "temperature_c": float(current.get("temperature_2m", 24.0)),
            "humidity": float(current.get("relative_humidity_2m", 80.0)) / 100.0,
            "rainfall_mm": float(current.get("precipitation", 0.0)),
            "wind_speed_ms": float(current.get("wind_speed_10m", 1.0)),
        }
        cache_manager.set(cache_key, result)
        return result


async def get_forecast_weather(lat: float, lon: float, days: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve a small multi-day forecast for temperature / humidity / rainfall.
    """
    if os.getenv("MOCK_WEATHER", "false").lower() == "true" or httpx is None:
        return await _mock_forecast(lat, lon, days)

    cache_key = f"weather:forecast:{lat:.3f}:{lon:.3f}:{days}"
    cached = cache_manager.get(cache_key)
    if cached:
        return cached

    async with httpx.AsyncClient(timeout=5.0) as client:
        # Open-Meteo daily forecast
        om_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            f"&forecast_days={days}"
        )
        for attempt in range(3):
            try:
                resp = await client.get(om_url)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception:
                if attempt == 2:
                    return await _mock_forecast(lat, lon, days)
                continue
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        tmax = daily.get("temperature_2m_max", [])
        tmin = daily.get("temperature_2m_min", [])
        rain = daily.get("precipitation_sum", [])

        out: List[Dict[str, Any]] = []
        for i, date_str in enumerate(dates):
            t_max = float(tmax[i]) if i < len(tmax) else 24.0
            t_min = float(tmin[i]) if i < len(tmin) else 20.0
            out.append(
                {
                    "date": date_str,
                    "temperature_c": (t_max + t_min) / 2,
                    "humidity": 0.8,  # simple default, refined via NASA POWER if desired
                    "rainfall_mm": float(rain[i]) if i < len(rain) else 0.0,
                }
            )
        cache_manager.set(cache_key, out)
        return out

