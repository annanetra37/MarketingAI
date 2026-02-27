from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CountryCreate(BaseModel):
    name: str
    code: Optional[str] = ""
    cluster: Optional[str] = "CLUSTER_A"
    notes: Optional[str] = ""


class CountryResponse(BaseModel):
    id: UUID
    name: str
    code: Optional[str]
    cluster: str
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
