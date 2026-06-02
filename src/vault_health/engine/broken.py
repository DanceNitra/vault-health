"""β operator — measures broken link ratio and lists broken links."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.vault import Vault


@dataclass
class BrokenReport:
    """Broken link metrics for the vault."""
    total_links: int = 0
    broken_links: int = 0
    broken_ratio: float = 0.0
    broken_score: float = 1.0  # 0.0 (all broken) - 1.0 (none broken)
    top_broken_files: list[dict[str, object]] = field(default_factory=list)


def analyze(vault: Vault) -> BrokenReport:
    """Analyse broken links across the vault."""
    report = BrokenReport()
    report.total_links = vault.total_wikilinks
    report.broken_links = vault.broken_links

    if vault.total_wikilinks > 0:
        report.broken_ratio = vault.broken_links / vault.total_wikilinks
        # Score: 0% broken = 1.0, 100% broken = 0.0
        report.broken_score = max(0.0, 1.0 - (report.broken_ratio * 10))

    # Top files with most broken links
    file_broken: list[tuple[str, int, list[str]]] = []
    for rel_path, vf in vault.files.items():
        if vf.broken_links:
            file_broken.append((rel_path, len(vf.broken_links), vf.broken_links))

    file_broken.sort(key=lambda x: x[1], reverse=True)

    for path, count, links in file_broken[:20]:
        report.top_broken_files.append({
            "path": path,
            "broken_count": count,
            "broken_links": links[:10],  # show up to 10 per file
        })

    return report
