from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.generated_content import GeneratedContent
from app.schemas.generated_content import GeneratedContentResponse
from typing import Optional, List

router = APIRouter(prefix="/content", tags=["Content"])

@router.get("/", response_model=List[GeneratedContentResponse])
def list_content(
    campaign_id: Optional[str] = None,
    type: Optional[str] = None,           # frontend sends ?type=
    content_type: Optional[str] = None,   # legacy alias
    agent_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(GeneratedContent)
    if campaign_id:
        q = q.filter(GeneratedContent.campaign_id == campaign_id)
    t = type or content_type
    if t:
        q = q.filter(GeneratedContent.type == t)
    if agent_type:
        q = q.filter(GeneratedContent.agent_type == agent_type)
    if status:
        q = q.filter(GeneratedContent.status == status)
    return q.order_by(GeneratedContent.created_at.desc()).all()


@router.get("/stats/summary")
def content_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total      = db.query(func.count(GeneratedContent.id)).scalar()
    total_cost = db.query(func.sum(GeneratedContent.cost_usd)).scalar() or 0.0
    total_tok  = db.query(func.sum(GeneratedContent.total_tokens)).scalar() or 0
    by_type    = db.query(GeneratedContent.type, func.count(GeneratedContent.id)).group_by(GeneratedContent.type).all()
    by_agent   = db.query(GeneratedContent.agent_type, func.count(GeneratedContent.id)).group_by(GeneratedContent.agent_type).all()
    by_status  = db.query(GeneratedContent.status, func.count(GeneratedContent.id)).group_by(GeneratedContent.status).all()
    return {
        "total_pieces": total, "total_cost_usd": round(float(total_cost), 4),
        "total_tokens": total_tok, "avg_cost_usd": round(float(total_cost) / total, 4) if total else 0,
        "by_type": dict(by_type), "by_agent": dict(by_agent), "by_status": dict(by_status),
    }


@router.get("/{content_id}", response_model=GeneratedContentResponse)
def get_content(content_id: str, db: Session = Depends(get_db)):
    c = db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Content not found")
    return c


@router.patch("/{content_id}/status")
def update_content_status(content_id: str, status: str, db: Session = Depends(get_db)):
    c = db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Content not found")
    c.status = status
    db.commit()
    return {"id": content_id, "status": status}


@router.delete("/{content_id}")
def delete_content(content_id: str, db: Session = Depends(get_db)):
    c = db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Content not found")
    db.delete(c)
    db.commit()
    return {"deleted": content_id}
