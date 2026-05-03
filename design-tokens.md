# Design Tokens — Vigil War Room Console

## Colour Tokens

| Token | Hex | Usage |
|---|---|---|
| `--color-bg` | `#0D1117` | Terminal background |
| `--color-surface` | `#161B22` | Panel surface |
| `--color-border` | `#30363D` | Panel borders |
| `--color-text-primary` | `#E6EDF3` | Primary text |
| `--color-text-muted` | `#8B949E` | Labels, metadata |
| `--color-accent` | `#1F6FEB` | Links, active state |
| `--color-success` | `#3FB950` | RESOLVED state, high scores |
| `--color-warning` | `#D29922` | HYPOTHESIZING state, mid scores |
| `--color-danger` | `#F85149` | ESCALATING state, low scores |
| `--color-ci` | `#1BA0D7` | CI tool badges |
| `--color-sp` | `#65A637` | SP tool badges |
| `--color-neutral` | `#6E7681` | IDLE / TRIAGE states |

## FSM State Colours

| State | Background | Text | Meaning |
|---|---|---|---|
| IDLE | `#161B22` | `#6E7681` | Waiting |
| TRIAGE | `#161B22` | `#D29922` | Classifying |
| INVESTIGATING | `#0D419D` | `#79C0FF` | Active tool calls |
| HYPOTHESIZING | `#3B2300` | `#F0883E` | Building hypothesis |
| REMEDIATING | `#0F2D1E` | `#3FB950` | Applying fix |
| ESCALATING | `#2D0F0F` | `#F85149` | Needs human |
| RESOLVED | `#0F2D1E` | `#3FB950` | Done |

## Typography

| Role | Font | Weight | Size | Notes |
|---|---|---|---|---|
| Panel headers | JetBrains Mono | 600 | 11px | Uppercase, letter-spaced |
| Body text | JetBrains Mono | 400 | 12px | All terminal output |
| State badges | JetBrains Mono | 700 | 10px | All caps |
| JSON output | JetBrains Mono | 400 | 11px | Syntax highlighted |
| Score values | JetBrains Mono | 600 | 14px | Tabular nums |

*All fonts: monospace only — this is a terminal dashboard, not a web UI.*

## Layout Zones

```
┌──────────────────────────────────────────────────────────────┐
│  HEADER — incident ID · current state · elapsed time · cost  │
├──────────────┬──────────────────────────┬────────────────────┤
│              │                          │                    │
│  ZONE 1      │  ZONE 2                  │  ZONE 3            │
│  MCP Tool    │  FSM Commander           │  Evaluator         │
│  Registry    │  Reasoning Trace         │  Score Panel       │
│              │                          │                    │
│  6 tools     │  State transitions       │  Precision         │
│  RBAC status │  Tool call log           │  Recall            │
│  Connection  │  Hypothesis building     │  Token cost        │
│  status      │  Confidence score        │  Tool efficiency   │
│              │                          │  Composite         │
├──────────────┴──────────────────────────┴────────────────────┤
│  FOOTER — recommended action · confidence · escalation path  │
└──────────────────────────────────────────────────────────────┘
```

### Zone Specifications

**Zone 1 — MCP Tool Registry** (25% width)
- Lists all 6 tools with source badge (SP / CI)
- Shows last-called tool highlighted in `--color-accent`
- Connection status: `●  LIVE` in `--color-success` or `○  MOCK` in `--color-warning`

**Zone 2 — FSM Commander** (50% width)
- State machine progress bar at top (7 states, active one highlighted)
- Scrolling trace log: timestamp · state · action · result
- Current hypothesis block in `--color-warning` until RESOLVED/ESCALATING
- Confidence meter: 0.00 → 1.00 with colour threshold at 0.75

**Zone 3 — Evaluator Score Panel** (25% width)
- Updates after each model comparison run
- Score rows: label · generic value · constrained value · delta
- Token cost row bold and colour-coded by magnitude
- Composite score at bottom with pass/fail threshold line

## Score Colour Scale

| Score | Colour | Hex |
|---|---|---|
| 0.85 – 1.00 | Green | `#3FB950` |
| 0.70 – 0.84 | Amber | `#D29922` |
| 0.00 – 0.69 | Red | `#F85149` |

## Tool Call Anatomy

```
┌─ TOOL CALL ────────────────────────────────────┐
│  [14:32:07]  run_spl_query          [SP]   │
│  ─────────────────────────────────────────────  │
│  Input:  index=network host=SJ-SW-01           │
│          | stats avg(out_errors) by interface   │
│  ─────────────────────────────────────────────  │
│  Result: GigE0/1  out_errors=2847/min  ▲ SPIKE │
│  Tokens: 312 in / 89 out                       │
└────────────────────────────────────────────────┘
```

## Animation Rules

- State transitions: 150ms fade on badge colour change — no slide or bounce
- Tool call card: appears instantly, no animation
- Score delta: 300ms count-up on numeric values
- ESCALATING state: static red border — no pulse (urgency without distraction)
- Token cost: updates in real time after each API call
