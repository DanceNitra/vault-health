"""Terminal output formatting using Rich."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..engine.depth import DepthReport


def print_report(report: DepthReport) -> None:
    """Print a formatted health report to the terminal."""
    console = Console()

    # Header
    console.print(Panel.fit(
        "[bold cyan]📊 VAULT HEALTH REPORT[/bold cyan]",
        border_style="cyan",
    ))
    console.print()

    # Depth section
    score_icon = "🟢" if report.depth_score >= 0.6 else "🟡" if report.depth_score >= 0.3 else "🔴"

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_column("Status")

    table.add_row(
        f"{score_icon} δ depth",
        f"{report.depth_score:.2%}",
        "target: >60%",
    )
    table.add_row("  Concepts", str(report.total_concepts), "")
    table.add_row("  Avg words/concept", f"{report.avg_words:.0f}", "")
    table.add_row("  Avg lines/concept", f"{report.avg_lines:.0f}", "")
    table.add_row("  Short (<100w)", str(report.files_under_100_words), "")
    table.add_row("  Medium (100-300w)",
                     str(report.files_under_300_words - report.files_under_100_words), "")
    table.add_row("  Deep (>300w)",
                     str(report.total_concepts - report.files_under_300_words), "")
    table.add_row("  Range", f"{report.min_words} – {report.max_words} words", "")

    console.print(table)
    console.print()
