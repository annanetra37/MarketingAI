"""
app/agents/cmo_agent.py — Triple I v4.0
Uses gpt-4o (power model) for strategic reasoning only.
All other agents use gpt-4o-mini via BaseAgent defaults.
"""

import json
from app.agents.base_agent import BaseAgent
from app.agents.content_agent import ContentAgent
from app.agents.seo_agent import SEOAgent
from app.agents.ads_agent import AdsAgent
from app.models.generated_content import GeneratedContent


class CMOAgent(BaseAgent):
    """
    Strategic CMO — creates campaign briefs, coordinates agents, chat interface.
    Uses gpt-4o (USE_POWER_MODEL=True) for strategic reasoning quality.
    """

    AGENT_TYPE      = "cmo"
    USE_POWER_MODEL = True   # Only agent using gpt-4o — strategic quality matters

    # ─────────────────────────────────────────────
    # Campaign Brief
    # ─────────────────────────────────────────────
    def create_campaign_brief(self, campaign_id) -> GeneratedContent:
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = (
            "You are the CMO of Triple I — AI-powered ESG & Carbon Reporting platform.\n"
            "Triple I: ESRS↔ISSB↔GRI↔TCFD auto-mapping, EcoHub engine, audit-ready outputs.\n"
            "Cluster A (Spain/France/Netherlands/Belgium/Sweden) = CSRD urgency.\n"
            "Cluster B (UAE/Japan) = ISSB/IFRS alignment.\n"
            "Think strategically. Every brief must be actionable and measurable."
        )

        user_prompt = (
            f"Create a strategic campaign brief.\n"
            f"Campaign: {campaign.name}\n"
            f"Goal: {campaign.goal}\n"
            f"Persona: {persona.name} | Pains: {json.dumps(persona.pains)}\n"
            f"Motivations: {json.dumps(persona.motivations)}\n"
            f"CTA: {persona.cta}\n"
            f"Country: {country.name} ({country.cluster}) | Notes: {country.notes}\n"
            f"Framework: {campaign.framework_focus} | Channel: {campaign.channel}\n\n"
            "Return JSON with: executive_summary, market_context, target_audience_insight, "
            "core_message, content_pillars (array of {pillar, rationale, examples}), "
            "channel_strategy, campaign_phases (array of {phase, timeline, tactics, success_metrics}), "
            "kpis (array of {metric, target, why}), competitive_angle, "
            "agent_tasks (array of {agent, task, priority, rationale})"
        )

        schema = {
            "type": "object",
            "properties": {
                "executive_summary":       {"type": "string"},
                "market_context":          {"type": "string"},
                "target_audience_insight": {"type": "string"},
                "core_message":            {"type": "string"},
                "content_pillars": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pillar":    {"type": "string"},
                            "rationale": {"type": "string"},
                            "examples":  {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["pillar", "rationale", "examples"],
                        "additionalProperties": False
                    }
                },
                "channel_strategy": {"type": "string"},
                "campaign_phases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "phase":           {"type": "string"},
                            "timeline":        {"type": "string"},
                            "tactics":         {"type": "array", "items": {"type": "string"}},
                            "success_metrics": {"type": "string"}
                        },
                        "required": ["phase", "timeline", "tactics", "success_metrics"],
                        "additionalProperties": False
                    }
                },
                "kpis": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "metric": {"type": "string"},
                            "target": {"type": "string"},
                            "why":    {"type": "string"}
                        },
                        "required": ["metric", "target", "why"],
                        "additionalProperties": False
                    }
                },
                "competitive_angle": {"type": "string"},
                "agent_tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "agent":     {"type": "string"},
                            "task":      {"type": "string"},
                            "priority":  {"type": "string"},
                            "rationale": {"type": "string"}
                        },
                        "required": ["agent", "task", "priority", "rationale"],
                        "additionalProperties": False
                    }
                }
            },
            "required": [
                "executive_summary", "market_context", "target_audience_insight",
                "core_message", "content_pillars", "channel_strategy",
                "campaign_phases", "kpis", "competitive_angle", "agent_tasks"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "campaign_brief", schema, max_tokens=2000)
        content = result["content"]

        campaign.cmo_brief = content["executive_summary"]
        self.db.commit()

        return self._save_content(
            campaign_id  = campaign_id,
            content_type = "cmo_brief",
            headline     = f"Campaign Brief: {campaign.name}",
            body         = content["executive_summary"],
            json_output  = content,
            usage        = result["usage"]
        )

    # ─────────────────────────────────────────────
    # Full 5-step pipeline
    # ─────────────────────────────────────────────
    def run_full_pipeline(self, campaign_id: str) -> dict:
        results = {}
        errors  = {}

        try:
            brief = self.create_campaign_brief(campaign_id)
            results["cmo_brief"] = str(brief.id)
        except Exception as e:
            errors["cmo_brief"] = str(e)

        try:
            seo = SEOAgent(self.db).generate_keyword_cluster(campaign_id)
            results["seo_report"] = str(seo.id)
        except Exception as e:
            errors["seo_report"] = str(e)

        try:
            ca = ContentAgent(self.db)
            linkedin = ca.generate_linkedin(campaign_id)
            results["linkedin"] = str(linkedin.id)
            try:
                blog = ca.generate_blog_from_linkedin(linkedin.id)
                results["blog"] = str(blog.id)
            except Exception as e:
                errors["blog"] = str(e)
        except Exception as e:
            errors["linkedin"] = str(e)

        try:
            ads = AdsAgent(self.db).generate_google_ads(campaign_id)
            results["google_ads"] = str(ads.id)
        except Exception as e:
            errors["google_ads"] = str(e)

        return {
            "campaign_id":  campaign_id,
            "generated":    results,
            "errors":       errors,
            "total_pieces": len(results)
        }

    # ─────────────────────────────────────────────
    # Chat — strategic Q&A, always power model
    # ─────────────────────────────────────────────
    def chat(self, message: str, context: dict = None) -> str:
        system_prompt = (
            "You are the CMO Agent for Triple I — AI-powered ESG & Carbon Reporting B2B SaaS.\n"
            "Triple I: ESRS↔ISSB↔GRI↔TCFD auto-mapping, EcoHub engine.\n"
            "Markets: Spain/France/Netherlands/Belgium/Sweden (CSRD) + UAE/Japan (ISSB).\n"
            "ICPs: SMEs (compliance-driven) + ESG Advisory Firms (scale-driven).\n"
            "Be concise, strategic, actionable. Use bullet points."
        )

        context_note = f"\n\nContext: {json.dumps(context)}" if context else ""
        result = self._call_model_free(system_prompt, message + context_note)
        return result["content"]