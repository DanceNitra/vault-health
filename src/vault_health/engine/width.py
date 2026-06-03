"""ω operator — measures width (breadth vs depth balance)."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.vault import Vault


@dataclass
class WidthReport:
    """Width metrics for the vault."""
    total_files: int = 0
    avg_words: float = 0.0
    short_files: int = 0       # <100 words (too shallow)
    medium_files: int = 0      # 100-300 words
    deep_files: int = 0        # >300 words (good depth)
    breadth_score: float = 0.0  # proportion of medium files (breadth sweet spot)
    depth_score: float = 0.0    # proportion of deep files
    width_score: float = 0.0    # composite breadth × depth balance
    by_directory: list[dict[str, object]] = field(default_factory=list)


def analyze(vault: Vault) -> WidthReport:
    """Analyse width (ω) — balance between breadth and depth."""
    report = WidthReport()
    report.total_files = vault.total_files

    # Directory-level analysis
    dir_stats: dict[str, list[int]] = {}

    short = 0
    medium = 0
    deep = 0
    total_words = 0

    for rel_path, vf in vault.files.items():
        wc = vf.word_count
        total_words += wc

        # Directory grouping (top-2 levels)
        parts = rel_path.split('/')
        dir_key = '/'.join(parts[:2]) if len(parts) > 1 else '/'
        dir_stats.setdefault(dir_key, []).append(wc)

        if wc < 100:
            short += 1
        elif wc < 300:
            medium += 1
        else:
            deep += 1

    report.short_files = short
    report.medium_files = medium
    report.deep_files = deep

    if vault.total_files > 0:
        report.avg_words = total_words / vault.total_files
        report.breadth_score = medium / vault.total_files
        report.depth_score = deep / vault.total_files

        # Width score: high when both breadth and depth are present
        # Penalize extreme imbalance (all shallow or all deep)
        breadth = report.breadth_score
        depth_score = report.depth_score
        # Ideal: breadth >= 20% AND depth >= 40%
        b_score = min(breadth / 0.2, 1.0)
        d_score = min(depth_score / 0.4, 1.0)
        report.width_score = 0.5 * b_score + 0.5 * d_score

    # Per-directory breakdown
    sorted_dir = sorted(dir_stats.items(),
                        key=lambda x: sum(x[1]),
                        reverse=True)
    for dir_key, word_counts in sorted_dir[:15]:
        total = len(word_counts)
        d_short = sum(1 for w in word_counts if w < 100)
        d_medium = sum(1 for w in word_counts if 100 <= w < 300)
        d_deep = sum(1 for w in word_counts if w >= 300)
        avg = sum(word_counts) / total if total > 0 else 0
        report.by_directory.append({
            "directory": dir_key,
            "files": total,
            "avg_words": round(avg, 0),
            "short": d_short,
            "medium": d_medium,
            "deep": d_deep,
        })

    return report
