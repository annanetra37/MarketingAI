"""
research_agent.py
=================
Research Agent — market intelligence, competitor analysis, and regulatory briefings.

Focus: identify CSRD compliance gaps competitors leave open, regulatory deadlines
creating urgency NOW, and market opportunities Triple I can capture FAST in Europe.
"""

import json
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.agents.triple_i_context import (
    get_master_context, REGULATORY_URGENCY, MARKETS, COMPETITIVE_POSITIONING
)
from app.models.generated_content import GeneratedContent


class ResearchAgent(BaseAgent):
    """
    🔬 Research Agent
    Produces competitor intelligence and regulatory briefings that arm
    the CMO, Content, and Ads agents with market-winning insights.
    """

    AGENT_TYPE = "research"

    # ─────────────────────────────────────────────
    # Competitor Analysis
    # ─────────────────────────────────────────────
    def competitor_analysis(self, campaign_id) -> GeneratedContent:
        """
        Analyse the competitive ESG reporting software landscape in the target market.
        Identifies gaps Triple I can exploit, especially around:
        - CSRD/ESRS native support (most competitors bolt it on)
        - Framework interoperability (ESRS ↔ ISSB ↔ GRI)
        - Pilot/SME accessibility (most tools are enterprise-only)
        - Fast onboarding vs. long implementation projects
        """
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = f"""
You are the Market Research Agent for Triple I.

{get_master_context()}

Your research mission:
- Identify how competitors fail to serve the CSRD-urgency market
- Find the messaging whitespace Triple I can own
- Surface the objections buyers have about switching from spreadsheets or legacy tools
- Map the competitive landscape for ESG reporting software in {country.name}

Key competitive insight to explore:
- Most ESG platforms have CSRD support as an add-on, not native
- Most are built for large enterprises, not 250–1500 employee SMEs
- Most require IT involvement — Triple I doesn't
- Most lack the Fast-Track Pilot model — they sell long implementation projects
- Most lack true framework interoperability across ESRS + ISSB + GRI simultaneously
        """.strip()

        user_prompt = f"""
Produce a competitive intelligence report for Triple I in {country.name}.

Persona: {persona.name}
Framework focus: {campaign.framework_focus}
Country context: {country.notes}

Analyse the ESG reporting software competitive landscape including:
- Enterprise platforms (SAP Sustainability, IBM Envizi, Salesforce Net Zero Cloud)
- Mid-market ESG tools (Persefoni, Watershed, Sphera, Sweep, Plan A, Normative)
- Manual/spreadsheet approaches (current state for most CSRD-phase-2 companies)
- Local consultants and Big 4 advisory services

For each competitor type, identify:
- Their positioning and strengths
- Their CSRD/ESRS weaknesses
- The gap Triple I's Fast-Track Sprint and EcoHub™ fills
- The messaging angle Triple I should use to win against them

Also identify:
- Top 3 objections buyers have that Triple I's sales team must overcome
- The #1 fear-based message that makes buyers choose Triple I over waiting
- Recommended differentiator to lead with for {persona.name} in {country.name}
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "market_summary": {"type": "string"},
                "competitor_analysis": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name":                   {"type": "string"},
                            "category":               {"type": "string"},
                            "positioning":            {"type": "string"},
                            "csrd_weakness":          {"type": "string"},
                            "triple_i_advantage":     {"type": "string"},
                            "win_message":            {"type": "string"}
                        },
                        "required": ["name", "category", "positioning", "csrd_weakness",
                                     "triple_i_advantage", "win_message"],
                        "additionalProperties": False
                    }
                },
                "market_gaps":                 {"type": "array", "items": {"type": "string"}},
                "messaging_whitespace":         {"type": "array", "items": {"type": "string"}},
                "top_buyer_objections":         {"type": "array", "items": {"type": "string"}},
                "objection_handling":           {"type": "array", "items": {"type": "string"}},
                "primary_fear_message":         {"type": "string"},
                "recommended_differentiators":  {"type": "array", "items": {"type": "string"}},
                "pilot_positioning_advice":     {"type": "string"},
                "content_intelligence":         {"type": "string"}
            },
            "required": [
                "market_summary", "competitor_analysis", "market_gaps",
                "messaging_whitespace", "top_buyer_objections", "objection_handling",
                "primary_fear_message", "recommended_differentiators",
                "pilot_positioning_advice", "content_intelligence"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "competitor_analysis", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="research",
            headline=f"Competitor Analysis — {country.name} | {persona.name}",
            body=content["market_summary"],
            json_output=content,
            usage=result["usage"]
        )

    # ─────────────────────────────────────────────
    # CSRD Regulatory Briefing
    # ─────────────────────────────────────────────
    def regulatory_briefing(self, campaign_id) -> GeneratedContent:
        """
        Produce a regulatory intelligence briefing that arms the marketing
        team with country-specific CSRD urgency data and deadline details.
        Used to make all outreach and content hyper-relevant.
        """
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = f"""
You are the Regulatory Intelligence Agent for Triple I.
You have deep knowledge of: CSRD, ESRS E1–E5/S1–S4/G1, GRI, ISSB/IFRS S1&S2, TCFD, VSME, GHG Protocol, SBTi.

{REGULATORY_URGENCY}

Your job: produce briefings that make Triple I's marketing hyper-relevant and urgent.
Every briefing must identify the SPECIFIC deadlines and compliance risks that create
buyer urgency for {persona.name} in {country.name} RIGHT NOW.
        """.strip()

        user_prompt = f"""
Produce a regulatory intelligence briefing for Triple I's marketing team.

Target: {persona.name} in {country.name} (Cluster: {country.cluster})
Framework focus: {campaign.framework_focus}
Country context: {country.notes}

BRIEFING MUST COVER:
1. current_csrd_status: What's the CSRD compliance status in {country.name} right now?
2. immediate_deadlines: Which companies are reporting WHEN — specific FY and company size thresholds
3. most_urgent_disclosures: Which ESRS topics (E1, S1, etc.) are most pressing for {persona.name}?
4. penalty_risk: What are the non-compliance consequences? Be specific and scary.
5. regulator_profile: Who is the national regulator and what are they focusing on?
6. market_opportunity: How many companies in {country.name} are in CSRD scope NOW?
7. fear_triggers: 3 specific fear triggers for {persona.name} that Triple I's messaging should use
8. urgency_statements: 5 ready-to-use urgency statements for ads/content
9. pilot_relevance: How does the Fast-Track E1+S1 Sprint map to the most urgent disclosures?
10. recommended_messaging: The #1 message angle for this country/persona right now
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "current_csrd_status":     {"type": "string"},
                "immediate_deadlines":     {"type": "array", "items": {"type": "string"}},
                "most_urgent_disclosures": {"type": "array", "items": {"type": "string"}},
                "penalty_risk":            {"type": "string"},
                "regulator_profile":       {"type": "string"},
                "market_opportunity":      {"type": "string"},
                "fear_triggers":           {"type": "array", "items": {"type": "string"}},
                "urgency_statements":      {"type": "array", "items": {"type": "string"}},
                "pilot_relevance":         {"type": "string"},
                "recommended_messaging":   {"type": "string"}
            },
            "required": [
                "current_csrd_status", "immediate_deadlines", "most_urgent_disclosures",
                "penalty_risk", "regulator_profile", "market_opportunity",
                "fear_triggers", "urgency_statements", "pilot_relevance", "recommended_messaging"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "regulatory_briefing", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="regulatory_briefing",
            headline=f"Regulatory Briefing — {country.name} | CSRD/ESRS {campaign.framework_focus}",
            body=content["current_csrd_status"],
            json_output=content,
            usage=result["usage"]
        )
