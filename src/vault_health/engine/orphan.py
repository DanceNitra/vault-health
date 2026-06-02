"""λ operator — measures orphan ratio and lists orphan files."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.vault import Vault


@dataclass
class OrphanReport:
    """Orphan metrics for the vault."""
    total_files: int = 0
    orphan_count: int = 0
    orphan_ratio: float = 0.0
    orphan_score: float = 1.0  # 0.0 (all orphan) - 1.0 (none orphan)
    orphan_files: list[dict[str, object]] = field(default_factory=list)


def analyze(vault: Vault) -> OrphanReport:
    """Analyse orphan files (zero inbound links) across the vault."""
    report = OrphanReport()
    report.total_files = vault.total_files

    orphans: list[tuple[str, int]] = []
    for rel_path, vf in vault.files.items():
        # A file is orphan if it has zero inbound links
        # Also has outbound links (otherwise it's just disconnected)
        if len(vf.inbound_links) == 0 and len(vf.wikilinks) >= 0:
            orphans.append((rel_path, len(vf.wikilinks)))

    report.orphan_count = len(orphans)
    if vault.total_files > 0:
        report.orphan_ratio = report.orphan_count / vault.total_files
        # Score: 0% orphan = 1.0, 50%+ orphan = 0.0
        report.orphan_score = max(0.0, 1.0 - (report.orphan_ratio * 5))

    # Sort by most outbound links first (most disconnected)
    orphans.sort(key=lambda x: x[1], reverse=True)

    for path, outbound in orphans[:30]:
        report.orphan_files.append({
            "path": path,
            "outbound_links": outbound,
        })

    return report
