from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from datetime import datetime


class Country(Base):
    __tablename__ = "countries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    code = Column(String(5))                   # ISO code e.g. "ES", "FR"
    cluster = Column(String, default="CLUSTER_A")  # "CLUSTER_A" | "CLUSTER_B"
    notes = Column(String, default="")         # Market-specific context
    created_at = Column(DateTime, default=datetime.utcnow)
