import React from 'react'
import { Box, Paper, Typography } from '@mui/material'
import { DemoScenario, DemoScheduleEntry, DemoTrain, approachProgress } from './demo'

export type SchematicMapProps = {
  scenario: DemoScenario
  schedule: DemoScheduleEntry[]
  now: Date
}

const W = 900
const H = 360
const yTop = 90
const yBottom = 270
const xLeft = 60
const xRight = 840
const xJunction = 560
const VANISH_P = 2.1 // disappear slightly past Station-2 (p=2 means exactly at Station-2)
const BEYOND_PIXELS = 28 // visual run-out beyond Station-2 before vanishing

const stationStyle = {
  rx: 10,
  ry: 10,
  fill: '#fff',
  stroke: '#cfd8dc',
}

function quadPoint(t: number, p0: [number, number], p1: [number, number], p2: [number, number]) {
  const x = (1 - t) * (1 - t) * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
  const y = (1 - t) * (1 - t) * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
  return { x, y }
}

function priorityColor(p: number) {
  switch (p) {
    case 1:
      return '#e53935'
    case 2:
      return '#fb8c00'
    case 3:
      return '#1e88e5'
    case 4:
      return '#43a047'
    default:
      return '#757575'
  }
}

function TrainGlyph({ x, y, label, color }: { x: number; y: number; label: string; color: string }) {
  const w = 44
  const h = 16
  return (
    <g>
      <rect x={x - w / 2} y={y - h / 2} width={w} height={h} rx={3} ry={3} fill={color} stroke="#263238" opacity={0.9} />
      <text x={x} y={y - 10} textAnchor="middle" fontSize={11} fill="#263238" fontWeight={600}>{label}</text>
    </g>
  )
}

function renderTrain(t: DemoTrain, scn: DemoScenario, sched: DemoScheduleEntry[], now: Date) {
  let p = approachProgress(scn, sched, t, now)
  // progress definition: 0..1 approach to junction, 1..2 travel from junction to Station-2 (right)
  if (p >= VANISH_P) return null // hide slightly after Station-2
  const color = priorityColor(t.priority)

  if (t.approach === 'main_left') {
    const pre = Math.min(1, p)
    const post = p > 1 ? Math.min(1, p - 1) : 0
    const beyond = p > 2 ? Math.min(1, (p - 2) / (VANISH_P - 2)) : 0
    let x = xLeft + (xJunction - xLeft) * pre
    let y = yTop
    if (p > 1) x = xJunction + (xRight - xJunction) * post + beyond * BEYOND_PIXELS
    return <TrainGlyph key={t.id} x={x} y={y} label={`T${t.id} P${t.priority}`} color={color} />
  }
  if (t.approach === 'main_right') {
    const pre = Math.min(1, p)
    const post = p > 1 ? Math.min(1, p - 1) : 0
    const beyond = p > 2 ? Math.min(1, (p - 2) / (VANISH_P - 2)) : 0
    let x = xRight - (xRight - xJunction) * pre
    let y = yTop
    if (p > 1) x = xJunction - (xJunction - xLeft) * post - beyond * BEYOND_PIXELS
    return <TrainGlyph key={t.id} x={x} y={y} label={`T${t.id} P${t.priority}`} color={color} />
  }
  // branch
  const pre = Math.min(1, p)
  const post = p > 1 ? Math.min(1, p - 1) : 0
  const beyond = p > 2 ? Math.min(1, (p - 2) / (VANISH_P - 2)) : 0
  const p0: [number, number] = [250, yBottom]
  const p1: [number, number] = [430, 220]
  const p2: [number, number] = [xJunction, yTop]
  const pt = quadPoint(pre, p0, p1, p2)
  let x = pt.x
  let y = pt.y
  if (p > 1) {
    x = xJunction + (xRight - xJunction) * post + beyond * BEYOND_PIXELS
    y = yTop
  }
  return <TrainGlyph key={t.id} x={x} y={y} label={`T${t.id} P${t.priority}`} color={color} />
}

export default function SchematicMap({ scenario, schedule, now }: SchematicMapProps) {
  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Box sx={{ mb: 1, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="subtitle2">Single-Track Junction Map</Typography>
        <Typography variant="caption" color="text.secondary">{now.toLocaleTimeString()}</Typography>
      </Box>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H}>
        {/* main track */}
        <path d={`M ${xLeft} ${yTop} L ${xRight} ${yTop}`} stroke="#90a4ae" strokeWidth={8} fill="none" strokeLinecap="round" />
        {/* branch track */}
        <path d={`M 250 ${yBottom} Q 430 220 ${xJunction} ${yTop}`} stroke="#90a4ae" strokeWidth={8} fill="none" strokeLinecap="round" />

        {/* stations */}
        <rect x={140} y={40} width={130} height={36} {...stationStyle} />
        <text x={205} y={63} textAnchor="middle" fontSize={14} fill="#37474f">Ameerpet</text>

        <rect x={640} y={40} width={130} height={36} {...stationStyle} />
        <text x={705} y={63} textAnchor="middle" fontSize={14} fill="#37474f">Parad Ground</text>

        <rect x={120} y={300} width={130} height={36} {...stationStyle} />
        <text x={185} y={323} textAnchor="middle" fontSize={14} fill="#37474f">MG Bus station</text>

        {/* Junction marker */}
        <circle cx={xJunction} cy={yTop} r={6} fill="#455a64" />

        {/* trains */}
        {scenario.trains.map((t) => renderTrain(t, scenario, schedule, now))}
      </svg>
    </Paper>
  )
}
