"""φ operator — measures coherence (domain bridge quality via frontmatter).

Uses pre-resolved inbound_links from vault scanner — O(n) instead of O(n²).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from ..core.vault import Vault


@dataclass
class CoherenceReport:
    """Coherence metrics for the vault."""
    total_files_with_domain: int = 0
    total_domains: int = 0
    domain_distribution: list[dict[str, object]] = field(default_factory=list)
    cross_domain_links: int = 0
    within_domain_links: int = 0
    cross_domain_ratio: float = 0.0
    coherence_score: float = 0.0  # 0.0 - 1.0


def analyze(vault: Vault) -> CoherenceReport:
    """Analyse coherence (φ) — domain bridge quality.

    Uses already-resolved inbound_links to find cross-domain references.
    """
    report = CoherenceReport()

    # Collect domains per file
    file_domain: dict[str, str] = {}
    domain_counts: Counter[str] = Counter()

    for rel_path, vf in vault.files.items():
        domain = vf.frontmatter.get('domain', '').strip().lower()
        if domain:
            file_domain[rel_path] = domain
            domain_counts[domain] += 1

    report.total_files_with_domain = len(file_domain)
    report.total_domains = len(domain_counts)

    # Domain distribution
    for domain, count in domain_counts.most_common():
        report.domain_distribution.append({
            "domain": domain,
            "count": count,
        })

    # Cross-domain analysis using inbound_links (already resolved)
    xdomain = 0
    within = 0

    for rel_path, vf in vault.files.items():
        target_domain = file_domain.get(rel_path, '')
        if not target_domain:
            continue

        for source_path in vf.inbound_links:
            source_domain = file_domain.get(source_path, '')
            if source_domain:
                if source_domain != target_domain:
                    xdomain += 1
                else:
                    within += 1

    report.cross_domain_links = xdomain
    report.within_domain_links = within
    total = xdomain + within
    if total > 0:
        report.cross_domain_ratio = xdomain / total
    else:
        report.cross_domain_ratio = 0.0

    # Coherence score: 0-1
    # Target: >= 20% cross-domain links
    report.coherence_score = min(report.cross_domain_ratio / 0.2, 1.0)

    return report
