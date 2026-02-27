import json
from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent
from app.models.campaign import Campaign


class AnalyticsAgent(BaseAgent):
    """
    📊 Analytics Agent — the feedback loop engine.
    Tracks KPIs, detects anomalies, runs A/B test analysis,
    generates performance insights and feeds them back to the Orchestrator.
    """

    AGENT_TYPE = "analytics"

    def analyze_campaign_performance(self, campaign_id: str) -> GeneratedContent:
        """
        Simulate & analyze campaign performance.
        In production, connects to real ad/analytics APIs.
        Returns structured performance report with recommendations.
        """
        campaign, persona, country = self.build_context(campaign_id)

        # Gather all content generated for this campaign
        content_records = (
            self.db.query(GeneratedContent)
            .filter(GeneratedContent.campaign_id == campaign_id)
            .all()
        )

        content_summary = [
            {"type": r.type, "status": r.status, "agent": r.agent_type}
            for r in content_records
        ]

        system_prompt = """
You are the Analytics Agent for Triple I — an AI-powered ESG & Carbon Reporting B2B SaaS.

You are the feedback loop engine. You:
- Analyze campaign performance data (real or simulated)
- Detect what's working and what isn't
- Run A/B test analysis across content variants
- Surface anomalies and opportunities
- Generate actionable recommendations for the CMO Orchestrator
- Score campaigns 1-10 on performance

Your output drives the autonomous improvement loop. Be specific, data-driven, and ruthlessly honest.
        """.strip()

        user_prompt = f"""
Analyze the marketing campaign performance for Triple I:

Campaign: {campaign.name}
Goal: {campaign.goal}
Persona: {persona.name}
Country: {country.name} (Cluster: {country.cluster})
Framework Focus: {campaign.framework_focus}
Channel: {campaign.channel}
Content Generated: {json.dumps(content_summary)}
Campaign Status: {campaign.status}

Generate a comprehensive performance analysis with:
1. performance_score: integer 1-10
2. kpi_analysis: array of KPIs with current_value, target, status (on_track/behind/ahead), trend
3. top_performing: what's working best (content type, angle, channel)
4. underperforming: what's falling short with specific reasons
5. anomalies: array of detected anomalies or unexpected patterns
6. ab_test_winner: if multiple variants, which won and why
7. audience_insights: what this data tells us about the target persona
8. channel_efficiency: ROAS/CAC estimates per channel
9. recommendations: array of 5 specific, prioritized actions for the orchestrator
10. budget_signal: "scale" | "maintain" | "reduce" | "pause" with reasoning
11. next_loop_focus: what the next autonomous cycle should prioritize
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "performance_score": {"type": "integer"},
                "kpi_analysis": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "metric": {"type": "string"},
                            "current_value": {"type": "string"},
                            "target": {"type": "string"},
                            "status": {"type": "string"},
                            "trend": {"type": "string"}
                        },
                        "required": ["metric", "current_value", "target", "status", "trend"],
                        "additionalProperties": False
                    }
                },
                "top_performing": {"type": "string"},
                "underperforming": {"type": "string"},
                "anomalies": {"type": "array", "items": {"type": "string"}},
                "ab_test_winner": {"type": "string"},
                "audience_insights": {"type": "string"},
                "channel_efficiency": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "best_channel": {"type": "string"},
                        "estimated_cac": {"type": "string"},
                        "estimated_roas": {"type": "string"}
                    },
                    "required": ["summary", "best_channel", "estimated_cac", "estimated_roas"],
                    "additionalProperties": False
                },
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "priority": {"type": "string"},
                            "action": {"type": "string"},
                            "expected_impact": {"type": "string"},
                            "agent": {"type": "string"}
                        },
                        "required": ["priority", "action", "expected_impact", "agent"],
                        "additionalProperties": False
                    }
                },
                "budget_signal": {"type": "string"},
                "budget_reasoning": {"type": "string"},
                "next_loop_focus": {"type": "string"}
            },
            "required": [
                "performance_score", "kpi_analysis", "top_performing", "underperforming",
                "anomalies", "ab_test_winner", "audience_insights", "channel_efficiency",
                "recommendations", "budget_signal", "budget_reasoning", "next_loop_focus"
            ],
            "additionalProperties": False
        }

        result = self._call_model(system_prompt, user_prompt, "analytics_report", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="analytics_report",
            headline=f"Analytics Report: {campaign.name} — Score {content['performance_score']}/10",
            body=content["next_loop_focus"],
            json_output=content,
            usage=result["usage"]
        )

    def run_ab_test_analysis(self, campaign_id: str) -> GeneratedContent:
        """
        Analyze A/B test results across all ad variants for a campaign.
        Identifies statistical winners and recommends which to scale.
        """
        campaign, persona, country = self.build_context(campaign_id)

        # Fetch ad content for comparison
        ads = (
            self.db.query(GeneratedContent)
            .filter(
                GeneratedContent.campaign_id == campaign_id,
                GeneratedContent.type.in_(["google_ads", "linkedin_ads"])
            )
            .all()
        )

        ads_summary = [{"id": str(a.id), "type": a.type, "headline": a.headline} for a in ads]

        system_prompt = """
You are the A/B Testing Analyst for Triple I's autonomous marketing system.
You determine which ad variants win, why they win, and prescribe exactly how to scale winners
and kill losers. Your analysis feeds directly into the Budget Optimization Agent.
        """.strip()

        user_prompt = f"""
Run A/B test analysis for:
Campaign: {campaign.name}
Channel: {campaign.channel}
Persona: {persona.name}
Country: {country.name}
Ad Assets: {json.dumps(ads_summary)}

Provide:
1. variant_results: simulated CTR/CVR for each variant
2. statistical_winner: which variant won
3. winning_factors: exactly WHY it won (copy angle, CTA, emotional trigger)
4. losing_factors: why others underperformed
5. scale_recommendation: how much budget to shift to winner
6. new_hypothesis: next variant to test based on learnings
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "variant_results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "variant": {"type": "string"},
                            "simulated_ctr": {"type": "string"},
                            "simulated_cvr": {"type": "string"},
                            "score": {"type": "integer"}
                        },
                        "required": ["variant", "simulated_ctr", "simulated_cvr", "score"],
                        "additionalProperties": False
                    }
                },
                "statistical_winner": {"type": "string"},
                "winning_factors": {"type": "array", "items": {"type": "string"}},
                "losing_factors": {"type": "array", "items": {"type": "string"}},
                "scale_recommendation": {"type": "string"},
                "new_hypothesis": {"type": "string"}
            },
            "required": [
                "variant_results", "statistical_winner", "winning_factors",
                "losing_factors", "scale_recommendation", "new_hypothesis"
            ],
            "additionalProperties": False
        }

        result = self._call_model(system_prompt, user_prompt, "ab_test_analysis", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="ab_test_analysis",
            headline=f"A/B Analysis: Winner → {content['statistical_winner']}",
            body=content["scale_recommendation"],
            json_output=content,
            usage=result["usage"]
        )
