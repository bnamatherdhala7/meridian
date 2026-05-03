"""Terminal report rendering for evaluator results."""
import json

from rich import box
from rich.console import Console
from rich.table import Table

console = Console()


def print_report(results: dict) -> None:
    console.print()
    console.rule("[bold]Evaluator Report[/bold]")
    console.print(f"  Incident:    [yellow]{results['incident_id']}[/yellow]")
    console.print(f"  Final state: [bold]{results['investigation']['final_state']}[/bold]")
    console.print()

    table = Table(title="Generic vs Constrained Output", box=box.ROUNDED, show_header=True)
    table.add_column("Dimension", style="bold", min_width=18)
    table.add_column("Investigation Run", justify="center")
    table.add_column("Generic LLM", justify="center", style="red")
    table.add_column("Constrained LLM", justify="center", style="green")

    inv = results["investigation"]
    gen = results["generic"]
    con = results["constrained"]

    table.add_row(
        "Total Tokens",
        f"{inv['total_tokens']:,}",
        f"{gen['total_tokens']:,}",
        f"{con['total_tokens']:,}",
    )
    table.add_row(
        "Cost (USD)",
        f"${inv['cost_usd']:.4f}",
        f"${gen['cost_usd']:.4f}",
        f"${con['cost_usd']:.4f}",
    )
    table.add_row(
        "Precision",
        f"{inv['precision']:.0%}",
        f"{gen['precision']:.0%}",
        f"{con['precision']:.0%}",
    )
    table.add_row(
        "Recall",
        f"{inv['recall']:.0%}",
        f"{gen['recall']:.0%}",
        f"{con['recall']:.0%}",
    )
    table.add_row("Tool Calls", str(inv["tool_calls"]), "—", "—")
    table.add_row("Duration (s)", str(inv["duration_secs"]), "—", "—")

    console.print(table)
    console.print(
        f"\n[bold green]Token savings (constrained vs generic):[/bold green] "
        f"[bold]{results['token_savings_pct']}%[/bold]"
    )

    if isinstance(con.get("output"), dict) and not con["output"].get("parse_error"):
        console.print("\n[bold]Constrained structured output:[/bold]")
        console.print_json(json.dumps(con["output"], indent=2))
