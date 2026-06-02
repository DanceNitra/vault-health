"""vault-health CLI — Tracer Bullet implementation.

Usage:
    vault-health scan --path <path>
    vault-health scan --path <path> --json
"""

from __future__ import annotations
import os as _os

import typer
from ..core.vault import scan as scan_vault
from ..engine import depth
from ..output.terminal import print_report

app = typer.Typer(
    name="vault-health",
    help="Epistemic Calculus CLI — measure your knowledge vault health",
    no_args_is_help=True,
)


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
    """Scan a vault and produce a health report."""
    resolved_path = _os.path.expanduser(path)
    resolved_path = _os.path.abspath(resolved_path)
    
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


if __name__ == "__main__":
    app()