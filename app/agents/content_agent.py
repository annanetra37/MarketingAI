from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent


class ContentAgent(BaseAgent):
    """
    Generates persona-aware, country-tailored marketing content.
    Supports: LinkedIn posts, blog articles, Twitter/X threads.
    """

    AGENT_TYPE = "content"

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────
    def _audience_angle(self, persona_name: str) -> str:
        angles = {
            "SME":      "Focus on compliance risk, simplicity, cost savings, and automation. "
                        "Speak to a CFO or Sustainability Manager who is overwhelmed and risk-averse.",
            "ADVISORY": "Focus on scalability, margin improvement, workflow efficiency, and client growth. "
                        "Speak to an ESG consultant who wants to differentiate their firm.",
        }
        return angles.get(persona_name, "Professional ESG tone. Emphasize value and reliability.")

    def _cluster_context(self, cluster: str) -> str:
        contexts = {
            "CLUSTER_A": "This is a CSRD-driven EU market. Emphasize regulatory urgency, ESRS compliance deadlines, "
                         "audit readiness, and the risk of non-compliance. Localize with EU regulatory language.",
            "CLUSTER_B": "This is an international ESG maturity market. Emphasize ISSB/IFRS convergence, "
                         "multinational reporting consistency, and global ESG alignment — not just EU regulation.",
        }
        return contexts.get(cluster, "Global ESG context.")

    def _build_system_prompt(self, campaign, persona, country) -> str:
        return f"""
You are the Content Agent for Triple I — an AI-powered ESG & Carbon reporting platform.

Triple I's positioning:
- The Framework Interoperability Translator: automatically maps ESRS ↔ ISSB ↔ GRI ↔ TCFD
- Carbon reporting automation for CSRD-pressured companies
- Audit-ready outputs powered by EcoHub (core sustainability engine)
- No manual ESG mapping. Ever.

Campaign context:
- Audience: {persona.name}
- Country: {country.name}
- Cluster context: {self._cluster_context(country.cluster)}
- Framework focus: {campaign.framework_focus}
- Campaign goal: {campaign.goal}
- Audience angle: {self._audience_angle(persona.name)}
- Tone: {persona.tone_guidelines}
- CTA: {persona.cta}

Content rules:
1. Be CONCRETE. Use real pain points, real frameworks (ESRS, GRI, ISSB, TCFD, Scope 1/2/3).
2. Do NOT be generic. Reference the specific country/cluster context.
3. Always end with the exact CTA provided.
4. Use numbers and percentages where they strengthen the argument.
5. Match tone exactly: SME = clear, simple, risk-reducing. Advisory = strategic, efficiency-driven.
        """.strip()

    # ─────────────────────────────────────────────
    # LinkedIn Post
    # ─────────────────────────────────────────────
    def generate_linkedin(self, campaign_id) -> GeneratedContent:
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = self._build_system_prompt(campaign, persona, country)
        user_prompt = """
Generate a high-performing LinkedIn post for Triple I.

The post must:
- Open with a hook that stops the scroll (question, stat, or bold claim)
- Have a body with short paragraphs or line breaks (LinkedIn formatting)
- Mention specific ESG frameworks (ESRS, GRI, ISSB, TCFD, or Scope 1/2/3 as relevant)
- Close with a strong CTA
- Include 5 relevant hashtags

Return JSON with: headline, hook, body, cta, hashtags (array of strings).
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "headline":  {"type": "string"},
                "hook":      {"type": "string"},
                "body":      {"type": "string"},
                "cta":       {"type": "string"},
                "hashtags":  {"type": "array", "items": {"type": "string"}}
            },
            "required": ["headline", "hook", "body", "cta", "hashtags"],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "linkedin_post", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="linkedin",
            headline=content["headline"],
            body=content["body"],
            json_output=content,
            usage=result["usage"]
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

        data = linkedin.json_output

        system_prompt = """
You are the Blog Expansion Agent for Triple I.

Triple I positioning:
- Carbon Reporting + ESG Framework Interoperability Engine
- Translates ESRS ↔ ISSB ↔ GRI ↔ TCFD automatically
- Built for CSRD-pressured SMEs and ESG Advisory firms
- Powered by EcoHub

Write authoritative, educational, SEO-optimized blog content.
Use clear H2 sections. Include real ESG framework references.
        """.strip()

        user_prompt = f"""
Expand this LinkedIn post into an 800–1200 word SEO blog article.

LinkedIn Headline: {data.get("headline", "")}
LinkedIn Hook: {data.get("hook", "")}
LinkedIn Body: {data.get("body", "")}
CTA: {data.get("cta", "")}

Blog structure requirements:
- title: SEO-optimized H1 (include primary keyword)
- meta_description: 150-160 chars, compelling, includes keyword
- sections: array of {{heading (H2), content (2-3 paragraphs each)}}
  - Section 1: The problem / pain (regulatory context, real numbers)
  - Section 2: Why current approaches fail (spreadsheets, manual mapping)
  - Section 3: The Triple I solution (interoperability, EcoHub engine)
  - Section 4: Practical steps / what to do now
- cta: strong closing call to action paragraph

Return valid JSON.
        """.strip()

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

        result  = self._call_model(system_prompt, user_prompt, "blog_post", schema)
        content = result["content"]
        first_section_body = content["sections"][0]["content"] if content["sections"] else ""

        return self._save_content(
            campaign_id=linkedin.campaign_id,
            content_type="blog",
            headline=content["title"],
            body=first_section_body,
            json_output=content,
            usage=result["usage"],
            parent_content_id=linkedin.id
        )

    # ─────────────────────────────────────────────
    # Twitter/X Thread
    # ─────────────────────────────────────────────
    def generate_twitter_thread(self, campaign_id) -> GeneratedContent:
        campaign, persona, country = self.build_context(campaign_id)

        system_prompt = self._build_system_prompt(campaign, persona, country)
        user_prompt = """
Write a Twitter/X thread for Triple I. 6-8 tweets.

Rules:
- Tweet 1: hook tweet (bold claim or shocking stat — max 280 chars)
- Tweets 2-6: each makes one clear, standalone point
- Tweet 7: practical "what to do" advice
- Tweet 8: CTA tweet with link placeholder

Return JSON with: topic, tweets (array of strings, each max 280 chars).
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "topic":  {"type": "string"},
                "tweets": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["topic", "tweets"],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "twitter_thread", schema)
        content = result["content"]
        body    = "\n\n".join([f"{i+1}/ {t}" for i, t in enumerate(content["tweets"])])

        return self._save_content(
            campaign_id=campaign_id,
            content_type="twitter",
            headline=content["topic"],
            body=body,
            json_output=content,
            usage=result["usage"]
        )
