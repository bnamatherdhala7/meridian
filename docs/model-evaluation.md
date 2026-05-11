# Model Evaluation — Findings and Engineering Roadmap

**The complete model evaluation now lives in the notebook itself:** [`splunk_evals.ipynb`](../splunk_evals.ipynb)

This consolidation means one tab during a demo or walkthrough — the benchmark code, the per-metric numerical results, the VP-level summary, and the engineering roadmap are all in the same place, in the right order.

## What's in the notebook

The notebook now reads as a complete narrative:

| Section | Content | Audience |
|---|---|---|
| **VP Executive Summary** (top) | The headline verdict + a 4-row priority table (P0–P3) with effort, owner, and outcome | VP / Product Manager |
| **Metric Glossary** | Plain-English definitions of Mean Absolute Scaled Error, symmetric Mean Absolute Percentage Error, and Continuous Ranked Probability Score — how to read each, and which to trust on which signal | Anyone — including the model-team partner you're sending the benchmark to |
| **What We Measured and Why** | The three foundation models compared (Cisco Time Series Model 1.0, Chronos-T5-Small, TimesFM-2.5-200M) and the requirements they're evaluated against | Setup |
| **Cells 1–27 — Benchmark code and results** | Environment setup, dataset generation, Cisco Time Series Model API discovery, three-model inference, final results table | Engineering |
| **Key Findings — Five Takeaways** (bottom) | Per-finding numerical evidence: CTSM wins overall and dominates BGP; both CTSM and Chronos are worse than naive on packet drop; CTSM's API blocks Continuous Ranked Probability Score measurement; sMAPE misleads on near-zero values | VP + Engineering |
| **Where Each Model Fits in Vigil** | Per-use-case model recommendation (hybrid CTSM + Chronos until quantile outputs ship) | Product |
| **Engineering Roadmap — Prioritized Next Steps** (bottom) | Per-priority breakdown — effort, timeline, cost, owner, dependency, success criteria — plus recommended sequencing block | Engineering |
| **Why This Benchmark Is the Right Foundation for the Cisco Conversation** | The two concrete asks for the Cisco Time Series Model team | Partnership / GTM |

## Why the notebook is the right home

A model evaluation should be co-located with the evaluation code. A reviewer should be able to:
- See the exact synthetic dataset that produced each metric
- Re-run the Cisco Time Series Model inference and verify the numbers
- Click on `make_packet_drop` and see how the burst-pattern series in Priority 2 of the roadmap would be generated

When the same content lived in a separate markdown file, the link between claims and evidence was implicit. In the notebook, the evidence is one cell away from the claim.

## Open the notebook

- **GitHub:** [`splunk_evals.ipynb`](../splunk_evals.ipynb) (renders inline)
- **Local:** `jupyter notebook splunk_evals.ipynb`
- **Colab:** the notebook header has a "Open in Colab" badge

For a 15-minute demo or walkthrough, scroll top-to-bottom — VP Executive Summary leads with the headline and priority table; Metric Glossary disambiguates the numbers; the benchmark code lets a technical reviewer verify; Key Findings + Engineering Roadmap close.
