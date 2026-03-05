"""
ads_agent.py
============
Ads Agent — generates Google Search and LinkedIn Sponsored ads for Triple I.

Ad creative philosophy:
- Google: capture high-intent CSRD/ESRS searches — Fear hook → Solution → Pilot CTA
- LinkedIn: interrupt compliance/sustainability decision-makers — Urgency → Demo → Sprint
- Always 3 A/B variants per ad type with different angles
- Primary CTA: ESRS Readiness Assessment (top of funnel) OR Fast-Track Sprint (bottom)
"""

import json
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.agents.triple_i_context import (
    get_master_context, get_fear_hooks, get_cta_library,
    VALUE_PROPS, REGULATORY_URGENCY
)
from app.models.generated_content import GeneratedContent


class AdsAgent(BaseAgent):
    """
    🎯 Ads Agent
    Generates high-converting Google Search Ads and LinkedIn Sponsored Content
    with 3 A/B variants each, aligned to the Fast-Track Compliance Sprint sales motion.
    """

    AGENT_TYPE = "ads"

    def _ads_system_prompt(self, campaign, persona, country) -> str:
        return f"""
You are the Performance Marketing Ads Agent for Triple I.

{get_master_context()}

ACTIVE CAMPAIGN:
  Persona: {persona.name}
  Country:  {country.name} (Cluster: {country.cluster})
  Framework: {campaign.framework_focus}
  Channel:   {campaign.channel}
  Country context: {country.notes}

AD CREATION RULES:
1. Every ad must LEAD WITH FEAR — CSRD deadline, compliance risk, or cost of failure.
2. Always include at least one specific claim: "80–90% cost reduction", "EcoHub™", "6-week sprint"
3. Primary CTA: "Book Free ESRS Assessment" (ToFu) OR "Start Compliance Sprint" (BoFu)
4. Secondary CTA: "Request Demo" for mid-funnel
5. A/B variants must test different angles: fear vs. speed vs. cost savings
6. NEVER be generic — always reference {country.name} regulatory context

{REGULATORY_URGENCY}

{get_fear_hooks()}

{get_cta_library()}
        """.strip()

    # ─────────────────────────────────────────────
    # Google Search Ads
    # ─────────────────────────────────────────────
    def generate_google_ads(self, campaign_id) -> GeneratedContent:
        """
        Generate 3 Google Search Ad variants.
        Variant A: Fear angle (CSRD deadline / non-compliance risk)
        Variant B: Speed angle (6-week sprint / fast compliance)
        Variant C: Cost angle (80–90% cheaper / replace spreadsheets)
        """
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = self._ads_system_prompt(campaign, persona, country)

        user_prompt = f"""
Generate 3 Google Search Ad variants for Triple I in {country.name} targeting {persona.name}.

Google Responsive Search Ad specs:
- Headlines: 3 per variant, max 30 chars each
- Descriptions: 2 per variant, max 90 chars each
- Display URL path: 2 segments, max 15 chars each

VARIANT A — Fear Angle:
  Hook: CSRD deadline urgency, penalty risk, audit failure
  CTA: Book Free ESRS Readiness Assessment

VARIANT B — Speed Angle:
  Hook: 6-week Fast-Track Compliance Sprint, fast results
  CTA: Start Your Compliance Sprint Today

VARIANT C — Cost/Value Angle:
  Hook: 80–90% cost reduction vs. manual, replace spreadsheets
  CTA: See the ROI — Request Demo

Keywords to integrate naturally (don't stuff):
- CSRD compliance, ESRS reporting, ESG software, {country.name} ESG, EcoHub

For each variant also provide:
- target_keywords: 5 best-match keywords for this variant
- bid_strategy: recommended Google Ads bid strategy
- audience_targeting: job titles / company sizes to target
- quality_score_estimate: 1–10

Return JSON with: variants (array of 3), campaign_notes, estimated_ctr.
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "variants": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "variant_name":       {"type": "string"},
                            "angle":              {"type": "string"},
                            "headlines":          {"type": "array", "items": {"type": "string"}},
                            "descriptions":       {"type": "array", "items": {"type": "string"}},
                            "display_url_paths":  {"type": "array", "items": {"type": "string"}},
                            "target_keywords":    {"type": "array", "items": {"type": "string"}},
                            "bid_strategy":       {"type": "string"},
                            "audience_targeting": {"type": "string"},
                            "quality_score_estimate": {"type": "integer"},
                            "cta_primary":        {"type": "string"}
                        },
                        "required": [
                            "variant_name", "angle", "headlines", "descriptions",
                            "display_url_paths", "target_keywords", "bid_strategy",
                            "audience_targeting", "quality_score_estimate", "cta_primary"
                        ],
                        "additionalProperties": False
                    }
                },
                "campaign_notes":  {"type": "string"},
                "estimated_ctr":   {"type": "string"},
                "negative_keywords": {"type": "array", "items": {"type": "string"}},
                "budget_recommendation": {"type": "string"}
            },
            "required": ["variants", "campaign_notes", "estimated_ctr", "negative_keywords", "budget_recommendation"],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "google_ads", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="google_ads",
            headline=f"Google Ads — {country.name} | {persona.name} (3 variants)",
            body=f"CTR est: {content['estimated_ctr']} | {content['campaign_notes']}",
            json_output=content,
            usage=result["usage"]
        )

    # ─────────────────────────────────────────────
    # LinkedIn Sponsored Content
    # ─────────────────────────────────────────────
    def generate_linkedin_ads(self, campaign_id) -> GeneratedContent:
        """
        Generate 3 LinkedIn Sponsored Content variants.
        Designed to interrupt sustainability / CFO / compliance decision-makers.
        """
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = self._ads_system_prompt(campaign, persona, country)

        user_prompt = f"""
Generate 3 LinkedIn Sponsored Content ad variants for Triple I.
Target: {persona.name} in {country.name}.

LinkedIn Single Image Ad specs:
- Introductory text: max 150 chars (shown above the image)
- Headline: max 70 chars
- Description: max 100 chars (shown below headline)
- CTA button: choose from [Learn More / Register / Request Demo / Sign Up / Download]

VARIANT A — Urgency/Fear:
  Angle: CSRD reporting deadline is here — companies still on spreadsheets are exposed
  Offer: Free ESRS Readiness Assessment
  CTA button: Register

VARIANT B — Fast-Track Sprint:
  Angle: 6 weeks to a draft ESRS report. No IT team. No consultants.
  Offer: Fast-Track Compliance Sprint (E1+S1)
  CTA button: Learn More

VARIANT C — Social Proof/Credibility:
  Angle: Cambridge-validated. Award-winning EcoHub™. 80–90% cost reduction.
  Offer: Request a live demo
  CTA button: Request Demo

For each variant provide:
- audience_job_titles: 5 exact LinkedIn job titles to target
- company_size_targeting: size range
- interest_targeting: 3 LinkedIn interest categories
- image_concept: brief description of ideal ad image/visual
- ab_test_hypothesis: what this variant is testing vs. the others

Return JSON with: variants (array of 3), targeting_notes, recommended_daily_budget_eur.
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "variants": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "variant_name":            {"type": "string"},
                            "angle":                   {"type": "string"},
                            "introductory_text":       {"type": "string"},
                            "headline":                {"type": "string"},
                            "description":             {"type": "string"},
                            "cta_button":              {"type": "string"},
                            "offer":                   {"type": "string"},
                            "audience_job_titles":     {"type": "array", "items": {"type": "string"}},
                            "company_size_targeting":  {"type": "string"},
                            "interest_targeting":      {"type": "array", "items": {"type": "string"}},
                            "image_concept":           {"type": "string"},
                            "ab_test_hypothesis":      {"type": "string"}
                        },
                        "required": [
                            "variant_name", "angle", "introductory_text", "headline",
                            "description", "cta_button", "offer", "audience_job_titles",
                            "company_size_targeting", "interest_targeting",
                            "image_concept", "ab_test_hypothesis"
                        ],
                        "additionalProperties": False
                    }
                },
                "targeting_notes":              {"type": "string"},
                "recommended_daily_budget_eur": {"type": "string"},
                "estimated_cpl_eur":            {"type": "string"},
                "campaign_objective":           {"type": "string"}
            },
            "required": [
                "variants", "targeting_notes",
                "recommended_daily_budget_eur", "estimated_cpl_eur", "campaign_objective"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "linkedin_ads", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="linkedin_ads",
            headline=f"LinkedIn Ads — {country.name} | {persona.name} (3 variants)",
            body=f"CPL est: {content['estimated_cpl_eur']} | Budget: {content['recommended_daily_budget_eur']}/day",
            json_output=content,
            usage=result["usage"]
        )
