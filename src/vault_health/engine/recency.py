"""ρ operator — measures recency (how recently files were updated)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from ..core.vault import Vault


@dataclass
class RecencyReport:
    """Recency metrics for the vault."""
    total_files: int = 0
    files_updated_7d: int = 0
    files_updated_30d: int = 0
    files_updated_90d: int = 0
    files_stale_over_90d: int = 0
    stale_ratio: float = 0.0
    recency_score: float = 0.0  # 0.0 - 1.0
    newest_files: list[dict[str, object]] = field(default_factory=list)
    oldest_files: list[dict[str, object]] = field(default_factory=list)


def analyze(vault: Vault) -> RecencyReport:
    """Analyse recency (ρ) of vault files."""
    report = RecencyReport()
    report.total_files = vault.total_files

    now = time.time()
    file_ages: list[tuple[str, float]] = []

    for rel_path, vf in vault.files.items():
        age_days = (now - vf.mtime) / 86400
        file_ages.append((rel_path, age_days))

        if age_days <= 7:
            report.files_updated_7d += 1
        if age_days <= 30:
            report.files_updated_30d += 1
        if age_days <= 90:
            report.files_updated_90d += 1
        if age_days > 90:
            report.files_stale_over_90d += 1

    if vault.total_files > 0:
        report.stale_ratio = report.files_stale_over_90d / vault.total_files
        # Score: 0% stale = 1.0, 50%+ stale = 0.0
        report.recency_score = max(0.0, 1.0 - report.stale_ratio)

    # Newest files
    file_ages.sort(key=lambda x: x[1])
    for path, age in file_ages[:10]:
        report.newest_files.append({
            "path": path,
            "age_days": round(age, 1),
        })

    # Oldest files
    file_ages.sort(key=lambda x: x[1], reverse=True)
    for path, age in file_ages[:10]:
        report.oldest_files.append({
            "path": path,
            "age_days": round(age, 1),
        })

    return report
