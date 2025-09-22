from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class SectionBase(BaseModel):
    section_code: str
    section_name: str
    section_type: Optional[str] = "single_line"
    start_station: str
    end_station: str
    length_km: float
    max_speed_limit: Optional[int] = 100
    signal_spacing_km: Optional[float] = 2.0
    has_automatic_signaling: Optional[bool] = False
    max_trains_per_hour: Optional[int] = 6
    has_crossing_station: Optional[bool] = True
    crossing_station_name: Optional[str] = None
    electrified: Optional[bool] = True
    gauge_type: Optional[str] = "broad_gauge"
    maintenance_windows: Optional[Any] = None
    weather_restrictions: Optional[Any] = None
    is_active: Optional[bool] = True

class SectionCreate(SectionBase):
    pass

class SectionUpdate(BaseModel):
    section_name: Optional[str] = None
    section_type: Optional[str] = None
    max_speed_limit: Optional[int] = None
    is_active: Optional[bool] = None

class SectionRead(SectionBase):
    id: int
    current_occupancy: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
