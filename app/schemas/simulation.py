from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class HoldInstruction(BaseModel):
    train_id: int
    hold_minutes: int

class SpeedRestriction(BaseModel):
    section_id: int
    max_speed_limit: int

class WhatIfScenario(BaseModel):
    section_id: int
    train_ids: List[int]
    holds: Optional[List[HoldInstruction]] = None
    speed_restrictions: Optional[List[SpeedRestriction]] = None
    start_time: Optional[datetime] = None

class SimulationResult(BaseModel):
    schedule: list
    metrics: dict
