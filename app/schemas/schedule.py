from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScheduleRead(BaseModel):
    id: int
    train_id: int
    section_id: int
    planned_entry: datetime
    planned_exit: datetime
    actual_entry: Optional[datetime] = None
    actual_exit: Optional[datetime] = None
    platform: Optional[str] = None
    track: Optional[str] = None
    status: str

    model_config = {
        "from_attributes": True
    }
