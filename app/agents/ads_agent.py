from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent


class AdsAgent(BaseAgent):
    """
    Generates paid advertising copy for Triple I.
    Supports: Google Ads (Search), LinkedIn Ads (Sponsored Content).
    Produces A/B variants with performance rationale.
    """

    AGENT_TYPE = "ads"

    def _audience_brief(self, persona_name: str, country_name: str, cluster: str) -> str:
        eu_note = "CSRD compliance deadline urgency is high. Use regulatory pressure as a hook." if cluster == "CLUSTER_A" else \
                  "ISSB/IFRS alignment is the key driver. Focus on global reporting consistency."
        persona_note = "Target: CFOs, Sustainability Managers, Compliance Officers at mid-market companies." if persona_name == "SME" else \
                       "Target: ESG consultants, sustainability directors at advisory and accounting firms."
        return f"Market: {country_name}. {eu_note}\n{persona_note}"

    # ─────────────────────────────────────────────
    # Google Search Ads
    # ─────────────────────────────────────────────
    def generate_google_ads(self, campaign_id) -> GeneratedContent:
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = f"""
You are the Paid Search Ads Agent for Triple I — ESG & Carbon Reporting platform.

Triple I USP: The ONLY tool that automatically translates between ESRS, ISSB, GRI, and TCFD.

{self._audience_brief(persona.name, country.name, country.cluster)}

Framework focus: {campaign.framework_focus}
Campaign goal: {campaign.goal}

Google Ads rules:
- Headline: max 30 characters each
- Description: max 90 characters each
- Include primary keyword in at least 2 headlines
- Create urgency, highlight differentiation, be specific
- A/B variants should test DIFFERENT angles, not just word changes
        """.strip()

        user_prompt = """
Generate a complete Google Search Ads set for Triple I.

Return JSON with:
- target_keywords: array of 5 search keywords this ad should target
- ad_group_name: descriptive name for this ad group
- variant_a: {{
    name: "Compliance Urgency",
    headlines: [array of 5 headlines, max 30 chars each],
    descriptions: [array of 2 descriptions, max 90 chars each],
    angle: what psychological angle this tests
  }}
- variant_b: {{
    name: "Efficiency/Scale",
    headlines: [array of 5 headlines, max 30 chars each],
    descriptions: [array of 2 descriptions, max 90 chars each],
    angle: what psychological angle this tests
  }}
- variant_c: {{
    name: "Interoperability USP",
    headlines: [array of 5 headlines, max 30 chars each],
    descriptions: [array of 2 descriptions, max 90 chars each],
    angle: what psychological angle this tests
  }}
- recommended_landing_page_focus: what the landing page should emphasize for best conversion
- negative_keywords: array of 5 keywords to exclude
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "target_keywords":  {"type": "array", "items": {"type": "string"}},
                "ad_group_name":    {"type": "string"},
                "variant_a": {
                    "type": "object",
                    "properties": {
                        "name":         {"type": "string"},
                        "headlines":    {"type": "array", "items": {"type": "string"}},
                        "descriptions": {"type": "array", "items": {"type": "string"}},
                        "angle":        {"type": "string"}
                    },
                    "required": ["name", "headlines", "descriptions", "angle"],
                    "additionalProperties": False
                },
                "variant_b": {
                    "type": "object",
                    "properties": {
                        "name":         {"type": "string"},
                        "headlines":    {"type": "array", "items": {"type": "string"}},
                        "descriptions": {"type": "array", "items": {"type": "string"}},
                        "angle":        {"type": "string"}
                    },
                    "required": ["name", "headlines", "descriptions", "angle"],
                    "additionalProperties": False
                },
                "variant_c": {
                    "type": "object",
                    "properties": {
                        "name":         {"type": "string"},
                        "headlines":    {"type": "array", "items": {"type": "string"}},
                        "descriptions": {"type": "array", "items": {"type": "string"}},
                        "angle":        {"type": "string"}
                    },
                    "required": ["name", "headlines", "descriptions", "angle"],
                    "additionalProperties": False
                },
                "recommended_landing_page_focus": {"type": "string"},
                "negative_keywords": {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "target_keywords", "ad_group_name",
                "variant_a", "variant_b", "variant_c",
                "recommended_landing_page_focus", "negative_keywords"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "google_ads", schema)
        content = result["content"]

        headline = f"Google Ads — {persona.name} | {country.name} | {campaign.framework_focus}"
        body     = f"Ad group: {content['ad_group_name']} | {len(content['target_keywords'])} target keywords | 3 A/B variants"

        return self._save_content(
            campaign_id=campaign_id,
            content_type="google_ads",
            headline=headline,
            body=body,
            json_output=content,
            usage=result["usage"]
        )

    # ─────────────────────────────────────────────
    # LinkedIn Sponsored Content Ads
    # ─────────────────────────────────────────────
    def generate_linkedin_ads(self, campaign_id) -> GeneratedContent:
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = f"""
You are the LinkedIn Ads Agent for Triple I — ESG & Carbon Reporting platform.

{self._audience_brief(persona.name, country.name, country.cluster)}
Framework focus: {campaign.framework_focus}

LinkedIn Sponsored Content rules:
- Introductory text: 150 chars max (shown in feed)
- Headline: 70 chars max
- Description: 100 chars max
- CTA button: must be one of [Learn More, Download, Sign Up, Request Demo, Contact Us]
- Image suggestion: describe what the visual should show
        """.strip()

        user_prompt = """
Generate 3 LinkedIn Sponsored Content ad variants for Triple I.

Return JSON with:
- audience_targeting: {{job_titles, industries, company_size, seniority}} (LinkedIn targeting parameters)
- variant_a, variant_b, variant_c: each containing {{
    name: variant label,
    introductory_text: max 150 chars,
    headline: max 70 chars,
    description: max 100 chars,
    cta_button: one of the allowed options,
    image_suggestion: describe the ideal visual,
    angle: what this variant tests
  }}
- budget_recommendation: daily budget range and bidding strategy suggestion
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "audience_targeting": {
                    "type": "object",
                    "properties": {
                        "job_titles":    {"type": "array", "items": {"type": "string"}},
                        "industries":    {"type": "array", "items": {"type": "string"}},
                        "company_size":  {"type": "string"},
                        "seniority":     {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["job_titles", "industries", "company_size", "seniority"],
                    "additionalProperties": False
                },
                "variant_a": {
                    "type": "object",
                    "properties": {
                        "name":                {"type": "string"},
                        "introductory_text":   {"type": "string"},
                        "headline":            {"type": "string"},
                        "description":         {"type": "string"},
                        "cta_button":          {"type": "string"},
                        "image_suggestion":    {"type": "string"},
                        "angle":               {"type": "string"}
                    },
                    "required": ["name","introductory_text","headline","description","cta_button","image_suggestion","angle"],
                    "additionalProperties": False
                },
                "variant_b": {
                    "type": "object",
                    "properties": {
                        "name":                {"type": "string"},
                        "introductory_text":   {"type": "string"},
                        "headline":            {"type": "string"},
                        "description":         {"type": "string"},
                        "cta_button":          {"type": "string"},
                        "image_suggestion":    {"type": "string"},
                        "angle":               {"type": "string"}
                    },
                    "required": ["name","introductory_text","headline","description","cta_button","image_suggestion","angle"],
                    "additionalProperties": False
                },
                "variant_c": {
                    "type": "object",
                    "properties": {
                        "name":                {"type": "string"},
                        "introductory_text":   {"type": "string"},
                        "headline":            {"type": "string"},
                        "description":         {"type": "string"},
                        "cta_button":          {"type": "string"},
                        "image_suggestion":    {"type": "string"},
                        "angle":               {"type": "string"}
                    },
                    "required": ["name","introductory_text","headline","description","cta_button","image_suggestion","angle"],
                    "additionalProperties": False
                },
                "budget_recommendation": {"type": "string"}
            },
            "required": ["audience_targeting", "variant_a", "variant_b", "variant_c", "budget_recommendation"],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "linkedin_ads", schema)
        content = result["content"]

        headline = f"LinkedIn Ads — {persona.name} | {country.name} | {campaign.framework_focus}"
        body     = f"3 ad variants | Targeting: {', '.join(content['audience_targeting']['job_titles'][:3])}"

        return self._save_content(
            campaign_id=campaign_id,
            content_type="linkedin_ads",
            headline=headline,
            body=body,
            json_output=content,
            usage=result["usage"]
        )
