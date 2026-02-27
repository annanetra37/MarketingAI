from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


class GeneratedContentResponse(BaseModel):
    id: UUID
    campaign_id: Optional[UUID]
    agent_type: Optional[str]
    type: Optional[str]
    headline: Optional[str]
    body: Optional[str]
    json_output: Optional[Any]
    parent_content_id: Optional[UUID]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    cost_usd: Optional[float]
    status: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
