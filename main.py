from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
import os

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

app.include_router(persona.router)
app.include_router(country.router)
app.include_router(campaign.router)
app.include_router(content.router)
app.include_router(generate.router)
app.include_router(logs.router)

# ── Serve the UI ─────────────────────────────────────────────────────────
# Resolve path relative to this file so it works regardless of cwd
_here     = os.path.dirname(os.path.abspath(__file__))
_frontend = os.path.join(_here, "frontend")

@app.get("/ui", include_in_schema=False)
@app.get("/ui/", include_in_schema=False)
def serve_ui():
    return FileResponse(os.path.join(_frontend, "index.html"))

@app.get("/", include_in_schema=False)
def root():
    # Redirect browser to UI; API clients hit /docs
    return RedirectResponse(url="/ui")
