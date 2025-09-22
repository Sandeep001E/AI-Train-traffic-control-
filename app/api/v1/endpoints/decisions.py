from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.train import Train
from app.models.section import Section
from app.models.decision import Decision, DecisionType, DecisionStatus
from app.schemas.decision import PrecedenceRequest, DecisionRead, DecisionCreate
from app.services.optimization.heuristic import HeuristicOptimizer

router = APIRouter()

@router.post("/precedence", response_model=DecisionRead)
def precedence_decision(payload: PrecedenceRequest, db: Session = Depends(get_db)):
    section = db.get(Section, payload.section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    trains = db.query(Train).filter(Train.id.in_(payload.train_ids)).all()
    if not trains:
        raise HTTPException(status_code=400, detail="No valid trains provided")

    start_time = payload.current_time or datetime.utcnow()
    schedule = HeuristicOptimizer.build_schedule(trains, section, start_time)
    metrics = HeuristicOptimizer.metrics_from_schedule(schedule)

    details = {
        "precedence_order": [item["train_id"] for item in schedule],
        "schedule": schedule,
        "metrics": metrics
    }

    decision = Decision(
        decision_type=DecisionType.PRECEDENCE,
        status=DecisionStatus.RECOMMENDED,
        section_id=section.id,
        details=details,
        explanation="Order determined by train priority, type, and scheduled departure times.",
        recommended_by="AI"
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision

@router.post("/crossing", response_model=DecisionRead)
def crossing_decision(payload: PrecedenceRequest, db: Session = Depends(get_db)):
    section = db.get(Section, payload.section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    trains = db.query(Train).filter(Train.id.in_(payload.train_ids)).all()
    if not trains:
        raise HTTPException(status_code=400, detail="No valid trains provided")

    # For a simple heuristic: reuse precedence order as crossing plan
    start_time = payload.current_time or datetime.utcnow()
    schedule = HeuristicOptimizer.build_schedule(trains, section, start_time)

    details = {
        "crossing_plan": schedule,
        "note": "Heuristic crossing plan based on precedence; refine with loop/platform constraints in OR model."
    }

    decision = Decision(
        decision_type=DecisionType.CROSSING,
        status=DecisionStatus.RECOMMENDED,
        section_id=section.id,
        details=details,
        explanation="Crossing plan derived from precedence and section constraints.",
        recommended_by="AI"
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision

@router.put("/{decision_id}/approve", response_model=DecisionRead)
def approve_decision(decision_id: int, db: Session = Depends(get_db)):
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    decision.status = DecisionStatus.APPROVED
    db.commit()
    db.refresh(decision)
    return decision

@router.put("/{decision_id}/override", response_model=DecisionRead)
def override_decision(decision_id: int, payload: DecisionCreate, db: Session = Depends(get_db)):
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    if payload.decision_type:
        # Keep the same type or change if explicitly provided
        decision.decision_type = DecisionType(payload.decision_type)
    if payload.details is not None:
        decision.details = payload.details
    if payload.explanation is not None:
        decision.explanation = payload.explanation

    decision.status = DecisionStatus.OVERRIDDEN
    db.commit()
    db.refresh(decision)
    return decision
