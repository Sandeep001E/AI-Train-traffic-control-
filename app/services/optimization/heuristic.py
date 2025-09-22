from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.models.train import Train
from app.models.section import Section

class HeuristicOptimizer:
    @staticmethod
    def precedence_order(trains: List[Train]) -> List[int]:
        # Sort trains by priority score, then by scheduled_departure
        def sort_key(t: Train):
            sched_dep = t.scheduled_departure or datetime.utcnow()
            return (-t.get_priority_score(), sched_dep)
        ordered = sorted(trains, key=sort_key)
        return [t.id for t in ordered]

    @staticmethod
    def build_schedule(
        trains: List[Train],
        section: Section,
        start_time: Optional[datetime] = None,
        holds: Optional[Dict[int, int]] = None,  # minutes by train_id
        section_speed_limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        if start_time is None:
            start_time = datetime.utcnow()

        holds = holds or {}
        effective_section_speed = min(section.max_speed_limit, section_speed_limit) if section_speed_limit else section.max_speed_limit

        # Determine order
        order = HeuristicOptimizer.precedence_order(trains)
        id_to_train = {t.id: t for t in trains}

        schedule = []
        current_time = start_time

        for tid in order:
            t = id_to_train[tid]
            # Determine effective speed as min of train speed and section limit
            train_speed = t.max_speed or 100
            effective_speed = min(train_speed, effective_section_speed)

            travel_minutes = section.get_travel_time_minutes(effective_speed)

            # Enforce priority-first entry: ignore scheduled_departure so higher priority enters first
            planned_entry = current_time
            # Still respect any explicit hold if provided
            if tid in holds and holds[tid] > 0:
                planned_entry = max(planned_entry, start_time + timedelta(minutes=holds[tid]))

            planned_exit = planned_entry + timedelta(minutes=travel_minutes)
            schedule.append({
                "train_id": t.id,
                "section_id": section.id,
                "planned_entry": planned_entry.isoformat(),
                "planned_exit": planned_exit.isoformat(),
                "effective_speed": effective_speed,
                "priority": t.priority.name if getattr(t, "priority", None) else "MEDIUM",
            })
            current_time = planned_exit

        return schedule

    @staticmethod
    def metrics_from_schedule(schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not schedule:
            return {
                "throughput_per_hour": 0,
                "average_headway_minutes": 0
            }
        # Compute simple metrics
        times = [datetime.fromisoformat(item["planned_exit"]) for item in schedule]
        times.sort()
        total_duration = (times[-1] - times[0]).total_seconds() / 3600 if len(times) > 1 else 1
        throughput = len(schedule) / total_duration if total_duration > 0 else len(schedule)

        headways = []
        for i in range(1, len(times)):
            headways.append((times[i] - times[i-1]).total_seconds() / 60)
        avg_headway = sum(headways)/len(headways) if headways else 0

        return {
            "throughput_per_hour": round(throughput, 2),
            "average_headway_minutes": round(avg_headway, 2)
        }
