import json
from sqlalchemy.orm import Session
from openai import OpenAI
from app.config import settings
from app.models.campaign import Campaign
from app.models.persona import Persona
from app.models.country import Country
from app.models.generated_content import GeneratedContent
from app import log_bus

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class BaseAgent:
    """
    Shared foundation for all Triple I marketing agents.
    Provides: DB access, OpenAI calls, structured output, cost tracking, DB persistence.
    """

    AGENT_TYPE = "base"

    def __init__(self, db: Session):
        self.db = db

    # ─────────────────────────────────────────────
    # Context builder — shared across all agents
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
    # Uses chat.completions for compatibility with older OpenAI SDKs
    # ─────────────────────────────────────────────
    def _call_model(self, system_prompt: str, user_prompt: str, schema_name: str, schema: dict) -> dict:
        """
        Request a structured JSON response. We rely on prompt instructions plus
        optional JSON response_format for SDKs that support it.
        """
        # Instruct the model to return JSON only
        schema_instructions = (
            "You MUST respond with STRICTLY valid JSON, no markdown code fences, "
            "and it must conform to this JSON schema named '{name}':\n{schema}\n"
        ).format(name=schema_name, schema=json.dumps(schema))

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt + "\n\n" + schema_instructions},
        ]

        # Try to use JSON response_format when available; fall back gracefully otherwise
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
            )
        except TypeError:
            # Older SDKs may not support response_format; just call without it
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
            )

        raw_text = response.choices[0].message.content
        content = json.loads(raw_text)
        usage = response.usage

        input_cost = usage.prompt_tokens * settings.COST_PER_INPUT_TOKEN
        output_cost = usage.completion_tokens * settings.COST_PER_OUTPUT_TOKEN
        cost = round(input_cost + output_cost, 6)

        log_bus.emit(
            "💰",
            f"{self.AGENT_TYPE} · {schema_name} — {usage.total_tokens} tokens · ${cost:.4f}",
            "info"
        )

        return {
            "content": content,
            "usage": {
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "estimated_cost_usd": cost,
            },
        }

    # ─────────────────────────────────────────────
    # Free-text LLM call (no schema enforcement)
    # ─────────────────────────────────────────────
    def _call_model_free(self, system_prompt: str, user_prompt: str) -> dict:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ]
        )

        text  = response.choices[0].message.content
        usage = response.usage

        input_cost  = usage.prompt_tokens     * settings.COST_PER_INPUT_TOKEN
        output_cost = usage.completion_tokens * settings.COST_PER_OUTPUT_TOKEN

        return {
            "content": text,
            "usage": {
                "input_tokens":       usage.prompt_tokens,
                "output_tokens":      usage.completion_tokens,
                "total_tokens":       usage.total_tokens,
                "estimated_cost_usd": round(input_cost + output_cost, 6)
            }
        }

    # ─────────────────────────────────────────────
    # Persist a GeneratedContent record to DB
    # ─────────────────────────────────────────────
    def _save_content(
        self,
        campaign_id,
        content_type: str,
        headline: str,
        body: str,
        json_output: dict,
        usage: dict,
        parent_content_id=None,
        status: str = "draft"
    ) -> GeneratedContent:

        record = GeneratedContent(
            campaign_id=campaign_id,
            agent_type=self.AGENT_TYPE,
            type=content_type,
            headline=headline,
            body=body,
            json_output=json_output,
            parent_content_id=parent_content_id,
            input_tokens=usage["input_tokens"],
            output_tokens=usage["output_tokens"],
            total_tokens=usage["total_tokens"],
            cost_usd=usage["estimated_cost_usd"],
            status=status
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        log_bus.emit("✅", f"Saved → {content_type} · {headline[:60]}", "success")
        return record
