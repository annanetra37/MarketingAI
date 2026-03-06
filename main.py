import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse

# Fix Railway's postgres:// → postgresql:// BEFORE any db imports
_raw_db_url = os.environ.get("DATABASE_URL", "")
if _raw_db_url.startswith("postgres://"):
    os.environ["DATABASE_URL"] = _raw_db_url.replace("postgres://", "postgresql://", 1)

from app.database import engine, Base
from app.models.persona import Persona
from app.models.country import Country
from app.models.campaign import Campaign
from app.models.generated_content import GeneratedContent
from app.api import persona, country, campaign, generate, content, logs

app = FastAPI(
    title="Triple I — Autonomous AI Marketing v4",
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

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

# ── Health check ─────────────────────────────────────────────────
@app.get("/health", include_in_schema=False)
def health():
    return JSONResponse({"status": "ok", "version": "4.0.0"})

# ── Debug endpoint — DELETE THIS AFTER CONFIRMING DEPLOY ─────────
@app.get("/debug/version", include_in_schema=False)
def debug_version():
    """Temporary: confirms which code version is actually running on Railway."""
    import inspect
    from app.agents.autonomous_orchestrator import AutonomousOrchestrator
    methods = [m for m in dir(AutonomousOrchestrator) if not m.startswith("_")]
    has_auto_generate = hasattr(AutonomousOrchestrator, "auto_generate_campaign_goals")
    has_triple_i_context = False
    try:
        from app.agents import triple_i_context
        has_triple_i_context = True
    except ImportError:
        pass
    return JSONResponse({
        "version": "4.0.0",
        "orchestrator_methods": methods,
        "has_auto_generate_campaign_goals": has_auto_generate,
        "has_triple_i_context": has_triple_i_context,
        "openai_key_set": bool(os.environ.get("OPENAI_API_KEY")),
        "database_url_set": bool(os.environ.get("DATABASE_URL")),
    })

app.include_router(persona.router)
app.include_router(country.router)
app.include_router(campaign.router)
app.include_router(content.router)
app.include_router(generate.router)
app.include_router(logs.router)

# ── Serve the UI ─────────────────────────────────────────────────
_here     = os.path.dirname(os.path.abspath(__file__))
_frontend = os.path.join(_here, "frontend")

_NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}

@app.get("/ui", include_in_schema=False)
@app.get("/ui/", include_in_schema=False)
def serve_ui():
    html_path = os.path.join(_frontend, "index.html")
    return FileResponse(html_path, headers=_NO_CACHE_HEADERS, media_type="text/html")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui")

_static_dir = os.path.join(_frontend, "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")