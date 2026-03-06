"""
app/agents/content_agent.py — Triple I v4.0
Token-optimized: target <$0.005 per LinkedIn post on gpt-4o-mini.

Optimisation techniques applied:
  1. System prompt stripped to essentials (~200 tokens vs ~500 before)
  2. User prompt uses concise bullet directives, not verbose paragraphs
  3. Schema uses minimal field descriptions (model doesn't need them)
  4. No redundant context repetition between system + user prompts
  5. max_tokens capped per content type to prevent runaway output costs
"""

from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent


class ContentAgent(BaseAgent):
    """Generates persona-aware, country-tailored marketing content."""

    AGENT_TYPE      = "content"
    USE_POWER_MODEL = False  # gpt-4o-mini — structured content is fine here

    # ── Compact context helpers (token-efficient) ─────────────────────────

    def _audience_angle(self, persona_name: str) -> str:
        return (
            "SME: overwhelmed CFO/Sustainability Manager, risk-averse, wants simplicity."
            if persona_name == "SME" else
            "ADVISORY: ESG consultant, wants scale, efficiency, client differentiation."
        )

    def _cluster_note(self, cluster: str) -> str:
        return (
            "CSRD/ESRS mandatory — use regulatory urgency, deadlines, audit risk."
            if cluster == "CLUSTER_A" else
            "ISSB/IFRS alignment focus — global reporting consistency."
        )

    def _build_system_prompt(self, campaign, persona, country) -> str:
        """
        Compact system prompt — ~180 tokens vs ~480 tokens before.
        All essential context preserved, verbosity eliminated.
        """
        return (
            f"You are Triple I's Content Agent. "
            f"Triple I: AI-powered ESG platform. "
            f"Differentiator: ESRS↔ISSB↔GRI↔TCFD auto-mapping, EcoHub engine, audit-ready outputs, 80-90% cost reduction vs manual.\n"
            f"Campaign: {campaign.name} | Focus: {campaign.framework_focus} | Channel: {campaign.channel}\n"
            f"Persona: {persona.name} — {self._audience_angle(persona.name)}\n"
            f"Market: {country.name} ({country.cluster}) — {self._cluster_note(country.cluster)}\n"
            f"Goal: {campaign.goal}\n"
            f"CTA: {persona.cta}\n"
            f"Rules: Be concrete. Use real frameworks. No generic ESG fluff. Match persona tone exactly."
        )

    # ─────────────────────────────────────────────
    # LinkedIn Post
    # ─────────────────────────────────────────────
    def generate_linkedin(self, campaign_id) -> GeneratedContent:
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = self._build_system_prompt(campaign, persona, country)

        # Compact user prompt — ~80 tokens vs ~120 before
        user_prompt = (
            "Write a LinkedIn post for Triple I.\n"
            "- Hook: bold claim or stat (1 line, scroll-stopper)\n"
            "- Body: 3-4 short paragraphs, ESG framework references, real pain points\n"
            "- CTA: use the exact CTA from context\n"
            "- 4 hashtags\n"
            "JSON: {headline, hook, body, cta, hashtags}"
        )

        schema = {
            "type": "object",
            "properties": {
                "headline": {"type": "string"},
                "hook":     {"type": "string"},
                "body":     {"type": "string"},
                "cta":      {"type": "string"},
                "hashtags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["headline", "hook", "body", "cta", "hashtags"],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "linkedin_post", schema, max_tokens=600)
        content = result["content"]

        return self._save_content(
            campaign_id  = campaign_id,
            content_type = "linkedin",
            headline     = content["headline"],
            body         = content["body"],
            json_output  = content,
            usage        = result["usage"]
        )

    # ─────────────────────────────────────────────
    # Blog from LinkedIn
    # ─────────────────────────────────────────────
    def generate_blog_from_linkedin(self, linkedin_content_id) -> GeneratedContent:
        linkedin = (
            self.db.query(GeneratedContent)
            .filter(GeneratedContent.id == linkedin_content_id)
            .first()
        )
        if not linkedin:
            raise ValueError("LinkedIn content not found")

        data = linkedin.json_output or {}

        # Compact system prompt — ~60 tokens
        system_prompt = (
            "You are Triple I's Blog Agent. "
            "Expand LinkedIn posts into SEO blog articles. "
            "Triple I: AI ESG platform — ESRS↔ISSB↔GRI↔TCFD auto-mapping, EcoHub engine. "
            "Write authoritative H2-structured content. Be specific, not generic."
        )

        # Compact user prompt — pass only essential LinkedIn data
        user_prompt = (
            f"Expand into a 600-800 word SEO blog article.\n"
            f"Headline: {data.get('headline','')}\n"
            f"Hook: {data.get('hook','')}\n"
            f"Body: {data.get('body','')[:300]}\n\n"  # truncate to save input tokens
            "JSON: {title, meta_description (150 chars), "
            "sections: [{heading, content}] x4, cta}"
        )

        schema = {
            "type": "object",
            "properties": {
                "title":            {"type": "string"},
                "meta_description": {"type": "string"},
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "heading": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["heading", "content"],
                        "additionalProperties": False
                    }
                },
                "cta": {"type": "string"}
            },
            "required": ["title", "meta_description", "sections", "cta"],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "blog_post", schema, max_tokens=1200)
        content = result["content"]
        first_section_body = content["sections"][0]["content"] if content.get("sections") else ""

        return self._save_content(
            campaign_id       = linkedin.campaign_id,
            content_type      = "blog",
            headline          = content["title"],
            body              = first_section_body,
            json_output       = content,
            usage             = result["usage"],
            parent_content_id = linkedin.id
        )

    # ─────────────────────────────────────────────
    # Twitter/X Thread
    # ─────────────────────────────────────────────
    def generate_twitter_thread(self, campaign_id) -> GeneratedContent:
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = self._build_system_prompt(campaign, persona, country)

        # Compact user prompt
        user_prompt = (
            "Write a 6-tweet Twitter/X thread for Triple I.\n"
            "Tweet 1: hook (shocking stat or bold claim, max 280 chars)\n"
            "Tweets 2-5: one clear point each, ESG framework references\n"
            "Tweet 6: CTA with link placeholder\n"
            "JSON: {topic, tweets: [string x6]}"
        )

        schema = {
            "type": "object",
            "properties": {
                "topic":  {"type": "string"},
                "tweets": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["topic", "tweets"],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "twitter_thread", schema, max_tokens=700)
        content = result["content"]
        body    = "\n\n".join([f"{i+1}/ {t}" for i, t in enumerate(content["tweets"])])

        return self._save_content(
            campaign_id  = campaign_id,
            content_type = "twitter",
            headline     = content["topic"],
            body         = body,
            json_output  = content,
            usage        = result["usage"]
        )

    # Alias for orchestrator compatibility
    generate_twitter = generate_twitter_thread