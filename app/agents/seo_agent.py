from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent


class SEOAgent(BaseAgent):
    """
    SEO intelligence for Triple I.
    Generates keyword clusters, optimizes content for search, finds content gaps.
    """

    AGENT_TYPE = "seo"

    # ─────────────────────────────────────────────
    # Keyword Cluster Research
    # ─────────────────────────────────────────────
    def generate_keyword_cluster(self, campaign_id) -> GeneratedContent:
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = f"""
You are the SEO Agent for Triple I — an ESG & Carbon reporting platform targeting CSRD-pressured companies.

Triple I differentiator: Framework Interoperability (ESRS ↔ ISSB ↔ GRI ↔ TCFD).
Products: Carbon footprint reporting, CSRD compliance, audit-ready outputs.

Target market:
- Persona: {persona.name}
- Country: {country.name} (Cluster: {country.cluster})
- Framework focus: {campaign.framework_focus}

You must think like an ESG-specialist SEO strategist. You know:
- What terms CSRD-pressured SMEs actually search for
- What advisory firms search for when evaluating software
- The difference between informational, commercial, and transactional intent
- How search volume and keyword difficulty interact for a new SaaS player
        """.strip()

        user_prompt = f"""
Generate a comprehensive SEO keyword cluster for Triple I in {country.name}.

Persona: {persona.name} | Framework: {campaign.framework_focus}

Return JSON with:
- summary: brief strategic overview of the SEO opportunity (2-3 sentences)
- primary_keywords: 5 high-priority keywords (objects with: keyword, estimated_monthly_volume, difficulty (Low/Medium/High), intent (Informational/Commercial/Transactional), rationale)
- secondary_keywords: 8 supporting keywords (same structure)
- long_tail_keywords: 6 long-tail phrases (same structure, lower volume but high intent)
- content_gap_topics: 4 content topic opportunities competitors aren't covering
- quick_wins: 3 keywords with Low difficulty + Commercial/Transactional intent (highest priority)
- recommended_page_titles: 3 SEO page title suggestions using the primary keywords
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "primary_keywords": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "keyword":                  {"type": "string"},
                            "estimated_monthly_volume": {"type": "string"},
                            "difficulty":               {"type": "string"},
                            "intent":                   {"type": "string"},
                            "rationale":                {"type": "string"}
                        },
                        "required": ["keyword", "estimated_monthly_volume", "difficulty", "intent", "rationale"],
                        "additionalProperties": False
                    }
                },
                "secondary_keywords": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "keyword":                  {"type": "string"},
                            "estimated_monthly_volume": {"type": "string"},
                            "difficulty":               {"type": "string"},
                            "intent":                   {"type": "string"},
                            "rationale":                {"type": "string"}
                        },
                        "required": ["keyword", "estimated_monthly_volume", "difficulty", "intent", "rationale"],
                        "additionalProperties": False
                    }
                },
                "long_tail_keywords": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "keyword":                  {"type": "string"},
                            "estimated_monthly_volume": {"type": "string"},
                            "difficulty":               {"type": "string"},
                            "intent":                   {"type": "string"},
                            "rationale":                {"type": "string"}
                        },
                        "required": ["keyword", "estimated_monthly_volume", "difficulty", "intent", "rationale"],
                        "additionalProperties": False
                    }
                },
                "content_gap_topics":      {"type": "array", "items": {"type": "string"}},
                "quick_wins":              {"type": "array", "items": {"type": "string"}},
                "recommended_page_titles": {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "summary", "primary_keywords", "secondary_keywords",
                "long_tail_keywords", "content_gap_topics", "quick_wins", "recommended_page_titles"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "seo_keyword_cluster", schema)
        content = result["content"]

        headline = f"SEO Keyword Cluster — {persona.name} | {country.name} | {campaign.framework_focus}"
        body     = content["summary"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="seo_report",
            headline=headline,
            body=body,
            json_output=content,
            usage=result["usage"]
        )

    # ─────────────────────────────────────────────
    # Optimize existing content for SEO
    # ─────────────────────────────────────────────
    def optimize_content(self, content_id) -> GeneratedContent:
        original = (
            self.db.query(GeneratedContent)
            .filter(GeneratedContent.id == content_id)
            .first()
        )
        if not original:
            raise ValueError("Content not found")

        system_prompt = """
You are an SEO optimization specialist for Triple I — a B2B SaaS ESG platform.
Your job: improve content for search visibility without losing the core message.
Focus on: title tags, meta descriptions, H2 structure, internal linking suggestions, keyword density.
        """.strip()

        user_prompt = f"""
Analyze and optimize this content for SEO:

Type: {original.type}
Headline: {original.headline}
Body: {original.body}
Full JSON: {original.json_output}

Return JSON with:
- optimized_title: improved SEO title (60 chars max)
- optimized_meta_description: 150-160 chars
- primary_keyword: single target keyword
- secondary_keywords: array of 3-5 supporting keywords
- seo_score_before: estimated score 0-100 with rationale
- seo_score_after: estimated score 0-100 with rationale
- improvements_made: array of specific changes/suggestions
- internal_link_suggestions: 3 content pieces Triple I should link to
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "optimized_title":           {"type": "string"},
                "optimized_meta_description":{"type": "string"},
                "primary_keyword":           {"type": "string"},
                "secondary_keywords":        {"type": "array", "items": {"type": "string"}},
                "seo_score_before":          {"type": "string"},
                "seo_score_after":           {"type": "string"},
                "improvements_made":         {"type": "array", "items": {"type": "string"}},
                "internal_link_suggestions": {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "optimized_title", "optimized_meta_description", "primary_keyword",
                "secondary_keywords", "seo_score_before", "seo_score_after",
                "improvements_made", "internal_link_suggestions"
            ],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "seo_optimization", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=original.campaign_id,
            content_type="seo_optimization",
            headline=f"SEO Optimization: {original.headline}",
            body=f"Score improvement: {content['seo_score_before']} → {content['seo_score_after']}",
            json_output=content,
            usage=result["usage"],
            parent_content_id=original.id
        )
