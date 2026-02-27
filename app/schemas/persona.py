from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class PersonaCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    pains: Optional[List[str]] = []
    motivations: Optional[List[str]] = []
    tone_guidelines: Optional[str] = ""
    cta: Optional[str] = "Book a free demo"


class PersonaResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    pains: Optional[List[str]]
    motivations: Optional[List[str]]
    tone_guidelines: Optional[str]
    cta: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
