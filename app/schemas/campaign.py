from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CampaignCreate(BaseModel):
    name: str
    persona_id: UUID
    country_id: UUID
    framework_focus: Optional[str] = "Carbon"
    channel: Optional[str] = "LinkedIn"
    goal: Optional[str] = ""


class CampaignResponse(BaseModel):
    id: UUID
    name: str
    persona_id: UUID
    country_id: UUID
    framework_focus: Optional[str]
    channel: Optional[str]
    goal: Optional[str]
    cmo_brief: Optional[str]
    status: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
