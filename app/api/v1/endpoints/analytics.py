from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.train import Train
from app.models.schedule import Schedule
from app.models.section import Section
from app.schemas.analytics import KPIResponse, DashboardResponse

router = APIRouter()

@router.get("/kpis", response_model=KPIResponse)
def get_kpis(db: Session = Depends(get_db)):
    # Load trains to compute punctuality and delays in Python (SQLite-compatible)
    trains = db.query(Train).all()
    total_with_arrival = sum(1 for t in trains if t.scheduled_arrival is not None)
    on_time = sum(1 for t in trains if t.scheduled_arrival and t.actual_arrival and t.actual_arrival <= t.scheduled_arrival)
    punctuality_rate = (on_time / total_with_arrival * 100) if total_with_arrival > 0 else 0.0

    delay_values = []
    for t in trains:
        if t.scheduled_arrival and t.actual_arrival:
            delta_minutes = (t.actual_arrival - t.scheduled_arrival).total_seconds() / 60.0
            if delta_minutes > 0:
                delay_values.append(delta_minutes)
    average_delay = sum(delay_values)/len(delay_values) if delay_values else 0.0

    # Section throughput per hour (use schedules completed in last 6 hours)
    now = datetime.utcnow()
    window_start = now - timedelta(hours=6)
    completed_in_window = db.query(Schedule).filter(Schedule.actual_exit.isnot(None), Schedule.actual_exit >= window_start).count()
    throughput_per_hour = completed_in_window / 6.0

    # Resource utilization percent (average of section utilization)
    sections = db.query(Section).all()
    if sections:
        utilizations = [s.utilization_percentage for s in sections]
        resource_utilization = sum(utilizations)/len(utilizations)
    else:
        resource_utilization = 0.0

    # Conflict resolution time seconds (placeholder until implemented)
    conflict_resolution_time_seconds = 0.0

    return KPIResponse(
        punctuality_rate=round(punctuality_rate, 2),
        average_delay_minutes=round(average_delay, 2),
        section_throughput_per_hour=round(throughput_per_hour, 2),
        resource_utilization_percent=round(resource_utilization, 2),
        conflict_resolution_time_seconds=round(conflict_resolution_time_seconds, 2)
    )

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    kpis = get_kpis(db)
    # Placeholder charts structure
    charts = {
        "delays_histogram": {
            "type": "histogram",
            "data": []
        },
        "throughput_timeseries": {
            "type": "timeseries",
            "data": []
        }
    }
    return DashboardResponse(kpis=kpis, charts=charts)
