# Model Evaluation — Findings and Improvement Roadmap
## Vigil Telemetry Forecasting Benchmark · Chronos vs. TimesFM vs. Cisco Time Series Model

**Author:** Bharat Namatherdhala
**Date:** May 2026
**Source notebook:** `splunk_evals.ipynb` — 60-series benchmark across Central Processing Unit utilisation, packet drop rate, and Border Gateway Protocol route count

---

## What This Document Is

This is a Product Manager's read of the Vigil model benchmark. It answers three questions a non-machine-learning reader needs answered before they can act on the results:

1. **What was measured, and what does each metric actually mean?**
2. **Which model is best for which Vigil use case, and why?**
3. **What is the prioritized list of things to do next, with clear owners and timelines?**

If you only read one section, read **Plain-English Verdict** below.

---

## Plain-English Verdict

> **Cisco Time Series Model (CTSM) is the most accurate model overall, and decisively the best for Border Gateway Protocol flap prediction — but it cannot drive Vigil's confidence-based decisions today because its public Application Programming Interface returns a single number per forecast, not a probability range. The single highest-leverage next step is asking Cisco to expose quantile outputs (one hour of work, zero engineering investment, unblocks everything downstream).**

The four roadmap items, in priority order:

| Priority | Item | Effort | Who | Outcome |
|:---:|---|---|---|---|
| **P0** | Ask Cisco to expose quantile outputs via Application Programming Interface | 1 hour | Product → Cisco team | Unblocks Continuous Ranked Probability Score measurement and confidence-based routing |
| **P1** | Test Cisco Time Series Model with multiresolution input on real Splunk telemetry | 1–2 days | Vigil engineering | May close the packet drop accuracy gap with zero training |
| **P2** | Continued pre-training on burst-pattern synthetic data | 2–3 weeks | Vigil engineering + Graphics Processing Unit budget | Fixes the structural training data gap for packet drop |
| **P3** | Supervised fine-tuning on labeled Splunk incident data | 4–6 weeks | Vigil engineering + Splunk data access | Domain-specific model calibrated to the customer's actual incidents |

---

## Metric Glossary — How to Read the Numbers

Three metrics drive every claim in this document. Here is what each one means in plain English, why it is used, and how to read its values.

### Mean Absolute Scaled Error (MASE)

- **What it measures:** How accurate the model's point forecast is, compared to a naive baseline. The naive baseline is "just copy yesterday's number forward."
- **How to read it:** A score of **1.0** means the model is exactly as accurate as the naive baseline. **Below 1.0** means the model beats the baseline. **Above 1.0** means the model is *worse than guessing yesterday's number* — a serious red flag.
- **Why this metric:** Mean Absolute Scaled Error is scale-independent and works whether the values are in milliseconds or billions of bytes. It also exposes models that look accurate on average but fail to beat the dumbest possible alternative.
- **Vigil's threshold:** Anything above 1.0 is unusable for live network operations. We need at least 0.85 to consider a model production-ready for that signal.

### Symmetric Mean Absolute Percentage Error (sMAPE)

- **What it measures:** The average percentage error between the prediction and the actual value, expressed symmetrically so over-predictions and under-predictions are weighted equally.
- **How to read it:** **Lower is better.** A symmetric Mean Absolute Percentage Error of 5% means the model is on average within 5% of the true value. Values above 50% mean the model is essentially guessing.
- **Why this metric:** It is intuitive — humans understand "off by 30%" instinctively, while Mean Absolute Scaled Error requires explanation.
- **The trap:** symmetric Mean Absolute Percentage Error becomes mathematically broken when the true value is near zero. A true value of 0.3% with a prediction of 1.3% is a 1 percentage point error — a tiny absolute error — but produces a 330% symmetric Mean Absolute Percentage Error. **For packet drop data (which sits near zero most of the time), ignore symmetric Mean Absolute Percentage Error and trust Mean Absolute Scaled Error instead.**

### Continuous Ranked Probability Score (CRPS)

- **What it measures:** How well-calibrated the model's *uncertainty* is — not just its prediction, but its confidence in that prediction. A model that says "I'm 80% confident the value will be between 40 and 55" is correct if it actually lands inside that range 80% of the time.
- **How to read it:** **Lower is better.** It penalises both inaccurate point predictions and over-confident or under-confident probability ranges.
- **Why this metric:** Vigil's whole architecture is built on confidence-based routing. The Finite State Machine's SUPPRESSED / REMEDIATING / ESCALATING decisions need to know not just "what will happen" but "how sure are we." Continuous Ranked Probability Score is the only metric that measures that calibration.
- **Why it cannot be measured for Cisco Time Series Model today:** The public Cisco Time Series Model Application Programming Interface returns a single point estimate. With no probability samples, there is no probability distribution to score. This is the single most important practical limitation in the benchmark.

### Acronyms Used Throughout

| Short Form | Full Form | What It Means in This Context |
|---|---|---|
| **CTSM** | Cisco Time Series Model | Cisco's foundation model for time-series forecasting, built on top of TimesFM with observability data added |
| **BGP** | Border Gateway Protocol | The protocol that decides how internet traffic flows between networks. Flap detection is one of the highest-stakes signals in network operations. |
| **CPU** | Central Processing Unit | Standard server CPU utilisation metric, smooth and well-behaved compared to packet drop |
| **API** | Application Programming Interface | The public endpoint Cisco exposes for calling the Cisco Time Series Model — currently single-point-forecast only |
| **GPU** | Graphics Processing Unit | Required for continued pre-training in Priority 2 of the roadmap |
| **MASE** | Mean Absolute Scaled Error | See Metric Glossary above |
| **sMAPE** | symmetric Mean Absolute Percentage Error | See Metric Glossary above |
| **CRPS** | Continuous Ranked Probability Score | See Metric Glossary above |

---

## What We Measured and Why

Vigil's pre-triage classifier needs to predict what a network metric will do in the next 24 steps — and be confident enough in that prediction to decide whether to suppress an alert, investigate it, or escalate immediately. That decision has real consequences: a wrong suppress means a real incident goes undetected; a wrong escalate wastes an engineer's time at 2am.

To make that decision reliably, the model must be:

1. **Accurate** — its point forecast must be closer to reality than a naive baseline (Mean Absolute Scaled Error below 1.0)
2. **Well-calibrated** — when it says "I am 80% confident," it must actually be right 80% of the time (Continuous Ranked Probability Score below the Chronos baseline)
3. **Strong specifically on the signals that matter most** — Border Gateway Protocol flap detection is the highest-stakes use case, since Border Gateway Protocol flaps cause network-wide outages

This benchmark evaluated three foundation models against those three requirements:

- **Cisco Time Series Model (CTSM-1.0)** — Cisco's network-tuned model
- **Chronos-T5-Small** — Amazon's foundation model
- **TimesFM-2.5-200M** — Google's foundation model

---

## Key Findings

### Finding 1 — Cisco Time Series Model is the most accurate model overall, but only barely

| Model | Overall Mean Absolute Scaled Error | Overall symmetric Mean Absolute Percentage Error |
|-------|:---:|:---:|
| **Cisco Time Series Model 1.0** | **0.967** | 29.88% |
| Chronos-T5-Small | 0.971 | **24.68%** |
| TimesFM-2.5-200M | 1.322 | 39.40% |

Cisco Time Series Model edges Chronos on Mean Absolute Scaled Error by 0.004 — a gap too small to matter operationally on its own. What makes Cisco Time Series Model the clear winner for Vigil is not the headline number, but **where** that accuracy shows up: Border Gateway Protocol flap detection (Finding 2).

TimesFM's Mean Absolute Scaled Error of 1.322 means it is significantly worse than the naive baseline. **TimesFM is unusable for Vigil and will not be discussed further.**

---

### Finding 2 — Cisco Time Series Model has a decisive advantage on Border Gateway Protocol flap detection

| Model | Border Gateway Protocol Mean Absolute Scaled Error | Border Gateway Protocol symmetric Mean Absolute Percentage Error |
|-------|:---:|:---:|
| **Cisco Time Series Model 1.0** | **0.80** | **2.82%** |
| Chronos-T5-Small | 0.83 | 2.92% |
| TimesFM-2.5-200M | 1.14 | 4.63% |

Border Gateway Protocol route count is a step-function signal — it holds steady at a stable level, then jumps abruptly when a session flaps. Cisco Time Series Model's Mean Absolute Scaled Error of 0.80 means it beats the naive baseline by 20% — the strongest result in the benchmark.

This matters because Border Gateway Protocol flaps are one of the leading causes of network-wide outages. Vigil's pre-triage classifier needs to catch the run-up to a Border Gateway Protocol flap before the session fully drops. **Cisco Time Series Model is the right model for this use case.**

---

### Finding 3 — Cisco Time Series Model has a meaningful weakness on packet drop

| Model | Packet Drop Mean Absolute Scaled Error | Packet Drop symmetric Mean Absolute Percentage Error |
|-------|:---:|:---:|
| Chronos-T5-Small | **1.27** | **65.55%** |
| **Cisco Time Series Model 1.0** | 1.27 | 80.86% |
| TimesFM-2.5-200M | 2.04 | 107.96% |

Cisco Time Series Model ties Chronos on Mean Absolute Scaled Error for packet drop (both 1.27), but its symmetric Mean Absolute Percentage Error is 80.86% — 15 percentage points worse than Chronos. Note: per Finding 5, symmetric Mean Absolute Percentage Error is unreliable for packet drop. The real read is on Mean Absolute Scaled Error: **both Cisco Time Series Model and Chronos are worse than the naive baseline on packet drop** (Mean Absolute Scaled Error 1.27 > 1.0).

**Why Cisco Time Series Model struggles with packet drop:** Packet drop is a burst-pattern signal — near-zero baseline punctuated by sudden large spikes. Cisco Time Series Model was trained predominantly on smooth observability metrics (Central Processing Unit, memory, request latency) from Cisco and Splunk's internal infrastructure. Burst-pattern signals are almost certainly underrepresented in that training corpus. The model has not seen enough examples of "flat line, then spike, then flat line" to forecast that pattern well.

This is exactly the move Cisco made to build Cisco Time Series Model from TimesFM in the first place — they added observability-domain data on top of the base model. The packet drop weakness is fixable with the same approach applied to burst-pattern data (see Priority 2 of the roadmap).

---

### Finding 4 — Cisco Time Series Model's lack of uncertainty quantification is its biggest practical limitation

Chronos and TimesFM both return 100 probability samples per forecast. Cisco Time Series Model's public Application Programming Interface returns a single point forecast only. This has direct consequences for Vigil:

- **Vigil's Finite State Machine routes alerts using confidence scores.** A model that says "the next value will be 47.3" with no uncertainty range cannot drive a probabilistic decision. A model that says "the next value has an 80% chance of being between 40 and 55" can.
- **Continuous Ranked Probability Score cannot be measured for Cisco Time Series Model** without sample outputs. We cannot answer "how often is Cisco Time Series Model's confidence right?" — which means we cannot trust it for escalation decisions even if its point accuracy is good.
- **This is an Application Programming Interface limitation, not a model limitation.** The Cisco Time Series Model architecture internally computes quantiles — the Hugging Face Spaces demo simply does not surface them in its response payload. This is fixable with a one-line change on Cisco's side.

This is the single most consequential finding in the benchmark. It is also the easiest to fix.

---

### Finding 5 — Packet drop symmetric Mean Absolute Percentage Error is misleading for all models

All three models show very high symmetric Mean Absolute Percentage Error on packet drop (65–108%). This is a mathematical artifact of the metric, not a model failure. Packet drop rates are typically near zero — when the true value is 0.3% and the model predicts 1.3%, that is a 1 percentage point absolute error but a 330% symmetric Mean Absolute Percentage Error.

**For packet drop, Mean Absolute Scaled Error is the reliable accuracy signal. Ignore symmetric Mean Absolute Percentage Error.**

---

## Where Each Model Fits in Vigil Today

Until Cisco Time Series Model exposes quantile outputs, Vigil's safest production strategy is **a hybrid**: Cisco Time Series Model where it dominates (Border Gateway Protocol), Chronos where confidence calibration matters (everything else).

| Vigil Use Case | Recommended Model | Reason |
|---|:---:|---|
| Border Gateway Protocol flap pre-triage classification | **Cisco Time Series Model** | Lowest Mean Absolute Scaled Error on Border Gateway Protocol (0.80) — most accurate on the most critical signal |
| Suppress vs. escalate confidence scoring | **Chronos** | Only model with calibrated probability distributions today (Continuous Ranked Probability Score measurable) |
| Central Processing Unit spike detection | **Chronos** | Comparable accuracy to Cisco Time Series Model, best symmetric Mean Absolute Percentage Error, and provides uncertainty estimates |
| Packet drop anomaly detection | **Chronos** | Tied with Cisco Time Series Model on Mean Absolute Scaled Error, but provides confidence intervals |
| General fallback for any new signal type | **Chronos** | Until Cisco Time Series Model exposes quantile outputs, Chronos is safer for any decision that uses confidence |

---

## Prioritized Roadmap

The benchmark identified two clear, actionable gaps: Cisco Time Series Model needs better burst-pattern signal handling, and Vigil needs Cisco Time Series Model's uncertainty outputs. The four items below are ordered by **priority**, where priority is a function of impact divided by effort. Do them in this order.

---

### Priority 0 — Ask Cisco to expose quantile outputs via Application Programming Interface

| Field | Value |
|---|---|
| **Effort** | 1 hour |
| **Timeline** | Dependent on Cisco's response time |
| **Cost** | Zero engineering investment |
| **Owner** | Product Management → Cisco Time Series Model team |
| **Dependency** | None |

**What:** Send a written request to the Cisco Time Series Model team asking for one of two things: (a) expose quantile outputs via the Hugging Face Spaces Application Programming Interface response payload, or (b) provide raw model weights for local inference where we can extract quantiles ourselves.

**Why this is Priority 0:** The Cisco Time Series Model architecture already computes quantiles internally — the Spaces demo just does not surface them. A small change on Cisco's side unlocks Continuous Ranked Probability Score measurement for Vigil and makes Cisco Time Series Model usable for Vigil's confidence-based decision logic. **This is the single highest-leverage move available to us.** Until this lands, Cisco Time Series Model is restricted to point-prediction use cases only.

**What to include in the request:**
- The packet drop and Border Gateway Protocol benchmark results from `splunk_evals.ipynb` — concrete, reproducible failure cases
- The specific use case: confidence-based suppress / remediate / escalate routing for live network incidents
- The proposed payload change: include `quantiles` array alongside the existing `forecast` field

**Success criterion:** Cisco Time Series Model Application Programming Interface returns quantile outputs. Re-run the benchmark with Continuous Ranked Probability Score enabled and compare against Chronos. If Cisco Time Series Model's Continuous Ranked Probability Score is competitive with Chronos, Vigil can move fully to Cisco Time Series Model.

---

### Priority 1 — Test Cisco Time Series Model with multiresolution input on real Splunk telemetry

| Field | Value |
|---|---|
| **Effort** | 1–2 days |
| **Timeline** | This sprint |
| **Cost** | Zero (Application Programming Interface calls only) |
| **Owner** | Vigil engineering |
| **Dependency** | Splunk read access (already in place) |

**What:** Cisco Time Series Model's core architectural advantage over TimesFM is **multiresolution input** — it accepts both coarse-grained (hourly) and fine-grained (per-minute) context simultaneously. The benchmark only fed fine-resolution data because the synthetic series were not structured with both resolutions. Real Splunk telemetry contains both natively.

**Why this is Priority 1:** Border Gateway Protocol flaps have weekly periodicity that only appears in hourly data. Packet drop bursts appear in per-minute data. Feeding both resolutions gives Cisco Time Series Model context that neither Chronos nor TimesFM receives — this is the feature Cisco specifically designed Cisco Time Series Model around. **It is plausible that multiresolution input alone closes the packet drop accuracy gap with zero training investment.** That makes it the second-highest-leverage move after Priority 0.

**How to test:**
1. Pull a sample of real telemetry from Splunk: one week of hourly data and one week of per-minute data for the same device, covering Border Gateway Protocol route count, Central Processing Unit utilisation, and packet drop rate.
2. Feed coarse and fine resolution pairs to Cisco Time Series Model.
3. Compare Mean Absolute Scaled Error against the synthetic-series benchmark results.

**Success criterion (clear pass/fail):**
- Packet drop Mean Absolute Scaled Error drops below 1.0 (beats naive baseline)
- Border Gateway Protocol Mean Absolute Scaled Error drops below 0.75

If either threshold is hit, Priority 0 + Priority 1 are sufficient for the next two quarters and we defer fine-tuning. If neither is hit, scope Priority 2 immediately.

---

### Priority 2 — Continued pre-training on burst-pattern synthetic data

| Field | Value |
|---|---|
| **Effort** | 2–3 weeks |
| **Timeline** | Next quarter |
| **Cost** | Graphics Processing Unit compute budget + engineering time |
| **Owner** | Vigil engineering + machine learning support |
| **Dependency** | Priority 1 results inform whether this is needed at all |

**What:** Generate or collect time series that look like packet drop — exponential baseline with burst windows, identical in structure to the `make_packet_drop` generator in the notebook. Run a continued pre-training pass on Cisco Time Series Model using the same multiresolution input format the model expects (coarse and fine resolution pairs).

**Why this is Priority 2:** This is exactly the move Cisco made to build Cisco Time Series Model from TimesFM in the first place — they added observability-domain data on top of the base model. The training data gap for burst-pattern signals is clear from the benchmark and well-understood. Even 50,000–100,000 synthetic burst-pattern series is likely enough to move the needle on packet drop without hurting Border Gateway Protocol or Central Processing Unit performance, since those signal types are already well-represented in the existing checkpoint.

**Why this is Priority 2 and not Priority 1:** It costs engineering time and Graphics Processing Unit compute. Priority 1 may make this unnecessary by simply feeding Cisco Time Series Model the right input format.

**What to prepare:**
- Generate 100,000 burst-pattern series using the `make_packet_drop` function as a starting point, varying burst frequency, duration, and amplitude
- Format as multiresolution pairs (downsample the fine series to create the coarse version)
- Run continued pre-training starting from Cisco Time Series Model's existing checkpoint

**Success criterion:** Packet drop Mean Absolute Scaled Error drops below 1.0 — beating the naive baseline, which the model currently fails to do.

---

### Priority 3 — Supervised fine-tuning on labeled Splunk incident data

| Field | Value |
|---|---|
| **Effort** | 4–6 weeks |
| **Timeline** | Next half |
| **Cost** | Live Splunk access, labeled incident windows, Graphics Processing Unit compute |
| **Owner** | Vigil engineering + Splunk customer data team |
| **Dependency** | Priorities 0–2 deliver most of the accuracy gain at lower cost |

**What:** Pull historical telemetry from Splunk with known incident timestamps — a packet drop event that caused a Priority 2 incident, a Border Gateway Protocol flap that triggered a page. Fine-tune Cisco Time Series Model specifically on those windows so the model learns to forecast the run-up to incidents more accurately than it would from random telemetry.

**Why this is Priority 3:** Supervised fine-tuning on real incident data produces a model specifically calibrated for the types of anomalies Vigil investigates — not just general burst patterns, but the exact signatures that precede real outages in a given customer's infrastructure. **Over time this becomes a proprietary advantage.**

**Why this is Priority 3 and not Priority 0:** It requires access to real Splunk customer data (not synthetic), labeled incident windows (not just raw telemetry), and a longer iteration cycle. Priorities 0–2 are faster, lower-risk, and likely to produce most of the achievable accuracy gain — fine-tuning is the move that takes Vigil from "good" to "domain-specific best."

**Success criterion:** Packet drop Mean Absolute Scaled Error below 0.90 and Border Gateway Protocol Mean Absolute Scaled Error below 0.75 on a held-out set of real incidents.

---

## Recommended Sequencing

```
THIS WEEK         Priority 0: File Cisco Application Programming Interface request — 1 hour
                  Priority 1: Begin multiresolution input test on real Splunk telemetry — 1–2 days

WEEK 2–3          Evaluate Priority 1 results
                    If packet drop Mean Absolute Scaled Error drops below 1.0:
                       Priorities 0 + 1 are sufficient. Defer Priority 2 and Priority 3.
                    If packet drop Mean Absolute Scaled Error stays above 1.0:
                       Scope Priority 2 immediately. Begin synthetic data generation.

NEXT QUARTER      Priority 2: Continued pre-training on burst-pattern synthetic data
                  Re-run benchmark with Continuous Ranked Probability Score enabled
                    (assuming Priority 0 has shipped on Cisco's side)

NEXT HALF         Priority 3: Supervised fine-tuning on labeled Splunk incident data
                  Integrate domain-fine-tuned Cisco Time Series Model into Vigil pre-triage classifier
```

---

## Why This Benchmark Is the Right Foundation for the Conversation with Cisco

The benchmark in `splunk_evals.ipynb` gives the Cisco Time Series Model team a **concrete, reproducible failure case** to act on. The packet drop result (Mean Absolute Scaled Error 1.27, symmetric Mean Absolute Percentage Error 80.86%) is not vague negative feedback — it is a specific signal type with a clear training data explanation and a testable fix.

That is the kind of input that moves a product team's roadmap. The two specific asks for Cisco — expose quantile outputs via Application Programming Interface, and validate Cisco Time Series Model with multiresolution input on real Splunk data — are low-cost for both sides and directly advance the case for deeper collaboration on Vigil's integration with Cisco Time Series Model.
