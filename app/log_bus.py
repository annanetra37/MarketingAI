"""
Triple I — Global Log Bus
Provides real-time log streaming to the frontend via Server-Sent Events.
All agents call log_bus.emit() to push log entries to connected clients.
"""
import asyncio
import time
from collections import deque
from typing import AsyncGenerator

# In-memory ring buffer — last 200 log lines kept for late-joining clients
_buffer: deque = deque(maxlen=200)

# Active SSE subscribers — set of asyncio.Queue
_subscribers: set = set()


def emit(icon: str, text: str, level: str = "info") -> None:
    """
    Emit a log entry. Safe to call from sync (agent) code.
    icon  : emoji e.g. "🧠", "✅", "❌", "💰"
    text  : human-readable message
    level : info | success | error | warn
    """
    entry = {
        "ts": time.strftime("%H:%M:%S"),
        "icon": icon,
        "text": text,
        "level": level,
    }
    _buffer.append(entry)
    # Push to all live subscribers (non-blocking)
    dead = set()
    for q in _subscribers:
        try:
            q.put_nowait(entry)
        except asyncio.QueueFull:
            dead.add(q)
    _subscribers.difference_update(dead)


async def stream() -> AsyncGenerator[str, None]:
    """
    AsyncGenerator that yields SSE-formatted strings.
    Yields the recent buffer first, then live entries.
    """
    q: asyncio.Queue = asyncio.Queue(maxsize=100)
    _subscribers.add(q)
    try:
        # Send recent history so the page shows previous activity on connect
        for entry in list(_buffer):
            yield _fmt(entry)

        # Then stream live
        while True:
            try:
                entry = await asyncio.wait_for(q.get(), timeout=20.0)
                yield _fmt(entry)
            except asyncio.TimeoutError:
                # Heartbeat — keeps the connection alive
                yield "event: ping\ndata: {}\n\n"
    finally:
        _subscribers.discard(q)


def _fmt(entry: dict) -> str:
    import json
    return f"data: {json.dumps(entry)}\n\n"
