import httpx
from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent
from app.config import settings


class LinkedInSchedulerAgent(BaseAgent):
    """
    📅 LinkedIn Scheduler Agent
    Posts content directly to LinkedIn via the LinkedIn API.

    Setup:
    1. Create app at https://www.linkedin.com/developers/apps
    2. Request permissions: r_liteprofile, w_member_social
    3. Complete OAuth2 → copy access token to .env as LINKEDIN_ACCESS_TOKEN
    4. Get Person URN: GET https://api.linkedin.com/v2/me  → set LINKEDIN_PERSON_ID
    5. Optional company page: LINKEDIN_ORG_ID
    """
    AGENT_TYPE = "linkedin_scheduler"
    BASE = "https://api.linkedin.com/v2"

    def check_credentials(self) -> dict:
        token = settings.LINKEDIN_ACCESS_TOKEN
        person_id = settings.LINKEDIN_PERSON_ID
        configured = bool(token and person_id and token != "your-linkedin-oauth2-token")
        return {
            "configured": configured,
            "person_id": person_id if configured else None,
            "has_org_id": bool(settings.LINKEDIN_ORG_ID),
            "message": "Ready to post!" if configured else "Add LINKEDIN_ACCESS_TOKEN + LINKEDIN_PERSON_ID to .env"
        }

    def post_now(self, content_id: str, post_as: str = "person") -> dict:
        record = self.db.query(GeneratedContent).filter(
            GeneratedContent.id == content_id
        ).first()
        if not record:
            raise ValueError(f"Content {content_id} not found")

        text = record.body or record.headline or ""
        if not text:
            raise ValueError("Content has no body text to post")

        token = settings.LINKEDIN_ACCESS_TOKEN
        if not token or token == "your-linkedin-oauth2-token":
            raise ValueError("LinkedIn credentials not configured. Add LINKEDIN_ACCESS_TOKEN to .env")

        author = (
            f"urn:li:organization:{settings.LINKEDIN_ORG_ID}"
            if post_as == "org" and settings.LINKEDIN_ORG_ID
            else f"urn:li:person:{settings.LINKEDIN_PERSON_ID}"
        )

        payload = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text[:3000]},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{self.BASE}/ugcPosts", json=payload, headers=headers)

        if resp.status_code not in (200, 201):
            raise ValueError(f"LinkedIn API error {resp.status_code}: {resp.text[:300]}")

        urn = resp.headers.get("x-restli-id", "posted")
        record.status = "published"
        self.db.commit()
        return {"success": True, "post_urn": urn, "content_id": str(content_id)}

    def schedule_from_distribution_plan(self, distribution_content_id: str,
                                         post_as: str = "person") -> dict:
        plan_record = self.db.query(GeneratedContent).filter(
            GeneratedContent.id == distribution_content_id
        ).first()
        if not plan_record:
            raise ValueError("Distribution plan not found")

        plan_data = plan_record.json_output or {}
        schedule = plan_data.get("weekly_schedule", plan_data.get("schedule", []))

        # Find LinkedIn posts in same campaign
        from app.models.generated_content import GeneratedContent as GC
        li_posts = self.db.query(GC).filter(
            GC.campaign_id == plan_record.campaign_id,
            GC.type == "linkedin",
            GC.status != "published"
        ).all()

        results = []
        for post in li_posts[:5]:
            try:
                r = self.post_now(str(post.id), post_as=post_as)
                results.append({"content_id": str(post.id), "status": "posted", "urn": r.get("post_urn")})
            except Exception as e:
                results.append({"content_id": str(post.id), "status": "failed", "error": str(e)})

        return {
            "scheduled": len([r for r in results if r["status"] == "posted"]),
            "failed": len([r for r in results if r["status"] == "failed"]),
            "results": results
        }
