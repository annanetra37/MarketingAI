"""
distribution_agent.py
=====================
Distribution Agent — deploys content across channels in a sequence designed
to drive the 5-step Fast-Track Sales Motion within 6 weeks.

Distribution is NOT just scheduling — it's the operationalisation of the
Fear → Assessment → Demo → Pilot → Close funnel.
"""

import json
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.agents.triple_i_context import (
    get_master_context, get_cta_library, SALES_STRATEGY
)
from app.models.generated_content import GeneratedContent


class DistributionAgent(BaseAgent):
    """
    📣 Distribution Agent
    Plans and sequences content deployment to maximise funnel velocity
    and achieve demo/pilot conversions within 6 weeks.
    """

    AGENT_TYPE = "distribution"

    def create_distribution_plan(self, campaign_id) -> GeneratedContent:
        """
        Create a distribution and deployment plan that operationalises the
        6-week sales cycle:
        - Week 1–2: Outreach + Fear-hook content → ESRS Assessment CTA
        - Week 3–4: Discovery + Demo content → pilot proposal
        - Week 5–6: Close content + case study / ROI proof → convert
        """
        campaign, persona, country = self.build_context(campaign_id)

        # Fetch recently generated content for context
        recent_content = (
            self.db.query(GeneratedContent)
            .filter(GeneratedContent.campaign_id == campaign_id)
            .order_by(GeneratedContent.created_at.desc())
            .limit(10)
            .all()
        )
        content_inventory = [
            {"type": c.type, "headline": c.headline}
            for c in recent_content
            if c.type in ("linkedin", "blog", "twitter", "google_ads", "linkedin_ads")
        ]

        system_prompt = f"""
You are the Distribution Agent for Triple I's autonomous marketing system.

{get_master_context()}

DISTRIBUTION PHILOSOPHY:
The goal is NOT to post content randomly. The goal is to move {persona.name}
in {country.name} through the 5-step sales motion in under 6 weeks:

Step 1 — Outreach: CSRD fear-hook content → drives to ESRS Readiness Assessment
Step 2 — Discovery: Educational content → nurtures into 30-min discovery call
Step 3 — Demo: Proof content (EcoHub™, Cambridge, 80–90% savings) → 45-min demo
Step 4 — Proposal: Fast-Track Sprint offer → pilot proposal (€5K–€15K, E1+S1, 6 weeks)
Step 5 — Close: Urgency amplifiers → convert to paid pilot

Distribution must:
- Sequence content to match buyer journey stage
- Identify the BEST posting times for {country.name} (timezone, working patterns)
- Align email nurture with social content — tell a coherent story
- Use LinkedIn for B2B reach; Google for intent capture; Email for nurture
- Every piece drives toward one urgent CTA

{SALES_STRATEGY}
        """.strip()

        user_prompt = f"""
Create a 6-week distribution and deployment plan for Triple I.

Campaign: {campaign.name}
Persona: {persona.name}
Country: {country.name} (Cluster: {country.cluster})
Channel: {campaign.channel}
Goal: {campaign.goal}
Country context: {country.notes}

Content inventory available: {json.dumps(content_inventory)}

PLAN MUST INCLUDE:
1. weekly_schedule: Day-by-day posting schedule for 6 weeks (map content type to sales step)
2. channel_tactics: Platform-specific tactics for LinkedIn, Google, and/or Email
3. posting_times: Optimal times for {country.name} audience (include timezone)
4. content_sequence: How content pieces build on each other to progress the buyer
5. email_flow: 5-email nurture sequence from ESRS Assessment download to pilot proposal
   - Email 1: Assessment results + fear amplifier (Day 0)
   - Email 2: How Triple I solves the gap (Day 3)
   - Email 3: Social proof — Cambridge, award, case reference (Day 7)
   - Email 4: Fast-Track Sprint offer — scoped, priced (Day 14)
   - Email 5: Urgency close — deadline reminder + pilot CTA (Day 21)
6. amplification_tactics: How to boost reach without extra spend (employee advocacy, reposting, etc.)
7. sales_enablement: What the sales team should be doing in parallel with each content week
8. six_week_milestones: Expected outcomes at end of each 2-week block
9. distribution_kpis: 5 measurable KPIs for this distribution plan
10. quick_wins: 3 things to do TODAY for immediate traction in {country.name}
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "weekly_schedule": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "week":          {"type": "integer"},
                            "sales_step":    {"type": "string"},
                            "daily_actions": {"type": "array", "items": {"type": "string"}},
                            "primary_cta":   {"type": "string"},
                            "goal":          {"type": "string"}
                        },
                        "required": ["week", "sales_step", "daily_actions", "primary_cta", "goal"],
                        "additionalProperties": False
                    }
                },
                "channel_tactics": {
                    "type": "object",
                    "properties": {
                        "linkedin": {"type": "string"},
                        "google":   {"type": "string"},
                        "email":    {"type": "string"}
                    },
                    "required": ["linkedin", "google", "email"],
                    "additionalProperties": False
                },
                "posting_times": {"type": "string"},
                "content_sequence": {"type": "array", "items": {"type": "string"}},
                "email_flow": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "email_number": {"type": "integer"},
                            "trigger":      {"type": "string"},
                            "subject":      {"type": "string"},
                            "preview_text": {"type": "string"},
                            "goal":         {"type": "string"},
                            "send_timing":  {"type": "string"},
                            "cta":          {"type": "string"}
                        },
                        "required": ["email_number", "trigger", "subject", "preview_text",
                                     "goal", "send_timing", "cta"],
                        "additionalProperties": False
                    }
                },
                "amplification_tactics":  {"type": "array", "items": {"type": "string"}},
                "sales_enablement":       {"type": "array", "items": {"type": "string"}},
                "six_week_milestones":    {"type": "array", "items": {"type": "string"}},
                "distribution_kpis":      {"type": "array", "items": {"type": "string"}},
                "quick_wins":             {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "weekly_schedule", "channel_tactics", "posting_times",
                "content_sequence", "email_flow", "amplification_tactics",
                "sales_enablement", "six_week_milestones", "distribution_kpis", "quick_wins"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "distribution_plan", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="distribution_plan",
            headline=f"6-Week Distribution Plan: {campaign.name}",
            body=f"Quick wins: {'; '.join(content['quick_wins'][:2])}",
            json_output=content,
            usage=result["usage"]
        )
