// Mock forecast fixtures — pre-computed Cisco Time Series Model + Chronos output
// per scenario. Drives the ForecastStrip component to show Vigil's proactive
// (forecast-driven) layer alongside the existing reactive FSM investigation.

export type TriggerType = 'threshold' | 'trajectory' | 'uncertainty' | 'none'

export interface ForecastSeries {
  metric: string                  // display name
  unit: string                    // value suffix
  device: string                  // device identifier
  history: number[]               // 60 historical values (oldest → newest)
  forecast_p50: number[]          // 24 median forecast steps
  forecast_p10: number[]          // 24 P10 lower-bound forecast steps
  forecast_p90: number[]          // 24 P90 upper-bound forecast steps
  threshold: number | null        // hard limit; null means no threshold
  threshold_direction: 'above' | 'below'
  trigger: {
    type: TriggerType
    severity: 'critical' | 'warning' | 'info' | 'none'
    projected_minutes_ahead: number | null
    message: string
    confidence: number            // 0–1
    model: 'CTSM' | 'Chronos' | 'CTSM + Chronos'
  }
}

export interface ForecastBundle {
  scenarioId: string
  horizon_steps: number
  step_minutes: number
  generated_at: string
  series: [ForecastSeries, ForecastSeries, ForecastSeries]   // BGP, CPU, packet drop
}

// ── Deterministic noise generator ─────────────────────────────
function rng(seed: number) {
  let s = seed
  return () => {
    s = (s * 9301 + 49297) % 233280
    return s / 233280
  }
}

function flat(value: number, jitter: number, seed: number, len: number): number[] {
  const r = rng(seed)
  return Array.from({ length: len }, () => value + (r() - 0.5) * jitter)
}

function trend(start: number, end: number, jitter: number, seed: number, len: number): number[] {
  const r = rng(seed)
  return Array.from({ length: len }, (_, i) => {
    const t = i / (len - 1)
    return start + (end - start) * t + (r() - 0.5) * jitter
  })
}

function burst(base: number, peak: number, peakAt: number, width: number, jitter: number, seed: number, len: number): number[] {
  const r = rng(seed)
  return Array.from({ length: len }, (_, i) => {
    const distance = Math.abs(i - peakAt)
    const burstShape = distance < width ? (peak - base) * (1 - distance / width) : 0
    return base + burstShape + (r() - 0.5) * jitter
  })
}

function band(p50: number[], spread: number): { p10: number[]; p90: number[] } {
  return {
    p10: p50.map(v => v - spread),
    p90: p50.map(v => v + spread),
  }
}

function widenBand(p50: number[], startSpread: number, endSpread: number): { p10: number[]; p90: number[] } {
  return {
    p10: p50.map((v, i) => v - (startSpread + (endSpread - startSpread) * (i / (p50.length - 1)))),
    p90: p50.map((v, i) => v + (startSpread + (endSpread - startSpread) * (i / (p50.length - 1)))),
  }
}

// ── Per-scenario fixtures ─────────────────────────────────────
// All scenarios share the same 24-step horizon (5 minutes per step = 2-hour window)

const HORIZON = 24
const STEP_MIN = 5

// PACKET LOSS — packet drop spikes, threshold trigger fires 8 min ahead
function packetLossBundle(): ForecastBundle {
  const bgpHistory = flat(847, 4, 11, 60)
  const bgpForecast = flat(847, 3, 12, HORIZON)
  const bgpBand = band(bgpForecast, 3)

  const cpuHistory = trend(62, 68, 5, 21, 60)
  const cpuForecast = trend(68, 74, 4, 22, HORIZON)
  const cpuBand = band(cpuForecast, 6)

  const drop50 = trend(0.4, 2.8, 0.3, 32, HORIZON)
  const dropHistory = trend(0.3, 0.5, 0.15, 31, 60)
  const dropBand = widenBand(drop50, 0.4, 1.6)

  return {
    scenarioId: 'packet_loss',
    horizon_steps: HORIZON,
    step_minutes: STEP_MIN,
    generated_at: '14:30 UTC',
    series: [
      {
        metric: 'BGP Route Count',
        unit: ' routes',
        device: 'sj-catalyst-01',
        history: bgpHistory,
        forecast_p50: bgpForecast,
        forecast_p10: bgpBand.p10,
        forecast_p90: bgpBand.p90,
        threshold: null,
        threshold_direction: 'below',
        trigger: {
          type: 'none', severity: 'none',
          projected_minutes_ahead: null,
          message: 'Stable — no projected change',
          confidence: 0.92,
          model: 'CTSM',
        },
      },
      {
        metric: 'CPU Utilization',
        unit: '%',
        device: 'sj-catalyst-01',
        history: cpuHistory,
        forecast_p50: cpuForecast,
        forecast_p10: cpuBand.p10,
        forecast_p90: cpuBand.p90,
        threshold: 85,
        threshold_direction: 'above',
        trigger: {
          type: 'trajectory', severity: 'warning',
          projected_minutes_ahead: 110,
          message: 'Slow upward drift — projected to approach 85% in ~110 min',
          confidence: 0.71,
          model: 'CTSM + Chronos',
        },
      },
      {
        metric: 'Packet Drop Rate',
        unit: '%',
        device: 'sj-catalyst-01 GigE0/1',
        history: dropHistory,
        forecast_p50: drop50,
        forecast_p10: dropBand.p10,
        forecast_p90: dropBand.p90,
        threshold: 1.0,
        threshold_direction: 'above',
        trigger: {
          type: 'threshold', severity: 'critical',
          projected_minutes_ahead: 8,
          message: 'P50 forecast breaches 1.0% threshold in 8 min — investigate now',
          confidence: 0.88,
          model: 'Chronos',
        },
      },
    ],
  }
}

// BGP FLAP — route count drops, threshold trigger fires 18 min ahead
function bgpFlapBundle(): ForecastBundle {
  const bgpHistory = flat(847, 4, 41, 60)
  const bgpForecast = trend(847, 620, 8, 42, HORIZON)
  const bgpBand = widenBand(bgpForecast, 4, 20)

  const cpuHistory = flat(54, 4, 51, 60)
  const cpuForecast = flat(55, 3, 52, HORIZON)
  const cpuBand = band(cpuForecast, 5)

  const dropHistory = flat(0.35, 0.12, 61, 60)
  const dropForecast = flat(0.36, 0.1, 62, HORIZON)
  const dropBand = band(dropForecast, 0.2)

  return {
    scenarioId: 'bgp_flap',
    horizon_steps: HORIZON,
    step_minutes: STEP_MIN,
    generated_at: '02:18 UTC',
    series: [
      {
        metric: 'BGP Route Count',
        unit: ' routes',
        device: 'sj-edge-01',
        history: bgpHistory,
        forecast_p50: bgpForecast,
        forecast_p10: bgpBand.p10,
        forecast_p90: bgpBand.p90,
        threshold: 700,
        threshold_direction: 'below',
        trigger: {
          type: 'threshold', severity: 'critical',
          projected_minutes_ahead: 18,
          message: 'CTSM projects route count drop below 700 in 18 min — pre-position remediation',
          confidence: 0.87,
          model: 'CTSM',
        },
      },
      {
        metric: 'CPU Utilization',
        unit: '%',
        device: 'sj-edge-01',
        history: cpuHistory,
        forecast_p50: cpuForecast,
        forecast_p10: cpuBand.p10,
        forecast_p90: cpuBand.p90,
        threshold: 85,
        threshold_direction: 'above',
        trigger: {
          type: 'none', severity: 'none',
          projected_minutes_ahead: null,
          message: 'Stable — no projected change',
          confidence: 0.94,
          model: 'CTSM',
        },
      },
      {
        metric: 'Packet Drop Rate',
        unit: '%',
        device: 'sj-edge-01 GigE0/0',
        history: dropHistory,
        forecast_p50: dropForecast,
        forecast_p10: dropBand.p10,
        forecast_p90: dropBand.p90,
        threshold: 1.0,
        threshold_direction: 'above',
        trigger: {
          type: 'none', severity: 'none',
          projected_minutes_ahead: null,
          message: 'Stable — no projected change',
          confidence: 0.91,
          model: 'Chronos',
        },
      },
    ],
  }
}

// CPU SPIKE — CPU spikes with very wide P90 band, uncertainty trigger fires
function cpuSpikeBundle(): ForecastBundle {
  const bgpHistory = trend(847, 832, 6, 71, 60)
  const bgpForecast = trend(832, 815, 5, 72, HORIZON)
  const bgpBand = widenBand(bgpForecast, 8, 14)

  const cpuHistory = burst(64, 94, 55, 8, 4, 81, 60)
  const cpuForecast = trend(92, 88, 6, 82, HORIZON)
  const cpuBand = widenBand(cpuForecast, 8, 22)

  const dropHistory = flat(0.4, 0.15, 91, 60)
  const dropForecast = flat(0.42, 0.12, 92, HORIZON)
  const dropBand = band(dropForecast, 0.18)

  return {
    scenarioId: 'cpu_spike',
    horizon_steps: HORIZON,
    step_minutes: STEP_MIN,
    generated_at: '09:42 UTC',
    series: [
      {
        metric: 'BGP Route Count',
        unit: ' routes',
        device: 'sj-core-01',
        history: bgpHistory,
        forecast_p50: bgpForecast,
        forecast_p10: bgpBand.p10,
        forecast_p90: bgpBand.p90,
        threshold: 800,
        threshold_direction: 'below',
        trigger: {
          type: 'trajectory', severity: 'warning',
          projected_minutes_ahead: 95,
          message: 'Slight degradation — likely CPU contention spillover',
          confidence: 0.68,
          model: 'CTSM',
        },
      },
      {
        metric: 'CPU Utilization',
        unit: '%',
        device: 'sj-core-01',
        history: cpuHistory,
        forecast_p50: cpuForecast,
        forecast_p10: cpuBand.p10,
        forecast_p90: cpuBand.p90,
        threshold: 85,
        threshold_direction: 'above',
        trigger: {
          type: 'uncertainty', severity: 'critical',
          projected_minutes_ahead: 0,
          message: 'Wide P10–P90 band — model uncertain; behaviour anomalous on a core device',
          confidence: 0.49,
          model: 'CTSM + Chronos',
        },
      },
      {
        metric: 'Packet Drop Rate',
        unit: '%',
        device: 'sj-core-01 backplane',
        history: dropHistory,
        forecast_p50: dropForecast,
        forecast_p10: dropBand.p10,
        forecast_p90: dropBand.p90,
        threshold: 1.0,
        threshold_direction: 'above',
        trigger: {
          type: 'none', severity: 'none',
          projected_minutes_ahead: null,
          message: 'Stable — no projected change',
          confidence: 0.90,
          model: 'Chronos',
        },
      },
    ],
  }
}

// FALSE POSITIVE — alert fired, but forecast confirms baseline is stable
function falsePositiveBundle(): ForecastBundle {
  const bgpHistory = flat(847, 3, 101, 60)
  const bgpForecast = flat(847, 2, 102, HORIZON)
  const bgpBand = band(bgpForecast, 2)

  // Brief blip in history (the threshold breach that fired the alert) but forecast says baseline
  const cpuHistory = [...flat(58, 3, 111, 50), ...burst(58, 78, 3, 4, 1, 112, 10)]
  const cpuForecast = flat(60, 2, 113, HORIZON)
  const cpuBand = band(cpuForecast, 4)

  const dropHistory = flat(0.32, 0.08, 121, 60)
  const dropForecast = flat(0.33, 0.07, 122, HORIZON)
  const dropBand = band(dropForecast, 0.15)

  return {
    scenarioId: 'false_positive',
    horizon_steps: HORIZON,
    step_minutes: STEP_MIN,
    generated_at: '03:07 UTC',
    series: [
      {
        metric: 'BGP Route Count',
        unit: ' routes',
        device: 'sj-catalyst-04',
        history: bgpHistory,
        forecast_p50: bgpForecast,
        forecast_p10: bgpBand.p10,
        forecast_p90: bgpBand.p90,
        threshold: null,
        threshold_direction: 'below',
        trigger: {
          type: 'none', severity: 'none',
          projected_minutes_ahead: null,
          message: 'Flat baseline — no projected change',
          confidence: 0.96,
          model: 'CTSM',
        },
      },
      {
        metric: 'CPU Utilization',
        unit: '%',
        device: 'sj-catalyst-04',
        history: cpuHistory,
        forecast_p50: cpuForecast,
        forecast_p10: cpuBand.p10,
        forecast_p90: cpuBand.p90,
        threshold: 85,
        threshold_direction: 'above',
        trigger: {
          type: 'none', severity: 'info',
          projected_minutes_ahead: null,
          message: 'Brief spike in history; forecast returns to baseline — alert is noise',
          confidence: 0.93,
          model: 'CTSM + Chronos',
        },
      },
      {
        metric: 'Packet Drop Rate',
        unit: '%',
        device: 'sj-catalyst-04 GigE0/2',
        history: dropHistory,
        forecast_p50: dropForecast,
        forecast_p10: dropBand.p10,
        forecast_p90: dropBand.p90,
        threshold: 1.0,
        threshold_direction: 'above',
        trigger: {
          type: 'none', severity: 'none',
          projected_minutes_ahead: null,
          message: 'Flat baseline — no projected change',
          confidence: 0.94,
          model: 'Chronos',
        },
      },
    ],
  }
}

const BUNDLES: Record<string, ForecastBundle> = {
  packet_loss:    packetLossBundle(),
  bgp_flap:       bgpFlapBundle(),
  cpu_spike:      cpuSpikeBundle(),
  false_positive: falsePositiveBundle(),
}

export function getForecastBundle(scenarioId: string): ForecastBundle {
  return BUNDLES[scenarioId] ?? BUNDLES.packet_loss
}
