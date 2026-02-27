from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, Integer, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from datetime import datetime


class GeneratedContent(Base):
    __tablename__ = "generated_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)

    # Which agent produced this
    agent_type = Column(String, default="content")
    # content | seo | ads | cmo | research | analytics | budget | distribution | orchestrator

    # Content type
    type = Column(String)
    # linkedin | blog | twitter | seo_report | google_ads | linkedin_ads | cmo_brief
    # research | analytics_report | budget_optimization | distribution_plan | ab_test_analysis

    # Core content
    headline = Column(String)
    body = Column(Text)
    json_output = Column(JSON)

    # Lineage
    parent_content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id"), nullable=True)

    # Token / cost tracking
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)

    # Workflow status
    status = Column(String, default="draft")   # draft | approved | published | archived
    created_at = Column(DateTime, default=datetime.utcnow)
