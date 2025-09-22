from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class PrecedenceRequest(BaseModel):
    section_id: int
    train_ids: List[int]
    current_time: Optional[datetime] = None

class DecisionCreate(BaseModel):
    decision_type: str
    train_id: Optional[int] = None
    section_id: Optional[int] = None
    details: Optional[Any] = None
    explanation: Optional[str] = None

class DecisionRead(BaseModel):
    id: int
    decision_type: str
    status: str
    train_id: Optional[int]
    section_id: Optional[int]
    details: Optional[Any]
    explanation: Optional[str]
    recommended_by: Optional[str]
    approved_by: Optional[str]
    created_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }
