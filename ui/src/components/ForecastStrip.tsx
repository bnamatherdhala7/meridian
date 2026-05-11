import { useMemo, useState } from 'react'
import { getForecastBundle, type ForecastSeries, type TriggerType } from '../data/forecasts'

interface Props {
  scenarioId: string
}

const TRIGGER_COLOR: Record<TriggerType, string> = {
  threshold:   'var(--orange)',
  trajectory:  'var(--amber)',
  uncertainty: 'var(--violet)',
  none:        'var(--green)',
}

const TRIGGER_LABEL: Record<TriggerType, string> = {
  threshold:   'THRESHOLD',
  trajectory:  'TRAJECTORY',
  uncertainty: 'UNCERTAINTY',
  none:        'STABLE',
}

const SEVERITY_GLOW: Record<string, string> = {
  critical: '0 0 0 1px var(--orange), 0 4px 12px rgba(239,95,51,0.18)',
  warning:  '0 0 0 1px var(--amber), 0 2px 8px rgba(245,158,11,0.15)',
  info:     'var(--shadow-md)',
  none:     'var(--shadow-md)',
}

// SVG sparkline + P10–P90 confidence band
function Sparkline({ series, width, height }: { series: ForecastSeries; width: number; height: number }) {
  const { history, forecast_p50, forecast_p10, forecast_p90, threshold, trigger } = series
  const all = [...history, ...forecast_p50, ...forecast_p10, ...forecast_p90, ...(threshold !== null ? [threshold] : [])]
  const min = Math.min(...all)
  const max = Math.max(...all)
  const range = max - min || 1
  const pad = 4
  const innerH = height - pad * 2
  const innerW = width - pad * 2
  const totalPoints = history.length + forecast_p50.length
  const stepX = innerW / (totalPoints - 1)

  const yOf = (v: number) => pad + innerH - ((v - min) / range) * innerH
  const xOf = (i: number) => pad + i * stepX

  const historyPath = history.map((v, i) => `${i === 0 ? 'M' : 'L'} ${xOf(i).toFixed(1)} ${yOf(v).toFixed(1)}`).join(' ')

  const forecastStart = history.length - 1
  const p50Path = forecast_p50.map((v, i) =>
    `${i === 0 ? 'M' : 'L'} ${xOf(forecastStart + i).toFixed(1)} ${yOf(v).toFixed(1)}`
  ).join(' ')

  // Confidence band — polygon between P90 (top) and P10 (bottom)
  const bandUp   = forecast_p90.map((v, i) => `${xOf(forecastStart + i).toFixed(1)},${yOf(v).toFixed(1)}`).join(' ')
  const bandDown = forecast_p10.map((v, i) => `${xOf(forecastStart + i).toFixed(1)},${yOf(v).toFixed(1)}`).reverse().join(' ')
  const bandPoints = `${bandUp} ${bandDown}`

  const triggerColor = TRIGGER_COLOR[trigger.type]
  const forecastDividerX = xOf(forecastStart)

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      style={{ display: 'block' }}
    >
      {/* Threshold line */}
      {threshold !== null && (
        <line
          x1={pad} y1={yOf(threshold)} x2={width - pad} y2={yOf(threshold)}
          stroke="var(--orange)"
          strokeWidth={1}
          strokeDasharray="3 3"
          opacity={0.55}
        />
      )}

      {/* Now divider */}
      <line
        x1={forecastDividerX} y1={pad} x2={forecastDividerX} y2={height - pad}
        stroke="var(--subtle)"
        strokeWidth={1}
        strokeDasharray="2 2"
        opacity={0.45}
      />

      {/* P10–P90 confidence band */}
      <polygon
        points={bandPoints}
        fill={triggerColor}
        opacity={0.13}
      />

      {/* History — solid */}
      <path
        d={historyPath}
        fill="none"
        stroke="var(--text)"
        strokeWidth={1.4}
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* P50 forecast — dashed */}
      <path
        d={p50Path}
        fill="none"
        stroke={triggerColor}
        strokeWidth={1.6}
        strokeDasharray="3 2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function ForecastCard({ series, width }: { series: ForecastSeries; width: number }) {
  const [open, setOpen] = useState(false)
  const lastHistory = series.history[series.history.length - 1]
  const lastForecast = series.forecast_p50[series.forecast_p50.length - 1]
  const triggerColor = TRIGGER_COLOR[series.trigger.type]
  const triggerLabel = TRIGGER_LABEL[series.trigger.type]
  const pulsing = series.trigger.severity === 'critical'

  return (
    <div
      className="forecast-card"
      style={{
        background: 'var(--card)',
        border: '1px solid var(--border-md)',
        borderRadius: 10,
        padding: '10px 12px 8px',
        boxShadow: SEVERITY_GLOW[series.trigger.severity],
        display: 'flex',
        flexDirection: 'column',
        gap: 6,
        minWidth: 0,
        transition: 'box-shadow 0.2s ease',
      }}
    >
      {/* Top row — metric + device + trigger pill */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{
            fontFamily: 'var(--font-sans)',
            fontSize: 12,
            fontWeight: 500,
            color: 'var(--text)',
            lineHeight: 1.1,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            {series.metric}
          </div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 9,
            color: 'var(--subtle)',
            marginTop: 2,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            {series.device}
          </div>
        </div>

        <span
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 9,
            fontWeight: 700,
            letterSpacing: '0.07em',
            color: triggerColor,
            background: `${triggerColor}18`,
            border: `1px solid ${triggerColor}38`,
            borderRadius: 20,
            padding: '2px 8px',
            whiteSpace: 'nowrap',
            animation: pulsing ? 'forecastPulse 1.4s ease-in-out infinite' : undefined,
          }}
        >
          {triggerLabel}
        </span>
      </div>

      {/* Sparkline */}
      <Sparkline series={series} width={width} height={56} />

      {/* Bottom row — now / forecast values + projected time */}
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, minWidth: 0 }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)' }}>NOW</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 600, color: 'var(--text)' }}>
            {lastHistory.toFixed(series.unit === '%' ? 2 : 0)}{series.unit}
          </span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--subtle)' }}>+2h</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: 600, color: triggerColor }}>
            {lastForecast.toFixed(series.unit === '%' ? 2 : 0)}{series.unit}
          </span>
        </div>

        {series.trigger.projected_minutes_ahead !== null && (
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 10,
            fontWeight: 600,
            color: triggerColor,
            whiteSpace: 'nowrap',
          }}>
            T−{series.trigger.projected_minutes_ahead}min
          </span>
        )}
      </div>

      {/* Trigger reasoning — collapsible */}
      <button
        onClick={() => setOpen(v => !v)}
        style={{
          background: 'transparent',
          border: 'none',
          padding: 0,
          margin: 0,
          textAlign: 'left',
          cursor: 'pointer',
          fontFamily: 'var(--font-sans)',
          fontSize: 10,
          color: 'var(--muted)',
          lineHeight: 1.35,
          display: 'flex',
          alignItems: 'flex-start',
          gap: 4,
        }}
      >
        <span style={{ color: 'var(--subtle)', fontFamily: 'var(--font-mono)', fontSize: 9, paddingTop: 1 }}>
          {open ? '▾' : '▸'}
        </span>
        <span style={{ flex: 1 }}>{series.trigger.message}</span>
      </button>

      {open && (
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 9,
          color: 'var(--muted)',
          background: 'var(--surface)',
          borderRadius: 6,
          padding: '6px 8px',
          display: 'flex',
          flexDirection: 'column',
          gap: 3,
        }}>
          <div><span style={{ color: 'var(--subtle)' }}>model:</span> {series.trigger.model}</div>
          <div><span style={{ color: 'var(--subtle)' }}>confidence:</span> {(series.trigger.confidence * 100).toFixed(0)}%</div>
          {series.threshold !== null && (
            <div><span style={{ color: 'var(--subtle)' }}>threshold:</span> {series.threshold_direction === 'above' ? '>' : '<'} {series.threshold}{series.unit}</div>
          )}
          <div><span style={{ color: 'var(--subtle)' }}>history:</span> 60 steps · <span style={{ color: 'var(--subtle)' }}>horizon:</span> 24 steps × 5min</div>
        </div>
      )}
    </div>
  )
}

export default function ForecastStrip({ scenarioId }: Props) {
  const bundle = useMemo(() => getForecastBundle(scenarioId), [scenarioId])
  const criticalCount = bundle.series.filter(s => s.trigger.severity === 'critical').length
  const warningCount = bundle.series.filter(s => s.trigger.severity === 'warning').length

  return (
    <div className="card forecast-card-container">
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="card-title">Forecast Engine — Proactive Layer</span>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 9,
            color: 'var(--subtle)',
            letterSpacing: '0.04em',
          }}>
            CTSM + Chronos · 24-step horizon · 5min steps
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {criticalCount > 0 && (
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 9,
              fontWeight: 700,
              letterSpacing: '0.06em',
              color: 'var(--orange)',
              background: 'rgba(239,95,51,0.12)',
              border: '1px solid rgba(239,95,51,0.3)',
              borderRadius: 20,
              padding: '2px 8px',
            }}>
              {criticalCount} CRITICAL TRIGGER{criticalCount > 1 ? 'S' : ''}
            </span>
          )}
          {warningCount > 0 && (
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 9,
              fontWeight: 700,
              letterSpacing: '0.06em',
              color: 'var(--amber)',
              background: 'rgba(245,158,11,0.12)',
              border: '1px solid rgba(245,158,11,0.3)',
              borderRadius: 20,
              padding: '2px 8px',
            }}>
              {warningCount} WARNING
            </span>
          )}
          {criticalCount === 0 && warningCount === 0 && (
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 9,
              fontWeight: 700,
              letterSpacing: '0.06em',
              color: 'var(--green)',
              background: 'rgba(0,166,80,0.12)',
              border: '1px solid rgba(0,166,80,0.3)',
              borderRadius: 20,
              padding: '2px 8px',
            }}>
              ALL STABLE
            </span>
          )}
        </div>
      </div>

      <div className="forecast-grid">
        {bundle.series.map((s, i) => (
          <ForecastCard key={i} series={s} width={300} />
        ))}
      </div>
    </div>
  )
}
