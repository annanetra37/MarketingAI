from app.agents.base_agent import BaseAgent
from app.agents.content_agent import ContentAgent
from app.agents.seo_agent import SEOAgent
from app.agents.ads_agent import AdsAgent
from app.models.campaign import Campaign
from app.models.generated_content import GeneratedContent
from app.models.persona import Persona
from app.models.country import Country
import json


class CMOAgent(BaseAgent):
    """
    The orchestrator. Acts as CMO — creates strategic briefs, coordinates all agents,
    reviews output quality, and drives the full campaign pipeline.
    """

    AGENT_TYPE = "cmo"

    # ─────────────────────────────────────────────
    # Strategic Brief Generation
    # ─────────────────────────────────────────────
    def create_campaign_brief(self, campaign_id) -> GeneratedContent:
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = f"""
You are the CMO of Triple I — an AI-powered ESG & Carbon Reporting platform.

Triple I strategic positioning:
- PRIMARY DIFFERENTIATOR: Framework Interoperability Translator (ESRS ↔ ISSB ↔ GRI ↔ TCFD)
- PRODUCT FOCUS: Carbon footprint reporting + CSRD compliance + audit-ready outputs
- ENGINE: EcoHub (core sustainability data engine)
- TARGET: CSRD-pressured SMEs (250-1500 employees) + ESG Advisory Firms
- MARKETS: Cluster A (Spain, France, Netherlands, Belgium, Sweden — CSRD urgency) | Cluster B (UAE, Japan — ISSB alignment)

Content allocation: 60% SME-focused, 40% Advisory-focused.
Geographic rule: NEVER run generic global campaigns. Always tailor per cluster.

You think strategically. You understand:
- What makes B2B SaaS marketing effective
- The difference between demand gen and demand capture
- How to sequence content for maximum funnel impact
- The ESG regulatory landscape deeply
        """.strip()

        user_prompt = f"""
Create a comprehensive marketing campaign brief for:

Campaign: {campaign.name}
Persona: {persona.name}
Country: {country.name} (Cluster: {country.cluster})
Framework Focus: {campaign.framework_focus}
Channel: {campaign.channel}
Goal: {campaign.goal}
Persona Pains: {json.dumps(persona.pains)}
Persona Motivations: {json.dumps(persona.motivations)}
Country Notes: {country.notes}

The brief must include:
- executive_summary: 2-3 sentence strategic overview
- market_context: regulatory/market situation in this country right now
- target_audience_insight: deep insight about this specific persona's mindset
- core_message: THE single message that runs through all campaign content
- content_pillars: array of 3 strategic content themes with rationale
- channel_strategy: specific recommendations for {campaign.channel}
- campaign_phases: array of 3 phases (phase name, timeline, tactics, success metrics)
- kpis: array of 5 specific, measurable KPIs with targets
- competitive_angle: how to position Triple I vs. manual/spreadsheet approach
- agent_tasks: array of recommended tasks for Content, SEO, and Ads agents
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "executive_summary":      {"type": "string"},
                "market_context":         {"type": "string"},
                "target_audience_insight":{"type": "string"},
                "core_message":           {"type": "string"},
                "content_pillars": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pillar":   {"type": "string"},
                            "rationale":{"type": "string"},
                            "examples": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["pillar", "rationale", "examples"],
                        "additionalProperties": False
                    }
                },
                "channel_strategy":     {"type": "string"},
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
                            "agent":       {"type": "string"},
                            "task":        {"type": "string"},
                            "priority":    {"type": "string"},
                            "rationale":   {"type": "string"}
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

        result  = self._call_model(system_prompt, user_prompt, "campaign_brief", schema)
        content = result["content"]

        # Save brief to campaign record too
        campaign.cmo_brief = content["executive_summary"]
        self.db.commit()

        return self._save_content(
            campaign_id=campaign_id,
            content_type="cmo_brief",
            headline=f"Campaign Brief: {campaign.name}",
            body=content["executive_summary"],
            json_output=content,
            usage=result["usage"]
        )

    # ─────────────────────────────────────────────
    # Full Pipeline Orchestration
    # ─────────────────────────────────────────────
    def run_full_pipeline(self, campaign_id: str) -> dict:
        """
        Runs the full agent pipeline:
        1. CMO Brief
        2. SEO Keyword Cluster
        3. LinkedIn Post
        4. Blog from LinkedIn
        5. Google Ads
        Returns a summary dict with all generated content IDs.
        """
        results = {}
        errors  = {}

        # 1. CMO Brief
        try:
            brief = self.create_campaign_brief(campaign_id)
            results["cmo_brief"] = str(brief.id)
        except Exception as e:
            errors["cmo_brief"] = str(e)

        # 2. SEO Research
        try:
            seo_agent = SEOAgent(self.db)
            seo = seo_agent.generate_keyword_cluster(campaign_id)
            results["seo_report"] = str(seo.id)
        except Exception as e:
            errors["seo_report"] = str(e)

        # 3. LinkedIn Post
        try:
            content_agent = ContentAgent(self.db)
            linkedin = content_agent.generate_linkedin(campaign_id)
            results["linkedin"] = str(linkedin.id)

            # 4. Blog from LinkedIn
            try:
                blog = content_agent.generate_blog_from_linkedin(linkedin.id)
                results["blog"] = str(blog.id)
            except Exception as e:
                errors["blog"] = str(e)

        except Exception as e:
            errors["linkedin"] = str(e)

        # 5. Google Ads
        try:
            ads_agent = AdsAgent(self.db)
            ads = ads_agent.generate_google_ads(campaign_id)
            results["google_ads"] = str(ads.id)
        except Exception as e:
            errors["google_ads"] = str(e)

        return {
            "campaign_id": campaign_id,
            "generated": results,
            "errors":    errors,
            "total_pieces": len(results)
        }

    # ─────────────────────────────────────────────
    # Chat interface — respond to strategic questions
    # ─────────────────────────────────────────────
    def chat(self, message: str, context: dict = None) -> str:
        system_prompt = """
You are the CMO Agent for Triple I — an AI-powered ESG & Carbon Reporting B2B SaaS platform.

Triple I positioning:
- The Framework Interoperability Translator: ESRS ↔ ISSB ↔ GRI ↔ TCFD
- Carbon reporting automation for CSRD-pressured SMEs (250-1500 employees)
- Target markets: Spain, France, Netherlands, Belgium, Sweden (Cluster A - CSRD urgency) + UAE, Japan (Cluster B - ISSB alignment)
- Two ICPs: SMEs (compliance-driven) and ESG Advisory Firms (scale-driven)
- Content split: 60% SME, 40% Advisory

You have full strategic marketing knowledge. You:
- Brief the Content Agent on what to write
- Direct the SEO Agent on which keywords to own
- Guide the Ads Agent on creative angles to test
- Monitor campaign performance and recommend pivots
- Think in funnels: awareness → consideration → conversion

Be concise, strategic, and actionable. Use bullet points for recommendations.
If the user asks you to create something, describe exactly what you would brief each agent to do.
        """.strip()

        context_note = ""
        if context:
            context_note = f"\n\nCurrent context: {json.dumps(context)}"

        result = self._call_model_free(system_prompt, message + context_note)
        return result["content"]
