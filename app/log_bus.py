"""
Triple I — Global Log Bus  (FIXED v2)
Provides real-time log streaming to the frontend via Server-Sent Events.
All agents call log_bus.emit() to push log entries to connected clients.

FIX: emit() is called from sync FastAPI route threads.
     We now use asyncio.get_event_loop() + call_soon_threadsafe() so the
     async SSE generator wakes up correctly even when called from sync code.
"""
import asyncio
import json
import time
from collections import deque
from typing import AsyncGenerator

# In-memory ring buffer — last 200 log lines kept for late-joining clients
_buffer: deque = deque(maxlen=200)

# Active SSE subscribers — set of asyncio.Queue
_subscribers: set = set()

# Reference to the main event loop (set on first use)
_loop: asyncio.AbstractEventLoop | None = None


def _get_loop() -> asyncio.AbstractEventLoop | None:
    """Return the running event loop if available."""
    global _loop
    try:
        running = asyncio.get_event_loop_policy().get_event_loop()
        if running.is_running():
            _loop = running
        return _loop
    except RuntimeError:
        return _loop


def emit(icon: str, text: str, level: str = "info") -> None:
    """
    Emit a log entry. Safe to call from sync (agent) code running in threads.
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

    loop = _get_loop()
    dead = set()

    for q in list(_subscribers):
        if loop and loop.is_running():
            # Called from a sync thread — schedule put on the async event loop
            try:
                loop.call_soon_threadsafe(q.put_nowait, entry)
            except Exception:
                dead.add(q)
        else:
            # Already on the event loop (rare) — put directly
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
    global _loop
    # Capture the running loop so emit() can schedule into it
    _loop = asyncio.get_event_loop()

    q: asyncio.Queue = asyncio.Queue(maxsize=200)
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
                # Heartbeat — keeps the connection alive through proxies
                yield "event: ping\ndata: {}\n\n"
    finally:
        _subscribers.discard(q)


def _fmt(entry: dict) -> str:
    return f"data: {json.dumps(entry)}\n\n"
