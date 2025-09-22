from pydantic import BaseModel
from typing import List, Dict, Any

class KPIResponse(BaseModel):
    punctuality_rate: float
    average_delay_minutes: float
    section_throughput_per_hour: float
    resource_utilization_percent: float
    conflict_resolution_time_seconds: float

class DashboardResponse(BaseModel):
    kpis: KPIResponse
    charts: Dict[str, Any]  # Keyed by chart name, values are chart data structures
