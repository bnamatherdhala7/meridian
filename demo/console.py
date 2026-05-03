"""War room console — single terminal dashboard for all three phases."""
from __future__ import annotations

import json
import pathlib
import threading
import time
from dataclasses import dataclass, field
from typing import Any

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from phase2_agent.commander import IncidentCommander, IncidentReport
from phase2_agent.states import STATES
from phase3_evaluator import evaluator, report as report_module

console = Console()

_FSM_SEP = " → "
_TERMINAL_STATES = {"ESCALATING", "RESOLVED"}
_STATE_STYLE = {
    "IDLE": "dim",
    "TRIAGE": "cyan",
    "INVESTIGATING": "yellow",
    "HYPOTHESIZING": "blue",
    "REMEDIATING": "green",
    "ESCALATING": "bold red",
    "RESOLVED": "bold green",
}


@dataclass
class _DashState:
    fsm_state: str = "IDLE"
    tool_calls: list[dict] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    status: str = "Initializing..."
    eval_results: dict | None = None
    done: bool = False


def _fsm_text(current: str) -> Text:
    text = Text()
    for i, s in enumerate(STATES):
        if s == current:
            text.append(f" {s} ", style=f"bold {_STATE_STYLE.get(s, '')} on grey15")
        elif STATES.index(s) < STATES.index(current):
            text.append(s, style="dim green")
        else:
            text.append(s, style="dim white")
        if i < len(STATES) - 1:
            text.append(_FSM_SEP, style="dim")
    return text


def _tool_table(tool_calls: list[dict]) -> Table:
    t = Table(box=box.SIMPLE, show_header=True, expand=True, padding=(0, 1))
    t.add_column("#", style="dim", width=3)
    t.add_column("Tool", style="cyan", min_width=22)
    t.add_column("Key Input", style="white")
    t.add_column("ms", justify="right", style="dim", width=5)
    for i, tc in enumerate(tool_calls[-8:], 1):
        vals = list(tc.get("input", {}).values())
        key_str = str(vals[0])[:42] if vals else ""
        t.add_row(str(i), tc["tool"], key_str, str(tc.get("duration_ms", "")))
    return t


def _evidence_text(evidence: list[str]) -> str:
    if not evidence:
        return "[dim]No evidence yet[/dim]"
    return "\n".join(f"• {e[:90]}" for e in evidence[-6:])


def _eval_text(results: dict | None, running: bool) -> str:
    if results is None:
        return "[dim]Waiting for investigation to complete...[/dim]" if not running else "[dim]Running evaluator...[/dim]"
    inv = results["investigation"]
    gen = results["generic"]
    con = results["constrained"]
    lines = [
        f"[bold]Investigation:[/bold]  {inv['total_tokens']:>6,} tokens  ${inv['cost_usd']:.4f}  "
        f"P:{inv['precision']:.0%}  R:{inv['recall']:.0%}  {inv['tool_calls']} tool calls",
        f"[green]Constrained:[/green]   {con['total_tokens']:>6,} tokens  ${con['cost_usd']:.4f}  "
        f"P:{con['precision']:.0%}  R:{con['recall']:.0%}",
        f"[red]Generic:[/red]        {gen['total_tokens']:>6,} tokens  ${gen['cost_usd']:.4f}  "
        f"P:{gen['precision']:.0%}  R:{gen['recall']:.0%}",
        "",
        f"[bold]Token savings (constrained vs generic): [green]{results['token_savings_pct']}%[/green][/bold]",
    ]
    return "\n".join(lines)


def _build_layout(ds: _DashState, scenario: dict, eval_running: bool) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="fsm_row", size=3),
        Layout(name="middle"),
        Layout(name="eval_row", size=9),
        Layout(name="footer", size=1),
    )
    layout["middle"].split_row(Layout(name="tools"), Layout(name="evidence"))

    layout["header"].update(Panel(
        Text.assemble(
            ("VIGIL", "bold blue"),
            (" — Incident Commander  │  ", "dim"),
            (scenario["incident_id"], "bold yellow"),
            ("  │  ", "dim"),
            (scenario["title"], "white"),
        ),
        style="blue",
    ))

    layout["fsm_row"].update(Panel(_fsm_text(ds.fsm_state), title="FSM State"))

    layout["tools"].update(Panel(
        _tool_table(ds.tool_calls),
        title=f"Tool Calls ({len(ds.tool_calls)})",
    ))
    layout["evidence"].update(Panel(
        _evidence_text(ds.evidence),
        title="Evidence",
    ))
    layout["eval_row"].update(Panel(
        _eval_text(ds.eval_results, eval_running),
        title="Phase 3 — Evaluator",
    ))

    status_style = "bold green" if ds.done else "bold yellow"
    layout["footer"].update(Text(f" {ds.status}", style=status_style))

    return layout


def main() -> None:
    scenario_path = pathlib.Path(__file__).parent.parent / "phase2_agent/scenarios/packet_loss_sj.json"
    scenario = json.loads(scenario_path.read_text())

    ds = _DashState()
    report_holder: dict[str, Any] = {}
    eval_running = False

    def on_event(event_type: str, data: Any) -> None:
        if event_type == "state_change":
            state = data.get("to") or data.get("state", ds.fsm_state)
            ds.fsm_state = state
            ds.status = f"FSM → {state}"
        elif event_type == "tool_call":
            ds.tool_calls.append(data)
            ds.status = f"Calling {data['tool']}..."

    def run_all() -> None:
        nonlocal eval_running
        commander = IncidentCommander()
        rpt: IncidentReport = commander.run(scenario, callback=on_event)
        report_holder["report"] = rpt
        ds.evidence = rpt.evidence
        ds.status = f"Investigation done — {rpt.final_state} ({rpt.total_tokens:,} tokens)"

        eval_running = True
        ds.status = "Running evaluator (generic vs constrained)..."
        eval_results = evaluator.evaluate(rpt)
        ds.eval_results = eval_results
        eval_running = False

        cost = evaluator.token_cost(rpt.input_tokens, rpt.output_tokens)
        ds.status = (
            f"Done — {rpt.final_state}  │  "
            f"{rpt.total_tokens:,} tokens  │  ${cost:.4f}  │  "
            f"{rpt.tool_calls} tool calls  │  {rpt.duration_secs}s"
        )
        ds.done = True

    thread = threading.Thread(target=run_all, daemon=True)
    thread.start()

    with Live(
        _build_layout(ds, scenario, eval_running),
        refresh_per_second=4,
        console=console,
    ) as live:
        while not ds.done:
            live.update(_build_layout(ds, scenario, eval_running))
            time.sleep(0.25)
        live.update(_build_layout(ds, scenario, eval_running))

    # Print final structured report
    console.print()
    if "report" in report_holder:
        rpt = report_holder["report"]
        console.print_json(json.dumps({
            "incident_id": rpt.incident_id,
            "final_state": rpt.final_state,
            "hypothesis": rpt.hypothesis,
            "evidence": rpt.evidence,
            "tool_calls": rpt.tool_calls,
            "recommended_action": rpt.recommended_action,
            "confidence": rpt.confidence,
            "total_tokens": rpt.total_tokens,
            "duration_secs": rpt.duration_secs,
        }, indent=2))

    if ds.eval_results:
        report_module.print_report(ds.eval_results)


if __name__ == "__main__":
    main()
