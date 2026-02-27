from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from datetime import datetime


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    persona_id = Column(UUID(as_uuid=True), ForeignKey("personas.id"), nullable=False)
    country_id = Column(UUID(as_uuid=True), ForeignKey("countries.id"), nullable=False)
    framework_focus = Column(String, default="Carbon")  # Carbon | Interoperability | Full ESG
    channel = Column(String, default="LinkedIn")        # LinkedIn | Google | Both
    goal = Column(Text, default="")
    cmo_brief = Column(Text, nullable=True)
    status = Column(String, default="active")           # active | paused | completed | archived
    created_at = Column(DateTime, default=datetime.utcnow)
