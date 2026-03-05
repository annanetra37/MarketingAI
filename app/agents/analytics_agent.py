"""
analytics_agent.py
==================
Analytics Agent — measures what matters for Triple I's fast-growth sales motion.

Core KPIs tracked:
- ESRS Readiness Assessment completions (ToFu)
- Discovery calls booked (MoFu)
- Fast-Track Sprint pilots signed (BoFu)
- Cost-per-pilot-lead by channel and country
- Content performance by funnel stage
"""

import json
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.agents.triple_i_context import get_master_context, SALES_STRATEGY
from app.models.generated_content import GeneratedContent


class AnalyticsAgent(BaseAgent):
    """
    📊 Analytics Agent
    Tracks funnel performance, A/B test results, and generates actionable
    insights to accelerate the 6-week sales cycle.
    """

    AGENT_TYPE = "analytics"

    def analyze_performance(self, campaign_id) -> GeneratedContent:
        """
        Analyse campaign performance against the Fear → Assessment → Sprint funnel.
        Identifies which content, channels, and messages are converting fastest.
        """
        campaign, persona, country = self.build_context(campaign_id)

        # Pull all generated content for this campaign
        all_content = (
            self.db.query(GeneratedContent)
            .filter(GeneratedContent.campaign_id == campaign_id)
            .order_by(GeneratedContent.created_at.desc())
            .all()
        )

        content_summary = [
            {
                "type":     c.type,
                "headline": c.headline,
                "status":   c.status,
                "created":  str(c.created_at)[:10]
            }
            for c in all_content
        ]

        system_prompt = f"""
You are the Analytics Agent for Triple I's autonomous marketing system.

{get_master_context()}

ANALYTICS FRAMEWORK:
Triple I's success metric is SPEED TO PILOT SIGNED within 6 weeks.
Every metric must map back to funnel velocity:

Funnel stage metrics:
1. FEAR STAGE (Awareness):
   - LinkedIn post impressions / engagement rate
   - Blog organic traffic / time-on-page
   - Google Ads CTR / Quality Score
   - Targets: LinkedIn engagement >3%, Blog CTR from search >2%, Ads CTR >5%

2. ASSESSMENT STAGE (Lead Gen):
   - ESRS Readiness Assessment completions
   - Email opt-in rate from content
   - Discovery call booking rate from assessment
   - Target: >15% of assessment completers book a discovery call

3. SPRINT STAGE (Conversion):
   - Discovery → Demo conversion rate
   - Demo → Pilot Proposal rate
   - Proposal → Pilot Signed rate (target: >30%)
   - Average deal velocity (target: <6 weeks)
   - Pilot price achieved (target: €5K–€15K)

4. CONTENT EFFICIENCY:
   - Cost per pilot lead by channel
   - Content pieces that drive most assessment completions
   - Which fear hooks get highest engagement

Anomaly detection priorities:
- If any Cluster A country has <2% LinkedIn engagement — flag immediately
- If discovery-to-demo rate drops below 50% — review qualification criteria
- If pilot proposal acceptance is below 30% — review pricing/scoping
        """.strip()

        user_prompt = f"""
Analyse the marketing performance for Triple I campaign: {campaign.name}

Persona: {persona.name}
Country: {country.name} (Cluster: {country.cluster})

Content generated so far:
{json.dumps(content_summary, indent=2)}

Provide a comprehensive performance analysis including:
1. funnel_health: assessment of each stage (fear/assessment/sprint) — green/amber/red
2. performance_score: overall campaign score /10 with rationale
3. top_performing_content: which content types/messages show strongest signals
4. underperforming_areas: what's not working and why
5. anomalies: anything unexpected that needs immediate attention
6. six_week_pipeline_forecast: estimated outcomes by end of week 6
7. channel_breakdown: performance by LinkedIn / Google / Email
8. fear_hook_effectiveness: are the CSRD urgency messages driving engagement?
9. pilot_conversion_forecast: likelihood of achieving paid pilot sign in 6 weeks
10. immediate_actions: 3 specific actions to take THIS WEEK to accelerate results
11. content_recommendations: what to generate next based on gaps
12. kpi_scorecard: array of KPIs with current value, target, and status
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "funnel_health": {
                    "type": "object",
                    "properties": {
                        "fear_stage":       {"type": "string"},
                        "assessment_stage": {"type": "string"},
                        "sprint_stage":     {"type": "string"}
                    },
                    "required": ["fear_stage", "assessment_stage", "sprint_stage"],
                    "additionalProperties": False
                },
                "performance_score":            {"type": "integer"},
                "performance_rationale":        {"type": "string"},
                "top_performing_content":       {"type": "array", "items": {"type": "string"}},
                "underperforming_areas":        {"type": "array", "items": {"type": "string"}},
                "anomalies":                    {"type": "array", "items": {"type": "string"}},
                "six_week_pipeline_forecast":   {"type": "string"},
                "channel_breakdown":            {"type": "array", "items": {"type": "string"}},
                "fear_hook_effectiveness":      {"type": "string"},
                "pilot_conversion_forecast":    {"type": "string"},
                "immediate_actions":            {"type": "array", "items": {"type": "string"}},
                "content_recommendations":      {"type": "array", "items": {"type": "string"}},
                "kpi_scorecard": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "kpi":     {"type": "string"},
                            "current": {"type": "string"},
                            "target":  {"type": "string"},
                            "status":  {"type": "string"}
                        },
                        "required": ["kpi", "current", "target", "status"],
                        "additionalProperties": False
                    }
                }
            },
            "required": [
                "funnel_health", "performance_score", "performance_rationale",
                "top_performing_content", "underperforming_areas", "anomalies",
                "six_week_pipeline_forecast", "channel_breakdown",
                "fear_hook_effectiveness", "pilot_conversion_forecast",
                "immediate_actions", "content_recommendations", "kpi_scorecard"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "performance_analysis", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="analytics_report",
            headline=f"Performance Analysis — {campaign.name} (Score: {content['performance_score']}/10)",
            body=content["performance_rationale"],
            json_output=content,
            usage=result["usage"]
        )

    def analyze_ab_test(self, campaign_id) -> GeneratedContent:
        """
        Analyse A/B test results across content variants and ad creatives.
        Determines which fear hooks, CTAs, and angles drive fastest pipeline.
        """
        campaign, persona, country = self.build_context(campaign_id)

        all_ads = (
            self.db.query(GeneratedContent)
            .filter(
                GeneratedContent.campaign_id == campaign_id,
                GeneratedContent.type.in_(["google_ads", "linkedin_ads"])
            )
            .order_by(GeneratedContent.created_at.desc())
            .first()
        )

        ads_context = all_ads.json_output if all_ads else {}

        system_prompt = f"""
You are the A/B Test Analysis Agent for Triple I.

{get_master_context()}

A/B testing priorities for Triple I:
- Test which fear hook drives highest ESRS Assessment completion
- Test ESRS Readiness Assessment CTA vs. Fast-Track Sprint CTA — which converts faster?
- Test fear angle vs. speed angle vs. cost angle in Google Ads
- Test urgency copy (deadline-driven) vs. outcome copy (results-driven) in LinkedIn
- Winner = highest PILOT CONVERSION RATE, not just CTR
        """.strip()

        user_prompt = f"""
Analyse A/B test results for Triple I campaign: {campaign.name}
Country: {country.name} | Persona: {persona.name}

Ad variants context: {json.dumps(ads_context)[:2000] if ads_context else 'No ad data yet'}

Provide A/B test analysis:
1. winner: which variant is winning and why
2. winning_angle: fear/speed/cost/proof — which message angle wins for this audience
3. winning_cta: ESRS Assessment OR Fast-Track Sprint — which CTA converts better
4. statistical_significance: confidence level in the winner
5. loser_analysis: why the losing variants underperformed
6. insights: 3 strategic insights from these test results
7. next_test_recommendations: 2 follow-up tests to run next
8. scale_recommendation: should we scale the winner? How much budget increase?
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "winner":                     {"type": "string"},
                "winning_angle":              {"type": "string"},
                "winning_cta":                {"type": "string"},
                "statistical_significance":   {"type": "string"},
                "loser_analysis":             {"type": "string"},
                "insights":                   {"type": "array", "items": {"type": "string"}},
                "next_test_recommendations":  {"type": "array", "items": {"type": "string"}},
                "scale_recommendation":       {"type": "string"}
            },
            "required": [
                "winner", "winning_angle", "winning_cta", "statistical_significance",
                "loser_analysis", "insights", "next_test_recommendations", "scale_recommendation"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "ab_test_analysis", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="ab_test_analysis",
            headline=f"A/B Test Winner: {content['winning_angle']} angle — {campaign.name}",
            body=f"Winner: {content['winner']} | CTA: {content['winning_cta']} | {content['scale_recommendation']}",
            json_output=content,
            usage=result["usage"]
        )
