from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.train import Train, TrainType, TrainStatus, Priority
from app.models.section import Section
from app.schemas.train import TrainCreate, TrainRead, TrainUpdate
from app.schemas.decision import PrecedenceRequest
from app.schemas.optimization import OROptimizeRequest, OROptimizeResult
from app.services.optimization.heuristic import HeuristicOptimizer
from app.services.optimization.or_linear import ORLinearOptimizer
from app.utils.audit import record_audit

router = APIRouter()

@router.get("/ping")
async def ping_trains():
    return {"module": "trains", "status": "ok"}

@router.get("/", response_model=List[TrainRead])
def list_trains(db: Session = Depends(get_db)):
    return db.query(Train).all()

@router.post("/", response_model=TrainRead)
def create_train(payload: TrainCreate, db: Session = Depends(get_db), request: Request = None):
    try:
        train = Train(
            train_number=payload.train_number,
            train_name=payload.train_name,
            train_type=TrainType(payload.train_type),
            status=TrainStatus(payload.status) if payload.status else TrainStatus.SCHEDULED,
            priority=Priority(payload.priority) if payload.priority else Priority.MEDIUM,
            max_speed=payload.max_speed or 100,
            length=payload.length or 0.0,
            weight=payload.weight or 0.0,
            origin_station=payload.origin_station,
            destination_station=payload.destination_station,
            route_description=payload.route_description,
            requires_platform=payload.requires_platform if payload.requires_platform is not None else True,
            can_use_loop_line=payload.can_use_loop_line if payload.can_use_loop_line is not None else True,
            scheduled_departure=payload.scheduled_departure,
            scheduled_arrival=payload.scheduled_arrival,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.add(train)
    db.commit()
    db.refresh(train)

    try:
        record_audit(
            db,
            action="create",
            entity_type="train",
            entity_id=train.id,
            details={"train_number": train.train_number},
            ip_address=(request.client.host if request and request.client else None),
            user_agent=(request.headers.get("User-Agent") if request else None)
        )
    except Exception:
        pass

    return train

@router.get("/{train_id}", response_model=TrainRead)
def get_train(train_id: int, db: Session = Depends(get_db)):
    train = db.get(Train, train_id)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    return train

@router.put("/{train_id}", response_model=TrainRead)
def update_train(train_id: int, payload: TrainUpdate, db: Session = Depends(get_db), request: Request = None):
    train = db.get(Train, train_id)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")

    data = payload.dict(exclude_unset=True)
    if "status" in data and data["status"]:
        data["status"] = TrainStatus(data["status"])
    if "priority" in data and data["priority"]:
        data["priority"] = Priority(data["priority"])

    for k, v in data.items():
        setattr(train, k, v)

    db.commit()
    db.refresh(train)

    try:
        record_audit(
            db,
            action="update",
            entity_type="train",
            entity_id=train.id,
            details=data,
            ip_address=(request.client.host if request and request.client else None),
            user_agent=(request.headers.get("User-Agent") if request else None)
        )
    except Exception:
        pass

    return train

@router.delete("/{train_id}")
def delete_train(train_id: int, db: Session = Depends(get_db), request: Request = None):
    train = db.get(Train, train_id)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    db.delete(train)
    db.commit()

    try:
        record_audit(
            db,
            action="delete",
            entity_type="train",
            entity_id=train_id,
            details=None,
            ip_address=(request.client.host if request and request.client else None),
            user_agent=(request.headers.get("User-Agent") if request else None)
        )
    except Exception:
        pass

    return {"status": "deleted", "id": train_id}

@router.post("/optimize")
def optimize_trains(payload: PrecedenceRequest, db: Session = Depends(get_db)):
    section = db.get(Section, payload.section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    trains = db.query(Train).filter(Train.id.in_(payload.train_ids)).all()
    if not trains:
        raise HTTPException(status_code=400, detail="No valid trains provided")

    schedule = HeuristicOptimizer.build_schedule(trains, section, payload.current_time)
    metrics = HeuristicOptimizer.metrics_from_schedule(schedule)

    return {"schedule": schedule, "metrics": metrics}

@router.post("/optimize_or", response_model=OROptimizeResult)
def optimize_trains_or(payload: OROptimizeRequest, db: Session = Depends(get_db)):
    section = db.get(Section, payload.section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    trains = db.query(Train).filter(Train.id.in_(payload.train_ids)).all()
    if not trains:
        raise HTTPException(status_code=400, detail="No valid trains provided")

    # Build holds dict
    holds = {}
    if payload.holds:
        for h in payload.holds:
            holds[h.train_id] = h.hold_minutes

    res = ORLinearOptimizer.optimize(
        trains=trains,
        section=section,
        start_time=payload.current_time,
        headway_minutes=payload.headway_minutes or 2.0,
        holds=holds,
        section_speed_limit=payload.section_speed_limit,
        time_limit_seconds=payload.time_limit_seconds or 10,
    )
    return res
