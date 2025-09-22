from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from app.schemas.simulation import HoldInstruction

class OROptimizeRequest(BaseModel):
    section_id: int
    train_ids: List[int]
    current_time: Optional[datetime] = None
    headway_minutes: Optional[float] = 2.0
    holds: Optional[List[HoldInstruction]] = None
    section_speed_limit: Optional[int] = None
    time_limit_seconds: Optional[int] = 10

class OROptimizeResult(BaseModel):
    status: Optional[str] = None
    objective: Optional[float] = None
    schedule: List[Any]
    metrics: Any
