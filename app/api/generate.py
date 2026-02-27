from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.agents.content_agent import ContentAgent
from app.agents.seo_agent import SEOAgent
from app.agents.ads_agent import AdsAgent
from app.agents.cmo_agent import CMOAgent
from app.agents.research_agent import ResearchAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.distribution_agent import DistributionAgent
from app.agents.autonomous_orchestrator import AutonomousOrchestrator
from app.agents.creative_agent import CreativeAgent
from app.agents.prospect_hunter_agent import ProspectHunterAgent
from app.agents.outreach_agent import OutreachAgent
from app.agents.linkedin_scheduler_agent import LinkedInSchedulerAgent
from app.schemas.generated_content import GeneratedContentResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/generate", tags=["Generate"])

# ── Content ───────────────────────────────────────────────────────────────
@router.post("/linkedin/{campaign_id}", response_model=GeneratedContentResponse)
def generate_linkedin(campaign_id: str, db: Session = Depends(get_db)):
    try: return ContentAgent(db).generate_linkedin(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/blog-from-linkedin/{content_id}", response_model=GeneratedContentResponse)
def generate_blog(content_id: str, db: Session = Depends(get_db)):
    try: return ContentAgent(db).generate_blog_from_linkedin(content_id)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/twitter/{campaign_id}", response_model=GeneratedContentResponse)
def generate_twitter(campaign_id: str, db: Session = Depends(get_db)):
    try: return ContentAgent(db).generate_twitter_thread(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

# ── SEO ───────────────────────────────────────────────────────────────────
@router.post("/seo/keywords/{campaign_id}", response_model=GeneratedContentResponse)
def generate_seo_keywords(campaign_id: str, db: Session = Depends(get_db)):
    try: return SEOAgent(db).generate_keyword_cluster(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/seo/optimize/{content_id}", response_model=GeneratedContentResponse)
def optimize_seo(content_id: str, db: Session = Depends(get_db)):
    try: return SEOAgent(db).optimize_content(content_id)
    except Exception as e: raise HTTPException(500, str(e))

# ── Ads ───────────────────────────────────────────────────────────────────
@router.post("/ads/google/{campaign_id}", response_model=GeneratedContentResponse)
def generate_google_ads(campaign_id: str, db: Session = Depends(get_db)):
    try: return AdsAgent(db).generate_google_ads(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/ads/linkedin/{campaign_id}", response_model=GeneratedContentResponse)
def generate_linkedin_ads(campaign_id: str, db: Session = Depends(get_db)):
    try: return AdsAgent(db).generate_linkedin_ads(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

# ── CMO ───────────────────────────────────────────────────────────────────
@router.post("/cmo/brief/{campaign_id}", response_model=GeneratedContentResponse)
def generate_cmo_brief(campaign_id: str, db: Session = Depends(get_db)):
    try: return CMOAgent(db).create_campaign_brief(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/cmo/pipeline/{campaign_id}")
def run_pipeline(campaign_id: str, db: Session = Depends(get_db)):
    try: return CMOAgent(db).run_full_pipeline(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

class ChatMessage(BaseModel):
    message: str
    context: Optional[dict] = None

@router.post("/cmo/chat")
def cmo_chat(payload: ChatMessage, db: Session = Depends(get_db)):
    try: return {"reply": CMOAgent(db).chat(payload.message, payload.context)}
    except Exception as e: raise HTTPException(500, str(e))

# ── Research ──────────────────────────────────────────────────────────────
@router.post("/research/competitors/{campaign_id}", response_model=GeneratedContentResponse)
def research_competitors(campaign_id: str, db: Session = Depends(get_db)):
    try: return ResearchAgent(db).analyze_competitors(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/research/regulatory/{campaign_id}", response_model=GeneratedContentResponse)
def regulatory_briefing(campaign_id: str, db: Session = Depends(get_db)):
    try: return ResearchAgent(db).regulatory_briefing(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

# ── Analytics ─────────────────────────────────────────────────────────────
@router.post("/analytics/performance/{campaign_id}", response_model=GeneratedContentResponse)
def analyze_performance(campaign_id: str, db: Session = Depends(get_db)):
    try: return AnalyticsAgent(db).analyze_campaign_performance(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/analytics/ab-test/{campaign_id}", response_model=GeneratedContentResponse)
def run_ab_test(campaign_id: str, db: Session = Depends(get_db)):
    try: return AnalyticsAgent(db).run_ab_test_analysis(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

# ── Budget ────────────────────────────────────────────────────────────────
@router.post("/budget/optimize/{campaign_id}", response_model=GeneratedContentResponse)
def optimize_budget(campaign_id: str, db: Session = Depends(get_db)):
    try: return BudgetAgent(db).optimize_budget(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

# ── Distribution ──────────────────────────────────────────────────────────
@router.post("/distribution/plan/{campaign_id}", response_model=GeneratedContentResponse)
def create_distribution_plan(campaign_id: str, db: Session = Depends(get_db)):
    try: return DistributionAgent(db).create_distribution_plan(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

# ── Autonomous Loop ───────────────────────────────────────────────────────
class LoopRequest(BaseModel):
    loop_mode: str = "full"

@router.post("/autonomous/loop/{campaign_id}")
def run_autonomous_loop(campaign_id: str, payload: LoopRequest, db: Session = Depends(get_db)):
    try: return AutonomousOrchestrator(db).run_autonomous_loop(campaign_id, loop_mode=payload.loop_mode)
    except Exception as e: raise HTTPException(500, str(e))

class AutoGoalsRequest(BaseModel):
    persona_id: str
    country_id: str

@router.post("/autonomous/generate-goals")
def auto_generate_goals(payload: AutoGoalsRequest, db: Session = Depends(get_db)):
    try: return AutonomousOrchestrator(db).auto_generate_campaign_goals(payload.persona_id, payload.country_id)
    except Exception as e: raise HTTPException(500, str(e))

# ── Creative Agent ────────────────────────────────────────────────────────
@router.post("/creative/for-content/{content_id}", response_model=GeneratedContentResponse)
def generate_creative_for_content(content_id: str, db: Session = Depends(get_db)):
    """🎨 Generate DALL-E 3 image + video script for any content piece."""
    try: return CreativeAgent(db).generate_for_content(content_id)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/creative/campaign/{campaign_id}", response_model=GeneratedContentResponse)
def generate_campaign_creative(campaign_id: str, db: Session = Depends(get_db)):
    """🎨 Full visual pack: hero image + all channel variants + video script."""
    try: return CreativeAgent(db).generate_for_campaign(campaign_id)
    except Exception as e: raise HTTPException(500, str(e))

# ── Prospect Hunter ───────────────────────────────────────────────────────
class ProspectHuntRequest(BaseModel):
    country_name: str
    cluster: str = "CLUSTER_A"
    persona_name: str = "SME"
    industry_focus: str = "all"
    min_employees: int = 250
    max_employees: int = 5000
    campaign_id: Optional[str] = None

@router.post("/prospects/hunt", response_model=GeneratedContentResponse)
def hunt_prospects(payload: ProspectHuntRequest, db: Session = Depends(get_db)):
    """🎯 Find 15 product-qualified ESG software prospects in any country."""
    try:
        return ProspectHunterAgent(db).hunt_prospects(
            country_name=payload.country_name, cluster=payload.cluster,
            persona_name=payload.persona_name, industry_focus=payload.industry_focus,
            min_employees=payload.min_employees, max_employees=payload.max_employees,
            campaign_id=payload.campaign_id,
        )
    except Exception as e: raise HTTPException(500, str(e))

class ProspectScoreRequest(BaseModel):
    company_name: str
    country: str
    campaign_id: Optional[str] = None

@router.post("/prospects/score", response_model=GeneratedContentResponse)
def score_prospect(payload: ProspectScoreRequest, db: Session = Depends(get_db)):
    """🎯 Score a specific company 1-100 as a Triple I prospect."""
    try:
        return ProspectHunterAgent(db).score_prospect(
            company_name=payload.company_name, country=payload.country,
            campaign_id=payload.campaign_id,
        )
    except Exception as e: raise HTTPException(500, str(e))

# ── Outreach Agent ────────────────────────────────────────────────────────
class OutreachRequest(BaseModel):
    company_name: str
    country: str
    persona_name: str = "SME"
    pain_point: str = ""
    trigger_event: str = ""
    decision_maker_title: str = "Sustainability Manager"
    industry: str = ""
    cluster: str = "CLUSTER_A"
    qualification_score: int = 80
    campaign_id: Optional[str] = None

@router.post("/outreach/sequence", response_model=GeneratedContentResponse)
def generate_outreach_sequence(payload: OutreachRequest, db: Session = Depends(get_db)):
    """📧 5-touch personalized email + LinkedIn sequence for a specific prospect."""
    try:
        return OutreachAgent(db).generate_email_sequence(
            company_name=payload.company_name,
            country=payload.country,
            persona_name=payload.persona_name,
            pain_point=payload.pain_point or "ESG reporting complexity",
            trigger_event=payload.trigger_event or "CSRD deadline approaching",
            key_title=payload.decision_maker_title,
            industry=payload.industry,
            cluster=payload.cluster,
            qualification_score=payload.qualification_score,
            campaign_id=payload.campaign_id,
        )
    except Exception as e: raise HTTPException(500, str(e))

class BulkOutreachRequest(BaseModel):
    prospect_list_content_id: str
    top_n: int = 5
    campaign_id: Optional[str] = None

@router.post("/outreach/bulk")
def generate_bulk_outreach(payload: BulkOutreachRequest, db: Session = Depends(get_db)):
    """📧 Auto-generate sequences for the top N prospects from a prospect list."""
    try:
        results = OutreachAgent(db).generate_bulk_sequences(
            prospect_list_content_id=payload.prospect_list_content_id,
            max_prospects=payload.top_n,
            campaign_id=payload.campaign_id,
        )
        ok  = [r for r in results if r.get("status") == "generated"]
        bad = [r for r in results if r.get("status") == "failed"]
        return {"sequences_created": len(ok), "failed": len(bad), "results": results}
    except Exception as e: raise HTTPException(500, str(e))

# ── LinkedIn Scheduler ────────────────────────────────────────────────────
@router.get("/linkedin/check-credentials")
def check_linkedin_credentials(db: Session = Depends(get_db)):
    try: return LinkedInSchedulerAgent(db).check_credentials()
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/linkedin/post-now/{content_id}")
def linkedin_post_now(content_id: str, post_as: str = "person", db: Session = Depends(get_db)):
    try: return LinkedInSchedulerAgent(db).post_now(content_id, post_as=post_as)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/linkedin/schedule-from-plan/{distribution_content_id}")
def schedule_from_plan(distribution_content_id: str, post_as: str = "person", db: Session = Depends(get_db)):
    try: return LinkedInSchedulerAgent(db).schedule_from_distribution_plan(distribution_content_id, post_as=post_as)
    except Exception as e: raise HTTPException(500, str(e))
