"""
autonomous_orchestrator.py — Triple I v4.0
Coordinates all 8 agents. Method names preserved to match generate.py API routes.
"""

import json
from typing import Optional
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.agents.cmo_agent import CMOAgent
from app.agents.content_agent import ContentAgent
from app.agents.seo_agent import SEOAgent
from app.agents.ads_agent import AdsAgent
from app.agents.research_agent import ResearchAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.distribution_agent import DistributionAgent
from app.models.generated_content import GeneratedContent


class AutonomousOrchestrator(BaseAgent):
    """
    🏗 Autonomous Marketing Orchestrator — The CMO Brain on Autopilot

    Runs the full autonomous loop:
    Goal → Research → Strategy → Generate → Distribute → Measure → Auto-adjust

    Loop modes:
      full          — All 9 phases (weekly run)
      generate_only — Strategy + Content + Ads + Distribution (first run)
      analyze_only  — Analytics + A/B test (mid-week check)
      optimize_only — Analytics + Budget (budget reallocation)
      fear_blitz    — CMO brief + LinkedIn + Twitter + Ads (rapid market entry)
    """

    AGENT_TYPE = "orchestrator"

    def __init__(self, db: Session):
        super().__init__(db)
        self.cmo          = CMOAgent(db)
        self.content      = ContentAgent(db)
        self.seo          = SEOAgent(db)
        self.ads          = AdsAgent(db)
        self.research     = ResearchAgent(db)
        self.analytics    = AnalyticsAgent(db)
        self.budget       = BudgetAgent(db)
        self.distribution = DistributionAgent(db)

    # ─────────────────────────────────────────────
    # Main loop
    # ─────────────────────────────────────────────
    def run_autonomous_loop(
        self,
        campaign_id: str,
        loop_mode: str = "full",
        on_step: Optional[callable] = None
    ) -> dict:
        """
        Execute the full autonomous marketing loop for a campaign.
        All agent method names match what's defined in each agent file.
        """

        def step(name, fn):
            try:
                result = fn()
                if on_step:
                    on_step(name, "success", str(result.id) if result else None)
                return {"status": "success", "id": str(result.id) if result else None}
            except Exception as e:
                if on_step:
                    on_step(name, "error", str(e))
                return {"status": "error", "error": str(e)}

        results        = {}
        steps_executed = []

        # ── PHASE 1: CMO STRATEGY BRIEF ────────────────────────────────
        if loop_mode in ("full", "generate_only", "fear_blitz"):
            results["cmo_brief"] = step(
                "cmo_brief",
                lambda: self.cmo.create_campaign_brief(campaign_id)
            )
            steps_executed.append("cmo_brief")

        # ── PHASE 2: RESEARCH ──────────────────────────────────────────
        if loop_mode in ("full", "generate_only"):
            # competitor_analysis() — matches research_agent.py v4 method name
            # Falls back gracefully if method name differs
            results["competitor_analysis"] = step(
                "competitor_analysis",
                lambda: (
                    self.research.competitor_analysis(campaign_id)
                    if hasattr(self.research, "competitor_analysis")
                    else self.research.analyze_competitors(campaign_id)
                )
            )
            steps_executed.append("competitor_analysis")

            results["regulatory_briefing"] = step(
                "regulatory_briefing",
                lambda: self.research.regulatory_briefing(campaign_id)
            )
            steps_executed.append("regulatory_briefing")

        # ── PHASE 3: SEO ───────────────────────────────────────────────
        if loop_mode in ("full", "generate_only"):
            results["seo_keywords"] = step(
                "seo_keywords",
                lambda: self.seo.generate_keyword_cluster(campaign_id)
            )
            steps_executed.append("seo_keywords")

        # ── PHASE 4: CONTENT ───────────────────────────────────────────
        if loop_mode in ("full", "generate_only", "fear_blitz"):
            results["linkedin"] = step(
                "linkedin",
                lambda: self.content.generate_linkedin(campaign_id)
            )
            steps_executed.append("linkedin")

            # Blog expands from LinkedIn — only if LinkedIn succeeded
            if results.get("linkedin", {}).get("status") == "success":
                linkedin_id = results["linkedin"]["id"]
                results["blog"] = step(
                    "blog",
                    lambda: self.content.generate_blog_from_linkedin(linkedin_id)
                )
                steps_executed.append("blog")

            # Twitter — method name: generate_twitter_thread OR generate_twitter
            results["twitter"] = step(
                "twitter",
                lambda: (
                    self.content.generate_twitter_thread(campaign_id)
                    if hasattr(self.content, "generate_twitter_thread")
                    else self.content.generate_twitter(campaign_id)
                )
            )
            steps_executed.append("twitter")

        # ── PHASE 5: ADS ───────────────────────────────────────────────
        if loop_mode in ("full", "generate_only", "fear_blitz"):
            results["google_ads"] = step(
                "google_ads",
                lambda: self.ads.generate_google_ads(campaign_id)
            )
            steps_executed.append("google_ads")

            results["linkedin_ads"] = step(
                "linkedin_ads",
                lambda: self.ads.generate_linkedin_ads(campaign_id)
            )
            steps_executed.append("linkedin_ads")

        # ── PHASE 6: DISTRIBUTION ──────────────────────────────────────
        if loop_mode in ("full", "generate_only"):
            results["distribution_plan"] = step(
                "distribution_plan",
                lambda: self.distribution.create_distribution_plan(campaign_id)
            )
            steps_executed.append("distribution_plan")

        # ── PHASE 7 & 8: ANALYTICS ─────────────────────────────────────
        if loop_mode in ("full", "analyze_only", "optimize_only"):
            # analyze_performance() — v4 method name; falls back to v3 name
            results["analytics_report"] = step(
                "analytics_report",
                lambda: (
                    self.analytics.analyze_performance(campaign_id)
                    if hasattr(self.analytics, "analyze_performance")
                    else self.analytics.analyze_campaign_performance(campaign_id)
                )
            )
            steps_executed.append("analytics_report")

            results["ab_test"] = step(
                "ab_test",
                lambda: (
                    self.analytics.analyze_ab_test(campaign_id)
                    if hasattr(self.analytics, "analyze_ab_test")
                    else self.analytics.run_ab_test_analysis(campaign_id)
                )
            )
            steps_executed.append("ab_test")

        # ── PHASE 9: BUDGET ────────────────────────────────────────────
        if loop_mode in ("full", "optimize_only"):
            results["budget_optimization"] = step(
                "budget_optimization",
                lambda: self.budget.optimize_budget(campaign_id)
            )
            steps_executed.append("budget_optimization")

        # ── LOOP SYNTHESIS ─────────────────────────────────────────────
        loop_summary = self._synthesize_loop(campaign_id, results, steps_executed)

        successes = sum(1 for v in results.values() if isinstance(v, dict) and v.get("status") == "success")
        errors    = sum(1 for v in results.values() if isinstance(v, dict) and v.get("status") == "error")

        return {
            "campaign_id":            campaign_id,
            "loop_mode":              loop_mode,
            "steps_executed":         steps_executed,
            "results":                results,
            "successes":              successes,
            "errors":                 errors,
            "loop_summary":           loop_summary,
            "next_loop_recommended":  loop_summary.get("next_loop_in_days", 7)
        }

    # ─────────────────────────────────────────────
    # Loop synthesis (CMO post-loop report)
    # ─────────────────────────────────────────────
    def _synthesize_loop(self, campaign_id: str, results: dict, steps: list) -> dict:
        """CMO synthesizes loop results into strategic insights for next cycle."""
        try:
            context_parts = {
                "steps_run":    steps,
                "successes":    [k for k, v in results.items() if isinstance(v, dict) and v.get("status") == "success"],
                "errors":       [k for k, v in results.items() if isinstance(v, dict) and v.get("status") == "error"],
                "error_details":{k: v.get("error") for k, v in results.items() if isinstance(v, dict) and v.get("status") == "error"}
            }

            system_prompt = """
You are the CMO for Triple I — an AI-powered ESG & Carbon Reporting B2B SaaS.
You just ran an autonomous marketing loop. Synthesize what happened and define next steps.
Focus on: Fear → ESRS Assessment → Fast-Track Compliance Sprint pipeline.
Be concise, strategic, and focused on what needs to happen next.
            """.strip()

            user_prompt = f"""
Synthesize this autonomous marketing loop:
{json.dumps(context_parts)}

Provide a loop summary with:
1. executive_summary: 2-3 sentence loop overview
2. top_wins: array of 3 key wins from this loop
3. key_blockers: array of main issues to resolve
4. strategy_adjustments: array of strategy changes for next cycle
5. next_loop_in_days: integer (1, 3, or 7)
6. next_loop_priority: single most important thing to do next cycle
7. loop_health: "excellent" | "good" | "needs_attention" | "critical"
            """.strip()

            schema = {
                "type": "object",
                "properties": {
                    "executive_summary":    {"type": "string"},
                    "top_wins":             {"type": "array", "items": {"type": "string"}},
                    "key_blockers":         {"type": "array", "items": {"type": "string"}},
                    "strategy_adjustments": {"type": "array", "items": {"type": "string"}},
                    "next_loop_in_days":    {"type": "integer"},
                    "next_loop_priority":   {"type": "string"},
                    "loop_health":          {"type": "string"}
                },
                "required": [
                    "executive_summary", "top_wins", "key_blockers",
                    "strategy_adjustments", "next_loop_in_days",
                    "next_loop_priority", "loop_health"
                ],
                "additionalProperties": False
            }

            result = self._call_model(system_prompt, user_prompt, "loop_summary", schema)
            return result["content"]

        except Exception as e:
            return {
                "executive_summary":    f"Loop completed with {len(steps)} steps.",
                "top_wins":             ["Content generated", "Pipeline executed"],
                "key_blockers":         [str(e)],
                "strategy_adjustments": ["Review errors and re-run"],
                "next_loop_in_days":    7,
                "next_loop_priority":   "Fix errors and re-run full loop",
                "loop_health":          "needs_attention"
            }

    # ─────────────────────────────────────────────
    # AI Goal Generator
    # Called by: POST /generate/autonomous/generate-goals
    # ─────────────────────────────────────────────
    def auto_generate_campaign_goals(self, persona_id: str, country_id: str) -> dict:
        """
        CMO autonomously generates campaign goals based on ICP + country.
        Method name matches the API route in generate.py — do not rename.
        """
        from app.models.persona import Persona
        from app.models.country import Country

        persona = self.db.query(Persona).filter(Persona.id == persona_id).first()
        country = self.db.query(Country).filter(Country.id == country_id).first()

        if not persona or not country:
            raise ValueError("Invalid persona or country ID")

        system_prompt = """
You are the CMO of Triple I — an AI-powered ESG & Carbon Reporting B2B SaaS.
You autonomously define campaign goals aligned to the Fear → ESRS Assessment →
Fast-Track Compliance Sprint (E1+S1, 6–8 weeks, €5K–€15K) sales motion.
Every goal must be SMART and tied to pipeline velocity.
        """.strip()

        user_prompt = f"""
Generate autonomous campaign goals for:
Persona: {persona.name}
Pains: {json.dumps(persona.pains)}
Motivations: {json.dumps(persona.motivations)}
Country: {country.name}
Cluster: {country.cluster}
Country Notes: {country.notes}

Output:
1. campaign_name: compelling, urgency-driven campaign name
2. primary_goal: main SMART goal tied to pilot pipeline
3. secondary_goals: array of 2 supporting goals
4. framework_focus: "Carbon" | "Interoperability" | "Full ESG"
5. recommended_channel: "LinkedIn" | "Google" | "Both"
6. budget_tier: "starter" | "growth" | "scale"
7. urgency_level: "high" | "medium" | "low" based on CSRD regulatory pressure
8. rationale: why these goals for this persona/country right now
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "campaign_name":       {"type": "string"},
                "primary_goal":        {"type": "string"},
                "secondary_goals":     {"type": "array", "items": {"type": "string"}},
                "framework_focus":     {"type": "string"},
                "recommended_channel": {"type": "string"},
                "budget_tier":         {"type": "string"},
                "urgency_level":       {"type": "string"},
                "rationale":           {"type": "string"}
            },
            "required": [
                "campaign_name", "primary_goal", "secondary_goals",
                "framework_focus", "recommended_channel", "budget_tier",
                "urgency_level", "rationale"
            ],
            "additionalProperties": False
        }

        result = self._call_model(system_prompt, user_prompt, "campaign_goals", schema)
        return result["content"]

    # Alias for backwards compatibility with any code using the v4 name
    generate_goals = auto_generate_campaign_goals