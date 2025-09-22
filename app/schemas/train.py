from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class TrainBase(BaseModel):
    train_number: str = Field(..., max_length=10)
    train_name: str
    train_type: str
    status: Optional[str] = None
    priority: Optional[int] = None
    max_speed: Optional[int] = 100
    length: Optional[float] = 0.0
    weight: Optional[float] = 0.0
    origin_station: Optional[str] = None
    destination_station: Optional[str] = None
    route_description: Optional[str] = None
    requires_platform: Optional[bool] = True
    can_use_loop_line: Optional[bool] = True

class TrainCreate(TrainBase):
    scheduled_departure: Optional[datetime] = None
    scheduled_arrival: Optional[datetime] = None

class TrainUpdate(BaseModel):
    train_name: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    max_speed: Optional[int] = None
    current_section_id: Optional[int] = None
    current_position_km: Optional[float] = None

class TrainRead(TrainBase):
    id: int
    current_section_id: Optional[int] = None
    current_position_km: Optional[float] = 0.0
    scheduled_departure: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    scheduled_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
