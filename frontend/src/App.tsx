import React, { useEffect, useState } from 'react'
import { api, Train, Section, OptimizeResponse, KPIs, OROptimizeResult } from './api'
import {
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  Container,
  Divider,
  Grid,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Alert,
  Stack,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material'
import SchematicMap from './SchematicMap'
import { buildDemoScenario, scheduleSingleJunction, DemoScheduleEntry, formatClock, scheduleHorizonMinutes, addMinutes } from './demo'

export default function App() {
  const [trains, setTrains] = useState<Train[]>([])
  const [sections, setSections] = useState<Section[]>([])
  const [kpis, setKpis] = useState<KPIs | null>(null)

  const [newTrain, setNewTrain] = useState({
    train_number: '',
    train_name: '',
    train_type: 'passenger',
    priority: 2,
    max_speed: 100,
    origin_station: '',
    destination_station: '',
  })

  const [newSection, setNewSection] = useState({
    section_code: '',
    section_name: '',
    start_station: '',
    end_station: '',
    length_km: 10,
  })

  const [selectedSectionId, setSelectedSectionId] = useState<number | null>(null)
  const [selectedTrainIds, setSelectedTrainIds] = useState<number[]>([])
  const [headway, setHeadway] = useState<number>(4)
  const [optResult, setOptResult] = useState<OptimizeResponse | OROptimizeResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Demo scenario: 5 trains, single junction, 3 stations
  const [scenario] = useState(buildDemoScenario)
  const [demoSchedule, setDemoSchedule] = useState<DemoScheduleEntry[]>([])
  const [simNow, setSimNow] = useState<Date>(scenario.startTime)
  const [playing, setPlaying] = useState(false)
  // Playback speed control
  const [speed, setSpeed] = useState(1) // 0.5x, 1x, 2x
  const TICK_MS = 100
  const BASE_MIN_PER_TICK = 0.01 // 0.6 simulated seconds per tick

  async function refreshAll() {
    try {
      setError(null)
      const [t, s, k] = await Promise.all([
        api.get<Train[]>('/trains/'),
        api.get<Section[]>('/sections/'),
        api.get<KPIs>('/analytics/kpis'),
      ])
      setTrains(t)
      setSections(s)
      setKpis(k)
      if (s.length && selectedSectionId == null) setSelectedSectionId(s[0].id)
    } catch (e: any) {
      setError(e.message)
    }
  }

  useEffect(() => {
    refreshAll()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Build demo schedule once
  useEffect(() => {
    setDemoSchedule(scheduleSingleJunction(scenario))
    setSimNow(scenario.startTime)
  }, [scenario])

  // Simple player to animate trains on the schematic
  useEffect(() => {
    if (!playing) return
    const horizon = scheduleHorizonMinutes(demoSchedule, scenario)
    const end = addMinutes(scenario.startTime, horizon)
    const id = setInterval(() => {
      const delta = BASE_MIN_PER_TICK * speed
      setSimNow((prev) => (prev >= end ? end : addMinutes(prev, delta)))
    }, TICK_MS)
    return () => clearInterval(id)
  }, [playing, demoSchedule, scenario, speed])

  async function addTrain() {
    try {
      setBusy(true)
      setError(null)
      const created = await api.post<Train>('/trains/', {
        ...newTrain,
        status: 'scheduled',
      })
      setTrains((prev) => [...prev, created])
      setNewTrain({ train_number: '', train_name: '', train_type: 'passenger', priority: 2, max_speed: 100, origin_station: '', destination_station: '' })
    } catch (e: any) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  async function addSection() {
    try {
      setBusy(true)
      setError(null)
      const created = await api.post<Section>('/sections/', newSection)
      setSections((prev) => [...prev, created])
      setNewSection({ section_code: '', section_name: '', start_station: '', end_station: '', length_km: 10 })
      if (!selectedSectionId) setSelectedSectionId(created.id)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  function toggleTrainSelection(id: number) {
    setSelectedTrainIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  async function runOptimization() {
    if (!selectedSectionId || selectedTrainIds.length === 0) {
      setError('Select a section and at least one train')
      return
    }
    try {
      setBusy(true)
      setError(null)
      const res = await api.post<OptimizeResponse>('/trains/optimize', {
        section_id: selectedSectionId,
        train_ids: selectedTrainIds,
      })
      setOptResult(res)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  async function runOROptimization() {
    if (!selectedSectionId || selectedTrainIds.length === 0) {
      setError('Select a section and at least one train')
      return
    }
    try {
      setBusy(true)
      setError(null)
      const res = await api.post<OROptimizeResult>('/trains/optimize_or', {
        section_id: selectedSectionId,
        train_ids: selectedTrainIds,
        headway_minutes: headway,
      })
      setOptResult(res)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  function resetSim() {
    setPlaying(false)
    setSimNow(scenario.startTime)
  }

  function stepSim() {
    // Step forward by exactly 20 seconds
    setSimNow((prev) => addMinutes(prev, 20 / 60))
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ bgcolor: 'success.main', width: 36, height: 36 }}>S</Avatar>
          <Box>
            <Typography variant="h6" fontWeight={700}>RIDSS — Railway Intelligent Decision Support System</Typography>
            <Typography variant="body2" color="text.secondary">AI-powered train precedence and crossing optimization with what-if simulation and KPIs.</Typography>
          </Box>
        </Box>
      </Box>

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
      )}

      {/* KPI Row */}
      <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 600 }}>KPIs</Typography>
      {kpis ? (
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} sm={6} md={3}><KpiCard label="Punctuality" value={`${kpis.punctuality_rate.toFixed(1)}%`} /></Grid>
          <Grid item xs={12} sm={6} md={3}><KpiCard label="Avg Delay" value={`${kpis.average_delay_minutes.toFixed(1)} min`} /></Grid>
          <Grid item xs={12} sm={6} md={3}><KpiCard label="Throughput" value={`${kpis.section_throughput_per_hour.toFixed(2)} tph`} /></Grid>
          <Grid item xs={12} sm={6} md={3}><KpiCard label="Utilization" value={`${kpis.resource_utilization_percent.toFixed(1)}%`} /></Grid>
        </Grid>
      ) : (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>Loading KPIs…</Typography>
      )}

      {/* Main two-column layout */}
      <Grid container spacing={2}>
        {/* Left column - forms */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>Section Code</Typography>

              <Typography variant="caption" color="text.secondary">Add Train</Typography>
              <Grid container spacing={1} sx={{ mt: 0.5 }}>
                <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Train No" value={newTrain.train_number} onChange={(e) => setNewTrain({ ...newTrain, train_number: e.target.value })} /></Grid>
                <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Train Name" value={newTrain.train_name} onChange={(e) => setNewTrain({ ...newTrain, train_name: e.target.value })} /></Grid>
                <Grid item xs={12} sm={6}>
                  <TextField select fullWidth size="small" label="Train Type" value={newTrain.train_type} onChange={(e) => setNewTrain({ ...newTrain, train_type: e.target.value })}>
                    <MenuItem value="passenger">Passenger</MenuItem>
                    <MenuItem value="express">Express</MenuItem>
                    <MenuItem value="superfast">Superfast</MenuItem>
                    <MenuItem value="freight">Freight</MenuItem>
                    <MenuItem value="special">Special</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={6} sm={3}><TextField fullWidth size="small" type="number" label="Priority (1-4)" value={newTrain.priority} onChange={(e) => setNewTrain({ ...newTrain, priority: Number(e.target.value) })} /></Grid>
                <Grid item xs={6} sm={3}><TextField fullWidth size="small" type="number" label="Max Speed (km/h)" value={newTrain.max_speed} onChange={(e) => setNewTrain({ ...newTrain, max_speed: Number(e.target.value) })} /></Grid>
                <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Origin" value={newTrain.origin_station} onChange={(e) => setNewTrain({ ...newTrain, origin_station: e.target.value })} /></Grid>
                <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Destination" value={newTrain.destination_station} onChange={(e) => setNewTrain({ ...newTrain, destination_station: e.target.value })} /></Grid>
                <Grid item xs={12}><Button variant="contained" disableElevation onClick={addTrain} disabled={busy || !newTrain.train_number || !newTrain.train_name} fullWidth>Add Train</Button></Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              <Typography variant="caption" color="text.secondary">Add Section</Typography>
              <Grid container spacing={1} sx={{ mt: 0.5 }}>
                <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Section Code" value={newSection.section_code} onChange={(e) => setNewSection({ ...newSection, section_code: e.target.value })} /></Grid>
                <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Section Name" value={newSection.section_name} onChange={(e) => setNewSection({ ...newSection, section_name: e.target.value })} /></Grid>
                <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="Start Station" value={newSection.start_station} onChange={(e) => setNewSection({ ...newSection, start_station: e.target.value })} /></Grid>
                <Grid item xs={12} sm={6}><TextField fullWidth size="small" label="End Station" value={newSection.end_station} onChange={(e) => setNewSection({ ...newSection, end_station: e.target.value })} /></Grid>
                <Grid item xs={12} sm={6}><TextField fullWidth size="small" type="number" label="Length (km)" value={newSection.length_km} onChange={(e) => setNewSection({ ...newSection, length_km: Number(e.target.value) })} /></Grid>
                <Grid item xs={12}><Button variant="outlined" onClick={addSection} disabled={busy || !newSection.section_code || !newSection.section_name} fullWidth>Add Section</Button></Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              <Grid container spacing={1} alignItems="center">
                <Grid item xs={12} sm={8}>
                  <TextField select fullWidth size="small" label="Section for optimization" value={selectedSectionId ?? ''} onChange={(e) => setSelectedSectionId(Number(e.target.value) || null)}>
                    <MenuItem value="">Select…</MenuItem>
                    {sections.map((s) => (
                      <MenuItem key={s.id} value={s.id}>{s.section_code} — {s.start_station}→{s.end_station}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField fullWidth size="small" type="number" label="Headway (min)" inputProps={{ step: 0.5, min: 0 }} value={headway} onChange={(e) => setHeadway(Number(e.target.value))} />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button variant="contained" disableElevation fullWidth onClick={runOptimization} disabled={busy || !selectedSectionId || selectedTrainIds.length === 0}>Run Heuristic</Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button variant="contained" color="secondary" disableElevation fullWidth onClick={runOROptimization} disabled={busy || !selectedSectionId || selectedTrainIds.length === 0}>Run OR Optimization</Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Right column - System Overview */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>System Overview</Typography>

              {/* Train selection table */}
              <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell width={40}></TableCell>
                      <TableCell>No</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell align="right">Priority</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {trains.map((t) => (
                      <TableRow key={t.id} hover>
                        <TableCell padding="checkbox">
                          <Checkbox checked={selectedTrainIds.includes(t.id)} onChange={() => toggleTrainSelection(t.id)} />
                        </TableCell>
                        <TableCell>{t.train_number}</TableCell>
                        <TableCell>{t.train_name}</TableCell>
                        <TableCell>{t.train_type}</TableCell>
                        <TableCell align="right">{t.priority ?? '-'}</TableCell>
                      </TableRow>
                    ))}
                    {trains.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={5} sx={{ color: 'text.secondary' }}>No trains yet</TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Schedule result */}
              {optResult && (
                <Box>
                  <Grid container spacing={2} sx={{ mb: 1 }}>
                    <Grid item xs={12} sm={6}><KpiCard label="Throughput" value={`${optResult.metrics.throughput_per_hour.toFixed(2)} tph`} /></Grid>
                    <Grid item xs={12} sm={6}><KpiCard label="Avg Headway" value={`${optResult.metrics.average_headway_minutes.toFixed(1)} min`} /></Grid>
                  </Grid>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Train</TableCell>
                          <TableCell>Planned Entry</TableCell>
                          <TableCell>Planned Exit</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {optResult.schedule.map((s, idx) => {
                          const t = trains.find((x) => x.id === s.train_id)
                          const label = t ? t.train_name : `#${s.train_id}`
                          return (
                            <TableRow key={idx}>
                              <TableCell>{label}</TableCell>
                              <TableCell>{formatDT(s.planned_entry)}</TableCell>
                              <TableCell>{formatDT(s.planned_exit)}</TableCell>
                            </TableRow>
                          )
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Stack direction="row" sx={{ mt: 2 }}>
        <Button variant="outlined" onClick={refreshAll} disabled={busy}>Refresh</Button>
      </Stack>

      <Box component="footer" sx={{ mt: 4 }}>
        <Typography variant="caption" color="text.secondary">Backend: http://localhost:8000 • Frontend: http://localhost:5173</Typography>
      </Box>

      {/* Demo: Single-Track Junction with 5 Trains */}
      <Box sx={{ mt: 3 }}>
        <Card variant="outlined">
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="h6" fontWeight={700}>Single-Track Demo — Priority-based Junction Scheduling</Typography>
              <Typography variant="body2" color="text.secondary">5 trains • 3 stations • Headway {scenario.headway_min} min • Clearance {scenario.clearance_min} min</Typography>
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} md={7}>
                <SchematicMap scenario={scenario} schedule={demoSchedule} now={simNow} />
                <Box sx={{ mt: 1, display: 'flex', gap: 1, alignItems: 'center' }}>
                  <Button variant="contained" onClick={() => setPlaying((p) => !p)}>{playing ? 'Pause' : 'Play'}</Button>
                  <Button variant="outlined" onClick={stepSim}>Step +20s</Button>
                  <Button variant="outlined" onClick={resetSim}>Reset</Button>
                  <FormControl size="small" sx={{ ml: 'auto', minWidth: 120 }}>
                    <InputLabel id="speed-label">Speed</InputLabel>
                    <Select
                      labelId="speed-label"
                      value={speed}
                      label="Speed"
                      onChange={(e) => setSpeed(Number(e.target.value))}
                    >
                      <MenuItem value={0.5}>0.5x</MenuItem>
                      <MenuItem value={1}>1x</MenuItem>
                      <MenuItem value={2}>2x</MenuItem>
                      <MenuItem value={3}>3x</MenuItem>
                      <MenuItem value={4}>4x</MenuItem>
                    </Select>
                  </FormControl>
                </Box>
              </Grid>
              <Grid item xs={12} md={5}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>Decision log</Typography>
                <Paper variant="outlined" sx={{ p: 1, maxHeight: 170, overflow: 'auto', mb: 2 }}>
                  {demoSchedule.map((s, idx) => (
                    <Typography key={idx} variant="body2" sx={{ mb: 0.5 }}>• {s.reason}</Typography>
                  ))}
                </Paper>

                <Typography variant="subtitle2" sx={{ mb: 1 }}>Scheduled Junction Times</Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Train</TableCell>
                        <TableCell align="right">P</TableCell>
                        <TableCell>Earliest</TableCell>
                        <TableCell>Entry</TableCell>
                        <TableCell>Exit</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {demoSchedule.map((s) => {
                        const t = scenario.trains.find((x) => x.id === s.train_id)!
                        return (
                          <TableRow key={t.id}>
                            <TableCell>{t.train_number} {t.name}</TableCell>
                            <TableCell align="right">{t.priority}</TableCell>
                            <TableCell>{formatClock(s.earliest_arrival)}</TableCell>
                            <TableCell>{formatClock(s.planned_entry)}</TableCell>
                            <TableCell>{formatClock(s.planned_exit)}</TableCell>
                          </TableRow>
                        )
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}

function KpiCard({ label, value }: { label: string, value: string }) {
  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
      <Typography variant="caption" color="text.secondary">{label}</Typography>
      <Typography variant="h6" fontWeight={700}>{value}</Typography>
    </Paper>
  )
}

function formatDT(dt: string) {
  try {
    return new Date(dt).toLocaleString()
  } catch {
    return dt
  }
}

// Note: formatClock is imported from './demo'
