"""
Main FastAPI application entry point.
Expected env vars: HOST, PORT, DEMO_MODE
Testing tips: Run with `uvicorn app.main:app --reload` for local dev.
"""
import json
import logging
import os
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.api.routes import router
from app.services.session_manager import session_manager

logger = logging.getLogger("agrisight")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AgriSight Live API")


@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next: Callable):
    """
    Emit structured JSON logs with basic latency and correlation fields.
    """
    start = time.perf_counter()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    session_id = request.headers.get("X-Session-ID", "")

    try:
        response = await call_next(request)
        latency_ms = (time.perf_counter() - start) * 1000.0
        log_record = {
            "timestamp": time.time(),
            "request_id": request_id,
            "session_id": session_id,
            "event_type": "http_request",
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "latency_ms": round(latency_ms, 2),
        }
        logger.info(json.dumps(log_record))
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as exc:  # noqa: BLE001
        latency_ms = (time.perf_counter() - start) * 1000.0
        log_record = {
            "timestamp": time.time(),
            "request_id": request_id,
            "session_id": session_id,
            "event_type": "http_error",
            "path": request.url.path,
            "method": request.method,
            "latency_ms": round(latency_ms, 2),
            "error": str(exc),
        }
        logger.error(json.dumps(log_record))
        raise


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "demo_mode": os.getenv("DEMO_MODE", "false").lower() == "true"}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    """
    Minimal Prometheus-style metrics endpoint.
    """
    active_sessions = len(session_manager.active_sessions)
    # For now these are simple gauges; detailed histograms can be added later.
    lines = [
        "# HELP agrisight_active_sessions Number of active analysis sessions.",
        "# TYPE agrisight_active_sessions gauge",
        f"agrisight_active_sessions {active_sessions}",
    ]
    return "\n".join(lines) + "\n"
