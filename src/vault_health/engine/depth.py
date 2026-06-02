"""δ operator — measures concept depth (word count, line count, section count)."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.vault import Vault


@dataclass
class DepthReport:
    """Depth metrics for the vault."""
    total_concepts: int = 0
    avg_words: float = 0.0
    avg_lines: float = 0.0
    min_words: int = 0
    max_words: int = 0
    files_under_100_words: int = 0
    files_under_300_words: int = 0
    files_under_500_words: int = 0
    depth_score: float = 0.0  # 0.0 - 1.0
    file_details: list[dict[str, object]] = field(default_factory=list)


def analyze(vault: Vault) -> DepthReport:
    """Analyse depth of all concept files in the vault."""
    report = DepthReport()

    words_list: list[int] = []

    for rel_path, vf in vault.files.items():
        wc = vf.word_count
        lc = vf.line_count
        words_list.append(wc)

        if wc < 100:
            report.files_under_100_words += 1
        if wc < 300:
            report.files_under_300_words += 1
        if wc < 500:
            report.files_under_500_words += 1

        report.file_details.append({
            "path": rel_path,
            "words": wc,
            "lines": lc,
        })

    report.total_concepts = len(words_list)

    if words_list:
        report.avg_words = sum(words_list) / len(words_list)
        report.avg_lines = sum(vf.line_count for vf in vault.files.values()) / len(words_list)
        report.min_words = min(words_list)
        report.max_words = max(words_list)

        # Depth score: composite metric
        # - proportion of files over 300 words (good depth)
        # - normalised by average words
        over_300 = sum(1 for w in words_list if w >= 300) / len(words_list)
        norm_avg = min(report.avg_words / 1000.0, 1.0)
        report.depth_score = 0.5 * over_300 + 0.5 * norm_avg

    return report
