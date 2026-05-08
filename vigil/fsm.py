"""
Vigil FSM — 7-state incident commander.
Wires RAG layers and MCP tools into a deterministic investigation sequence.
"""
from dataclasses import dataclass, field
from typing import Any
import time

from vigil.rag import SPLKnowledgeRAG, IncidentMemoryRAG, RAGHit
from vigil import mcp_client as mcp
from vigil.classifier import classify


STATES = ["IDLE", "TRIAGE", "INVESTIGATING", "HYPOTHESIZING", "REMEDIATING", "ESCALATING", "RESOLVED"]

EGRESS_CONCENTRATION_THRESHOLD = 0.60
INCIDENT_MEMORY_CONFIDENCE     = 0.75
BLAST_RADIUS_BLOCK             = {"HIGH", "CRITICAL"}


@dataclass
class Evidence:
    tool:   str
    result: Any
    tokens: int = 0


@dataclass
class InvestigationReport:
    incident_id:    str
    device:         str
    alert_text:     str
    outcome:        str = "UNKNOWN"
    final_state:    str = "IDLE"
    states_visited: list = field(default_factory=list)
    evidence:       list = field(default_factory=list)
    rag_hits:       list = field(default_factory=list)
    decision_rules: list = field(default_factory=list)
    elapsed_s:      float = 0.0
    token_count:    int = 0
    confidence:     float = 0.0
    error:          str = ""


class VigilFSM:
    def __init__(self):
        self.spl_rag      = SPLKnowledgeRAG()
        self.incident_rag = IncidentMemoryRAG()

    def investigate(self, incident_id: str, device: str, alert_text: str) -> InvestigationReport:
        report = InvestigationReport(
            incident_id = incident_id,
            device      = device,
            alert_text  = alert_text
        )
        start = time.time()

        # ── Pre-triage classifier ───────────────────────────────
        should_run, score, reason = classify(alert_text)
        if not should_run:
            report.final_state = "IDLE"
            report.outcome     = "SUPPRESSED"
            report.decision_rules.append(f"classifier:{reason}  score:{score}")
            report.elapsed_s   = round(time.time() - start, 2)
            return report

        report.states_visited.append("TRIAGE")

        try:
            # ── TRIAGE ─────────────────────────────────────────
            spl_hits = self.spl_rag.get_patterns(alert_text, phase="TRIAGE", top_k=3)
            report.rag_hits.extend([{"layer": "SPL", "phase": "TRIAGE", "hits":
                [{"id": h.id, "title": h.title, "score": h.score} for h in spl_hits]}])

            primary_spl = spl_hits[0].metadata.get("spl", "") if spl_hits else ""
            if primary_spl and "$device$" in primary_spl:
                primary_spl = primary_spl.replace("$device$", device)

            triage_result = mcp.run_splunk_query(primary_spl) if primary_spl else {"raw": "no_spl"}
            report.evidence.append(Evidence("splunk_run_query", triage_result))

            ko_result = mcp.get_knowledge_objects(alert_text[:80])
            report.evidence.append(Evidence("splunk_get_knowledge_objects", ko_result))

            # ── INVESTIGATING ───────────────────────────────────
            report.states_visited.append("INVESTIGATING")

            incident_hits = self.incident_rag.get_similar_incidents(alert_text, top_k=3)
            report.rag_hits.extend([{"layer": "Incident", "phase": "INVESTIGATING", "hits":
                [{"id": h.id, "title": h.title, "score": h.score, "outcome": h.metadata.get("outcome")} for h in incident_hits]}])

            topology = mcp.get_network_topology(device)
            report.evidence.append(Evidence("ci_get_network_topology", topology))

            telemetry = mcp.get_telemetry_metrics(device)
            report.evidence.append(Evidence("ci_get_telemetry_metrics", telemetry))

            # ── HYPOTHESIZING ───────────────────────────────────
            report.states_visited.append("HYPOTHESIZING")

            spl_context = {
                "fsm_state":   "HYPOTHESIZING",
                "device":      device,
                "triage_data": str(triage_result)[:200],
                "topology":    str(topology)[:200],
            }
            generated = mcp.generate_spl(
                f"Investigate: {alert_text[:200]}",
                context=spl_context
            )
            report.evidence.append(Evidence("saia_generate_spl", generated))

            gen_spl = generated.get("spl", generated.get("raw", ""))
            if gen_spl:
                gen_result = mcp.run_splunk_query(gen_spl)
                report.evidence.append(Evidence("splunk_run_query_hyp", gen_result))

            # ── Decision logic ─────────────────────────────────
            blast_radius         = topology.get("blast_radius", "UNKNOWN")
            top_incident_score   = incident_hits[0].score if incident_hits else 0.0
            top_incident_outcome = incident_hits[0].metadata.get("outcome", "") if incident_hits else ""

            triage_raw = str(triage_result).lower()
            egress_high  = any(f"{p}%" in triage_raw or f"{p}.0" in triage_raw for p in range(61, 100))
            threat_match = "threat_intel_match=true" in triage_raw or "threat_score" in triage_raw

            if egress_high and threat_match:
                outcome = "ESCALATING"
                rule    = "single_ip_egress_above_threshold + threat_intel_match"
            elif blast_radius in BLAST_RADIUS_BLOCK and "unknown" in triage_raw:
                outcome = "ESCALATING"
                rule    = f"blast_radius={blast_radius} + unknown_process"
            elif (top_incident_score >= INCIDENT_MEMORY_CONFIDENCE
                  and top_incident_outcome == "REMEDIATING"
                  and blast_radius not in BLAST_RADIUS_BLOCK):
                outcome = "REMEDIATING"
                rule    = f"incident_memory_match={top_incident_score:.2f} deterministic_fix=known"
            else:
                outcome = "ESCALATING"
                rule    = "ambiguous_evidence_default_escalate"

            report.decision_rules.append(rule)
            report.outcome     = outcome
            report.final_state = outcome
            report.states_visited.append(outcome)
            report.states_visited.append("RESOLVED")
            report.confidence  = round(top_incident_score, 2)

        except Exception as e:
            report.error       = str(e)
            report.final_state = "ESCALATING"
            report.outcome     = "ESCALATING"
            report.decision_rules.append(f"error_default_escalate:{e}")

        report.elapsed_s   = round(time.time() - start, 2)
        report.token_count = len(report.evidence) * 800
        return report
