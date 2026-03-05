"""
autonomous_orchestrator.py
==========================
Autonomous Loop Coordinator for Triple I's marketing system.

The loop is designed around ONE goal: sign a Fast-Track Compliance Sprint
pilot (€5K–€15K) within 6 weeks in Cluster A European markets.

Loop modes:
- full:          All 13 steps — weekly autonomous run
- generate_only: Strategy + Content + Ads + Distribution — first run
- analyze_only:  Analytics + A/B test — quick performance check
- optimize_only: Analytics + Budget — budget reallocation only
- fear_blitz:    NEW — rapid fear-hook content for immediate market entry
"""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent
from app.agents.triple_i_context import get_master_context, SALES_STRATEGY, MARKETS
from app.models.generated_content import GeneratedContent
from app import log_bus


class AutonomousOrchestrator(BaseAgent):
    """
    🔄 Autonomous Loop Orchestrator
    Coordinates all 8 agents in sequence to execute the Fear → Pilot → Close
    sales motion continuously and self-improve each cycle.
    """

    AGENT_TYPE = "orchestrator"

    def run_autonomous_loop(self, campaign_id: str, loop_mode: str = "full") -> dict:
        """
        Execute the autonomous marketing loop.

        Loop modes:
          full          — All 13 steps. Run weekly.
          generate_only — Steps 1–6. First-run campaign launch.
          analyze_only  — Steps 7–9. Mid-week performance check.
          optimize_only — Steps 7 + 9. Budget reallocation only.
          fear_blitz    — Steps 1, 3, 4, 5. Rapid fear-hook content push for fast market entry.
        """
        from app.agents.cmo_agent import CMOAgent
        from app.agents.research_agent import ResearchAgent
        from app.agents.seo_agent import SEOAgent
        from app.agents.content_agent import ContentAgent
        from app.agents.ads_agent import AdsAgent
        from app.agents.distribution_agent import DistributionAgent
        from app.agents.analytics_agent import AnalyticsAgent
        from app.agents.budget_agent import BudgetAgent

        campaign, persona, country = self.build_context(campaign_id)

        results = {}
        errors  = {}
        log     = []

        def step(name: str, fn):
            """Execute a single loop step with error capture and logging."""
            log_bus.emit("🔄", f"Starting: {name}", "info")
            try:
                result = fn()
                results[name] = str(result.id) if hasattr(result, "id") else str(result)
                log_bus.emit("✅", f"Completed: {name}", "success")
                log.append({"step": name, "status": "ok", "id": results[name]})
            except Exception as e:
                errors[name] = str(e)
                log_bus.emit("❌", f"Failed: {name} — {str(e)}", "error")
                log.append({"step": name, "status": "error", "error": str(e)})

        # ─── Define all steps ────────────────────────────────────────
        cmo        = CMOAgent(self.db)
        research   = ResearchAgent(self.db)
        seo        = SEOAgent(self.db)
        content    = ContentAgent(self.db)
        ads        = AdsAgent(self.db)
        distrib    = DistributionAgent(self.db)
        analytics  = AnalyticsAgent(self.db)
        budget     = BudgetAgent(self.db)

        all_steps = {
            # Step 1 — CMO creates fear-first campaign brief
            "1_cmo_brief": lambda: cmo.create_campaign_brief(campaign_id),

            # Step 2 — Research: find regulatory urgency + competitive gaps
            "2_regulatory_briefing": lambda: research.regulatory_briefing(campaign_id),

            # Step 3 — SEO: capture CSRD fear-stage and conversion-stage searches
            "3_seo_keywords": lambda: seo.generate_keyword_cluster(campaign_id),

            # Step 4 — Content: fear-first LinkedIn post
            "4_linkedin": lambda: content.generate_linkedin(campaign_id),

            # Step 5 — Content: Twitter/X fear thread
            "5_twitter": lambda: content.generate_twitter(campaign_id),

            # Step 6 — Ads: Google + LinkedIn with A/B variants
            "6_google_ads":   lambda: ads.generate_google_ads(campaign_id),
            "7_linkedin_ads": lambda: ads.generate_linkedin_ads(campaign_id),

            # Step 7 (blog depends on LinkedIn — run after step 4 result)
            "8_blog": None,  # set dynamically below

            # Step 8 — Distribution: 6-week sales motion deployment plan
            "9_distribution": lambda: distrib.create_distribution_plan(campaign_id),

            # Step 9 — Competitor analysis
            "10_competitor_analysis": lambda: research.competitor_analysis(campaign_id),

            # Step 10 — Analytics: funnel performance + pipeline forecast
            "11_analytics": lambda: analytics.analyze_performance(campaign_id),

            # Step 11 — A/B test analysis: which fear hooks win?
            "12_ab_test": lambda: analytics.analyze_ab_test(campaign_id),

            # Step 12 — Budget: optimise spend toward pilot conversions
            "13_budget": lambda: budget.optimize_budget(campaign_id),
        }

        # ─── Execute by mode ─────────────────────────────────────────
        log_bus.emit(
            "🚀",
            f"Triple I Autonomous Loop [{loop_mode.upper()}] — {campaign.name} | {country.name}",
            "info"
        )
        log_bus.emit(
            "🎯",
            f"Goal: Fear → ESRS Assessment → Fast-Track Sprint pilot in 6 weeks",
            "info"
        )

        if loop_mode == "full":
            active = [
                "1_cmo_brief", "2_regulatory_briefing", "3_seo_keywords",
                "4_linkedin", "5_twitter", "6_google_ads", "7_linkedin_ads",
                "9_distribution", "10_competitor_analysis",
                "11_analytics", "12_ab_test", "13_budget"
            ]
        elif loop_mode == "generate_only":
            active = [
                "1_cmo_brief", "3_seo_keywords",
                "4_linkedin", "5_twitter", "6_google_ads", "7_linkedin_ads",
                "9_distribution"
            ]
        elif loop_mode == "analyze_only":
            active = ["11_analytics", "12_ab_test"]

        elif loop_mode == "optimize_only":
            active = ["11_analytics", "13_budget"]

        elif loop_mode == "fear_blitz":
            # Fastest path to market: CMO brief → LinkedIn → Twitter → Ads
            # Use this for immediate Cluster A entry
            active = [
                "1_cmo_brief", "4_linkedin", "5_twitter",
                "6_google_ads", "7_linkedin_ads"
            ]
            log_bus.emit("⚡", "FEAR BLITZ MODE — rapid content push for fast market entry", "info")

        else:
            active = ["1_cmo_brief"]  # fallback

        # Execute active steps
        for step_name in active:
            fn = all_steps.get(step_name)
            if fn:
                step(step_name, fn)

        # Blog depends on LinkedIn completing successfully
        if "4_linkedin" in active and "4_linkedin" in results:
            linkedin_id = results["4_linkedin"]
            step("8_blog", lambda: content.generate_blog_from_linkedin(linkedin_id))

        # ─── CMO synthesis ───────────────────────────────────────────
        synthesis = self._synthesize_loop(
            campaign_id=campaign_id,
            campaign_name=campaign.name,
            persona=persona.name,
            country=country.name,
            loop_mode=loop_mode,
            results=results,
            errors=errors,
            cmo=cmo
        )

        log_bus.emit(
            "🏁",
            f"Loop complete — {len(results)} steps succeeded, {len(errors)} errors",
            "success" if not errors else "warning"
        )

        return {
            "campaign_id":   campaign_id,
            "campaign_name": campaign.name,
            "loop_mode":     loop_mode,
            "country":       country.name,
            "persona":       persona.name,
            "completed_at":  datetime.utcnow().isoformat(),
            "steps_ok":      len(results),
            "steps_failed":  len(errors),
            "generated":     results,
            "errors":        errors,
            "synthesis":     synthesis,
            "log":           log
        }

    def _synthesize_loop(self, campaign_id, campaign_name, persona, country,
                         loop_mode, results, errors, cmo) -> str:
        """Have the CMO synthesise the loop results and recommend next cycle priorities."""
        synthesis_prompt = f"""
The autonomous marketing loop just completed for:
Campaign: {campaign_name}
Country: {country}
Persona: {persona}
Mode: {loop_mode}

Steps completed: {list(results.keys())}
Errors: {list(errors.keys()) if errors else 'None'}

As the CMO for Triple I, provide a 3-sentence synthesis:
1. What was achieved in this loop (fear-hook content created, pipeline actions taken)
2. The #1 priority for the next loop cycle to advance toward a Fast-Track Sprint pilot
3. Any urgent action the sales team should take THIS WEEK based on what was generated

Keep it tactical, brief, and focused on closing a pilot within 6 weeks.
        """.strip()

        try:
            result = cmo.chat(synthesis_prompt)
            return result
        except Exception as e:
            return f"Synthesis unavailable: {str(e)}"

    def generate_goals(self, persona_id: str, country_id: str) -> dict:
        """
        AI-generated campaign goals using CMO strategy.
        Returns 3 goal options mapped to the Fast-Track Sprint sales motion.
        """
        from app.models.persona import Persona
        from app.models.country import Country
        from app.agents.cmo_agent import CMOAgent

        persona = self.db.query(Persona).filter(Persona.id == persona_id).first()
        country = self.db.query(Country).filter(Country.id == country_id).first()

        if not persona or not country:
            raise ValueError("Persona or country not found")

        system_prompt = f"""
You are the CMO for Triple I.

{get_master_context()}

Generate 3 campaign goal options. Each goal must:
1. Be directly tied to the Fast-Track Compliance Sprint (E1+S1, 6–8 weeks, €5K–€15K)
2. Include a specific target metric (e.g. "5 ESRS Assessment completions per week")
3. Be achievable within 6 weeks given {country.name} market dynamics
4. Map to one of: awareness (fear stage), lead-gen (assessment stage), or conversion (sprint stage)
        """.strip()

        user_prompt = f"""
Generate 3 smart campaign goals for:
Persona: {persona.name} ({', '.join(persona.pains[:2]) if persona.pains else 'compliance-driven'})
Country: {country.name} (Cluster: {country.cluster})
Context: {country.notes}

Return JSON: goals (array of 3 objects with: goal_title, description, primary_metric, funnel_stage, timeline)
        """.strip()

        schema = {
            "type": "object",
            "properties": {
                "goals": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "goal_title":       {"type": "string"},
                            "description":      {"type": "string"},
                            "primary_metric":   {"type": "string"},
                            "funnel_stage":     {"type": "string"},
                            "timeline":         {"type": "string"}
                        },
                        "required": ["goal_title", "description", "primary_metric",
                                     "funnel_stage", "timeline"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["goals"],
            "additionalProperties": False
        }

        result = CMOAgent(self.db)._call_model(
            system_prompt, user_prompt, "goal_generator", schema
        )
        return result["content"]
