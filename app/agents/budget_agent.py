import json
from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent


class BudgetAgent(BaseAgent):
    """
    💰 Budget Optimization Agent
    Moves budget to high-performing channels, pauses underperformers,
    forecasts ROI, and feeds reallocation decisions to the Orchestrator.
    """

    AGENT_TYPE = "budget"

    def optimize_budget(self, campaign_id: str) -> GeneratedContent:
        """
        Analyze performance signals and produce a budget reallocation plan.
        Integrates with the Analytics Agent output.
        """
        campaign, persona, country = self.build_context(campaign_id)

        # Fetch latest analytics report for context
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

        system_prompt = """
You are the Budget Optimization Agent for Triple I's autonomous marketing system.

You think like a performance marketing CFO:
- Every euro/dollar must earn its keep
- Scale what's working, ruthlessly cut what isn't
- Never let budget sit idle when ROI signals are clear
- Think in 7-day and 30-day optimization windows
- Always tie budget decisions to pipeline and revenue impact

You output a precise, actionable budget reallocation plan.
        """.strip()

        user_prompt = f"""
Generate a budget optimization plan for:

Campaign: {campaign.name}
Goal: {campaign.goal}
Channel: {campaign.channel}
Persona: {persona.name}
Country: {country.name} (Cluster: {country.cluster})
Latest Analytics Signals: {json.dumps(analytics_context)}

Produce:
1. current_allocation: simulated current budget breakdown by channel
2. recommended_allocation: exact new allocation with % shifts
3. channels_to_scale: which to increase and by how much
4. channels_to_pause: which to pause/cut and why
5. roi_forecast_7d: 7-day projected ROI after reallocation
6. roi_forecast_30d: 30-day projected ROI
7. budget_moves: array of specific moves (move X budget from A to B because Y)
8. total_budget_efficiency_gain: estimated % improvement
9. risk_flags: what could go wrong with this reallocation
10. auto_rules: automated bidding/budget rules to implement
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "current_allocation": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "channel": {"type": "string"},
                            "current_pct": {"type": "number"},
                            "performance": {"type": "string"}
                        },
                        "required": ["channel", "current_pct", "performance"],
                        "additionalProperties": False
                    }
                },
                "recommended_allocation": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "channel": {"type": "string"},
                            "recommended_pct": {"type": "number"},
                            "change": {"type": "string"},
                            "rationale": {"type": "string"}
                        },
                        "required": ["channel", "recommended_pct", "change", "rationale"],
                        "additionalProperties": False
                    }
                },
                "channels_to_scale": {"type": "array", "items": {"type": "string"}},
                "channels_to_pause": {"type": "array", "items": {"type": "string"}},
                "roi_forecast_7d": {"type": "string"},
                "roi_forecast_30d": {"type": "string"},
                "budget_moves": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"},
                            "from_channel": {"type": "string"},
                            "to_channel": {"type": "string"},
                            "amount_pct": {"type": "number"},
                            "reasoning": {"type": "string"}
                        },
                        "required": ["action", "from_channel", "to_channel", "amount_pct", "reasoning"],
                        "additionalProperties": False
                    }
                },
                "total_budget_efficiency_gain": {"type": "string"},
                "risk_flags": {"type": "array", "items": {"type": "string"}},
                "auto_rules": {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "current_allocation", "recommended_allocation", "channels_to_scale",
                "channels_to_pause", "roi_forecast_7d", "roi_forecast_30d",
                "budget_moves", "total_budget_efficiency_gain", "risk_flags", "auto_rules"
            ],
            "additionalProperties": False
        }

        result = self._call_model(system_prompt, user_prompt, "budget_optimization", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="budget_optimization",
            headline=f"Budget Optimization: +{content['total_budget_efficiency_gain']} efficiency",
            body=f"Scale: {', '.join(content['channels_to_scale'])} | Pause: {', '.join(content['channels_to_pause'])}",
            json_output=content,
            usage=result["usage"]
        )
