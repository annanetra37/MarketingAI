"""
app/agents/base_agent.py — Triple I v4.0

Two-tier model routing:
  MODEL_MINI  = gpt-4o-mini  → all agents by default  ($0.15/$0.60 per 1M tokens)
  MODEL_POWER = gpt-4o       → CMO only               ($2.50/$10.00 per 1M tokens)

max_tokens is now passed per call to hard-cap output costs.
LinkedIn target: <$0.005 per post at ~400 input + 400 output tokens on mini.
"""

import json
import os
from sqlalchemy.orm import Session
from openai import OpenAI
from app.config import settings
from app.models.campaign import Campaign
from app.models.persona import Persona
from app.models.country import Country
from app.models.generated_content import GeneratedContent
from app import log_bus

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ── Model tier resolution ─────────────────────────────────────────────────
_env_override = os.environ.get("OPENAI_MODEL", "")
MODEL_MINI    = os.environ.get("OPENAI_MODEL_MINI",  _env_override or "gpt-4o-mini")
MODEL_POWER   = os.environ.get("OPENAI_MODEL_POWER", _env_override or "gpt-4o")

# Verified OpenAI pricing (per token, not per 1M)
_RATES = {
    "gpt-4o-mini": {"in": 0.00000015,  "out": 0.0000006},   # $0.15/$0.60 per 1M
    "gpt-4o":      {"in": 0.0000025,   "out": 0.00001},      # $2.50/$10.00 per 1M
}

def _rate(model: str, direction: str) -> float:
    # Fallback to gpt-4o rates for unknown models
    rates = _RATES.get(model) or _RATES.get("gpt-4o")
    return rates[direction]


class BaseAgent:
    """
    Shared foundation for all Triple I marketing agents.
    USE_POWER_MODEL = False (default) → gpt-4o-mini, cheap + fast
    USE_POWER_MODEL = True            → gpt-4o, for CMO strategic reasoning only
    """

    AGENT_TYPE      = "base"
    USE_POWER_MODEL = False

    def __init__(self, db: Session):
        self.db = db

    def _active_model(self, force_power: bool = False) -> str:
        return MODEL_POWER if (force_power or self.USE_POWER_MODEL) else MODEL_MINI

    # ─────────────────────────────────────────────
    # Context builder
    # ─────────────────────────────────────────────
    def build_context(self, campaign_id):
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        persona = self.db.query(Persona).filter(Persona.id == campaign.persona_id).first()
        country = self.db.query(Country).filter(Country.id == campaign.country_id).first()
        return campaign, persona, country

    # ─────────────────────────────────────────────
    # Core LLM call — structured JSON output
    # max_tokens caps output to control cost
    # ─────────────────────────────────────────────
    def _call_model(
        self,
        system_prompt: str,
        user_prompt:   str,
        schema_name:   str,
        schema:        dict,
        force_power:   bool = False,
        max_tokens:    int  = 1000,   # default cap — override per call type
    ) -> dict:
        model = self._active_model(force_power)

        schema_instructions = (
            "Respond ONLY with valid JSON matching this schema — "
            "no markdown, no explanation:\n"
            f"{json.dumps(schema, separators=(',', ':'))}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt + "\n\n" + schema_instructions},
        ]

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
            )
        except TypeError:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
            )

        raw_text = response.choices[0].message.content
        content  = json.loads(raw_text)
        usage    = response.usage

        in_cost  = usage.prompt_tokens     * _rate(model, "in")
        out_cost = usage.completion_tokens * _rate(model, "out")
        cost     = round(in_cost + out_cost, 6)

        log_bus.emit(
            "💰",
            f"{self.AGENT_TYPE} [{model}] · {schema_name} "
            f"— in:{usage.prompt_tokens} out:{usage.completion_tokens} · ${cost:.5f}",
            "info",
        )

        return {
            "content": content,
            "usage": {
                "input_tokens":       usage.prompt_tokens,
                "output_tokens":      usage.completion_tokens,
                "total_tokens":       usage.total_tokens,
                "estimated_cost_usd": cost,
            },
        }

    # ─────────────────────────────────────────────
    # Free-text call — CMO chat, always power model
    # ─────────────────────────────────────────────
    def _call_model_free(self, system_prompt: str, user_prompt: str) -> dict:
        model    = MODEL_POWER
        response = client.chat.completions.create(
            model    = model,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens = 800,
        )

        text  = response.choices[0].message.content
        usage = response.usage

        in_cost  = usage.prompt_tokens     * _rate(model, "in")
        out_cost = usage.completion_tokens * _rate(model, "out")

        return {
            "content": text,
            "usage": {
                "input_tokens":       usage.prompt_tokens,
                "output_tokens":      usage.completion_tokens,
                "total_tokens":       usage.total_tokens,
                "estimated_cost_usd": round(in_cost + out_cost, 6),
            },
        }

    # ─────────────────────────────────────────────
    # Persist to DB
    # ─────────────────────────────────────────────
    def _save_content(
        self,
        campaign_id,
        content_type:      str,
        headline:          str,
        body:              str,
        json_output:       dict,
        usage:             dict,
        parent_content_id = None,
        status:            str = "draft",
    ) -> GeneratedContent:

        record = GeneratedContent(
            campaign_id       = campaign_id,
            agent_type        = self.AGENT_TYPE,
            type              = content_type,
            headline          = headline,
            body              = body,
            json_output       = json_output,
            parent_content_id = parent_content_id,
            input_tokens      = usage["input_tokens"],
            output_tokens     = usage["output_tokens"],
            total_tokens      = usage["total_tokens"],
            cost_usd          = usage["estimated_cost_usd"],
            status            = status,
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        log_bus.emit("✅", f"Saved → {content_type} · {headline[:60]}", "success")
        return record