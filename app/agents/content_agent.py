"""
content_agent.py
================
Content Agent — generates LinkedIn posts, blog articles, and Twitter/X threads
for Triple I.  Every piece leads with fear/urgency (CSRD deadlines), follows
with Triple I value, and closes with the Fast-Track Compliance Sprint CTA.
"""

import json
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.agents.triple_i_context import (
    get_master_context, get_fear_hooks, get_cta_library,
    VALUE_PROPS, ICP_SME, ICP_ADVISORY
)
from app.models.generated_content import GeneratedContent


class ContentAgent(BaseAgent):
    """
    ✍️ Content Agent
    Generates persona-aware, fear-first, CSRD-urgent content across
    LinkedIn, Blog, and Twitter/X channels.
    """

    AGENT_TYPE = "content"

    # ─────────────────────────────────────────────
    # Shared system prompt
    # ─────────────────────────────────────────────
    def _build_system_prompt(self, campaign, persona, country) -> str:
        is_sme = "SME" in persona.name.upper() or "sme" in persona.name.lower()
        icp_block = ICP_SME if is_sme else ICP_ADVISORY

        return f"""
You are the Content Agent for Triple I — an AI-powered ESG & Carbon Reporting B2B SaaS.

{get_master_context()}

ACTIVE CAMPAIGN CONTEXT:
  Persona: {persona.name}
  Country:  {country.name} (Cluster: {country.cluster})
  Framework: {campaign.framework_focus}
  Channel:   {campaign.channel}
  Goal:      {campaign.goal}
  Persona pains: {json.dumps(persona.pains)}
  Persona motivations: {json.dumps(persona.motivations)}
  Country context: {country.notes}

{icp_block}

CONTENT CREATION RULES (non-negotiable):
1. ALWAYS lead with fear/urgency — CSRD deadline, compliance risk, audit pressure.
2. Follow with Triple I value — specific product capability that solves the fear.
3. Close with the Fast-Track Compliance Sprint CTA or ESRS Readiness Assessment CTA.
4. Use REAL framework names: ESRS E1, ESRS S1, CSRD, VSME, GHG Protocol, Scope 1/2/3.
5. Reference the 80–90% cost reduction claim where relevant.
6. Mention EcoHub™ by name — it's the award-winning AI engine.
7. Be CONCRETE — no generic ESG talk. Reference {country.name}-specific regulatory context.
8. Tone: {'direct, simple, risk-reducing — the SME is scared and needs clarity' if is_sme else 'strategic, ROI-driven — the advisory firm wants scale and efficiency'}.
9. Never mention competitors by name.
10. Every piece must funnel toward one action: demo, assessment, or pilot.

{get_fear_hooks()}

{get_cta_library()}
        """.strip()

    # ─────────────────────────────────────────────
    # LinkedIn Post
    # ─────────────────────────────────────────────
    def generate_linkedin(self, campaign_id) -> GeneratedContent:
        """
        Generate a high-performing LinkedIn post.
        Opens with a fear hook, builds with CSRD urgency + Triple I value,
        closes with Fast-Track Sprint or ESRS Assessment CTA.
        """
        campaign, persona, country = self.build_context(campaign_id)
        system_prompt = self._build_system_prompt(campaign, persona, country)

        user_prompt = f"""
Generate a high-performing LinkedIn post for Triple I targeting {persona.name} in {country.name}.

STRUCTURE REQUIRED:
1. HOOK (1–2 lines): fear-based — CSRD deadline, compliance risk, or audit pressure
2. BODY (3–5 short paragraphs): regulatory context → problem → Triple I solution
3. PROOF (1 line): cite the 80–90% cost reduction, EcoHub™ award, or Cambridge ecosystem
4. CTA (1 line): Book ESRS Readiness Assessment or Start Fast-Track Sprint
5. HASHTAGS: 5 relevant ones including #CSRD #ESRS and country-specific tags

Formatting: short paragraphs with line breaks (LinkedIn style). No bullet-heavy walls of text.
The post should feel written by a knowledgeable ESG insider, not a salesperson.

Return JSON with: headline, hook, body, proof_point, cta, hashtags (array).
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "headline":    {"type": "string"},
                "hook":        {"type": "string"},
                "body":        {"type": "string"},
                "proof_point": {"type": "string"},
                "cta":         {"type": "string"},
                "hashtags":    {"type": "array", "items": {"type": "string"}}
            },
            "required": ["headline", "hook", "body", "proof_point", "cta", "hashtags"],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "linkedin_post", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="linkedin",
            headline=content["headline"],
            body=f"{content['hook']}\n\n{content['body']}\n\n{content['proof_point']}\n\n{content['cta']}",
            json_output=content,
            usage=result["usage"]
        )

    # ─────────────────────────────────────────────
    # Blog Article (expanded from LinkedIn)
    # ─────────────────────────────────────────────
    def generate_blog_from_linkedin(self, linkedin_content_id) -> GeneratedContent:
        """
        Expand a LinkedIn post into a full SEO-optimised blog article.
        Structure: fear-hook intro → problem depth → Triple I solution → pilot CTA.
        """
        linkedin = (
            self.db.query(GeneratedContent)
            .filter(GeneratedContent.id == linkedin_content_id)
            .first()
        )
        if not linkedin:
            raise ValueError("LinkedIn content not found")

        data = linkedin.json_output or {}
        campaign, persona, country = self.build_context(str(linkedin.campaign_id))

        system_prompt = f"""
You are the Blog Content Agent for Triple I.

{get_master_context()}

Blog writing principles:
- Open with the fear/urgency angle — CSRD deadlines are LIVE
- Build credibility with specific framework knowledge (ESRS E1, S1, GHG Protocol)
- Position Triple I's Fast-Track Compliance Sprint as the natural solution
- Include the ESRS Readiness Assessment as a lead magnet reference
- SEO-optimised: use H2s, target long-tail CSRD/ESRS keywords
- Tone matches {persona.name}: {'clear and practical for compliance-focused SME readers' if 'SME' in persona.name.upper() else 'strategic and ROI-focused for advisory professionals'}
- End with a clear, urgent CTA

{get_fear_hooks()}
{get_cta_library()}
        """.strip()

        user_prompt = f"""
Expand this LinkedIn post into a 700–900 word SEO-optimised blog article for Triple I.

Source LinkedIn post:
Headline: {data.get('headline', '')}
Hook: {data.get('hook', '')}
Body: {data.get('body', '')}
CTA: {data.get('cta', '')}

Target audience: {persona.name} in {country.name}
Framework focus: {campaign.framework_focus}

BLOG STRUCTURE:
1. Title (SEO-friendly, includes CSRD/ESRS + country if relevant)
2. Meta description (155 chars, includes primary keyword)
3. Intro paragraph: opens with the fear hook, expands the stakes
4. H2 Section 1: The regulatory pressure in {country.name} right now
5. H2 Section 2: Why spreadsheets/manual approaches fail ESRS audits
6. H2 Section 3: How Triple I's Fast-Track Compliance Sprint works (E1+S1, 6–8 weeks)
7. H2 Section 4: What you get — audit-ready ESRS report, real output, real deadline met
8. CTA paragraph: Book ESRS Readiness Assessment OR Start Fast-Track Sprint

Include: EcoHub™ mention, 80–90% cost reduction stat, Cambridge ecosystem credibility.
Return JSON with: title, meta_description, intro, sections (array of h2+content), cta_paragraph, reading_time_minutes.
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "title":             {"type": "string"},
                "meta_description":  {"type": "string"},
                "intro":             {"type": "string"},
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "h2":      {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["h2", "content"],
                        "additionalProperties": False
                    }
                },
                "cta_paragraph":        {"type": "string"},
                "reading_time_minutes": {"type": "integer"}
            },
            "required": ["title", "meta_description", "intro", "sections", "cta_paragraph", "reading_time_minutes"],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "blog_article", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=str(linkedin.campaign_id),
            content_type="blog",
            headline=content["title"],
            body=content["intro"],
            json_output=content,
            usage=result["usage"]
        )

    # ─────────────────────────────────────────────
    # Twitter / X Thread
    # ─────────────────────────────────────────────
    def generate_twitter(self, campaign_id) -> GeneratedContent:
        """
        Generate a Twitter/X thread.
        Opener creates fear, thread educates on CSRD/ESRS,
        final tweet promotes ESRS Readiness Assessment or Fast-Track Sprint.
        """
        campaign, persona, country = self.build_context(campaign_id)
        system_prompt = self._build_system_prompt(campaign, persona, country)

        user_prompt = f"""
Generate a Twitter/X thread for Triple I targeting {persona.name} in {country.name}.

THREAD STRUCTURE:
Tweet 1 (Hook): Bold fear statement — CSRD deadline, compliance risk, or cost of failure
Tweet 2: Explain the regulatory situation in {country.name} — specific and credible
Tweet 3: The problem with current approaches (spreadsheets / manual / legacy tools)
Tweet 4: Introduce Triple I's solution — E1+S1, EcoHub™, 6-week sprint
Tweet 5: Credibility — Cambridge ecosystem, Innovation Award, 80–90% cost reduction
Tweet 6 (CTA): Book ESRS Readiness Assessment or Fast-Track Sprint — link to triplei.io

Rules:
- Each tweet max 280 characters
- Tweet 1 must make people stop scrolling
- Thread should work as a complete sales argument
- Include numbers, deadlines, and framework names
- Hashtags only on tweet 1 and tweet 6

Return JSON with: thread_hook, tweets (array of strings), hashtags (array).
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "thread_hook": {"type": "string"},
                "tweets":      {"type": "array", "items": {"type": "string"}},
                "hashtags":    {"type": "array", "items": {"type": "string"}}
            },
            "required": ["thread_hook", "tweets", "hashtags"],
            "additionalProperties": False
        }

        result  = self._call_model(system_prompt, user_prompt, "twitter_thread", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="twitter",
            headline=content["thread_hook"],
            body="\n\n".join(content["tweets"]),
            json_output=content,
            usage=result["usage"]
        )
