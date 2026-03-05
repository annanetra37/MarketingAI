"""
seo_agent.py
============
SEO Agent — owns keyword strategy and content optimisation for Triple I.

Priority: capture high-intent CSRD/ESRS searches from companies under
compliance pressure in Cluster A European markets.  Every keyword cluster
is mapped to a funnel stage: fear (awareness) → assessment (lead-gen) →
Fast-Track Sprint (conversion).
"""

import json
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.agents.triple_i_context import get_master_context, REGULATORY_URGENCY, MARKETS
from app.models.generated_content import GeneratedContent


class SEOAgent(BaseAgent):
    """
    🔍 SEO Agent
    Generates keyword clusters aligned with CSRD urgency and the
    Fear → Assessment → Pilot conversion funnel.
    """

    AGENT_TYPE = "seo"

    # ─────────────────────────────────────────────
    # Keyword Cluster Research
    # ─────────────────────────────────────────────
    def generate_keyword_cluster(self, campaign_id) -> GeneratedContent:
        """
        Generate a full keyword cluster that captures:
        - Fear-stage searches (CSRD deadline anxiety, compliance risk)
        - Solution-stage searches (ESRS reporting software, ESG automation)
        - Conversion-stage searches (CSRD software price, ESG pilot, ESRS consultant)
        """
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = f"""
You are the SEO Agent for Triple I — an AI-powered ESG & Carbon Reporting platform.

{get_master_context()}

SEO STRATEGY FOR TRIPLE I:
Triple I needs FAST results in Europe — especially Cluster A (Spain, France, Netherlands,
Belgium, Sweden).  The keyword strategy must capture three buyer moments:

1. FEAR STAGE (awareness): Companies just realising CSRD applies to them
   - High urgency, high volume, informational intent
   - Examples: "CSRD compliance deadline 2025", "ESRS E1 reporting requirements"

2. ASSESSMENT STAGE (consideration): Companies actively evaluating solutions
   - Lead-gen intent — these are the ESRS Readiness Assessment searchers
   - Examples: "CSRD readiness assessment", "ESRS gap analysis tool", "ESG reporting software SME"

3. CONVERSION STAGE (decision): Ready to buy or trial
   - Highest commercial intent — these convert to Fast-Track Sprint pilots
   - Examples: "CSRD reporting software price", "ESRS consultant cost", "ESG software pilot"

For {country.name} (Cluster: {country.cluster}):
{country.notes}

Your keyword output must power:
- Landing pages for the ESRS Readiness Assessment (free lead-gen)
- Landing pages for the Fast-Track Compliance Sprint (€5K–€15K paid pilot)
- Blog content that ranks for fear-stage searches
- PPC ads that capture conversion-stage intent

{REGULATORY_URGENCY}
        """.strip()

        user_prompt = f"""
Generate a comprehensive SEO keyword cluster for Triple I in {country.name}.

Persona: {persona.name}
Framework focus: {campaign.framework_focus}
Campaign goal: {campaign.goal}

REQUIRED OUTPUT:
1. primary_keywords: 5–8 high-priority, commercially viable terms (with funnel stage: fear/assessment/conversion)
2. secondary_keywords: 10–15 supporting terms
3. long_tail_keywords: 10–15 specific phrases (3–6 words) capturing urgent buyer queries
4. fear_stage_keywords: 5–8 terms for companies just realising they need to comply
5. assessment_cta_keywords: 5–8 terms that map to the ESRS Readiness Assessment offer
6. pilot_cta_keywords: 5–8 terms that map to the Fast-Track Compliance Sprint offer
7. local_keywords: 5+ {country.name}-specific terms (local language variants if relevant)
8. content_gap_topics: 5 blog topics Triple I should own that competitors aren't covering
9. quick_wins: 3 pages/landing pages Triple I should create IMMEDIATELY for fast results
10. recommended_page_titles: 5 SEO-optimised page/post titles
11. negative_keywords: 5+ terms to exclude from PPC (avoid wasting budget)
12. summary: 2–3 sentence overview of the SEO opportunity and priority actions

Focus on terms that drive the Fear → Assessment → Fast-Track Sprint funnel.
Include local language where relevant (Spanish for ES, French for FR, Dutch for NL, etc.).
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "summary":                {"type": "string"},
                "primary_keywords": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "keyword":     {"type": "string"},
                            "funnel_stage": {"type": "string"},
                            "intent":      {"type": "string"},
                            "priority":    {"type": "string"}
                        },
                        "required": ["keyword", "funnel_stage", "intent", "priority"],
                        "additionalProperties": False
                    }
                },
                "secondary_keywords":     {"type": "array", "items": {"type": "string"}},
                "long_tail_keywords":     {"type": "array", "items": {"type": "string"}},
                "fear_stage_keywords":    {"type": "array", "items": {"type": "string"}},
                "assessment_cta_keywords":{"type": "array", "items": {"type": "string"}},
                "pilot_cta_keywords":     {"type": "array", "items": {"type": "string"}},
                "local_keywords":         {"type": "array", "items": {"type": "string"}},
                "content_gap_topics":     {"type": "array", "items": {"type": "string"}},
                "quick_wins":             {"type": "array", "items": {"type": "string"}},
                "recommended_page_titles":{"type": "array", "items": {"type": "string"}},
                "negative_keywords":      {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "summary", "primary_keywords", "secondary_keywords",
                "long_tail_keywords", "fear_stage_keywords", "assessment_cta_keywords",
                "pilot_cta_keywords", "local_keywords", "content_gap_topics",
                "quick_wins", "recommended_page_titles", "negative_keywords"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "seo_keyword_cluster", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="seo_report",
            headline=f"SEO Keyword Cluster — {persona.name} | {country.name} | {campaign.framework_focus}",
            body=content["summary"],
            json_output=content,
            usage=result["usage"]
        )

    # ─────────────────────────────────────────────
    # Optimise existing content for SEO
    # ─────────────────────────────────────────────
    def optimize_content(self, content_id) -> GeneratedContent:
        """
        SEO-optimise an existing piece of content.
        Ensures fear-hook is in H1/title, CSRD keywords in H2s,
        and Fast-Track Sprint CTA in meta description.
        """
        original = (
            self.db.query(GeneratedContent)
            .filter(GeneratedContent.id == content_id)
            .first()
        )
        if not original:
            raise ValueError("Content not found")

        campaign, persona, country = self.build_context(str(original.campaign_id))

        system_prompt = f"""
You are the SEO Optimisation Agent for Triple I.

{get_master_context()}

SEO optimisation priorities for Triple I:
1. Title/H1 must include a CSRD/ESRS urgency signal AND the primary keyword
2. Meta description must mention the ESRS Readiness Assessment or Fast-Track Sprint
3. H2 structure must cover: regulatory context → problem → Triple I solution → CTA
4. Keyword density: primary keyword 1–2%, secondary keywords naturally distributed
5. Internal linking suggestions: always suggest linking to the ESRS Assessment landing page
6. Every optimised piece must make the Fear → Assessment → Pilot funnel clear
        """.strip()

        user_prompt = f"""
SEO-optimise this Triple I content piece.

Content type: {original.type}
Current headline: {original.headline}
Current body: {original.body[:1000]}

Target persona: {persona.name} in {country.name}
Framework: {campaign.framework_focus}

Provide:
1. optimised_title: SEO-friendly, includes CSRD/ESRS + urgency signal
2. meta_description: 155 chars, primary keyword + ESRS Assessment or Sprint CTA
3. h2_structure: recommended H2 headings that cover the fear → value → CTA arc
4. keyword_insertions: specific phrases to add and where
5. cta_optimisation: how to strengthen the CTA for conversion
6. internal_links: 2–3 suggested internal links to add
7. schema_markup_type: recommended schema (Article, FAQPage, HowTo, etc.)
8. seo_score_before: estimated score out of 10
9. seo_score_after: estimated score after changes
10. priority_changes: top 3 changes for maximum SEO impact
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "optimised_title":      {"type": "string"},
                "meta_description":     {"type": "string"},
                "h2_structure":         {"type": "array", "items": {"type": "string"}},
                "keyword_insertions":   {"type": "array", "items": {"type": "string"}},
                "cta_optimisation":     {"type": "string"},
                "internal_links":       {"type": "array", "items": {"type": "string"}},
                "schema_markup_type":   {"type": "string"},
                "seo_score_before":     {"type": "integer"},
                "seo_score_after":      {"type": "integer"},
                "priority_changes":     {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "optimised_title", "meta_description", "h2_structure",
                "keyword_insertions", "cta_optimisation", "internal_links",
                "schema_markup_type", "seo_score_before", "seo_score_after",
                "priority_changes"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "seo_optimization", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=str(original.campaign_id),
            content_type="seo_optimisation",
            headline=f"SEO Optimisation: {content['optimised_title']}",
            body=f"Score: {content['seo_score_before']}/10 → {content['seo_score_after']}/10 | {content['meta_description']}",
            json_output=content,
            usage=result["usage"]
        )
