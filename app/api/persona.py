from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.persona import Persona
from app.schemas.persona import PersonaCreate, PersonaResponse

router = APIRouter(prefix="/personas", tags=["Personas"])


@router.post("/", response_model=PersonaResponse)
def create_persona(persona: PersonaCreate, db: Session = Depends(get_db)):
    db_persona = Persona(**persona.dict())
    db.add(db_persona)
    db.commit()
    db.refresh(db_persona)
    return db_persona


@router.get("/", response_model=list[PersonaResponse])
def list_personas(db: Session = Depends(get_db)):
    return db.query(Persona).all()


@router.get("/{persona_id}", response_model=PersonaResponse)
def get_persona(persona_id: str, db: Session = Depends(get_db)):
    p = db.query(Persona).filter(Persona.id == persona_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Persona not found")
    return p


@router.delete("/{persona_id}")
def delete_persona(persona_id: str, db: Session = Depends(get_db)):
    p = db.query(Persona).filter(Persona.id == persona_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Persona not found")
    db.delete(p)
    db.commit()
    return {"deleted": persona_id}


@router.post("/seed")
def seed_personas(db: Session = Depends(get_db)):
    """Seed the two default Triple I personas."""
    defaults = [
        {
            "name": "SME",
            "description": "Mid-market company (250–1500 employees) under CSRD/ESG regulatory pressure.",
            "pains": [
                "Overwhelmed by CSRD/ESRS complexity",
                "No internal ESG expertise",
                "Fear of non-compliance fines",
                "Manual spreadsheet reporting is unsustainable",
                "Auditors demanding more structured data",
                "Multiple frameworks (ESRS, GRI, TCFD) with different requirements",
            ],
            "motivations": [
                "Avoid regulatory penalties",
                "Satisfy auditors and board",
                "Reduce ESG reporting time from months to days",
                "Simple, automated, reliable",
                "Demonstrate sustainability to customers and investors",
            ],
            "tone_guidelines": "Clear, direct, risk-reducing. No jargon. Speak to the CFO and Sustainability Manager who are overwhelmed and scared of getting it wrong.",
            "cta": "Book a free CSRD readiness assessment →",
        },
        {
            "name": "ADVISORY",
            "description": "ESG advisory firm, Big4 sustainability practice, or accounting firm offering ESG services.",
            "pains": [
                "Manual ESG reporting doesn't scale across client portfolio",
                "Framework translation between ESRS/ISSB/GRI is time-consuming",
                "Clients demand faster turnaround",
                "Competitive pressure from larger consultancies",
                "Hard to standardize quality across team",
                "Staff time wasted on repetitive data mapping",
            ],
            "motivations": [
                "Scale ESG services without hiring more staff",
                "Increase margins on ESG engagements",
                "Differentiate from competitors with technology",
                "Serve more clients with same team",
                "Become the go-to ESG tech-enabled advisory",
            ],
            "tone_guidelines": "Strategic, efficiency-driven, peer-to-peer. Speak to a principal or director who thinks in margins and growth. They want competitive advantage.",
            "cta": "See how advisory firms scale ESG with Triple I →",
        },
    ]

    created = []
    for d in defaults:
        existing = db.query(Persona).filter(Persona.name == d["name"]).first()
        if not existing:
            p = Persona(**d)
            db.add(p)
            created.append(d["name"])

    db.commit()
    return {"seeded": created, "message": f"Created {len(created)} personas"}
