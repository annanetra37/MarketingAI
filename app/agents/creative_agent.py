import json
from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent
from openai import OpenAI
from app.config import settings
from app import log_bus

client = OpenAI(api_key=settings.OPENAI_API_KEY)

BRAND_STYLE = (
    "Ultra-modern B2B SaaS aesthetic. Near-black background (#030305). "
    "Neon green (#00ff88) and electric cyan (#00ddff) accents. "
    "Clean geometric shapes, data visualization motifs, ESG/sustainability theme: "
    "leaves, carbon molecules, network nodes, globe, compliance checkmarks. "
    "Photorealistic or high-end 3D render style. No text overlaid on image."
)


class CreativeAgent(BaseAgent):
    """
    🎨 Creative Agent
    Generates DALL-E 3 images + video scripts for every content type.
    Falls back gracefully if DALL-E is unavailable.
    """
    AGENT_TYPE = "creative"

    # ── Generate multimedia for a single content piece ──────────────────
    def generate_for_content(self, content_id: str) -> GeneratedContent:
        log_bus.emit("🎨", f"Creative Agent — loading content {content_id[:8]}…", "info")
        source = self.db.query(GeneratedContent).filter(
            GeneratedContent.id == content_id
        ).first()
        if not source:
            log_bus.emit("❌", f"Content {content_id} not found", "error")
            raise ValueError(f"Content {content_id} not found")

        log_bus.emit("✍️", f"Building creative brief for: {source.type}", "info")
        brief = self._make_brief(source)
        log_bus.emit("🖼️", "Calling DALL-E 3 to generate image…", "info")
        image = self._dalle(brief.get("primary_image_prompt", ""))
        if image.get("success"):
            log_bus.emit("🖼️", "DALL-E 3 image generated successfully", "success")
        else:
            log_bus.emit("⚠️", f"DALL-E fallback: {image.get('error','unknown')}", "warn")
        brief["generated_image"] = image
        brief["source_content_id"] = str(source.id)
        brief["source_content_type"] = source.type

        return self._save_content(
            campaign_id=source.campaign_id,
            content_type="multimedia",
            headline=f"🎨 Creative: {source.headline or source.type}",
            body=brief.get("social_caption", "")[:300],
            json_output=brief,
            usage={"input_tokens": 600, "output_tokens": 400,
                   "total_tokens": 1000, "estimated_cost_usd": 0.046},
            parent_content_id=source.id,
        )

    # ── Generate full campaign visual pack ──────────────────────────────
    def generate_for_campaign(self, campaign_id: str) -> GeneratedContent:
        log_bus.emit("🎨", f"Creative Agent — full visual pack for campaign {campaign_id[:8]}…", "info")
        campaign, persona, country = self.build_context(campaign_id)

        system = f"""You are Creative Director for Triple I — AI-powered ESG & Carbon Reporting.
Brand: dark background, neon green (#00ff88), cyan (#00ddff), ultra-modern B2B SaaS.
Campaign: {persona.name} | {country.name} | {campaign.framework_focus} | Goal: {campaign.goal}
Write world-class DALL-E 3 prompts that produce stunning, professional visuals."""

        user = f"""Create a complete visual identity package for this ESG software campaign.

Brand style: {BRAND_STYLE}

Return JSON with these exact keys:
- hero_prompt: main campaign hero image prompt (very detailed, 150+ words)
- linkedin_post_prompt: square 1:1 LinkedIn feed visual
- linkedin_banner_prompt: wide 1.91:1 LinkedIn sponsored banner
- google_display_prompt: Google Display Ad visual
- twitter_header_prompt: Twitter/X thread header card
- email_header_prompt: email newsletter header
- video_script: object with keys: title, duration_seconds, hook, scenes (array of: scene_number, duration_seconds, visual_description, voiceover_text, b_roll_notes), cta_scene (visual, voiceover, text_overlay), music_mood, style_notes
- creative_rationale: why these visuals resonate with {persona.name} in {country.name}
- color_palette: array of objects with hex and usage
- typography_recommendations: headline font, body font, usage notes"""

        schema = {
            "type": "object",
            "properties": {
                "hero_prompt": {"type": "string"},
                "linkedin_post_prompt": {"type": "string"},
                "linkedin_banner_prompt": {"type": "string"},
                "google_display_prompt": {"type": "string"},
                "twitter_header_prompt": {"type": "string"},
                "email_header_prompt": {"type": "string"},
                "video_script": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "duration_seconds": {"type": "integer"},
                        "hook": {"type": "string"},
                        "scenes": {"type": "array", "items": {
                            "type": "object",
                            "properties": {
                                "scene_number": {"type": "integer"},
                                "duration_seconds": {"type": "integer"},
                                "visual_description": {"type": "string"},
                                "voiceover_text": {"type": "string"},
                                "b_roll_notes": {"type": "string"}
                            },
                            "required": ["scene_number","duration_seconds","visual_description","voiceover_text","b_roll_notes"],
                            "additionalProperties": False
                        }},
                        "cta_scene": {"type": "object",
                            "properties": {"visual": {"type": "string"}, "voiceover": {"type": "string"}, "text_overlay": {"type": "string"}},
                            "required": ["visual","voiceover","text_overlay"], "additionalProperties": False},
                        "music_mood": {"type": "string"},
                        "style_notes": {"type": "string"}
                    },
                    "required": ["title","duration_seconds","hook","scenes","cta_scene","music_mood","style_notes"],
                    "additionalProperties": False
                },
                "creative_rationale": {"type": "string"},
                "color_palette": {"type": "array", "items": {
                    "type": "object",
                    "properties": {"hex": {"type": "string"}, "usage": {"type": "string"}},
                    "required": ["hex","usage"], "additionalProperties": False
                }},
                "typography_recommendations": {"type": "string"}
            },
            "required": ["hero_prompt","linkedin_post_prompt","linkedin_banner_prompt",
                         "google_display_prompt","twitter_header_prompt","email_header_prompt",
                         "video_script","creative_rationale","color_palette","typography_recommendations"],
            "additionalProperties": False
        }

        result = self._call_model(system, user, "campaign_creative", schema)
        data = result["content"]
        log_bus.emit("🖼️", "Generating hero image with DALL-E 3…", "info")
        data["generated_hero_image"] = self._dalle(data["hero_prompt"])
        if data["generated_hero_image"].get("success"):
            log_bus.emit("🖼️", "Hero image generated!", "success")
        else:
            log_bus.emit("⚠️", "DALL-E fallback — use prompt manually", "warn")

        return self._save_content(
            campaign_id=campaign_id,
            content_type="multimedia",
            headline=f"🎨 Visual Pack — {campaign.name}",
            body=data["creative_rationale"][:300],
            json_output=data,
            usage=result["usage"],
        )

    # ── Internal: creative brief for one piece ───────────────────────────
    def _make_brief(self, source) -> dict:
        type_hints = {
            "linkedin": "Square 1:1, stops scroll, professional but bold.",
            "blog": "Wide 16:9 hero, cinematic editorial quality.",
            "twitter": "16:9 header card, bold high-contrast shareable.",
            "google_ads": "Clean display ad, high contrast, minimal.",
            "linkedin_ads": "LinkedIn banner, professional, aspirational.",
            "cmo_brief": "Executive document header, authority.",
            "research": "Data visualization, market intelligence.",
            "distribution_plan": "Content calendar planning aesthetic.",
            "analytics_report": "Dashboard KPI visualization.",
            "budget_optimization": "Finance ROI optimization visual.",
        }
        hint = type_hints.get(source.type, "Professional B2B SaaS visual.")
        snippet = (source.body or "")[:400]

        user = f"""Generate multimedia package for:
Type: {source.type}
Headline: {source.headline or ""}
Content: {snippet}
Platform: {hint}
Brand: {BRAND_STYLE}

Return JSON:
- primary_image_prompt: detailed DALL-E 3 prompt (100+ words, specific lighting, composition, mood)
- platform_specs: array of objects with platform, dimensions, format_notes
- image_alt_text: SEO alt text
- social_caption: ready-to-post caption
- video_concept: 30-second video concept
- design_notes: instructions for human designer"""

        schema = {
            "type": "object",
            "properties": {
                "primary_image_prompt": {"type": "string"},
                "platform_specs": {"type": "array", "items": {
                    "type": "object",
                    "properties": {"platform": {"type": "string"}, "dimensions": {"type": "string"}, "format_notes": {"type": "string"}},
                    "required": ["platform","dimensions","format_notes"], "additionalProperties": False
                }},
                "image_alt_text": {"type": "string"},
                "social_caption": {"type": "string"},
                "video_concept": {"type": "string"},
                "design_notes": {"type": "string"}
            },
            "required": ["primary_image_prompt","platform_specs","image_alt_text","social_caption","video_concept","design_notes"],
            "additionalProperties": False
        }

        result = self._call_model(
            "You are a world-class creative director for B2B SaaS. Write stunning DALL-E 3 prompts.",
            user, "creative_brief", schema
        )
        return result["content"]

    # ── DALL-E 3 image generation ────────────────────────────────────────
    def _dalle(self, prompt: str) -> dict:
        try:
            resp = client.images.generate(
                model="dall-e-3",
                prompt=prompt[:4000],
                size="1024x1024",
                quality="hd",
                style="vivid",
                n=1,
                response_format="url",
            )
            return {
                "success": True,
                "url": resp.data[0].url,
                "revised_prompt": getattr(resp.data[0], "revised_prompt", prompt),
                "model": "dall-e-3",
                "note": "URL expires ~1 hour — save immediately"
            }
        except Exception as e:
            return {
                "success": False,
                "url": None,
                "error": str(e),
                "prompt_for_manual_generation": prompt,
                "fallback": "Use prompt above in Midjourney, Adobe Firefly, or Canva AI"
            }
