from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.country import Country
from app.schemas.country import CountryCreate, CountryResponse

router = APIRouter(prefix="/countries", tags=["Countries"])


@router.post("/", response_model=CountryResponse)
def create_country(country: CountryCreate, db: Session = Depends(get_db)):
    db_country = Country(**country.dict())
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country


@router.get("/", response_model=list[CountryResponse])
def list_countries(db: Session = Depends(get_db)):
    return db.query(Country).all()


@router.get("/{country_id}", response_model=CountryResponse)
def get_country(country_id: str, db: Session = Depends(get_db)):
    c = db.query(Country).filter(Country.id == country_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Country not found")
    return c


@router.post("/seed")
def seed_countries(db: Session = Depends(get_db)):
    """Seed all 7 Triple I target markets with cluster assignments."""
    defaults = [
        # ── CLUSTER A — CSRD urgency markets ──────────────────────────
        {
            "name": "Spain",
            "code": "ES",
            "cluster": "CLUSTER_A",
            "notes": "CSRD transposed into Spanish law. Large number of SMEs newly in scope for FY2025 reporting. Regulator: CNMV. Strong demand from manufacturing, retail, and real estate sectors.",
        },
        {
            "name": "France",
            "code": "FR",
            "cluster": "CLUSTER_A",
            "notes": "France has existing DPEF (extra-financial reporting declaration) which maps to CSRD. Advanced ESG awareness. Regulator: AMF. Companies already have some reporting experience. High advisory market.",
        },
        {
            "name": "Netherlands",
            "code": "NL",
            "cluster": "CLUSTER_A",
            "notes": "Strong ESG culture, Amsterdam-based multinationals, high sustainability awareness. AFM regulator. Companies here tend to be ahead of compliance curve but need framework interoperability.",
        },
        {
            "name": "Belgium",
            "code": "BE",
            "cluster": "CLUSTER_A",
            "notes": "Mix of French and Flemish business culture. High density of mid-market companies in CSRD scope. EU headquarters proximity creates regulatory awareness. Strong advisory ecosystem.",
        },
        {
            "name": "Sweden",
            "code": "SE",
            "cluster": "CLUSTER_A",
            "notes": "Highly sustainability-conscious market. Many companies already report voluntarily. CSRD adds formal structure. High willingness to invest in sustainability technology. Strong circular economy focus.",
        },
        # ── CLUSTER B — ISSB/global ESG alignment markets ─────────────
        {
            "name": "UAE",
            "code": "AE",
            "cluster": "CLUSTER_B",
            "notes": "Rapidly growing ESG mandate driven by UAE Net Zero 2050 strategy and Dubai Sustainable Finance Framework. ISSB/IFRS S1&S2 adoption underway. High interest from financial services, real estate, energy sectors. Advisory market growing fast.",
        },
        {
            "name": "Japan",
            "code": "JP",
            "cluster": "CLUSTER_B",
            "notes": "Japan FSA mandating IFRS S1/S2-aligned disclosures for listed companies. Keidanren pushing voluntary ESG. Strong demand from manufacturing multinationals (Toyota, Sony supply chains). Conservative buyers — reliability and audit trail are critical.",
        },
    ]

    created = []
    for d in defaults:
        existing = db.query(Country).filter(Country.name == d["name"]).first()
        if not existing:
            c = Country(**d)
            db.add(c)
            created.append(d["name"])

    db.commit()
    return {"seeded": created, "message": f"Created {len(created)} countries"}
