import json
from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent


class DistributionAgent(BaseAgent):
    """
    📣 Distribution Agent
    Plans & executes content deployment across channels.
    Manages posting schedules, SEO deployment, email flows, and ad launches.
    In production, integrates with platform APIs.
    """

    AGENT_TYPE = "distribution"

    def create_distribution_plan(self, campaign_id: str) -> GeneratedContent:
        """
        Creates a comprehensive multi-channel distribution plan
        for all generated content in a campaign.
        """
        campaign, persona, country = self.build_context(campaign_id)

        # Gather all approved/draft content
        content_records = (
            self.db.query(GeneratedContent)
            .filter(GeneratedContent.campaign_id == campaign_id)
            .all()
        )

        content_inventory = [
            {"type": r.type, "headline": r.headline, "status": r.status}
            for r in content_records
        ]

        system_prompt = """
You are the Distribution Agent for Triple I's autonomous marketing system.

You are the execution layer. You translate strategy into precise deployment plans:
- Optimal posting times per channel and region
- Content sequencing for funnel progression
- Cross-channel amplification tactics
- Email nurture sequence triggers
- SEO content deployment cadence
- Ad launch timing and dayparting

You think like a growth hacker with media buyer instincts.
ESG/B2B SaaS context: your audience is compliance officers and ESG advisors.
They check LinkedIn 8–9am and 12–1pm on weekdays. Decision cycles are 3–6 months.
        """.strip()

        user_prompt = f"""
Create a distribution plan for:

Campaign: {campaign.name}
Goal: {campaign.goal}
Channel: {campaign.channel}
Persona: {persona.name}
Country: {country.name} (Cluster: {country.cluster})
Content Ready: {json.dumps(content_inventory)}

Produce:
1. weekly_schedule: day-by-day posting plan for next 7 days
2. channel_tactics: specific tactics per channel (LinkedIn, Google, Email, SEO)
3. posting_times: optimal times per channel for this country/persona
4. content_sequence: recommended order of content for funnel flow
5. amplification_tactics: cross-channel amplification moves
6. email_flow: 3-email nurture sequence triggered by content engagement
7. seo_deployment: when and how to publish blog content for max SEO impact
8. automation_triggers: what actions should auto-trigger what next
9. distribution_kpis: what to measure to know if distribution is working
10. quick_wins: 3 things to deploy in next 24 hours for immediate impact
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "weekly_schedule": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "day": {"type": "string"},
                            "actions": {"type": "array", "items": {"type": "string"}},
                            "channel": {"type": "string"},
                            "time": {"type": "string"}
                        },
                        "required": ["day", "actions", "channel", "time"],
                        "additionalProperties": False
                    }
                },
                "channel_tactics": {
                    "type": "object",
                    "properties": {
                        "linkedin": {"type": "string"},
                        "google": {"type": "string"},
                        "email": {"type": "string"},
                        "seo": {"type": "string"}
                    },
                    "required": ["linkedin", "google", "email", "seo"],
                    "additionalProperties": False
                },
                "posting_times": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "channel": {"type": "string"},
                            "best_time": {"type": "string"},
                            "rationale": {"type": "string"}
                        },
                        "required": ["channel", "best_time", "rationale"],
                        "additionalProperties": False
                    }
                },
                "content_sequence": {"type": "array", "items": {"type": "string"}},
                "amplification_tactics": {"type": "array", "items": {"type": "string"}},
                "email_flow": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "email_number": {"type": "integer"},
                            "trigger": {"type": "string"},
                            "subject": {"type": "string"},
                            "goal": {"type": "string"},
                            "send_timing": {"type": "string"}
                        },
                        "required": ["email_number", "trigger", "subject", "goal", "send_timing"],
                        "additionalProperties": False
                    }
                },
                "seo_deployment": {"type": "string"},
                "automation_triggers": {"type": "array", "items": {"type": "string"}},
                "distribution_kpis": {"type": "array", "items": {"type": "string"}},
                "quick_wins": {"type": "array", "items": {"type": "string"}}
            },
            "required": [
                "weekly_schedule", "channel_tactics", "posting_times",
                "content_sequence", "amplification_tactics", "email_flow",
                "seo_deployment", "automation_triggers", "distribution_kpis", "quick_wins"
            ],
            "additionalProperties": False
        }

        result = self._call_model(system_prompt, user_prompt, "distribution_plan", schema)
        content = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="distribution_plan",
            headline=f"Distribution Plan: {campaign.name}",
            body=f"Quick wins: {'; '.join(content['quick_wins'][:2])}",
            json_output=content,
            usage=result["usage"]
        )
