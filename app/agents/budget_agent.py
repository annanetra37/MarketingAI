"""
budget_agent.py
===============
Budget Agent — optimises spend to maximise pilot conversions within the
6-week sales cycle and available runway.

Budget philosophy: every euro must either:
a) Drive an ESRS Readiness Assessment completion (ToFu)
b) Accelerate a discovery call booking (MoFu)
c) Close a Fast-Track Compliance Sprint pilot (BoFu at €5K–€15K)

Ruthlessly kill everything else.
"""

import json
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.agents.triple_i_context import get_master_context, SALES_STRATEGY, MARKETS
from app.models.generated_content import GeneratedContent


class BudgetAgent(BaseAgent):
    """
    💰 Budget Agent
    Allocates and reallocates marketing budget to maximise pilot conversions
    in Cluster A European markets within the 6-week sales cycle.
    """

    AGENT_TYPE = "budget"

    def optimize_budget(self, campaign_id) -> GeneratedContent:
        """
        Analyse performance signals and produce a budget allocation plan.
        Ties every spend decision to cost-per-pilot-lead and pilot pipeline value.
        """
        campaign, persona, country = self.build_context(campaign_id)

        # Fetch latest analytics for context
        analytics = (
            self.db.query(GeneratedContent)
            .filter(
                GeneratedContent.campaign_id == campaign_id,
                GeneratedContent.type == "analytics_report"
            )
            .order_by(GeneratedContent.created_at.desc())
            .first()
        )
        analytics_context = analytics.json_output if analytics else {}

        system_prompt = f"""
You are the Budget Optimisation Agent for Triple I's marketing system.

{get_master_context()}

BUDGET PHILOSOPHY:
Triple I is at MVP stage with finite runway. Every euro must earn its keep.
The only metrics that matter for budget decisions:
1. Cost-per-ESRS-Assessment-completion (target: <€50)
2. Cost-per-discovery-call-booked (target: <€200)
3. Cost-per-pilot-signed (target: <€1,000 — pilot value is €5K–€15K)
4. Days-to-first-pilot from campaign launch (target: <42 days / 6 weeks)

Budget allocation principles:
- Cluster A (Spain, France, Netherlands, Belgium, Sweden) gets 80% of budget
- LinkedIn gets primary budget for SME/Advisory targeting
- Google gets budget only for high-intent CSRD search terms
- Never run awareness-only campaigns — all spend must funnel to assessments or demos
- Pause any channel where cost-per-assessment exceeds €100 for 7+ days
- Scale immediately when cost-per-pilot-lead is below €500

Fast-Track Sprint pilot economics:
- Pilot price: €5K–€15K
- Platform cost to serve a pilot: minimal (SaaS delivery)
- Target: 3–5 pilot closings in first 90 days to prove model
- Conversion path: Spend → Assessment → Discovery → Demo → Pilot Proposal → Close

{SALES_STRATEGY}
        """.strip()

        user_prompt = f"""
Create a budget optimisation plan for Triple I campaign: {campaign.name}
Country: {country.name} (Cluster: {country.cluster}) | Persona: {persona.name}

Latest analytics data: {json.dumps(analytics_context)[:2000] if analytics_context else 'Initial run — no analytics data yet'}

PROVIDE:
1. current_allocation: Assessment of current spend distribution by channel
2. recommended_allocation: Optimal distribution with rationale (must sum to 100%)
3. pilot_economics: Cost-per-pilot projections at different budget levels
4. cluster_a_allocation: How to split Cluster A budget across Spain/France/Netherlands/Belgium/Sweden
5. channels_to_scale: Which channels to invest more in and why
6. channels_to_pause: Which to pause and why
7. esrs_assessment_budget: How much to spend on driving ESRS Assessment completions
8. sprint_pilot_budget: How much to spend on direct Fast-Track Sprint promotion
9. roi_forecast_30d: Projected pipeline value in 30 days at recommended spend
10. roi_forecast_90d: Projected pilots closed and revenue in 90 days
11. budget_moves: Specific reallocation actions with amounts
12. auto_rules: Automated budget rules to implement (pause if X, scale if Y)
13. risk_flags: Spend risks to watch
14. minimum_viable_budget: Minimum monthly spend to achieve first pilot in 6 weeks
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "current_allocation": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "channel":         {"type": "string"},
                            "current_pct":     {"type": "number"},
                            "performance":     {"type": "string"},
                            "cost_per_lead":   {"type": "string"}
                        },
                        "required": ["channel", "current_pct", "performance", "cost_per_lead"],
                        "additionalProperties": False
                    }
                },
                "recommended_allocation": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "channel":          {"type": "string"},
                            "recommended_pct":  {"type": "number"},
                            "change":           {"type": "string"},
                            "rationale":        {"type": "string"}
                        },
                        "required": ["channel", "recommended_pct", "change", "rationale"],
                        "additionalProperties": False
                    }
                },
                "pilot_economics":             {"type": "string"},
                "cluster_a_allocation":        {"type": "string"},
                "channels_to_scale":           {"type": "array", "items": {"type": "string"}},
                "channels_to_pause":           {"type": "array", "items": {"type": "string"}},
                "esrs_assessment_budget":      {"type": "string"},
                "sprint_pilot_budget":         {"type": "string"},
                "roi_forecast_30d":            {"type": "string"},
                "roi_forecast_90d":            {"type": "string"},
                "budget_moves": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action":        {"type": "string"},
                            "from_channel":  {"type": "string"},
                            "to_channel":    {"type": "string"},
                            "amount_pct":    {"type": "number"},
                            "reasoning":     {"type": "string"}
                        },
                        "required": ["action", "from_channel", "to_channel", "amount_pct", "reasoning"],
                        "additionalProperties": False
                    }
                },
                "auto_rules":                  {"type": "array", "items": {"type": "string"}},
                "risk_flags":                  {"type": "array", "items": {"type": "string"}},
                "minimum_viable_budget":       {"type": "string"},
                "total_budget_efficiency_gain":{"type": "string"}
            },
            "required": [
                "current_allocation", "recommended_allocation", "pilot_economics",
                "cluster_a_allocation", "channels_to_scale", "channels_to_pause",
                "esrs_assessment_budget", "sprint_pilot_budget",
                "roi_forecast_30d", "roi_forecast_90d", "budget_moves",
                "auto_rules", "risk_flags", "minimum_viable_budget",
                "total_budget_efficiency_gain"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "budget_optimization", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="budget_optimization",
            headline=f"Budget Plan: {content['total_budget_efficiency_gain']} efficiency gain — {campaign.name}",
            body=f"Scale: {', '.join(content['channels_to_scale'])} | Pause: {', '.join(content['channels_to_pause'])} | 90d forecast: {content['roi_forecast_90d']}",
            json_output=content,
            usage=result["usage"]
        )
