# Incident Scenarios

Three reference scenarios cover the two FSM exit paths and one pre-triage suppression.
Running A + B back-to-back validates that the routing logic is real and not hardcoded.
Scenario D validates the pre-triage classifier independently.

---

## Scenario Comparison

| Field | A — Packet Loss | B — BGP Flap | C — CPU Spike |
|---|---|---|---|
| Incident ID | INC-20240214-001 | INC-20240214-002 | INC-20240214-004 |
| Priority | P2 | P3 | P1 |
| Device | sj-catalyst-01 | sj-core-02 | sj-core-01 |
| Tool calls | 5 | 4 | 5 |
| Final state | **ESCALATING** | **REMEDIATING** | **ESCALATING** |
| Tokens | 4,847 | 3,241 | 5,102 |
| Confidence | 0.93 | 0.97 | 0.89 |
| Decision trigger | src_ip >60% of egress | keepalive_timeout, no threats | unknown pid, high blast radius |
| Demo value | Security escalation path | Safe auto-remediation path | High blast radius escalation |

---

## Scenario A — Packet Loss / Potential Exfiltration

**File:** `packet_loss_sj.json`

Interface `GigE0/1` on `sj-catalyst-01` is dropping packets with 2,847 out_errors/min.
Netflow analysis shows a single internal IP (`10.14.22.87`) accounts for 71.2% of
egress traffic, exceeding the 60% threshold. 847 distinct destination IPs are observed
(high port spread). The FSM routes to **ESCALATING** at HYPOTHESIZING because the egress
threshold breach satisfies the first ESCALATING trigger in `decide_next_state`.

FSM path: `IDLE → TRIAGE → INVESTIGATING → ESCALATING → RESOLVED`

---

## Scenario B — BGP Flap / Keepalive Timeout

**File:** `bgp_flap_sj.json`

BGP peer `10.14.0.1` on `sj-core-02` has reset 3 times in the last hour. Splunk logs
show the reset reason is `keepalive_timeout` consistently across all 3 flaps. No
concurrent interface anomalies. No traffic anomalies on adjacent interfaces. No threat
intel hits.

The FSM routes to **REMEDIATING** because all four gate conditions in `decide_next_state`
are satisfied:

1. `is_security_threat = False`
2. `root_cause = "keepalive_timeout"` is in `_SAFE_REMEDIATION_PATTERNS`
3. `confidence = 0.97 >= 0.90`
4. `concurrent_anomalies = False`

Recommended action: increase BGP hold-time from 90s to 180s on `sj-core-02` and its
peer. Reversible, low-blast-radius, deterministic expected outcome.

FSM path: `IDLE → TRIAGE → INVESTIGATING → HYPOTHESIZING → REMEDIATING → RESOLVED`

---

## Scenario C — CPU Spike / Unknown Process

**File:** `cpu_spike_sj.json`

CPU utilization on `sj-core-01` reached 94%. An unknown pid is consuming 24% CPU.
BGP and STP are both showing degraded performance. The device is a core switch with
multiple downstream dependencies — high blast radius. No safe remediation pattern
matches the unknown process.

The FSM routes to **ESCALATING** because:
- `root_cause = "unknown_process"` is not in `_SAFE_REMEDIATION_PATTERNS`
- `blast_radius = "high"` triggers the high blast radius ESCALATING rule
- `is_security_threat` is ambiguous — unknown process on core infra

FSM path: `IDLE → TRIAGE → INVESTIGATING → HYPOTHESIZING → ESCALATING → RESOLVED`

---

## Scenario D — False Positive (Pre-Triage Suppression)

**File:** `false_positive_demo.json`

CPU warning threshold breach on `sj-core-01`. Single alert, no correlated signals.
The same alert has fired 5 times in the last hour without escalation. Raw severity: low.

This scenario is handled by the **pre-triage classifier** (`phase2_agent/pre_triage.py`)
before the FSM is invoked. The classifier scores the alert and suppresses it — no LLM
call is made, no tokens are spent. This demonstrates the 0-token suppression path for
high-volume noise alerts.

Pre-triage result: `SUPPRESS` (repeat_count=5, single signal, no correlated anomalies)

---

## Why Three FSM Scenarios Matter

A demo that only ever escalates proves nothing about the decision logic. Any model that
defaults to "escalate when uncertain" would produce the same output on Scenario A.

Scenario B forces the FSM to prove it can distinguish a **security threat** (which must
involve a human) from a **deterministic operational fault** (which can be resolved
automatically). The gap between the two paths is the core product claim:

> Vigil reduces Mean Time to Resolve (MTTR) for known-safe incidents by routing them
> to auto-remediation, while reserving human attention for genuine threats.

Scenario C demonstrates the second ESCALATING path — not because of a security signal,
but because of operational risk (unknown process, high blast radius). This proves the
FSM has two distinct escalation reasons, not one.

Running all three scenarios also produces three different token profiles (4,847 / 3,241 /
5,102) and three different evaluator outcomes, making the cost-per-incident comparison
more credible than a single data point.

If the FSM were hardcoded to always escalate, Scenario B would fail its
`expected_final_state` assertion. A passing Scenario B run is therefore a correctness
gate for the routing logic, not just a demo.
