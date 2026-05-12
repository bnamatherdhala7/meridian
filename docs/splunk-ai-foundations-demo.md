# Demo Plan — Splunk AI Foundations · Senior Staff PM

**Candidate:** Bharat Namatherdhala
**Role:** Senior Staff Product Manager — Splunk AI Foundations
**Project shown:** Vigil — Agentic Incident Commander for Network Operations
**Demo budget:** 15 minutes demo + 15 minutes Q&A

---

## Why This Project Fits This Role

Every major JD responsibility maps to a shipped Vigil artifact:

| JD Responsibility | Vigil Artifact |
|---|---|
| *"Domain-specific foundation models (such as the **Cisco Time Series Model**)"* | `splunk_evals.ipynb` — 60-series benchmark of CTSM vs Chronos vs TimesFM. Five findings + 4-priority engineering roadmap in the same notebook. |
| *"Build agentic workflow frameworks"* | Phase 2 — 7-state Finite State Machine with auditable transitions, per-state tool allowlists, threshold-based routing. |
| *"Standardize AI skills using protocols like **MCP**"* | Phase 1 — bridges Splunk MCP server + Cisco Catalyst MCP server in one investigation loop. Two new Catalyst tools (`get_network_topology`, `get_telemetry_metrics`) fill a real gap. |
| *"Responsible AI & Governance"* | Splunk AI Governance Alignment table mapping all five Splunk principles to architecture. Pydantic JSON audit trail per investigation. |
| *"Addressing financial goals (e.g., **cloud margin**)"* | Three cost levers — schema enforcement + prompt caching + Haiku tiering = **80–85% off unconstrained baseline. ~$620K/year saved at 10K alerts/day.** |
| *"GTM & Ecosystem"* | `docs/competitive-landscape.md` — 5-tier market map, 25+ vendors, three defensible advantages, partnership posture vs Cisco roadmap. |
| *"Customer Advocacy"* | Four Customer Problems framed entirely in **Splunk's own published 2025–2026 research** — 55% false positives, 81% manual investigation pain, 78% tool sprawl, reactive ops dead per Splunk 2026 predictions. |

---

## Opening Line — The 30-Second Anchor

If you only have 30 seconds, say this:

> *"Cisco and Splunk both shipped Model Context Protocol servers. Neither shipped the reasoning layer that connects them. I built that reasoning layer — and the Cisco Time Series Model evaluation that grounds it — as a working prototype. Every responsibility in this role is something I've already built, measured, and shipped against."*

That sentence does three things at once: (1) names the gap, (2) signals you've done the work, (3) ties to the JD without naming it.

---

## Demo Flow at a Glance — 10 Beats, 15 Minutes

| # | Beat | Time | What to Show | JD Hook |
|:-:|---|:-:|---|---|
| 1 | Opening + One-Line Story | 1 min | PRD: *The One-Line Story* | Sets up everything |
| 2 | The Four Customer Problems | 1 min | PRD: *The Four Customer Problems* | Customer Advocacy |
| 3 | Why Now — Splunk leadership | 30 sec | PRD: *Why Now — Splunk's 2026 Direction* | Industry timing |
| 4 | Model Evaluation (notebook) ⭐ | 3 min | `splunk_evals.ipynb` | **Develop Specialized Models** |
| 5 | Platform Architecture + Live Run | 4 min | PRD: *The Platform — Four Phases* + UI | **Enable Agentic Workflows** + **Build Connectivity** |
| 6 | Cost Discipline | 1.5 min | PRD: *Phase 3 Evaluator* + *Results & Outcomes* | **Financial Goals / Cloud Margin** |
| 7 | Competitive Position | 1 min | PRD: *Competitive Position* | **GTM & Ecosystem** |
| 8 | Vigil as Platform ⭐ | 2 min | PRD: *How Vigil Scales as a Platform* | **Drive AI Platform Strategy** |
| 9 | Cisco AI Canvas integration | 1 min | PRD: *How Vigil Fits Cisco's AI Roadmap* | Partnership story |
| 10 | The Bottom Line — close | 30 sec | PRD: *The Bottom Line* | Strategic close |

---

## Beat-by-Beat Talk Track

### Beat 1 — Opening (1 min)

**JD hook:** Sets up the demo.
**Show:** PRD top section (One-Line Story) on screen.

**Talk track:**

> "Splunk's 2026 predictions explicitly say reactive operations are no longer enough — agentic AI is the path. Cisco's AgenticOps vision at Cisco Live 2025 says the same thing. Neither has shipped the application layer that fulfills that vision. I built a prototype of it."

> "**Vigil is an agentic incident commander that bridges Splunk MCP and Cisco Catalyst MCP in one investigation loop, grounded by domain-specific foundation models — Cisco Time Series Model for forecasting, a swappable foundation-model agent for reasoning (Claude today, Cisco Deep Network Model at GA), OpenAI embeddings for retrieval.**"

> "Up-front honest framing: this is mock data and a single-engineer prototype. But every responsibility in the AI Foundations job description maps to something I've built and measured here. I'll walk you through it in 15 minutes."

**Key signal:** You're showing PM thinking and execution rigor, not selling a startup. The "mock data, single-engineer prototype" acknowledgment up-front earns credibility for everything that follows.

**Pivot to next:** *"Before I built anything, I went to Splunk's own research..."*

---

### Beat 2 — The Four Customer Problems (1 min)

**JD hook:** Customer Advocacy.
**Show:** PRD section *"The Four Customer Problems — In Splunk's Own Words."*

**Talk track:**

> "These aren't generic industry pains. Every single problem statement is anchored in Splunk's own 2025–2026 published material."

> "**Problem 1 — false positive fatigue:** 55% of orgs deal with too many false positives, 32% of an analyst's day spent on false alarms, 94% of CISOs name false alerts as a top burnout driver. Vigil's answer is Phase 2.5 pre-triage — 35–40% of alerts suppressed at zero tokens before any model call."

> "**Problem 2 — manual fragmented investigation:** 81% of SOC pros name disconnected tools as the number-one slowdown. $58K average cost per incident. Vigil bridges Splunk and Cisco Catalyst in one loop — 47 minutes to 35 seconds."

> "**Problem 3 — tool sprawl:** 78% say tools are disconnected. Vigil's answer is structural — Vigil is a reasoning layer, not another platform. Same RBAC, same data, no new data plane."

> "**Problem 4 — reactive operations are no longer enough:** This is a direct quote from Splunk's 2026 predictions. Vigil's Phase 4 forecasting layer — Cisco Time Series Model plus Chronos — fires triggers up to 10 hours before the alert system would."

**Key signal:** *"I read Splunk's own research and built against its published language, not generic industry stats."* This is the Senior Staff PM tell — depth of upfront research, not vibes.

**Pivot to next:** *"Splunk's leadership backed all of this up explicitly in 2026..."*

---

### Beat 3 — Why Now (30 sec)

**JD hook:** Industry timing.
**Show:** PRD section *"Why Now — Splunk's 2026 Direction"* — the 6-row table.

**Talk track:**

> "Six rows mapping Splunk's own published predictions to what Vigil already ships. The two that matter most:"

> "**Hao Yang, Splunk Security Predictions 2026** — and I'll read this exactly: *'MTTR becomes less a measure of performance and more a snapshot of how late we were in the process. SOC directors will look toward outcome-based measures — reduction in false positives, precision of autonomous triage, risk avoided rather than risk responded to.'* That's why Vigil's results table leads with suppression rate and precision, not MTTR."

> "**Cisco Time Series Model launched November 24, 2025** — open weights, 300 billion datapoints, designed for observability and agentic workflows. Vigil benchmarked it against Chronos and TimesFM the week it dropped. **CTSM v1.0 is due early 2026. The partnership window is open now.**"

**Key signal:** *Vigil is precisely aligned with what Splunk is publicly saying — not ahead of the market, with the market.*

**Pivot to next:** *"Let me show you the benchmark — this is the JD's 'develop specialized models' responsibility, demonstrated."*

---

### Beat 4 — Model Evaluation (notebook) ⭐ HIGHEST-LEVERAGE BEAT (3 min)

**JD hook:** *"Develop Specialized Models: ensuring they outperform general-purpose alternatives through rigorous evaluation."* This is the single most important beat — the Cisco Time Series Model is literally named in the JD.

**Show:** `splunk_evals.ipynb` — scroll to the **VP Executive Summary** at the top, then to the **Key Findings — Five Takeaways** section near the bottom.

**Talk track:**

> "Cisco Time Series Model is in your job description. The week it dropped, I ran a 60-series benchmark — Border Gateway Protocol route count, CPU utilization, packet drop rate — comparing CTSM, Amazon's Chronos-T5-Small, and Google's TimesFM-2.5 on Mean Absolute Scaled Error and symmetric Mean Absolute Percentage Error."

*Scroll to results table.*

> "**Three findings.** First: CTSM is the most accurate model overall — MASE 0.967 versus Chronos 0.971 versus TimesFM 1.322. The win shows up exactly where it matters — Border Gateway Protocol flap detection, MASE 0.80. **TimesFM at 1.14 is worse than a naive baseline — copying yesterday's number forward beats it.**"

> "Second: CTSM has a meaningful weakness on packet drop — MASE 1.27, tied with Chronos but worse than naive on both. That's a training data gap. CTSM was trained on smooth observability metrics; packet drop is a burst-pattern signal. Burst patterns are underrepresented."

> "Third — and this is the most consequential finding: **CTSM's public API returns a single point forecast.** No quantile outputs. That blocks Continuous Ranked Probability Score measurement and blocks confidence-based routing — which is the whole point of Vigil's Finite State Machine."

*Pause.* *Scroll to the Engineering Roadmap section at the bottom.*

> "So I wrote a four-priority product roadmap for the CTSM team. **Priority 0 — ask Cisco to expose quantile outputs via API.** One hour of work on their side. The reason it's one hour: **Splunk's own CTSM launch blog states explicitly that the model 'produces quantile and point predictions'** — the quantiles are already in the architecture, only the API response payload is missing them. Unblocks confidence routing across every Vigil deployment."

> "**Priority 1** — one to two days — test CTSM with proper multiresolution input on real Splunk telemetry. The benchmark only fed fine-resolution data; CTSM was designed for coarse + fine simultaneously. May close the packet drop gap with zero training investment."

> "**Priority 2** — next quarter — continued pre-training on burst-pattern synthetic data. **Priority 3** — next half — supervised fine-tuning on labeled Splunk incident windows. **That's the proprietary moat over time** — every customer's labeled incidents flow back into CTSM, the base model gets domain-specific to their environment."

**Key signal:** You don't just consume foundation models — you evaluate them rigorously, identify gaps, write product plans an internal model team can act on. **This is exactly what the JD asks for.**

**Pivot to next:** *"Let me show you the actual workflow this benchmark grounds..."*

**Anticipated Q:** "How would you measure success on each priority?" *Answer ready in the notebook: packet drop MASE below 1.0 beats naive; BGP MASE below 0.75; CRPS competitive with Chronos.*

---

### Beat 5 — Platform Architecture + Live Run (4 min)

**JD hook:** *"Enable Agentic Workflows"* + *"Build Connectivity via MCP."*
**Show:** PRD section *"The Platform — Four Phases in One Loop"* (the architecture diagram) first (30 sec), then switch to the running UI for the live run.

**Talk track — Part A: Architecture overview (45 sec):**

*Show the 4-phase platform diagram in the PRD.*

> "Four phases, one loop. Alert comes in. **Phase 2.5 Pre-Triage** — rules-based, zero tokens, sub-millisecond — filters 35–40% of alerts before any model call. Surviving alerts go through **Phase 2 Finite State Machine investigation** — TRIAGE, INVESTIGATING, HYPOTHESIZING — grounded by Pinecone Retrieval-Augmented Generation."

> "**Phase 1** is the MCP bridge — Vigil consumes four Splunk MCP tools and adds two new Cisco Catalyst tools that exist in neither vendor's published server. **Phase 3 Evaluator** scores every run. **Phase 4 Proactive Forecasting** runs continuously and fires pre-alerts before the FSM."

> "Now let me run a real scenario in the UI."

**Talk track — Part B: Live run on Packet Loss scenario (2.5 min):**

*Switch to UI tab. Click "Packet Loss" scenario, then "Run Investigation."*

> "Watch the Forecast Strip at the top — packet drop is already orange, T-minus 8 minutes to threshold breach. **The forecast fired the trigger before the alert system would have**. Now the alert arrives."

*Point to Pre-Triage entering the feed.*

> "**Pre-Triage**: alert scored 0.78, three corroborating signals, proceed. Zero tokens, sub-millisecond — that's the rules-based logical filter, deliberately not a model. **TRIAGE** — Pinecone retrieves the `packet_loss_egress` SPL pattern. Topology lookup: this device is on VLAN 100, uplink to sj-core-01."

> "**INVESTIGATING** — telemetry pulled, run_spl confirms 2847 errors per minute starting 14:30. Pinecone Incident Memory hits — INC-2024-0891, 0.84 similarity, prior exfiltration incident, ESCALATED."

> "**HYPOTHESIZING** — generated SPL finds source IP 10.14.22.87 at 71.2% of egress. Threshold rule fires: single source IP above 60% of egress equals potential exfiltration. **ESCALATING**."

*Click "Full Trace" button to open the overlay.*

> "Open the Full Trace overlay — every event timestamped from T+0, every input and output captured, every state transition with the rule that fired inline. Copy JSON or download as a file. **This is the audit trail Splunk's 2026 governance prediction calls 'mandatory' — shipped, not roadmapped.**"

**Talk track — Part C: Phase 4 forecasting cycle (45 sec):**

*Close the overlay. Click through the four scenario tabs.*

> "Cycle through the four scenarios — Packet Loss fires threshold trigger 8 minutes ahead, BGP Flap fires threshold 18 minutes ahead, CPU Spike fires uncertainty trigger because the P90 confidence band widens dangerously, False Positive — and this is the killer frame — **stays all-green. The foundation model confirms the alert is noise before the FSM even runs.**"

> "Three knowledge sources, three time orientations. **Past** — Pinecone incident memory. **Present** — pre-triage rules + Splunk telemetry. **Future** — CTSM and Chronos forecast. **No current competitor has all three.**"

**Caveat to surface proactively:** *"The forecast data is pre-computed fixtures matched to each scenario. The architecture is real and shippable; live model inference is one week of work, gated on Cisco exposing quantile outputs — that's Priority 0 in my model-evaluation roadmap."*

**Key signal:** Live demo, end-to-end, audit-trail visible. Shows three JD responsibilities composed: domain-specific models + agentic workflows + connectivity via MCP.

**Pivot to next:** *"Let me show what this actually costs to run..."*

---

### Beat 6 — Cost Discipline (1.5 min)

**JD hook:** *"Addressing financial goals (e.g., cloud margin)."*
**Show:** PRD *Phase 3 — Evaluator* table (the precision/cost comparison) then jump to the *Results & Outcomes* table for the $620K row.

**Talk track:**

> "The JD calls out cloud margin explicitly. Here's the stack I shipped."

> "**Baseline** — unconstrained generic LLM, $0.056 per investigation. **Lever 0 — schema enforcement** on the same base model takes that to $0.024, with precision rising from 0.55 to 0.91. **That precision number matches Cisco's claimed Deep Network Model target — today, using prompt engineering alone.**"

> "**Lever 1 — prompt caching with Anthropic's `cache_control` markers.** System prompt and tools are static within an FSM state's multi-turn loop. First call writes the cache at 1.25x cost; subsequent calls read at 10% — 90% discount on cached tokens."

> "**Lever 2 — model tiering.** Haiku 4.5 — $1 input, $5 output per million tokens — for the routing states. Sonnet 4.6 — $3 / $15 — reserved for HYPOTHESIZING where the actual root-cause decision happens. Haiku is roughly three times cheaper; the final transition decision still runs on Sonnet so the 0.91 precision floor is preserved."

> "**Net effective cost: $0.010 to $0.014 per investigation — 80 to 85% lower than the unconstrained baseline.** At 10,000 alerts per day, annual saving rises from $423K to approximately $620K versus unconstrained. **That maps directly to cloud margin in the JD.**"

**Key signal:** Unit economics fluency. Senior Staff PM cares about cost per decision, not just whether the system works.

**Pivot to next:** *"So where does Vigil sit in the market?"*

---

### Beat 7 — Competitive Position (1 min)

**JD hook:** *"GTM & Ecosystem"* + *"strategic narratives for partners."*
**Show:** PRD *Competitive Position* — the market map quadrant.

**Talk track:**

> "I went deep on competitive positioning — 25 vendors across five tiers. Full breakdown in `docs/competitive-landscape.md`."

> "Two axes: scope — network-specialist versus general observability — and autonomy — reactive versus agentic. **Vigil sits alone in the upper-left.** Cisco AgenticOps is closest but not shipped. AWS DevOps Agent plus Splunk shipped April 2025 — application-layer, not network. Splunk IT Service Intelligence does forecasting with statistical models, not foundation models. Datadog Bits AI and Dynatrace Davis are agentic but observability-broad, not network-specialist."

> "**Three defensible advantages.** First, Cisco plus Splunk in one investigation loop — owned by the same parent post-acquisition, but no shipped product bridges them. Second, foundation-model forecasting plus agentic investigation in one system — forecasting specialists don't investigate, agentic competitors don't forecast. Vigil is the only product unifying both."

> "Third — and this is the strongest Senior Staff PM signal — **Vigil is built to absorb Cisco's roadmap, not race it.** When AI Canvas ships, the FSM maps to a Canvas workflow. When Deep Network Model ships, the LLM call swaps out. Partnership posture, not competition."

**Key signal:** Ecosystem thinking. You think about commercial trajectory and partnership dynamics, not just features.

**Pivot to next:** *"That brings us to the platform thesis — this isn't just an application..."*

---

### Beat 8 — Vigil as a Platform ⭐ (2 min)

**JD hook:** *"Drive AI Platform Strategy"* + *"shipped as a world-class platform to our global customers and developer ecosystem."*
**Show:** PRD *"How Vigil Scales as a Platform — One Workflow, Customized Per Team"* — start with the identity definition, then the **Orchestrator Pattern diagram**, then the team customization diagram.

**Talk track:**

> "If you treat Vigil as one application — incident commander — you ship one application. If you treat it as the platform layer underneath, the same code becomes the substrate Splunk Security Operations, Splunk Observability, Splunk IT Service Intelligence, Cisco AgenticOps, and Cisco Cloud Security all build on. **Same code, ten times the surface area.**"

> "The identity in one sentence: **Vigil is an MCP-guided workflow. Customizable, auditable, human-in-the-loop. Each team forks the default workflow, adds their own steps, and configures their own confidence thresholds — autonomous on routine cases, human approval on novel or high-risk.**"

*Show the **Orchestrator Pattern diagram** — framed as the target Cisco AI Canvas GA architecture.*

> "Here's the architecture this lands on at General Availability. **At the top is Cisco's foundation-model stack — Cisco Deep Network Model handling agentic reasoning inside FSM states, Cisco Time Series Model handling Phase 4 forecasting.** Cisco-native at GA. Today the implementation transitionally uses Anthropic Claude until Cisco Deep Network Model ships in early 2026 — **drop-in replacement, no orchestrator changes, schema enforcement preserves the 0.91 precision contract.**"

> "**Vigil MCP sits in the middle as the orchestrator.** Vigil's manifest defines the Finite State Machine transitions, RAG retrieval triggers, forecast confidence bands, audit schema, approval thresholds. **At the bottom are the downstream MCPs** — Splunk MCP with its 14 tools, Cisco Catalyst MCP with the two new Vigil-contributed tools, and any other MCP a team adds inside the Canvas tenant — ServiceNow, PagerDuty, Slack, GLaaS."

> "**The key insight that makes this scale on Cisco's stack:** Vigil MCP doesn't call Splunk MCP — Cisco Deep Network Model does (today, Claude does). The manifest tells whichever foundation model is running which tools to call, in what order, with what approval thresholds. **At Canvas GA, you add any MCP to the tenant and reference its tools from Vigil's manifest. That is how the platform scales on Cisco-native infrastructure — by adding tools to the catalogue, not by rewriting Vigil. The orchestrator does not change; only the catalogue of downstream tools grows.**"

*Now show the team customization diagram — canonical workflow at top, three team forks in the middle, MCP registry at the bottom.*

> "And here's how that scales business-wise. One canonical workflow at the top. Three team forks in the middle — each with their own custom steps and their own approval threshold. **Splunk SecOps requires human approval on every ESCALATING; Splunk Observability requires analyst approval before public status-page publication; Cisco AgenticOps configures per Canvas tenant.** Every custom step they add registers as a new MCP tool — and flows back into the registry, available to every other team's workflow."

> "**Why this scales.** Onboarding a new team takes one to two weeks versus six to twelve months building from scratch. Knowledge accumulates in one registry, not in five silos. One governance posture, configured per team via thresholds — not five inconsistent audit formats. Every Claude release, every Cisco Time Series Model release, improves every team's workflow simultaneously."

> "**The one sentence:** Vigil is the agentic equivalent of a Splunk dashboard — one shared engine, customized per team, scaled by adding new MCP tools and approval policies, not by rewriting the agent every time a new use case shows up. **That's the AI Foundations charter expressed as a product.**"

**Key signal:** This is the strongest Senior Staff PM signal of the whole demo. You're not pitching a feature — you're pitching a platform-substrate strategy.

**Pivot to next:** *"And it's built specifically to plug into Cisco's announced roadmap..."*

---

### Beat 9 — Cisco AI Canvas Integration (1 min)

**JD hook:** Partnership / GTM / strategic narratives.
**Show:** PRD *"How Vigil Fits Cisco's AI Roadmap"* with the Canvas integration diagram.

**Talk track:**

> "Cisco announced AgenticOps at Cisco Live 2025 — three roadmap components. **Vigil plugs into all three.**"

*Show the Canvas integration diagram.*

> "**AI Canvas** is the agentic orchestration platform, targeting 2026. Vigil's 7-state FSM IS the workflow that runs on Canvas — the transition graph maps directly to a Canvas template. **No rewrite when Canvas ships.**"

> "**Skills Registry** — the MCP tool catalog. Vigil registers its two new Catalyst tools — `get_network_topology` and `get_telemetry_metrics` — into the registry, and consumes other Skills from it. **Vigil is both consumer and contributor.**"

> "**Deep Network Model** — Cisco's network-tuned LLM, target early 2026. Drop-in replacement for the Claude call inside FSM reasoning states. Schema enforcement preserves the 0.91 precision floor — the model behind the wall changes; the contract doesn't. **Cisco Time Series Model is already benchmarked and used in Phase 4 today.**"

> "**Why this matters for Cisco:** every AgenticOps customer who adopts AI Canvas needs an incident commander workflow to run on it. Vigil is that workflow — with measured precision, measured cost, and a working audit trail. **The canonical first application.**"

**Key signal:** You're not asking Cisco to adapt to Vigil — you've built Vigil to adapt to Cisco. That's partnership-first thinking.

**Pivot to close:** *"So the question I'd close with..."*

---

### Beat 10 — The Bottom Line (30 sec)

**JD hook:** Closing pitch.
**Show:** PRD *"The Bottom Line"* table.

**Talk track:**

> "Cisco's AgenticOps timeline is 2025–2026. Splunk's 2026 predictions made the agentic-AI direction explicit. Every meaningful capability in that combined vision is buildable today, on the tooling both companies have already shipped. I built a single-engineer prototype to demonstrate it. The numbers are measurable: 0.91 precision, 80–85% cost reduction, full audit trail, three trigger types in the proactive forecasting layer."

> "**The question I'd close with is: who owns the agentic reasoning layer when Cisco AI Canvas ships in 2026? And who has the platform substrate that the next 50 applications build on?** That's what this role is for. That's what I want to do."

**Key signal:** End on a question that invites discussion. Position yourself as the person who has already thought about *where this lives in the organization*.

---

## Q&A — Likely Questions, Prepared Answers

### Technical Depth

**Q: "Why CTSM and not just fine-tune a GPT or Claude model on time series?"**
> "Two reasons. First, transformer architecture works for time series only when you tokenize the values correctly — Chronos does it by scaling and quantization, CTSM extends TimesFM with multiresolution input. A general LLM fine-tuned on time-series numerics underperforms a model architected for the modality — Amazon's Chronos paper makes that case quantitatively. Second, CTSM has 500 million parameters and was pre-trained on 300 billion observability datapoints — out of reach for fine-tuning a general LLM on a customer's data. The right answer is: use CTSM as the base, fine-tune on the customer's labeled incident corpus — that's Priority 3 in my roadmap."

**Q: "How do you decide Haiku vs Sonnet vs Opus?"**
> "Tier by decision criticality, not by state. Routing states (TRIAGE, INVESTIGATING) orchestrate tool calls — light cognition, Haiku handles it. HYPOTHESIZING is the actual root-cause decision — that's where Sonnet earns its 3x premium. Opus only if the customer workload requires reasoning beyond Sonnet, which the benchmark hasn't shown. The discipline is measure precision per tier — if Haiku drops precision below threshold for routing states, switch back. 0.91 precision is the gate."

**Q: "Why a Finite State Machine instead of LangGraph or CrewAI?"**
> "Auditability. FSM transitions are deterministic threshold rules — every SUPPRESSED, REMEDIATING, ESCALATING decision cites the rule that fired. Agent frameworks give you the workflow primitive, but the LLM controls the transitions; for live network infrastructure, that's the wrong default. The FSM enforces a senior engineer's investigation methodology consistently. When AI Canvas ships, the FSM maps to a Canvas workflow — same primitive, Cisco-native runtime."

**Q: "How would you measure success for the AI Foundations platform?"**
> "Three primary KPIs. **Adoption depth** — number of customer agents in production, investigations per customer per day, percentage of customer alerts touched by the platform. **Outcome quality** — false-positive suppression rate, autonomous triage precision, audit-trail completeness, cost per correct decision. **Ecosystem velocity** — Skills in the registry, partner-built agents, time from skill submission to ecosystem availability. Splunk's 2026 predictions explicitly name MTTR as a downstream metric — outcome-based measures lead."

### Product Strategy

**Q: "How do you balance internal product teams versus external customers?"**
> "Dogfood internally before external GA. Vigil's incident commander pattern is the first internal customer of the AI Foundations platform — Splunk Security, Observability, ITSI use it, surface bugs, harden the SDKs. Six months later, the same primitives ship as a developer SDK with case studies from internal usage. That's how Anthropic, OpenAI, AWS shipped their agent frameworks — internal customer first, external GA second."

**Q: "What's the biggest risk to this strategy?"**
> "Cisco Deep Network Model timeline slipping past 2026. The platform's positioning assumes Cisco ships foundation models we can productize. If that slips, we either wait, partner with Anthropic and Google more deeply, or invest in our own training — out of scope for an application company. Mitigation: structure the platform so the model layer is swappable. Vigil's 3p model abstraction already does that — orchestration and audit-trail layers don't depend on which foundation model is underneath."

**Q: "How do you engage with early design partners?"**
> "Three-tier engagement. Tier 1 design partners get pre-release SDK access, weekly PM-led product sessions, direct Slack to engineering — and commit to ship one production agent within 90 days. Tier 2 partners get monthly office hours and early docs. Tier 3 is the public developer community. The signal that matters: how many Tier 1 partners renew for a second 90-day commitment. Renewal rate is the only honest measure of value."

### Behavioral

**Q: "Tell me about a hard product decision you made on this project."**
> "Whether to make pre-triage rules-based or use a small ML classifier. Rules-based scores 35–40% of alerts at zero tokens, sub-millisecond, every decision auditable. A small classifier might marginally improve recall at the cost of latency, opacity, and adding a training pipeline. I chose rules. The argument that locked it: **pre-triage is logical filtering, not pattern recognition** — the patterns are already articulable, so a model is the wrong tool. **Putting a foundation model where rules are correct is the cargo-cult AI thinking the Splunk Foundations platform should actively discourage in its developer SDK.**"

**Q: "First 90 days in this role?"**
> "Three deliverables. Weeks 1–4: read every Splunk State of Security and Observability report, every recorded customer call from the prior quarter, write a one-pager on the top five jobs-to-be-done for the platform. Validate with five customers. Weeks 5–8: audit the existing AI Foundations roadmap, identify three highest-leverage cuts and three biggest missing investments. Weeks 9–12: ship one visible win — a published evaluation benchmark, a developer-facing SDK improvement, or a customer-validated case study. **Senior Staff PMs earn credibility through shipped artifacts in the first quarter, not strategy documents.**"

---

## What NOT to Do in the Demo

| Pitfall | What to Do Instead |
|---|---|
| Overselling mock as production | Acknowledge mock data once up-front, then move on. The architecture is real; the data is demo-scale by design. |
| Reading slides verbatim | Talk through them. The interviewer can read; they want to hear your reasoning. |
| Diving into Python implementation details | Stay architectural and strategic unless they pull you into code. |
| Claiming roadmap items as shipped | "I built a forecasting layer with mock data; live wiring is documented in my model-evaluation roadmap" is the honest framing. |
| Bashing competitors | "Splunk IT Service Intelligence does forecasting with statistical models, not foundation models" — *factual difference, not criticism.* |
| Skipping the caveat on Phase 4 | Always say the forecast is mock fixtures + how long live wiring would take. Honesty here is a credibility deposit. |

---

## What TO Land

| Signal You're Sending | How to Land It |
|---|---|
| *I read Splunk's published research before building* | Cite Hao Yang, Kamal Hathi, Patrick Lin, Dimitri McKay by name |
| *I can productize foundation models, not just consume them* | Walk through the CTSM benchmark + the 4-priority roadmap |
| *I think in audit trails and governance* | Open the Full Trace overlay; show the Governance Alignment table |
| *I think about unit economics* | Walk through the three cost levers — schema, caching, tiering |
| *I think about ecosystem and partnership posture* | "Built to absorb Cisco's roadmap, not race it" |
| *I have strong opinions defensible by reasoning* | Pre-triage = rules, not ML — deliberately chosen |
| *I think platform substrate, not feature* | The "How Vigil Scales as a Platform" beat — one workflow, customized per team |

---

## Pre-Demo Checklist

- [ ] UI running cleanly on `http://localhost:5173` (or wherever Vite assigned)
- [ ] All four scenarios runnable; one recent run already in History so Full Trace overlay has data even before live runs
- [ ] **Tab 1:** PRD open at the One-Line Story section
- [ ] **Tab 2:** `splunk_evals.ipynb` open at the VP Executive Summary
- [ ] **Tab 3:** `docs/competitive-landscape.md` open at the market map
- [ ] **Tab 4:** Vigil UI (`http://localhost:5173`)
- [ ] Phone on Do Not Disturb
- [ ] Glass of water nearby — 30 minutes is a long demo

---

## The Final Frame to Land

Senior Staff PM at the AI Foundations level isn't about *can you build this* — it's about *can you build the platform that lets other PMs and engineers build things like this 10x faster.*

The closing line:

> *"What I shipped here is one application of an AI Foundations platform. The role you're hiring for is to build the platform so the next 50 of these get built by other people. That's what I want to do."*
