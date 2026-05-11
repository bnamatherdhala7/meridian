# Demo Plan — Splunk AI Foundations · Senior Staff PM

**Candidate:** Bharat Namatherdhala
**Role:** Senior Staff Product Manager — Splunk AI Foundations
**Project shown:** Vigil — Agentic Incident Commander for Network Operations
**Demo budget:** 15 minutes demo + 15 minutes Q&A

---

## Why This Project Fits This Role

Read the JD again — every major responsibility maps to a shipped artifact in Vigil:

| JD Responsibility | Vigil Artifact |
|---|---|
| *"Domain-specific foundation models (such as the **Cisco Time Series Model**)"* | `splunk_evals.ipynb` — 60-series benchmark of CTSM vs Chronos vs TimesFM. `docs/model-evaluation.md` — five findings + prioritized 4-step productization roadmap. |
| *"Build agentic workflow frameworks"* | Phase 2 — 7-state Finite State Machine with auditable transitions, per-state tool allowlists, threshold-based routing. |
| *"Standardize AI skills using protocols like **MCP**"* | Phase 1 — bridges Splunk MCP server + Cisco Catalyst MCP server in one investigation loop. Two new Catalyst tools (`get_network_topology`, `get_telemetry_metrics`) fill a real gap. |
| *"Responsible AI & Governance"* | `docs/prd.md` — Splunk AI Governance Alignment table mapping all five Splunk principles to architecture. Pydantic JSON audit trail per investigation. |
| *"Addressing financial goals (e.g., **cloud margin**)"* | Cost-reduction stack: schema enforcement (57% off) + prompt caching (Lever 1) + Haiku tiering (Lever 2) = 80–85% off unconstrained baseline. $423K → ~$620K annual saving at 10K alerts/day. |
| *"GTM & Ecosystem"* | `docs/competitive-landscape.md` — 5-tier market map, 25+ vendors, three defensible advantages, ecosystem partnership posture vs. Cisco roadmap. |
| *"Customer Advocacy / unarticulated needs"* | Top-5 Customer Problems framed entirely in **Splunk's own published 2025-2026 research** — 55% false positives, 81% manual investigation pain, etc. |

**The one-line story to open with:**
> *"Cisco and Splunk both shipped MCP servers. Neither shipped the reasoning layer that connects them. I built that reasoning layer — and the foundation-model evaluation that grounds it — as a working prototype. Every responsibility in this role is something I've already built, measured, and shipped against."*

---

## Demo Flow — 15 Minutes, 9 Beats

| # | Beat | Time | What to Show | JD Hook |
|:-:|---|:-:|---|---|
| 1 | Opening pitch | 1 min | One-Line Story slide / spoken | Sets up the whole demo |
| 2 | Customer problems in Splunk's own words | 1 min | PRD Section "Five Customer Problems" | Customer Advocacy |
| 3 | Domain-specific model evaluation | 3 min | `splunk_evals.ipynb` results table + `docs/model-evaluation.md` priorities | **Develop Specialized Models** |
| 4 | Agentic workflow framework | 2 min | Run the Packet Loss scenario in the UI · Full Trace overlay | **Enable Agentic Workflows** |
| 5 | MCP standardization | 1 min | Phase 1 architecture diagram + the two new Catalyst tools | **Build Connectivity** |
| 6 | Proactive forecasting layer | 2 min | Forecast Strip across 4 scenarios — especially False Positive (all-green) | **Drive AI Platform Strategy** + **Specialized Models** |
| 7 | Cloud margin (cost discipline) | 2 min | PRD cost table + Levers 1+2 breakdown | **Financial Goals (cloud margin)** |
| 8 | Responsible AI alignment | 1 min | PRD Splunk AI Governance Alignment table | **Responsible AI & Governance** |
| 9 | Where it sits in the market | 1 min | `competitive-landscape.md` market map quadrant + 5-tier summary | **GTM & Ecosystem** |
| — | Close + pivot to Q&A | 1 min | The Bottom Line table from PRD | — |

---

## Beat-by-Beat Talk Track

### Beat 1 — Opening (1 min)

**Show:** PRD page 1 (One-Line Story) or just the running UI.

**Say:**
> "Splunk's 2026 prediction says traditional reactive operations are no longer enough — agentic AI is the path. Cisco's AgenticOps vision says the same thing. Neither has shipped the application layer that fulfills that vision. I built a prototype of it. **Vigil is an agentic incident commander that bridges Splunk MCP and Cisco Catalyst MCP in one investigation loop, grounded by domain-specific foundation models — Cisco's Time Series Model for forecasting, Anthropic Claude for reasoning, OpenAI embeddings for retrieval. It's mock data and a single-engineer prototype, but every responsibility in your job description maps to something I built and measured here."**

**Key:** Acknowledge mock status proactively. You're showing PM thinking, not selling a startup.

---

### Beat 2 — Customer Problems (1 min)

**Show:** PRD section *"The Five Customer Problems — In Splunk's Own Words"*

**Say:**
> "Before I built anything, I went to Splunk's own research. The 5 problems Vigil targets aren't a guess — every one is anchored in Splunk's published 2025-2026 material: 55% of orgs have too many false positives (State of Security 2025), 81% of SOC pros name manual investigation as the #1 contributor to slow response (Dimitri McKay), 73% of observability teams report outages caused by ignored alerts (Patrick Lin)."

> "The signal that mattered most was **Hao Yang's 2026 prediction** that MTTR becomes 'a snapshot of how late we were in the process' — outcome-based KPIs like false positive reduction, autonomous triage precision, and risk avoided are the real measures. That's why Vigil's results table leads with suppression rate and precision, not Mean Time to Resolve."

**Key insight to land:** This is a Senior Staff PM signal — *I read the org's own research and built against its language, not generic industry stats.*

---

### Beat 3 — Domain-Specific Model Evaluation (3 min) ⭐ HIGHEST-LEVERAGE BEAT

**This is the beat where you most directly demonstrate the JD's "Develop Specialized Models" responsibility.**

**Show:**
1. Open `splunk_evals.ipynb` — scroll to the Three-Model Benchmark Results table.
2. Then open `docs/model-evaluation.md` — show the Plain-English Verdict + Priority table.

**Say:**
> "The Cisco Time Series Model is in your job description. I ran a 60-series benchmark — Border Gateway Protocol route count, Central Processing Unit utilization, packet drop rate — comparing CTSM, Amazon's Chronos, and Google's TimesFM on Mean Absolute Scaled Error and symmetric Mean Absolute Percentage Error."

> "Three findings: (1) **CTSM is the most accurate model overall, but the win shows up where it matters — Border Gateway Protocol flap detection, MASE 0.80 versus Chronos 0.83 versus TimesFM 1.14.** TimesFM is worse than a naive baseline for BGP. (2) **CTSM has a meaningful weakness on packet drop** — MASE 1.27, tied with Chronos but worse than naive. That's a training data gap: CTSM was trained on smooth observability metrics; burst-pattern signals like packet drop are underrepresented. (3) **CTSM's public API today returns point forecasts only — no quantile outputs.** That blocks Continuous Ranked Probability Score measurement and blocks confidence-based routing."

> "So I wrote a **product roadmap** for the CTSM team — four prioritized items: P0 ask Cisco to expose quantile outputs via API (one hour of work on their side, unblocks confidence-based decisions everywhere); P1 test CTSM with proper multiresolution input on real Splunk data (one to two days, may close the packet drop gap with zero training); P2 continued pre-training on burst-pattern synthetic data (next quarter); P3 supervised fine-tuning on labeled Splunk incident windows (next half — the proprietary moat over time)."

**Key:** Show that you don't just consume models — you evaluate them rigorously, identify gaps, and write a product plan that an internal model team could act on. **This is exactly what the JD asks for.**

**Anticipated follow-up:** "How would you measure success for these priorities?" Have the success criteria ready — they're in the doc: packet drop MASE < 1.0 (beats naive), BGP MASE < 0.75, CRPS competitive with Chronos.

---

### Beat 4 — Agentic Workflow Framework (2 min)

**Show:** Run the **Packet Loss scenario** live in the UI. While it runs, open the Full Trace overlay.

**Say:**
> "When the alert fires, the system makes five sequential decisions, all auditable. **Pre-Triage rules-based — zero tokens, sub-millisecond — decides this alert is real**. State transitions are threshold-based, not black-box LLM judgment: every transition cites the rule that fired. **TRIAGE retrieves the right SPL pattern from Pinecone, runs the topology lookup. INVESTIGATING pulls telemetry and queries logs. INVESTIGATING retrieves a past incident match at 0.84 similarity — INC-2024-0891, exfiltration, ESCALATED. HYPOTHESIZING confirms a single source IP at 71% of egress — threshold rule fires — ESCALATING.**"

> "Open the Full Trace overlay — every event timestamped from T+0, every input and output captured, every state transition with its reason inline. Copy JSON or download as a file. **This is the audit trail Splunk's 2026 governance prediction calls 'mandatory' — shipped, not roadmapped.**"

**Key:** Hover on the state transitions to show the reasoning in line. Then click the Full Trace button — this is your "log everything" answer.

---

### Beat 5 — MCP Standardization (1 min)

**Show:** Phase 1 section of the PRD with the two Catalyst tool tables.

**Say:**
> "The MCP servers exist — Splunk shipped 14 tools in v1.1, generally available. Cisco Catalyst ships its own. **Nobody bridges them.** Vigil consumes Splunk's existing four most useful tools and adds two new Cisco Catalyst tools that exist in neither vendor's published server: `get_network_topology` and `get_telemetry_metrics`. Stateless, RBAC passthrough — the agent inherits the Splunk user's permissions, no privilege escalation."

> "This is the kind of standardization the JD asks for — universal connectors for AI workflows. Same shape, both vendors, one investigation loop."

**Key:** Don't over-explain MCP — assume your interviewer knows. Land the *new tools fill a gap* point quickly.

---

### Beat 6 — Proactive Forecasting Layer (2 min)

**Show:** The Forecast Strip at the top of the UI. Click through all four scenarios.

**Say:**
> "This is where domain-specific foundation models and agentic workflows compose. **Cisco Time Series Model runs continuously on Splunk telemetry — Border Gateway Protocol routes, CPU, packet drop — forecasting 24 steps ahead, about two hours.** Chronos runs in parallel and provides the P10 / P50 / P90 probability distribution — that's what drives the FSM's confidence routing."

> "Three trigger types: threshold (P50 forecast breaches a hard limit — orange pulse), trajectory (slow drift — amber), uncertainty (P90 is dangerous even when P50 looks fine — violet). For the BGP Flap scenario, **the trigger fires 18 minutes before the alert system would**. For the False Positive scenario, **all three sparklines stay green — the foundation model confirms the alert is noise before the FSM even runs.**"

> "This gives Vigil three knowledge sources, one per time orientation — **past** (Pinecone incident memory), **present** (pre-triage rules + Splunk telemetry), **future** (CTSM + Chronos forecast). No current competitor has all three. This is the architecture Splunk's leadership has been calling for — Kamal Hathi: *'agentic AI lets organizations get ahead of incidents, contain issues before they spread.'*"

**Key:** This is the *most direct* demonstration of the JD's "domain-specific foundation models" plus "agentic workflows" responsibilities composed into one system. The False Positive frame (all-green strip) is the killer image.

**Caveat to surface proactively:** *"The forecast data here is pre-computed fixtures matched to each scenario's signature — the architecture is real and shippable; live model inference is roughly a week of work and is gated on Cisco exposing quantile outputs, which is Priority 0 in my model-evaluation roadmap."*

---

### Beat 7 — Cloud Margin (2 min)

**Show:** PRD Phase 3 Evaluator table + the "Two further cost levers" table immediately below.

**Say:**
> "The JD calls out cloud margin explicitly. Here's the stack I shipped."

> "Baseline: unconstrained generic LLM, $0.056 per investigation. **Lever 0 — schema enforcement** on the same base model takes it to $0.024, with precision rising from 0.55 to 0.91 — that's matching Cisco's claimed Deep Network Model target, today, using prompt engineering alone."

> "**Lever 1 — prompt caching with Anthropic's `cache_control` markers.** System prompt and tools are static within an FSM state's multi-turn loop. First call writes the cache at 1.25x cost, subsequent calls read it at 10% — that's a 90% discount on cached tokens."

> "**Lever 2 — model tiering.** Haiku 4.5 — $1 / $5 per million tokens — for the routing states: TRIAGE, INVESTIGATING, REMEDIATING. Sonnet 4.6 — $3 / $15 — reserved for HYPOTHESIZING where the actual root-cause decision happens. Haiku is roughly 3x cheaper, the final decision still runs on Sonnet so the 0.91 precision is preserved."

> "**Net effective cost: $0.010 to $0.014 per investigation — 80 to 85% lower than the unconstrained baseline.** At 10,000 alerts per day, annual saving rises from $423K to roughly $620K. That maps directly to cloud margin."

**Key:** This is the financial-discipline signal. Senior Staff PM cares about unit economics. Have the per-token math ready if pressed.

---

### Beat 8 — Responsible AI (1 min)

**Show:** PRD Splunk AI Governance Alignment table.

**Say:**
> "Splunk publishes five AI governance principles. Vigil implements all five as core architecture, not a compliance afterthought."

> "**Accountability** — Pydantic JSON report per investigation: FSM transitions, tool calls, RAG retrievals, forecast snapshot, confidence, evidence. **Transparency** — every transition cites the rule that fired, not black-box LLM judgment. **Privacy** — RBAC passthrough; no raw logs leave the customer's data plane beyond Pinecone summaries. **Fairness** — rules-based pre-triage + configurable thresholds prevent model drift across incident classes. **Resilience** — default-to-escalation; the system never guesses on live infrastructure."

**Key:** Land "core architecture not bolted on" and move on. This is a signal of seriousness, not a long discussion.

---

### Beat 9 — Competitive Position (1 min)

**Show:** `docs/competitive-landscape.md` market map quadrant.

**Say:**
> "I went deep on competitive positioning — 25 vendors across five tiers. Two axes: scope (network-specialist vs. general observability) and autonomy (reactive vs. agentic). **Vigil sits alone in the upper-left.** Cisco AgenticOps is closest but not shipped. AWS DevOps Agent + Splunk shipped in April 2025 — applications-layer, not network. Splunk's IT Service Intelligence has forecasting but statistical models only, not foundation models. Datadog Bits AI and Dynatrace Davis are agentic but observability-broad, not network-specialist."

> "**Three defensible advantages:** Cisco + Splunk in one loop — owned by the same parent post-acquisition but no shipped product bridges them. Foundation-model forecasting + agentic investigation in one system — forecasting specialists don't investigate, agentic competitors don't forecast. **Built to absorb Cisco's roadmap, not race it** — when AI Canvas ships, the FSM maps to a Canvas workflow; when Deep Network Model ships, the LLM call swaps out. Partnership posture, not competition."

**Key:** This shows ecosystem thinking and the GTM mindset. The "built to absorb Cisco's roadmap" line is your strongest *Senior Staff PM* signal — it shows you think about the platform's commercial trajectory, not just its features.

---

### Closing (1 min)

**Show:** PRD "The Bottom Line" table.

**Say:**
> "Cisco's AgenticOps timeline is 2025-2026. Every meaningful capability in that vision is buildable today, on Splunk's and Cisco's own released tooling, with measurable results. I built it as a single-engineer prototype to demonstrate the architecture. **The question I'm interested in answering with you is — who owns the incident commander layer when AI Canvas ships, and how do we make it Cisco's?**"

**Key:** End on a question that invites discussion. You're framing yourself as the person who's already thought about *where this lives in the org*.

---

## Q&A — Likely Questions, Prepared Answers

### Technical Depth Questions

**Q: "Why CTSM and not just fine-tune a GPT or Claude model on time series?"**
> "Two reasons. First, transformer architecture works for time series only when you tokenize the values appropriately — Chronos does this by scaling and quantization, CTSM extends TimesFM with multiresolution input. A general LLM fine-tuned on time series numerics underperforms a model architected for the modality. Amazon's Chronos paper makes this case quantitatively. Second, CTSM has 500 million parameters and was pre-trained on 300 billion observability datapoints — that scale is out of reach for fine-tuning a general LLM on a customer's data. The right answer is: use CTSM as the base, fine-tune it on the customer's labeled incident corpus — that's Priority 3 in my roadmap doc."

**Q: "How do you decide when to use Haiku vs Sonnet vs Opus?"**
> "Tier by decision criticality, not by state. Routing states (TRIAGE, INVESTIGATING) orchestrate tool calls — light cognition, Haiku handles it. HYPOTHESIZING is the actual root-cause decision — that's where Sonnet earns its 3x premium. Opus only if the customer's incident workload requires reasoning beyond what Sonnet handles, which the benchmark hasn't shown yet. The discipline is *measure precision per tier* — if Haiku drops precision below the threshold for routing states, switch back. The 0.91 precision number is the gate."

**Q: "Why a Finite State Machine instead of LangGraph or CrewAI?"**
> "Auditability. The FSM transitions are deterministic threshold rules — every SUPPRESSED, REMEDIATING, or ESCALATING decision cites the rule that fired. Agent frameworks like LangGraph give you the workflow primitive but the LLM controls the transitions; for live network infrastructure, that's the wrong default. The FSM enforces the senior engineer's investigation methodology consistently. When AI Canvas ships, the FSM maps to a Canvas workflow — same primitive, Cisco-native runtime."

**Q: "How would you measure success for the AI Foundations platform?"**
> "Three primary KPIs, all customer-facing. **Adoption depth** — number of customer agents in production, number of investigations per customer per day, percentage of customer alerts touched by the platform. **Outcome quality** — false positive suppression rate, autonomous triage precision, percentage of investigations with full audit trail, cost per correct decision. **Ecosystem velocity** — number of skills in the Skills Registry, number of partner-built agents, time from skill submission to ecosystem availability. Splunk's 2026 prediction explicitly names MTTR as a *downstream* metric — outcome-based measures lead."

### Product Strategy Questions

**Q: "How do you balance internal use cases versus shipping to external customers?"**
> "The platform should be dogfooded internally before external GA. Concretely: Vigil's incident commander pattern should ship as the first internal customer of the AI Foundations platform — security and observability portfolios use it, surface bugs, harden the SDKs. Six months later, the same primitives ship as a developer SDK with case studies from internal usage. This is how Anthropic, OpenAI, and AWS shipped their agent frameworks — internal customer first, external GA second."

**Q: "What's the biggest risk to this strategy?"**
> "Cisco's Deep Network Model timeline slipping past 2026. The platform's positioning assumes Cisco ships foundation models that we can productize. If that slips, we either (a) wait, losing time-to-market, (b) partner with Anthropic / Google more deeply to fill the gap, or (c) invest in our own model training, which is out of scope for an application company at our scale. Mitigation: structure the platform so the model layer is swappable — that's what Vigil's 3p model abstraction already does. The orchestration and audit trail layers don't depend on which foundation model is underneath."

**Q: "How do you engage with early design partners?"**
> "Three-tier engagement. Tier 1 design partners get pre-release SDK access plus weekly PM-led product sessions and direct Slack to engineering. They commit to ship one production agent built on the platform within 90 days. Tier 2 partners get monthly office hours and early access to docs. Tier 3 is the public developer community — GitHub issues, monthly office hours, public roadmap. The signal that matters: how many Tier 1 partners renew for a second 90-day commitment. Renewal rate is the only honest measure of whether the platform creates value for them."

### Behavioral / Closing Questions

**Q: "Tell me about a hard product decision you made on this project."**
> "Whether to make pre-triage rules-based or use a small ML classifier. The rules-based approach scores 35-40% of alerts at zero tokens, sub-millisecond, every decision auditable. A small classifier might marginally improve recall on edge cases, at the cost of latency, opacity, and adding a model training pipeline. I chose rules. The argument that locked it: pre-triage is *logical filtering, not pattern recognition* — the patterns are already articulable by the team, so a model is the wrong tool. **Putting a foundation model where rules are correct is the kind of cargo-cult AI thinking the Splunk Foundations platform should actively discourage in its developer SDK.**"

**Q: "What would you do in the first 90 days in this role?"**
> "Three deliverables. Week 1-4: read the customer evidence — every Splunk State of Security / Observability report, every recorded customer call from the prior quarter — and write a one-pager on the top 5 jobs-to-be-done for the platform. Validate that with five customers. Week 5-8: audit the existing AI Foundations roadmap, identify the three highest-leverage cuts and the three biggest missing investments. Week 9-12: ship one visible win — a published evaluation benchmark, a developer-facing SDK improvement, or a customer-validated use case study. Senior Staff PMs earn credibility through shipped artifacts in the first quarter, not strategy documents."

---

## What NOT to Do in the Demo

- **Don't oversell the prototype as production.** It's mock data. Acknowledge it once at the start. You're showing PM thinking and execution rigor, not a startup.
- **Don't read the slides.** Talk through them. The interviewer can read.
- **Don't get into Python implementation details** unless they ask. The depth signal is architectural and strategic.
- **Don't claim to have done parts that are roadmap.** "I built a forecasting layer with mock data; the live wiring is documented in my model-evaluation roadmap" is the honest framing.
- **Don't bash competitors.** "Splunk IT Service Intelligence does forecasting with statistical models, not foundation models" — *factual difference*, not criticism.

---

## What TO Land in the Demo

| Signal You're Sending | How to Land It |
|---|---|
| *I read Splunk's published research before building* | Cite specific Splunk authors (Hao Yang, Kamal Hathi, Patrick Lin, Dimitri McKay) by name |
| *I can productize foundation models, not just consume them* | Walk through the CTSM benchmark + the 4-priority roadmap |
| *I think in audit trails and governance, not just features* | Show the Full Trace overlay; show the AI Governance Alignment table |
| *I think about unit economics* | Walk through the three cost levers — schema, caching, tiering |
| *I think about ecosystem and partnership posture* | "Built to absorb Cisco's roadmap, not race it" |
| *I have strong opinions defensible by reasoning* | Pre-triage = rules, not ML — *deliberately chosen* |

---

## Pre-Demo Checklist

- [ ] UI running cleanly on `http://localhost:5174` (or wherever)
- [ ] All four scenarios runnable; recent run already in History so the Full Trace overlay has data even before live runs
- [ ] PRD open in a second tab at the *Five Customer Problems* section
- [ ] `docs/model-evaluation.md` open in a third tab
- [ ] `docs/competitive-landscape.md` open in a fourth tab
- [ ] `splunk_evals.ipynb` open in a fifth tab
- [ ] Phone on Do Not Disturb
- [ ] Glass of water nearby — 30 minutes is a long demo

---

## The Final Frame

Senior Staff PM at the AI Foundations level isn't about *can you build this* — it's about *can you build the platform that lets other PMs and engineers build things like this 10x faster.* The closing line to land:

> *"What I shipped here is one application of an AI Foundations platform. The role you're hiring for is to build the platform so the next 50 of these get built by other people. That's what I want to do."*
