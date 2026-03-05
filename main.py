"""
main.py — Triple I Autonomous AI Marketing Platform v4.0
FastAPI entry point. Serves both the REST API and the frontend UI.

Railway deployment notes:
- PORT is injected by Railway automatically
- DATABASE_URL is injected by the linked PostgreSQL service
- OPENAI_API_KEY must be set in Railway environment variables
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse

from app.database import engine, Base
from app.models.persona import Persona
from app.models.country import Country
from app.models.campaign import Campaign
from app.models.generated_content import GeneratedContent
from app.api import persona, country, campaign, generate, content, logs

# ── Fix Railway's postgres:// → postgresql:// URL scheme ─────────────────
# Railway injects DATABASE_URL as postgres://... but SQLAlchemy needs postgresql://
_raw_db_url = os.environ.get("DATABASE_URL", "")
if _raw_db_url.startswith("postgres://"):
    os.environ["DATABASE_URL"] = _raw_db_url.replace("postgres://", "postgresql://", 1)

app = FastAPI(
    title="Triple I — Autonomous AI Marketing v4",
    description="8 AI agents. One loop. Fear → ESRS Assessment → Fast-Track Sprint pilot.",
    version="4.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auto-create all DB tables on startup ─────────────────────────────────
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Triple I Autonomous Marketing AI v4.0 — ONLINE")
    print(f"   Model: {os.environ.get('OPENAI_MODEL', 'gpt-4o')}")
    print(f"   DB:    {'connected' if os.environ.get('DATABASE_URL') else 'NOT SET'}")
    print(f"   Key:   {'set' if os.environ.get('OPENAI_API_KEY') else 'NOT SET ⚠️'}")

# ── Health check — required by Railway ───────────────────────────────────
@app.get("/health", include_in_schema=False)
def health():
    return JSONResponse({"status": "ok", "version": "4.0.0"})

# ── Routers ───────────────────────────────────────────────────────────────
app.include_router(persona.router)
app.include_router(country.router)
app.include_router(campaign.router)
app.include_router(content.router)
app.include_router(generate.router)
app.include_router(logs.router)

# ── Frontend UI ───────────────────────────────────────────────────────────
_here     = os.path.dirname(os.path.abspath(__file__))
_frontend = os.path.join(_here, "frontend")

_NO_CACHE = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma":        "no-cache",
    "Expires":       "0",
}

@app.get("/ui", include_in_schema=False)
@app.get("/ui/", include_in_schema=False)
def serve_ui():
    """Serve the Command Center UI with no-cache headers."""
    html_path = os.path.join(_frontend, "index.html")
    return FileResponse(html_path, headers=_NO_CACHE, media_type="text/html")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui")

# ── Optional static assets ────────────────────────────────────────────────
_static_dir = os.path.join(_frontend, "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")
