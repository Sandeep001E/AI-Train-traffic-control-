from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import pulp

from app.models.train import Train
from app.models.section import Section
from app.services.optimization.heuristic import HeuristicOptimizer


class ORLinearOptimizer:
    @staticmethod
    def optimize(
        trains: List[Train],
        section: Section,
        start_time: Optional[datetime] = None,
        headway_minutes: float = 2.0,
        holds: Optional[Dict[int, int]] = None,  # minutes per train_id
        section_speed_limit: Optional[int] = None,
        time_limit_seconds: int = 10,
    ) -> Dict[str, Any]:
        """
        Build a MILP to minimize weighted completion time subject to:
        - Non-overlap between any two trains with headway
        - Start times not earlier than release times (scheduled departure/now)
        Weights are based on train priority (higher priority => larger weight in objective).
        """
        if start_time is None:
            start_time = datetime.utcnow()
        holds = holds or {}

        # Precompute travel times and release times in minutes from start_time
        effective_section_speed = section.max_speed_limit
        if section_speed_limit is not None:
            effective_section_speed = min(effective_section_speed, section_speed_limit)

        ids = [t.id for t in trains]
        idx = {tid: k for k, tid in enumerate(ids)}

        travel = {}
        release = {}
        weights = {}
        for t in trains:
            eff_speed = min(t.max_speed or 100, effective_section_speed)
            travel_minutes = section.get_travel_time_minutes(eff_speed)
            travel[t.id] = max(0.1, float(travel_minutes))

            r_time = max(start_time, t.scheduled_departure or start_time)
            if t.id in holds and holds[t.id] > 0:
                r_time = max(r_time, start_time + timedelta(minutes=holds[t.id]))
            release_minutes = max(0.0, (r_time - start_time).total_seconds() / 60.0)
            release[t.id] = release_minutes

            # Priority weights: higher priority => larger weight
            # Default to MEDIUM (2) if missing
            try:
                w = getattr(t.priority, "value", 2)
            except Exception:
                w = 2
            weights[t.id] = float(w)

        n = len(ids)
        if n <= 1:
            # Trivial schedule
            schedule = []
            for tid in ids:
                st = start_time + timedelta(minutes=release[tid])
                et = st + timedelta(minutes=travel[tid])
                schedule.append({
                    "train_id": tid,
                    "section_id": section.id,
                    "planned_entry": st.isoformat(),
                    "planned_exit": et.isoformat(),
                    "effective_speed": effective_section_speed,
                    "priority_weight": weights[tid],
                })
            schedule.sort(key=lambda x: x["planned_entry"])
            metrics = HeuristicOptimizer.metrics_from_schedule(schedule)
            return {"schedule": schedule, "metrics": metrics}

        # Big-M
        M = max(release.values()) + sum(travel.values()) + headway_minutes + 60.0

        # Problem
        prob = pulp.LpProblem("TrainScheduling", pulp.LpMinimize)

        # Variables
        t_vars = {tid: pulp.LpVariable(f"t_{tid}", lowBound=release[tid], cat=pulp.LpContinuous) for tid in ids}
        y_vars = {}
        for i in range(n):
            for j in range(i + 1, n):
                ti, tj = ids[i], ids[j]
                y_vars[(ti, tj)] = pulp.LpVariable(f"y_{ti}_{tj}", lowBound=0, upBound=1, cat=pulp.LpBinary)

        # Objective: minimize sum weights * (start + travel)
        prob += pulp.lpSum(weights[tid] * (t_vars[tid] + travel[tid]) for tid in ids)

        # Non-overlap constraints with headway
        for i in range(n):
            for j in range(i + 1, n):
                ti, tj = ids[i], ids[j]
                y = y_vars[(ti, tj)]
                # If y=1 => i before j
                prob += t_vars[tj] >= t_vars[ti] + travel[ti] + headway_minutes - M * (1 - y)
                # If y=0 => j before i
                prob += t_vars[ti] >= t_vars[tj] + travel[tj] + headway_minutes - M * y

        # Solve
        solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit_seconds)
        prob.solve(solver)

        # Build schedule; if not optimal, still use current solution if available
        schedule: List[Dict[str, Any]] = []
        status = pulp.LpStatus[prob.status]

        for tid in ids:
            start_min = pulp.value(t_vars[tid])
            if start_min is None:
                # Fallback to release time
                start_min = release[tid]
            st_dt = start_time + timedelta(minutes=float(start_min))
            et_dt = st_dt + timedelta(minutes=float(travel[tid]))
            schedule.append({
                "train_id": tid,
                "section_id": section.id,
                "planned_entry": st_dt.isoformat(),
                "planned_exit": et_dt.isoformat(),
                "effective_speed": effective_section_speed,
                "priority_weight": weights[tid],
            })

        schedule.sort(key=lambda x: x["planned_entry"])
        metrics = HeuristicOptimizer.metrics_from_schedule(schedule)

        return {
            "status": status,
            "objective": pulp.value(prob.objective),
            "schedule": schedule,
            "metrics": metrics,
        }
