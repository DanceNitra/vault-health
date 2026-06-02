"""vault-health CLI — Tracer Bullet implementation.

Usage:
    vh --path <path>
    vh --path <path> --json
    vh broken --path <path>
    vh orphan --path <path>
"""

from __future__ import annotations

import os as _os

import typer

from ..core.vault import scan as scan_vault
from ..engine import broken as broken_engine
from ..engine import depth
from ..engine import orphan as orphan_engine
from ..output.reports import print_broken_report, print_orphan_report
from ..output.terminal import print_report

app = typer.Typer(
    name="vault-health",
    help="Epistemic Calculus CLI — measure your knowledge vault health",
    no_args_is_help=True,
)


def _resolve_path(path: str) -> str:
    resolved = _os.path.expanduser(path)
    return _os.path.abspath(resolved)


@app.command()
def scan(
    path: str = typer.Option(
        ..., "--path", "-p",
        help="Path to the vault directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    json: bool = typer.Option(
        False, "--json", "-j", help="Output as JSON instead of terminal",
    ),
) -> None:
    """Scan a vault and produce a depth health report."""
    resolved_path = _resolve_path(path)
    vault = scan_vault(resolved_path)
    report = depth.analyze(vault)

    if json:
        import json as json_mod
        output = json_mod.dumps({
            "total_files": vault.total_files,
            "total_wikilinks": vault.total_wikilinks,
            "broken_links": vault.broken_links,
            "depth": {
                "score": report.depth_score,
                "total_concepts": report.total_concepts,
                "avg_words": round(report.avg_words, 1),
                "files_under_100": report.files_under_100_words,
                "files_under_300": report.files_under_300_words,
                "files_under_500": report.files_under_500_words,
            },
        }, indent=2)
        print(output)
    else:
        print_report(report)


@app.command()
def broken(
    path: str = typer.Option(
        ..., "--path", "-p",
        help="Path to the vault directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
) -> None:
    """Report broken wikilinks in the vault."""
    resolved_path = _resolve_path(path)
    vault = scan_vault(resolved_path)
    report_obj = broken_engine.analyze(vault)
    print_broken_report(report_obj)


@app.command()
def orphan(
    path: str = typer.Option(
        ..., "--path", "-p",
        help="Path to the vault directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
) -> None:
    """Report orphan files (zero inbound links) in the vault."""
    resolved_path = _resolve_path(path)
    vault = scan_vault(resolved_path)
    report_obj = orphan_engine.analyze(vault)
    print_orphan_report(report_obj)


if __name__ == "__main__":
    app()
