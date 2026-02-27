from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent


class ResearchAgent(BaseAgent):
    """
    Market intelligence agent for Triple I.
    Analyzes competitors, regulatory landscape, and content opportunities.
    Note: Web search integration is architecture-ready — currently uses LLM knowledge.
    To enable live web search, inject a search_fn callable.
    """

    AGENT_TYPE = "research"

    def __init__(self, db, search_fn=None):
        super().__init__(db)
        self.search_fn = search_fn  # Optional: pass a web search function

    # ─────────────────────────────────────────────
    # Competitor Content Analysis
    # ─────────────────────────────────────────────
    def analyze_competitors(self, campaign_id) -> GeneratedContent:
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = f"""
You are the Research Agent for Triple I — ESG & Carbon Reporting platform.

Your job: analyze the competitive landscape for Triple I in {country.name},
focusing on the {persona.name} segment and {campaign.framework_focus} framework positioning.

Known competitors in ESG/CSRD space:
- Watershed, Persefoni, Sweep, Greenly (carbon accounting)
- Workiva, Enablon (ESG reporting platforms)
- Salesforce Net Zero Cloud
- Specialised CSRD tools from big4 accounting firms
- Manual consulting approaches

Analyze honestly. Triple I's edge: Framework Interoperability + SME/Advisory focus.
        """.strip()

        user_prompt = f"""
Produce a competitive intelligence report for Triple I in {country.name}.

Focus: {persona.name} segment | Framework: {campaign.framework_focus}

Return JSON with:
- market_summary: overview of the ESG software market in {country.name} (3-4 sentences)
- competitor_analysis: array of 5 competitors, each with:
  {{name, positioning, strengths (array), weaknesses (array), triple_i_advantage (how Triple I wins vs them)}}
- market_gaps: array of 4 underserved opportunities Triple I can own
- messaging_whitespace: topics/angles competitors are NOT covering (Triple I can dominate)
- threat_assessment: biggest competitive threats and mitigation strategy
- content_intelligence: what content is performing well in this space (based on your knowledge)
- recommended_differentiators: 3 key messages Triple I should hammer to stand out
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
                            "name":               {"type": "string"},
                            "positioning":        {"type": "string"},
                            "strengths":          {"type": "array", "items": {"type": "string"}},
                            "weaknesses":         {"type": "array", "items": {"type": "string"}},
                            "triple_i_advantage": {"type": "string"}
                        },
                        "required": ["name", "positioning", "strengths", "weaknesses", "triple_i_advantage"],
                        "additionalProperties": False
                    }
                },
                "market_gaps":              {"type": "array", "items": {"type": "string"}},
                "messaging_whitespace":     {"type": "array", "items": {"type": "string"}},
                "threat_assessment":        {"type": "string"},
                "content_intelligence":     {"type": "string"},
                "recommended_differentiators": {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "market_summary", "competitor_analysis", "market_gaps",
                "messaging_whitespace", "threat_assessment",
                "content_intelligence", "recommended_differentiators"
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
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = """
You are the Regulatory Intelligence Agent for Triple I.
You have deep knowledge of ESG reporting regulations: CSRD, ESRS, GRI, ISSB/IFRS S1&S2, TCFD.
Your job: produce actionable regulatory briefings that help Triple I's marketing team
understand the regulatory pressure driving demand in each market.
        """.strip()

        user_prompt = f"""
Produce a regulatory intelligence briefing for Triple I's marketing team.

Country: {country.name} | Cluster: {country.cluster}
Persona: {persona.name}
Framework Focus: {campaign.framework_focus}

Return JSON with:
- regulatory_snapshot: current state of ESG/CSRD regulation in {country.name}
- key_deadlines: array of upcoming reporting deadlines with {{deadline, regulation, who_affected, urgency_level}}
- compliance_pain_points: top 5 pain points companies face with current regulations
- framework_requirements: what {campaign.framework_focus} specifically requires in {country.name}
- marketing_hooks: 5 regulatory-driven urgency messages Triple I can use in campaigns
- content_calendar_triggers: regulatory events/dates that should trigger content publishing
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "regulatory_snapshot": {"type": "string"},
                "key_deadlines": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "deadline":       {"type": "string"},
                            "regulation":     {"type": "string"},
                            "who_affected":   {"type": "string"},
                            "urgency_level":  {"type": "string"}
                        },
                        "required": ["deadline", "regulation", "who_affected", "urgency_level"],
                        "additionalProperties": False
                    }
                },
                "compliance_pain_points":       {"type": "array", "items": {"type": "string"}},
                "framework_requirements":       {"type": "string"},
                "marketing_hooks":              {"type": "array", "items": {"type": "string"}},
                "content_calendar_triggers":    {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "regulatory_snapshot", "key_deadlines", "compliance_pain_points",
                "framework_requirements", "marketing_hooks", "content_calendar_triggers"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "regulatory_briefing", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="research",
            headline=f"Regulatory Briefing — {country.name} | {campaign.framework_focus}",
            body=content["regulatory_snapshot"],
            json_output=content,
            usage=result["usage"]
        )
