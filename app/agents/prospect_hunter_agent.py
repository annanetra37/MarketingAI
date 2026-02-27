from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent
from app import log_bus


class ProspectHunterAgent(BaseAgent):
    """
    🎯 Prospect Hunter Agent
    Finds product-qualified companies in any country that are likely
    to buy Triple I ESG/carbon reporting software right now.
    """
    AGENT_TYPE = "prospect_hunter"

    def hunt_prospects(self, country_name: str, cluster: str, persona_name: str,
                       industry_focus: str = "all", min_employees: int = 250,
                       max_employees: int = 5000, campaign_id: str = None) -> GeneratedContent:
        log_bus.emit("🎯", f"Prospect Hunter — scanning {country_name} for {persona_name} buyers…", "info")

        cluster_ctx = {
            "CLUSTER_A": "EU CSRD-regulated market. Companies 250+ employees must comply from FY2025. Regulatory trigger: ESRS mandatory reporting deadlines.",
            "CLUSTER_B": "ISSB/IFRS S1&S2 market. Listed companies, financial services, multinationals under investor/exchange pressure.",
        }.get(cluster, "Global ESG market.")

        persona_ctx = {
            "SME": "Mid-market CFOs, Sustainability Managers, Compliance Officers. 250-1500 employees. Budget €30k-150k.",
            "ADVISORY": "ESG advisory firms, Big4 practices, accounting firms. ESG Directors, Partners. Need to scale services.",
        }.get(persona_name, "B2B enterprise buyers.")

        system = f"""You are a B2B sales intelligence expert for ESG software.
Market: {cluster_ctx}
ICP: {persona_ctx}
Triple I: AI-powered ESG & Carbon Reporting. Auto-translates ESRS↔ISSB↔GRI↔TCFD. Cuts reporting time 80%.
Produce accurate, specific, actionable prospect intelligence."""

        user = f"""Find product-qualified prospects for Triple I in {country_name}.

Parameters: country={country_name}, cluster={cluster}, persona={persona_name}, industry={industry_focus}, size={min_employees}-{max_employees} employees

Return JSON:
- market_overview: current ESG software buying environment (3-4 sentences)
- buying_signals: array of 5 specific signals a company is buying NOW
- ideal_prospect_profile: exact firmographic + psychographic profile
- prospect_companies: array of 15 companies, each with: company_name, industry, employees_estimate, headquarters, why_qualified, pain_point, trigger_event, key_decision_makers (array), linkedin_search_query, qualification_score (1-10 integer), outreach_priority ("hot"/"warm"/"cold")
- industries_ranked: array of top 5 industries, each with: industry, rank (integer), rationale
- timing_intelligence: best time to reach (regulatory calendar)
- competitive_displacement: which competitor they use and how to displace
- channel_recommendations: array of best channels
- account_based_marketing_plays: array of 3 ABM plays"""

        schema = {
            "type": "object",
            "properties": {
                "market_overview": {"type": "string"},
                "buying_signals": {"type": "array", "items": {"type": "string"}},
                "ideal_prospect_profile": {"type": "string"},
                "prospect_companies": {"type": "array", "items": {
                    "type": "object",
                    "properties": {
                        "company_name": {"type": "string"},
                        "industry": {"type": "string"},
                        "employees_estimate": {"type": "string"},
                        "headquarters": {"type": "string"},
                        "why_qualified": {"type": "string"},
                        "pain_point": {"type": "string"},
                        "trigger_event": {"type": "string"},
                        "key_decision_makers": {"type": "array", "items": {"type": "string"}},
                        "linkedin_search_query": {"type": "string"},
                        "qualification_score": {"type": "integer"},
                        "outreach_priority": {"type": "string"}
                    },
                    "required": ["company_name","industry","employees_estimate","headquarters",
                                 "why_qualified","pain_point","trigger_event","key_decision_makers",
                                 "linkedin_search_query","qualification_score","outreach_priority"],
                    "additionalProperties": False
                }},
                "industries_ranked": {"type": "array", "items": {
                    "type": "object",
                    "properties": {"industry": {"type": "string"}, "rank": {"type": "integer"}, "rationale": {"type": "string"}},
                    "required": ["industry","rank","rationale"], "additionalProperties": False
                }},
                "timing_intelligence": {"type": "string"},
                "competitive_displacement": {"type": "string"},
                "channel_recommendations": {"type": "array", "items": {"type": "string"}},
                "account_based_marketing_plays": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["market_overview","buying_signals","ideal_prospect_profile","prospect_companies",
                         "industries_ranked","timing_intelligence","competitive_displacement",
                         "channel_recommendations","account_based_marketing_plays"],
            "additionalProperties": False
        }

        result = self._call_model(system, user, "prospect_intelligence", schema)
        data = result["content"]
        hot = sum(1 for p in data["prospect_companies"] if p.get("outreach_priority") == "hot")

        return self._save_content(
            campaign_id=campaign_id,
            content_type="prospect_list",
            headline=f"🎯 {len(data['prospect_companies'])} Prospects — {country_name} | {persona_name} ({hot} HOT)",
            body=data["market_overview"],
            json_output=data,
            usage=result["usage"],
        )

    def score_prospect(self, company_name: str, country: str,
                       campaign_id: str = None) -> GeneratedContent:
        log_bus.emit("⚡", f"Scoring prospect: {company_name} ({country})…", "info")

        user = f"""Score this company as a Triple I prospect:
Company: {company_name}, Country: {country}

Return JSON:
- qualification_score: integer 1-100
- fit_assessment: "Low"/"Medium"/"High"/"Perfect"
- urgency_score: integer 1-10
- budget_likelihood: "Low"/"Medium"/"High"
- decision_timeline_estimate: string
- top_3_reasons_to_buy: array of 3 strings
- red_flags: array of strings
- recommended_approach: string
- suggested_subject_line: string"""

        schema = {
            "type": "object",
            "properties": {
                "qualification_score": {"type": "integer"},
                "fit_assessment": {"type": "string"},
                "urgency_score": {"type": "integer"},
                "budget_likelihood": {"type": "string"},
                "decision_timeline_estimate": {"type": "string"},
                "top_3_reasons_to_buy": {"type": "array", "items": {"type": "string"}},
                "red_flags": {"type": "array", "items": {"type": "string"}},
                "recommended_approach": {"type": "string"},
                "suggested_subject_line": {"type": "string"}
            },
            "required": ["qualification_score","fit_assessment","urgency_score","budget_likelihood",
                         "decision_timeline_estimate","top_3_reasons_to_buy","red_flags",
                         "recommended_approach","suggested_subject_line"],
            "additionalProperties": False
        }

        result = self._call_model(
            "You are a B2B sales qualification expert for ESG software. Be specific and evidence-based.",
            user, "prospect_score", schema
        )
        data = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="prospect_score",
            headline=f"Score: {data['qualification_score']}/100 — {company_name} ({data['fit_assessment']} fit)",
            body=data["recommended_approach"],
            json_output=data,
            usage=result["usage"],
        )
