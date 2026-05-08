"""
CLI entry point.
Usage:
  python scripts/run_investigation.py --scenario 0
  python scripts/run_investigation.py --alert "High CPU on core-sw-03" --device core-sw-03
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel   import Panel
from rich.table   import Table

from vigil.fsm       import VigilFSM
from vigil.evaluator import evaluate

console = Console()

SCENARIOS = [
    {
        "id":     "INC-2026-TEST-001",
        "device": "sw-core-01",
        "alert":  "High packet loss detected on sw-core-01. Interface Gi0/1 drop rate 12%. Single source IP 192.168.4.17 = 71% of egress traffic."
    },
    {
        "id":     "INC-2026-TEST-002",
        "device": "edge-rt-02",
        "alert":  "BGP peer reset 3x in 90 minutes on edge-rt-02. Keepalive timeout to upstream-isp-01. Partial route withdrawal observed."
    },
    {
        "id":     "INC-2026-TEST-003",
        "device": "core-sw-03",
        "alert":  "CPU utilization 94% on core-sw-03 for 11 minutes. Unknown process consuming resources. Multiple downstream services degraded."
    },
]


def main():
    parser = argparse.ArgumentParser(description="Vigil Incident Commander")
    parser.add_argument("--scenario", type=int, choices=[0, 1, 2], help="Run a pre-built scenario (0, 1, or 2)")
    parser.add_argument("--alert",  type=str, help="Custom alert text")
    parser.add_argument("--device", type=str, help="Device name (with --alert)")
    parser.add_argument("--id",     type=str, default="INC-CUSTOM-001", help="Incident ID")
    args = parser.parse_args()

    if args.scenario is not None:
        sc = SCENARIOS[args.scenario]
    elif args.alert and args.device:
        sc = {"id": args.id, "device": args.device, "alert": args.alert}
    else:
        console.print("[red]Provide --scenario 0|1|2 or --alert + --device[/red]")
        sys.exit(1)

    console.rule("[bold yellow]VIGIL — Incident Commander[/bold yellow]")
    console.print(f"\n[bold]Incident:[/bold] {sc['id']}")
    console.print(f"[bold]Device:  [/bold] {sc['device']}")
    console.print(f"[bold]Alert:   [/bold] {sc['alert']}\n")

    fsm = VigilFSM()
    with console.status("[yellow]Investigating...[/yellow]", spinner="dots"):
        report = fsm.investigate(sc["id"], sc["device"], sc["alert"])

    eval_result = evaluate(report)

    console.rule("FSM Trace")
    console.print(" → ".join(report.states_visited))

    console.rule("Evidence Collected")
    t = Table("Tool", "Result preview")
    for e in report.evidence:
        preview = str(e.result)[:80].replace("\n", " ")
        t.add_row(e.tool, preview)
    console.print(t)

    console.rule("RAG Retrievals")
    for layer in report.rag_hits:
        console.print(f"\n[purple]{layer['layer']} RAG[/purple] — {layer['phase']}")
        for h in layer["hits"]:
            console.print(f"  {h['score']:.2f}  {h['title']}")

    color = "red" if report.outcome == "ESCALATING" else "green"
    console.print(Panel(
        f"[bold {color}]{report.outcome}[/bold {color}]\n\n"
        f"Rules: {', '.join(report.decision_rules)}\n"
        f"Confidence: {report.confidence}  |  Elapsed: {report.elapsed_s}s",
        title="Decision"
    ))

    console.rule("Evaluator")
    et = Table("Metric", "Value")
    et.add_row("Precision",            str(eval_result.precision))
    et.add_row("Recall",               str(eval_result.recall))
    et.add_row("FSM states visited",   str(eval_result.fsm_states))
    et.add_row("RAG layers used",      str(eval_result.rag_layers))
    et.add_row("Composite score",      str(eval_result.composite))
    et.add_row("Tokens (generic)",     str(eval_result.token_generic))
    et.add_row("Tokens (constrained)", str(eval_result.token_constrained))
    et.add_row("Token savings",        f"{eval_result.token_savings_pct}%")
    et.add_row("Cost (constrained)",   f"${eval_result.cost_constrained}")
    console.print(et)

    if report.error:
        console.print(f"\n[red]Errors: {report.error}[/red]")


if __name__ == "__main__":
    main()
