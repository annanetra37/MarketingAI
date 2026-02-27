from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from datetime import datetime


class Persona(Base):
    __tablename__ = "personas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)        # e.g. "SME", "ADVISORY"
    description = Column(String)
    pains = Column(JSON, default=list)                         # list of pain point strings
    motivations = Column(JSON, default=list)                   # list of motivation strings
    tone_guidelines = Column(String, default="")
    cta = Column(String, default="Book a free demo")
    created_at = Column(DateTime, default=datetime.utcnow)
