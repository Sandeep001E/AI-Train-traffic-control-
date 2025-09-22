from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime

from app.core.database import get_db
from app.models.train import Train
from app.models.section import Section
from app.schemas.simulation import WhatIfScenario, SimulationResult
from app.services.optimization.heuristic import HeuristicOptimizer

router = APIRouter()

@router.post("/what-if", response_model=SimulationResult)
def run_what_if(scenario: WhatIfScenario, db: Session = Depends(get_db)):
    section = db.get(Section, scenario.section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    trains = db.query(Train).filter(Train.id.in_(scenario.train_ids)).all()
    if not trains:
        raise HTTPException(status_code=400, detail="No valid trains provided")

    # Build holds dict
    holds: Dict[int, int] = {}
    if scenario.holds:
        for h in scenario.holds:
            holds[h.train_id] = h.hold_minutes

    # Determine section speed limit override if provided
    section_speed_limit = None
    if scenario.speed_restrictions:
        for sr in scenario.speed_restrictions:
            if sr.section_id == scenario.section_id:
                section_speed_limit = sr.max_speed_limit
                break

    start_time = scenario.start_time or datetime.utcnow()

    schedule = HeuristicOptimizer.build_schedule(
        trains,
        section,
        start_time=start_time,
        holds=holds,
        section_speed_limit=section_speed_limit,
    )
    metrics = HeuristicOptimizer.metrics_from_schedule(schedule)

    return SimulationResult(schedule=schedule, metrics=metrics)
