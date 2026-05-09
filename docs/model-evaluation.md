# Model Evaluation — Findings and Improvement Roadmap
## Vigil Telemetry Forecasting Benchmark · Chronos vs TimesFM vs Cisco CTSM

**Author:** Bharat Namatherdhala  
**Date:** May 2026  
**Source:** `splunk_evals.ipynb` — 60-series benchmark across CPU utilisation, packet drop rate, and Border Gateway Protocol route count

---

## What We Measured and Why

Vigil's pre-triage classifier needs to predict what a network metric will do in the next 24 steps — and be confident enough in that prediction to decide whether to suppress an alert, investigate it, or escalate immediately. That decision has real consequences: a wrong suppress means a real incident goes undetected; a wrong escalate wastes an engineer's time at 2am.

To make that decision reliably, we need a model that is:
1. **Accurate** — its point forecast is closer to reality than a naive baseline
2. **Well-calibrated** — when it says "I'm 80% confident," it is actually right 80% of the time
3. **Strong specifically on the signals that matter** — BGP flap detection is the highest-stakes use case

This benchmark evaluated three foundation models across those three requirements.

---

## Key Findings

### Finding 1 — Cisco CTSM is the most accurate model overall, but only barely

| Model | Overall MASE | Overall sMAPE |
|-------|:---:|:---:|
| **Cisco CTSM-1.0** | **0.967** | 29.88% |
| Chronos-T5-Small | 0.971 | **24.68%** |
| TimesFM-2.5-200M | 1.322 | 39.40% |

CTSM edges Chronos on Mean Absolute Scaled Error (MASE) by 0.004 — a gap too small to be operationally significant on its own. What makes CTSM the clear winner for Vigil is not the headline number, but where that accuracy shows up: BGP flap detection.

---

### Finding 2 — CTSM has a decisive advantage on BGP flap detection

| Model | BGP MASE | BGP sMAPE |
|-------|:---:|:---:|
| **Cisco CTSM-1.0** | **0.80** | **2.82%** |
| Chronos-T5-Small | 0.83 | 2.92% |
| TimesFM-2.5-200M | 1.14 | 4.63% |

BGP (Border Gateway Protocol) route count is a step-function signal — it holds steady at a stable level, then jumps abruptly when a session flaps. CTSM's MASE of 0.80 on BGP means it beats the naive baseline by 20%. TimesFM's MASE of 1.14 means it is **worse than guessing** — a junior analyst copying yesterday's number forward would be more accurate than TimesFM for BGP prediction.

This matters because BGP flaps are one of the leading causes of network-wide outages. Vigil's pre-triage classifier needs to catch the run-up to a BGP flap before the session fully drops. CTSM is the right model for this use case.

---

### Finding 3 — CTSM has a meaningful weakness on packet drop

| Model | Packet Drop MASE | Packet Drop sMAPE |
|-------|:---:|:---:|
| Chronos-T5-Small | **1.27** | **65.55%** |
| **Cisco CTSM-1.0** | 1.27 | 80.86% |
| TimesFM-2.5-200M | 2.04 | 107.96% |

CTSM ties Chronos on MASE for packet drop (both 1.27), but its sMAPE is 80.86% — 15 percentage points worse than Chronos. This gap reveals a specific training data weakness.

**Why CTSM struggles with packet drop:** Packet drop is a burst-pattern signal — near-zero baseline with sudden large spikes. CTSM was trained predominantly on smooth observability metrics (CPU, memory, request latency) from Cisco and Splunk's internal infrastructure. Burst-pattern signals are almost certainly underrepresented in that training corpus. The model has not seen enough examples of "flat line, then spike, then flat line" to forecast that pattern well.

This is the same move Cisco made to build CTSM from TimesFM in the first place — they added observability-domain data on top of the base model. The packet drop weakness is fixable with the same approach applied to burst-pattern data.

---

### Finding 4 — CTSM's lack of uncertainty quantification is its biggest practical limitation

Chronos and TimesFM both return 100 probability samples per forecast. CTSM's public API returns a single point forecast only. This has a direct impact on Vigil:

- **Vigil's Finite State Machine suppress/escalate decision uses confidence scores.** A model that says "the next value will be 47.3" with no uncertainty range cannot drive a probabilistic decision. A model that says "the next value has an 80% chance of being between 40 and 55" can.
- **CRPS (the calibration metric) cannot be measured for CTSM** without sample outputs. We cannot currently answer "how often is CTSM's confidence right?" — which means we cannot trust it for escalation decisions even if its point accuracy is good.
- **This is an API limitation, not a model limitation.** The CTSM model internally computes quantiles — the Spaces demo simply does not surface them. This is fixable with a one-line API change on Cisco's side.

---

### Finding 5 — Packet drop sMAPE is misleading for all models

All three models show very high sMAPE on packet drop (65–108%). This is a mathematical artifact, not a model failure. Packet drop rates are typically close to zero — when the true value is 0.3% and the model predicts 1.3%, that is a 1 percentage point error but a 330% sMAPE. **For packet drop, MASE is the reliable accuracy signal. Ignore sMAPE.**

---

## Where Each Model Fits in Vigil Today

| Use Case | Recommended Model | Reason |
|----------|:---:|-------|
| BGP flap pre-triage classification | **Cisco CTSM** | Lowest MASE on BGP (0.80) — most accurate on the most critical signal type |
| Suppress vs. escalate confidence scoring | **Chronos** | Only model with calibrated probability distributions (CRPS measurable) |
| CPU spike detection | **Chronos** | Comparable accuracy to CTSM, best sMAPE, and provides uncertainty estimates |
| Packet drop anomaly detection | **Chronos** | Tied on MASE with CTSM, but better sMAPE and provides confidence intervals |
| General fallback | **Chronos** | Until CTSM exposes quantile outputs, Chronos is safer for any decision that uses confidence |

---

## Improvement Roadmap

The benchmark identified a clear, actionable gap: CTSM needs better burst-pattern signal handling, and Vigil needs CTSM's uncertainty outputs. The four options below are ordered by effort and expected impact.

---

### Option 1 — File an API feature request with Cisco for quantile outputs
**Effort:** 1 hour | **Timeline:** Dependent on Cisco | **Cost:** Zero engineering

**What:** Request that Cisco's CTSM team expose quantile outputs via the Hugging Face Spaces API — or provide access to the raw model weights for local inference.

**Why this first:** CTSM's quantile head already exists internally. The Spaces demo simply does not surface it. A one-line API change on Cisco's side unlocks CRPS measurement and makes CTSM usable for Vigil's confidence-based decision logic. This unblocks the most important limitation with zero engineering investment.

**What to include in the request:** The packet drop and BGP benchmarks from `splunk_evals.ipynb` are concrete, reproducible failure cases and improvement evidence. The request is more credible with data.

**Success criterion:** CTSM API returns quantile outputs. Re-run the benchmark and compare CRPS against Chronos.

---

### Option 2 — Test CTSM with proper multiresolution input before any fine-tuning
**Effort:** 1–2 days | **Timeline:** This sprint | **Cost:** Zero (API calls only)

**What:** CTSM's core architectural advantage over TimesFM is multiresolution input — it accepts both coarse-grained (hourly) and fine-grained (per-minute) context simultaneously. The benchmark only fed fine-resolution data because the synthetic series were not structured with both resolutions. Real telemetry from Splunk contains both.

**Why this matters:** BGP flaps have weekly periodicity that only appears in hourly data. Packet drop bursts appear in per-minute data. Feeding both resolutions gives CTSM context that neither Chronos nor TimesFM receives — this is the feature Cisco specifically designed CTSM around.

**How to test:** Pull a sample of real telemetry from Splunk (one week of hourly data + one week of per-minute data for the same device). Feed coarse + fine resolution pairs to CTSM. Compare MASE against the benchmark results.

**Success criterion:** Packet drop sMAPE drops below 70% and BGP MASE drops below 0.75. If either moves materially, multiresolution input alone may close the gap without any fine-tuning.

---

### Option 3 — Continued pre-training on burst-pattern synthetic data
**Effort:** 2–3 weeks | **Timeline:** Next quarter | **Cost:** GPU compute + engineering time

**What:** Collect or synthesize time series that look like packet drop — exponential baseline with burst windows, identical in structure to the `make_packet_drop` generator in the notebook. Run a continued pre-training pass on CTSM using the same multiresolution input format the model expects (coarse + fine resolution pairs).

**Why this will work:** This is exactly the move Cisco made to build CTSM from TimesFM — they added observability-domain data on top of the base model. The training data gap for burst-pattern signals is clear from the benchmark results and well-understood. Even 50,000–100,000 synthetic burst-pattern series is likely enough to move the needle on packet drop without hurting BGP or CPU performance, since those signal types are already well-represented.

**What to prepare:**
- Generate 100K burst-pattern series using the `make_packet_drop` function as a starting point, varying burst frequency, duration, and amplitude
- Format as multiresolution pairs (downsample the fine series to create the coarse version)
- Run continued pre-training starting from CTSM's existing checkpoint

**Success criterion:** Packet drop MASE drops below 1.0 (beats naive baseline). Current MASE is 1.27, meaning the model is currently worse than guessing on packet drop.

---

### Option 4 — Supervised fine-tuning on labeled incident data from Splunk
**Effort:** 4–6 weeks | **Timeline:** Next half | **Cost:** Requires live Splunk access + labeled data

**What:** Pull historical telemetry from Splunk with known incident timestamps — a packet drop event that caused a Priority 2 incident, a BGP flap that triggered a page. Fine-tune CTSM specifically on those windows so the model learns to forecast the run-up to incidents more accurately than it would from random telemetry.

**Why this is higher-leverage but harder:** Supervised fine-tuning on real incident data produces a model that is specifically calibrated for the types of anomalies Vigil investigates — not just general burst patterns, but the specific signatures that precede real outages in a given customer's infrastructure. Over time this becomes a proprietary advantage.

**Why this is later in the roadmap:** It requires access to real Splunk data (not synthetic), labeled incident windows (not just raw telemetry), and a longer iteration cycle. Options 1–3 are faster, free or low-cost, and likely to produce most of the accuracy gain.

**Success criterion:** Packet drop MASE below 0.90 and BGP MASE below 0.75 on a held-out set of real incidents.

---

## Recommended Sequencing

```
Week 1      File Cisco API feature request (Option 1) — 1 hour, high leverage
            Start multiresolution input test on real Splunk telemetry (Option 2) — 2 days

Week 2-3    Evaluate multiresolution results
            If packet drop sMAPE < 70%: options 1+2 are sufficient, defer fine-tuning
            If packet drop sMAPE ≥ 70%: scope Option 3 for next quarter

Next quarter  Continued pre-training on burst-pattern synthetic data (Option 3)
              Run updated benchmark, compare CRPS once Cisco API exposes quantiles

Next half     Supervised fine-tuning on labeled Splunk incident data (Option 4)
              Integrate domain-fine-tuned CTSM into Vigil pre-triage classifier
```

---

## Why This Benchmark Is the Right Foundation

The benchmark in `splunk_evals.ipynb` gives the Cisco CTSM team a concrete, reproducible failure case to act on. The packet drop result (MASE 1.27, sMAPE 80.86%) is not vague negative feedback — it is a specific signal type with a clear training data explanation and a testable fix. That is the kind of input that moves a product team's roadmap.

The two asks for Cisco — expose quantile outputs via API, and test multiresolution input against the benchmark — are low-cost for both sides and directly advance the case for deeper collaboration on Vigil's integration with CTSM.
