"""
cmo_agent.py
============
CMO Orchestrator — Strategic brain of the Triple I autonomous marketing system.

Knows Triple I's full product, both ICPs, all target markets, and the
Fear → Pilot → 6-Week Close sales strategy.  Coordinates all other agents.
"""

import json
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.agents.triple_i_context import (
    get_master_context, get_fear_hooks, get_cta_library,
    SALES_STRATEGY, ICP_SME, ICP_ADVISORY, MARKETS, VALUE_PROPS
)
from app.models.generated_content import GeneratedContent


class CMOAgent(BaseAgent):
    """
    🧠 CMO Orchestrator
    Sets strategy, creates campaign briefs, runs the 5-step pipeline,
    and answers strategic questions via chat.
    """

    AGENT_TYPE = "cmo"

    # ─────────────────────────────────────────────
    # Campaign Brief
    # ─────────────────────────────────────────────
    def create_campaign_brief(self, campaign_id: str) -> GeneratedContent:
        """
        Generate a comprehensive campaign brief embedding the Fear → Pilot →
        6-Week Close sales motion and full product context.
        """
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = f"""
You are the CMO for Triple I — an AI-powered ESG & Carbon Reporting B2B SaaS platform.
You are also the strategic orchestrator for all marketing agents.

{get_master_context()}

YOUR STRATEGIC MANDATE:
- Every campaign brief MUST embed the Fear → Value → Pilot sales motion
- CSRD urgency is your #1 lever — use it relentlessly
- All briefs must accelerate a sub-6-week sales cycle
- Cluster A (Spain, France, Netherlands, Belgium, Sweden) is the IMMEDIATE priority
- Content must drive to one of three actions:
  1. Book a free ESRS Readiness Assessment
  2. Start a Fast-Track Compliance Sprint (€5K–€15K pilot)
  3. Book a live demo

Geographic rule: NEVER run generic global campaigns. Always tailor per cluster.
Think in funnels: fear → credibility → demo request → pilot → close.
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

The brief must:
1. Lead with the regulatory fear/urgency angle for {country.name}
2. Position the Fast-Track Compliance Sprint (E1+S1, 6–8 weeks, €5K–€15K) as the primary CTA
3. Include the ESRS Readiness Assessment as the lead-gen hook
4. Define the exact 5-step sales motion for this persona/country combo
5. Specify content that creates fear FIRST, then demonstrates Triple I value

Return JSON with all required fields.
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "executive_summary":        {"type": "string"},
                "market_context":           {"type": "string"},
                "regulatory_urgency":       {"type": "string"},
                "target_audience_insight":  {"type": "string"},
                "core_message":             {"type": "string"},
                "fear_hook":                {"type": "string"},
                "pilot_cta":                {"type": "string"},
                "lead_gen_hook":            {"type": "string"},
                "content_pillars": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "pillar":    {"type": "string"},
                            "rationale": {"type": "string"},
                            "formats":   {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["pillar", "rationale", "formats"],
                        "additionalProperties": False
                    }
                },
                "channel_strategy": {"type": "string"},
                "sales_cycle_plan": {
                    "type": "object",
                    "properties": {
                        "week_1_2": {"type": "string"},
                        "week_3_4": {"type": "string"},
                        "week_5_6": {"type": "string"}
                    },
                    "required": ["week_1_2", "week_3_4", "week_5_6"],
                    "additionalProperties": False
                },
                "campaign_phases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "phase":           {"type": "string"},
                            "timeline":        {"type": "string"},
                            "tactics":         {"type": "array", "items": {"type": "string"}},
                            "success_metrics": {"type": "array", "items": {"type": "string"}}
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
                            "kpi":    {"type": "string"},
                            "target": {"type": "string"},
                            "why":    {"type": "string"}
                        },
                        "required": ["kpi", "target", "why"],
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
                "executive_summary", "market_context", "regulatory_urgency",
                "target_audience_insight", "core_message", "fear_hook", "pilot_cta",
                "lead_gen_hook", "content_pillars", "channel_strategy",
                "sales_cycle_plan", "campaign_phases", "kpis",
                "competitive_angle", "agent_tasks"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "campaign_brief", schema)
        content = result["content"]

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
        Runs the full 5-step pipeline:
        1. CMO Brief  2. SEO Keywords  3. LinkedIn  4. Blog  5. Google Ads
        """
        from app.agents.seo_agent import SEOAgent
        from app.agents.content_agent import ContentAgent
        from app.agents.ads_agent import AdsAgent

        results = {}
        errors  = {}

        for step, fn in [
            ("cmo_brief",    lambda: self.create_campaign_brief(campaign_id)),
            ("seo_report",   lambda: SEOAgent(self.db).generate_keyword_cluster(campaign_id)),
            ("linkedin",     lambda: ContentAgent(self.db).generate_linkedin(campaign_id)),
        ]:
            try:
                obj = fn()
                results[step] = str(obj.id)
            except Exception as e:
                errors[step] = str(e)

        # Blog from LinkedIn (depends on linkedin step)
        if "linkedin" in results:
            try:
                blog = ContentAgent(self.db).generate_blog_from_linkedin(results["linkedin"])
                results["blog"] = str(blog.id)
            except Exception as e:
                errors["blog"] = str(e)

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
    # Strategic Chat Interface
    # ─────────────────────────────────────────────
    def chat(self, message: str, context: dict = None) -> str:
        """
        Strategic Q&A — answers any marketing or sales question
        with full product + strategy knowledge.
        """
        system_prompt = f"""
You are the CMO for Triple I — an AI-powered ESG & Carbon Reporting B2B SaaS platform.
You have complete strategic knowledge of the product, market, and sales motion.

{get_master_context()}

Your communication style:
- Always think about Fear → Value → Pilot → Close
- Be direct and actionable — no vague advice
- Give concrete recommendations with specific copy examples
- Reference real ESRS/CSRD deadlines to justify urgency
- Always end recommendations with a specific next action

You can:
- Create campaign briefs with the Fast-Track Compliance Sprint as the centrepiece
- Recommend channel strategy per country cluster
- Draft copy hooks, CTAs, and outreach messages
- Define ICP qualification criteria for discovery calls
- Sequence content for maximum funnel velocity
- Explain how to position Triple I vs. spreadsheets or legacy ESG tools
        """.strip()

        context_note = ""
        if context:
            context_note = f"\n\nCurrent campaign context: {json.dumps(context)}"

        result = self._call_model_free(system_prompt, message + context_note)
        return result["content"]
