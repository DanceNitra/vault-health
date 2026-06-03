"""Output formatting for all vault-health reports."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..engine.broken import BrokenReport
from ..engine.coherence import CoherenceReport
from ..engine.connectivity import ConnectivityReport
from ..engine.orphan import OrphanReport
from ..engine.recency import RecencyReport
from ..engine.width import WidthReport


def _score_icon(score: float) -> str:
    if score >= 0.8:
        return "🟢"
    if score >= 0.5:
        return "🟡"
    return "🔴"


def print_broken_report(report: BrokenReport) -> None:
    """Print a formatted broken link report."""
    console = Console()
    icon = _score_icon(report.broken_score)
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
        f"{icon} β broken ratio",
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
    icon = _score_icon(report.orphan_score)
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
        f"{icon} λ orphan ratio",
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
            icon2 = "🟡" if outbound > 0 else "⚪"
            console.print(f"  {icon2} {path} ({outbound} outbound)")


def print_connectivity_report(report: ConnectivityReport) -> None:
    """Print connectivity (κ) report."""
    console = Console()
    icon = _score_icon(report.connectivity_score)
    console.print(Panel.fit(
        f"[bold cyan]{icon} CONNECTIVITY REPORT[/bold cyan]",
        border_style="cyan",
    ))
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_column("Status")

    table.add_row(f"{icon} κ connectivity", f"{report.avg_outbound:.1f}/file",
                  f"target: >5 | score: {report.connectivity_score:.2f}")
    status_symbol = "✅" if report.avg_outbound >= 5 else "⚠️"
    table.add_row("  Avg outbound", f"{report.avg_outbound:.1f}",
                  status_symbol)
    table.add_row("  Avg inbound", f"{report.avg_inbound:.1f}", "")
    table.add_row("  Zero outbound", str(report.files_with_zero_outbound), "")
    table.add_row("  Zero inbound", str(report.files_with_zero_inbound), "")

    console.print(table)
    console.print()

    if report.top_connected:
        console.print("[bold]Most connected files:[/bold]")
        for entry in report.top_connected:
            path: str = entry["path"]  # type: ignore[assignment]
            total: int = entry["total"]  # type: ignore[assignment]
            ob: int = entry["outbound"]  # type: ignore[assignment]
            ib: int = entry["inbound"]  # type: ignore[assignment]
            console.print(f"  🔗 {path} ({ob}→, {ib}←, {total} total)")


def print_recency_report(report: RecencyReport) -> None:
    """Print recency (ρ) report."""
    console = Console()
    icon = _score_icon(report.recency_score)
    console.print(Panel.fit(
        f"[bold yellow]{icon} RECENCY REPORT[/bold yellow]",
        border_style="yellow",
    ))
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_column("Status")

    table.add_row(f"{icon} ρ recency",
                  f"{report.files_updated_30d}/{report.total_files}",
                  f"target: <30d stale | score: {report.recency_score:.2f}")
    table.add_row("  Updated <7d", str(report.files_updated_7d), "")
    table.add_row("  Updated <30d", str(report.files_updated_30d), "")
    table.add_row("  Updated <90d", str(report.files_updated_90d), "")
    table.add_row("  Stale >90d", str(report.files_stale_over_90d), "")

    console.print(table)


def print_width_report(report: WidthReport) -> None:
    """Print width (ω) report."""
    console = Console()
    icon = _score_icon(report.width_score)
    console.print(Panel.fit(
        f"[bold orange3]{icon} WIDTH REPORT[/bold orange3]",
        border_style="orange3" if hasattr(console, 'border_style') else "yellow",
    ))
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_column("Status")

    table.add_row(f"{icon} ω width",
                  f"{report.breadth_score:.0%} med / {report.depth_score:.0%} deep",
                  f"target: >20% med | score: {report.width_score:.2f}")
    table.add_row("  Short (<100w)", str(report.short_files), "")
    table.add_row("  Medium (100-300w)", str(report.medium_files), "")
    table.add_row("  Deep (>300w)", str(report.deep_files), "")

    console.print(table)
    console.print()

    if report.by_directory:
        console.print("[bold]By directory:[/bold]")
        for entry in report.by_directory:
            dir_name: str = entry["directory"]  # type: ignore[assignment]
            files: int = entry["files"]  # type: ignore[assignment]
            avg: float = entry["avg_words"]  # type: ignore[assignment]
            d_short: int = entry["short"]  # type: ignore[assignment]
            d_medium: int = entry["medium"]  # type: ignore[assignment]
            d_deep: int = entry["deep"]  # type: ignore[assignment]
            msg = (
                f"  📁 {dir_name} — {files} files, {avg:.0f} avg"
                f" ({d_short}S/{d_medium}M/{d_deep}D)"
            )
            console.print(msg)


def print_coherence_report(report: CoherenceReport) -> None:
    """Print coherence (φ) report."""
    console = Console()
    icon = _score_icon(report.coherence_score)
    console.print(Panel.fit(
        f"[bold white]{icon} COHERENCE REPORT[/bold white]",
        border_style="white",
    ))
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_column("Status")

    table.add_row(f"{icon} φ coherence",
                  f"{report.cross_domain_ratio:.1%} cross-domain",
                  f"target: >20% | score: {report.coherence_score:.2f}")
    table.add_row("  Files with domain", str(report.total_files_with_domain), "")
    table.add_row("  Unique domains", str(report.total_domains), "")
    table.add_row("  Cross-domain links", str(report.cross_domain_links), "")
    table.add_row("  Within-domain links", str(report.within_domain_links), "")

    console.print(table)
    console.print()

    if report.domain_distribution:
        console.print("[bold]Domain distribution:[/bold]")
        for entry in report.domain_distribution:
            domain: str = entry["domain"]  # type: ignore[assignment]
            count: int = entry["count"]  # type: ignore[assignment]
            console.print(f"  📂 {domain}: {count} files")


def print_full_report(
    depth_score: float,
    broken: BrokenReport,
    orphan: OrphanReport,
    connectivity: ConnectivityReport,
    recency: RecencyReport,
    width: WidthReport,
    coherence: CoherenceReport,
) -> None:
    """Print a comprehensive combined vault health report."""
    console = Console()

    console.print(Panel.fit(
        "[bold cyan]📊 VAULT HEALTH — FULL REPORT[/bold cyan]",
        border_style="cyan",
    ))
    console.print()

    table = Table(show_header=True, box=None, padding=(0, 2))
    table.add_column("Op", style="cyan", width=4)
    table.add_column("Metric", style="bold", width=18)
    table.add_column("Value", width=22)
    table.add_column("Score", width=8)

    table.add_row("🟢", "δ Depth", f"{depth_score:.2%}", f"{depth_score:.2f}")
    table.add_row(
        "🔵", "κ Connectivity", f"{connectivity.avg_outbound:.1f}/file",
        f"{connectivity.connectivity_score:.2f}",
    )
    table.add_row(
        "🟡", "ρ Recency",
        f"{recency.files_updated_30d}/{recency.total_files}",
        f"{recency.recency_score:.2f}",
    )
    table.add_row(
        "🔴", "β Broken", f"{broken.broken_links}/{broken.total_links}",
        f"{broken.broken_score:.2f}",
    )
    table.add_row(
        "🟣", "λ Orphan", f"{orphan.orphan_count}/{orphan.total_files}",
        f"{orphan.orphan_score:.2f}",
    )
    table.add_row(
        "🟠", "ω Width",
        f"{width.breadth_score:.0%} med\n{width.depth_score:.0%} deep",
        f"{width.width_score:.2f}",
    )
    table.add_row(
        "⚪", "φ Coherence",
        f"{coherence.cross_domain_ratio:.1%} cross",
        f"{coherence.coherence_score:.2f}",
    )

    console.print(table)

    # Overall
    scores = [
        depth_score,
        connectivity.connectivity_score,
        recency.recency_score,
        broken.broken_score,
        orphan.orphan_score,
        width.width_score,
        coherence.coherence_score,
    ]
    avg = sum(scores) / len(scores)
    console.print()
    icon = _score_icon(avg)
    console.print(f"[bold]{icon} Overall health: {avg:.2f} / 1.00[/bold]")
