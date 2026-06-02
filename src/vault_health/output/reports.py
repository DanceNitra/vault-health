"""Output formatting for broken link and orphan reports."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..engine.broken import BrokenReport
from ..engine.orphan import OrphanReport


def print_broken_report(report: BrokenReport) -> None:
    """Print a formatted broken link report."""
    console = Console()

    score_icon = (
        "🟢" if report.broken_score >= 0.8
        else "🟡" if report.broken_score >= 0.5
        else "🔴"
    )
    console.print(Panel.fit(
        "[bold red]🔗 BROKEN LINK REPORT[/bold red]",
        border_style="red",
    ))
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_column("Status")

    table.add_row(
        f"{score_icon} β broken ratio",
        f"{report.broken_ratio:.2%}",
        f"target: <1% | score: {report.broken_score:.2f}",
    )
    table.add_row("  Total links", str(report.total_links), "")
    table.add_row("  Broken", str(report.broken_links), "")

    console.print(table)
    console.print()

    if report.top_broken_files:
        console.print("[bold]Top files with broken links:[/bold]")
        for entry in report.top_broken_files:
            path: str = entry["path"]  # type: ignore[assignment]
            count: int = entry["broken_count"]  # type: ignore[assignment]
            links: list[str] = entry["broken_links"]  # type: ignore[assignment]
            console.print(f"  [red]✗[/red] {path} — [{count}]")
            for link in links:
                console.print(f"    → [[{link}]]")


def print_orphan_report(report: OrphanReport) -> None:
    """Print a formatted orphan report."""
    console = Console()

    score_icon = (
        "🟢" if report.orphan_score >= 0.8
        else "🟡" if report.orphan_score >= 0.5
        else "🔴"
    )
    console.print(Panel.fit(
        "[bold yellow]👻 ORPHAN REPORT[/bold yellow]",
        border_style="yellow",
    ))
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_column("Status")

    table.add_row(
        f"{score_icon} λ orphan ratio",
        f"{report.orphan_ratio:.2%}",
        f"target: <1% | score: {report.orphan_score:.2f}",
    )
    table.add_row("  Total files", str(report.total_files), "")
    table.add_row("  Orphans", str(report.orphan_count), "")

    console.print(table)
    console.print()

    if report.orphan_files:
        console.print("[bold]Orphan files:[/bold]")
        for entry in report.orphan_files:
            path: str = entry["path"]  # type: ignore[assignment]
            outbound: int = entry["outbound_links"]  # type: ignore[assignment]
            icon = "🟡" if outbound > 0 else "⚪"
            console.print(f"  {icon} {path} ({outbound} outbound)")
