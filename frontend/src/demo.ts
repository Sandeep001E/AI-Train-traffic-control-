export type DemoTrain = {
  id: number
  train_number: string
  name: string
  priority: number // 1 = highest
  speed_kmh: number
  origin: 'Station-1' | 'Station-2' | 'Station-3'
  destination: 'Station-1' | 'Station-2' | 'Station-3'
  approach: 'main_left' | 'main_right' | 'branch' // which side they approach the junction from
  distance_to_junction_km: number // distance at t0
}

export type DemoScenario = {
  startTime: Date
  headway_min: number
  clearance_min: number
  trains: DemoTrain[]
  // initial normalized progress per train id:
  // 0..1 = approach toward junction, 1..2 = from junction to Station-2 (right side)
  initialP?: Record<number, number>
}

export type DemoScheduleEntry = {
  train_id: number
  earliest_arrival: Date
  planned_entry: Date
  planned_exit: Date
  reason: string
}

export function roundToNextMinute(d: Date) {
  const dt = new Date(d)
  dt.setSeconds(0, 0)
  return dt
}

export function addMinutes(d: Date, mins: number) {
  return new Date(d.getTime() + mins * 60_000)
}

export function minutesBetween(a: Date, b: Date) {
  return (b.getTime() - a.getTime()) / 60_000
}

export function formatClock(d: Date) {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function buildDemoScenario(): DemoScenario {
  const t0 = roundToNextMinute(new Date())
  const trains: DemoTrain[] = [
    {
      id: 1,
      train_number: '11205',
      name: 'Red line Express',
      priority: 4,
      speed_kmh: 80,
      origin: 'Station-1',
      destination: 'Station-2',
      approach: 'main_left',
      distance_to_junction_km: 8,
    },
    {
      id: 2,
      train_number: '11020',
      name: 'Blue Line Local',
      priority: 1,
      speed_kmh: 60,
      origin: 'Station-1',
      destination: 'Station-2',
      approach: 'main_left',
      distance_to_junction_km: 5,
    },
    // All trains move left → right towards Station-2 (through the junction)
    {
      id: 3,
      train_number: '12902',
      name: 'Falaknuma Flyer',
      priority: 3,
      speed_kmh: 100,
      origin: 'Station-1',
      destination: 'Station-2',
      approach: 'main_left',
      distance_to_junction_km: 6,
    },
    {
      id: 4,
      train_number: '12727',
      name: 'Hitech City Special',
      priority: 2,
      speed_kmh: 90,
      origin: 'Station-3',
      destination: 'Station-2',
      approach: 'branch',
      distance_to_junction_km: 4,
    },
    {
      id: 5,
      train_number: '20910',
      name: 'Chennai Express',
      priority: 5,
      speed_kmh: 50,
      origin: 'Station-3',
      destination: 'Station-2',
      approach: 'branch',
      distance_to_junction_km: 7,
    },
  ]

  // Place trains according to requested initial scene:
  // T3 in front of Station-2 (post-junction), T2 in front of Station-1 (pre-junction),
  // T5 in front of Station-3 (branch start), T1 behind T2 (further left),
  // T4 between T3 and T5 (mid branch).
  const initialP: Record<number, number> = {
    3: 1.7,  // near Station-2 on right segment
    2: 0.20, // near Station-1 on main left
    5: 0.12, // near Station-3 on branch start
    1: 0.06, // behind T2 on main left
    4: 0.55, // between T5 and junction on branch
  }

  return {
    startTime: t0,
    headway_min: 2,
    clearance_min: 1.5,
    trains,
    initialP,
  }
}

export function computeEarliestArrival(start: Date, t: DemoTrain) {
  const travel_min = (t.distance_to_junction_km / t.speed_kmh) * 60
  return addMinutes(start, travel_min)
}

// ETA to junction in minutes considering initial normalized progress (initialP)
export function etaToJunctionMinutes(scn: DemoScenario, t: DemoTrain) {
  const baseMin = (t.distance_to_junction_km / t.speed_kmh) * 60
  const p0 = scn.initialP?.[t.id] ?? 0
  if (p0 >= 1) return 0 // already beyond the junction at t0
  const remaining = Math.max(0, 1 - Math.min(1, p0))
  return baseMin * remaining
}

// Simple priority-based single junction scheduler with fixed headway and clearance
export function scheduleSingleJunction(scn: DemoScenario): DemoScheduleEntry[] {
  const list = [...scn.trains]
    .sort((a, b) => {
      const ea = etaToJunctionMinutes(scn, a)
      const eb = etaToJunctionMinutes(scn, b)
      if (ea !== eb) return ea - eb // front-of-queue (earlier ETA) first
      return a.priority - b.priority || a.id - b.id
    })

  const result: DemoScheduleEntry[] = []
  let lastExit: Date | null = null
  const lastEntryByApproach: Record<DemoTrain['approach'], Date | null> = {
    main_left: null,
    main_right: null,
    branch: null,
  }
  // Ensure next entry is at least clearance + safety to avoid any junction overlap
  const effectiveHeadway = Math.max(scn.headway_min, scn.clearance_min + 0.25)

  for (const t of list) {
    const etaMin = etaToJunctionMinutes(scn, t)
    const earliest = addMinutes(scn.startTime, etaMin)
    let entry = earliest
    // Enforce global junction headway (no two trains in junction too close)
    const minEntryByJunction = lastExit ? addMinutes(lastExit, effectiveHeadway) : scn.startTime
    if (entry < minEntryByJunction) entry = minEntryByJunction
    // Enforce same-direction spacing so trains on the same approach don't overlap
    const prevSameDir = lastEntryByApproach[t.approach]
    if (prevSameDir) {
      const minEntryByDirection = addMinutes(prevSameDir, effectiveHeadway)
      if (entry < minEntryByDirection) entry = minEntryByDirection
    }
    const exit = addMinutes(entry, scn.clearance_min)

    const directionNote = prevSameDir ? ` and same-approach headway after ${formatClock(prevSameDir)}` : ''
    const reason = result.length === 0
      ? `Step 1: ${t.name} (P${t.priority}) is ahead (ETA ${formatClock(earliest)}). Scheduled at ${formatClock(entry)}.`
      : `Next: ${t.name} (P${t.priority}) chosen by ETA ${formatClock(earliest)}; ` +
        `respect junction headway after ${formatClock(lastExit ?? scn.startTime)}${directionNote} → schedule ${formatClock(entry)}.`

    result.push({ train_id: t.id, earliest_arrival: earliest, planned_entry: entry, planned_exit: exit, reason })
    lastExit = exit
    lastEntryByApproach[t.approach] = entry
  }

  return result
}

type SimTimes = { release: Date; simEntry: Date; simExit: Date; vanish: Date; startP: number }

// Build a continuous animation timeline so only one train moves at a time
// and each train keeps a smooth speed derived from physical ETA/clearance.
function computeSimTimeline(
  scn: DemoScenario,
  sched: DemoScheduleEntry[],
  trains: DemoTrain[]
): Record<number, SimTimes> {
  const byId: Record<number, DemoTrain> = Object.fromEntries(trains.map((t) => [t.id, t]))
  const runoutMin = Math.max(0.5, scn.headway_min - 0.25)
  const result: Record<number, SimTimes> = {}

  let lastVanish = scn.startTime
  for (const s of sched) {
    const t = byId[s.train_id]
    if (!t) continue
    const startP = scn.initialP?.[t.id] ?? 0
    const preDur = startP >= 1 ? 0 : Math.max(0.5, etaToJunctionMinutes(scn, t))
    const clearance = Math.max(0.1, minutesBetween(s.planned_entry, s.planned_exit))

    const release = lastVanish
    const simEntry = addMinutes(release, preDur)
    const simExit = addMinutes(simEntry, clearance)
    const vanish = addMinutes(simExit, runoutMin)

    result[t.id] = { release, simEntry, simExit, vanish, startP }
    lastVanish = vanish
  }
  return result
}

export function approachProgress(scn: DemoScenario, sched: DemoScheduleEntry[], train: DemoTrain, now: Date) {
  const s = sched.find((x) => x.train_id === train.id)
  if (!s) return 0
  const tl = computeSimTimeline(scn, sched, scn.trains)
  const st = tl[train.id]
  const vanishP = 2.1
  if (!st) return 0

  // Before release: hold
  if (now <= st.release) return st.startP
  // Pre-junction: startP -> 1 over [release, simEntry]
  if (now <= st.simEntry) {
    const denom = Math.max(0.25, minutesBetween(st.release, st.simEntry))
    const r = Math.min(1, Math.max(0, minutesBetween(st.release, now) / denom))
    return st.startP + (1 - st.startP) * r
  }
  // Post-junction: 1 -> vanish over [simEntry, vanish]
  if (now <= st.vanish) {
    const denom = Math.max(0.25, minutesBetween(st.simEntry, st.vanish))
    const r = Math.min(1, Math.max(0, minutesBetween(st.simEntry, now) / denom))
    return 1 + (vanishP - 1) * r
  }
  return vanishP
}

export function scheduleHorizonMinutes(sched: DemoScheduleEntry[], scn: DemoScenario) {
  if (sched.length === 0) return 15
  const tl = computeSimTimeline(scn, sched, scn.trains)
  // find last vanish across all trains
  let lastVanish = scn.startTime
  for (const s of sched) {
    const st = tl[s.train_id]
    if (st && st.vanish > lastVanish) lastVanish = st.vanish
  }
  // add a small buffer to ensure we see the last disappear
  return Math.ceil(minutesBetween(scn.startTime, addMinutes(lastVanish, 0.5)))
}
