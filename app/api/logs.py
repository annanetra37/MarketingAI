"""
Triple I — Real-time Log Stream API
GET /logs/stream  → Server-Sent Events feed of all agent activity
GET /logs/recent  → JSON array of last 50 log entries
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from app import log_bus

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/stream")
async def log_stream():
    """
    Server-Sent Events endpoint.
    Connect with: const es = new EventSource('/logs/stream')
    Each event: data: {"ts":"14:32:01","icon":"🧠","text":"...","level":"info"}
    """
    return StreamingResponse(
        log_bus.stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # Disable nginx buffering
            "Connection": "keep-alive",
        },
    )


@router.get("/recent")
def recent_logs():
    """Return the last 50 log entries as JSON (for page load / polling fallback)."""
    return JSONResponse(list(log_bus._buffer)[-50:])
