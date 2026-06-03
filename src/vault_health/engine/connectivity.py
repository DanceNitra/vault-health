"""κ operator — measures connectivity (average links per file)."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.vault import Vault


@dataclass
class ConnectivityReport:
    """Connectivity metrics for the vault."""
    total_files: int = 0
    total_links: int = 0
    avg_outbound: float = 0.0
    avg_inbound: float = 0.0
    median_outbound: float = 0.0
    files_with_zero_outbound: int = 0
    files_with_zero_inbound: int = 0
    connectivity_score: float = 0.0  # 0.0 - 1.0
    top_connected: list[dict[str, object]] = field(default_factory=list)


def analyze(vault: Vault) -> ConnectivityReport:
    """Analyse connectivity (κ) of the vault."""
    report = ConnectivityReport()
    report.total_files = vault.total_files
    report.total_links = vault.total_wikilinks

    outbounds: list[int] = []
    inbounds: list[int] = []
    zero_out = 0
    zero_in = 0

    for vf in vault.files.values():
        ob = len(vf.wikilinks)
        ib = len(vf.inbound_links)
        outbounds.append(ob)
        inbounds.append(ib)

        if ob == 0:
            zero_out += 1
        if ib == 0:
            zero_in += 1

    report.files_with_zero_outbound = zero_out
    report.files_with_zero_inbound = zero_in

    if outbounds:
        report.avg_outbound = sum(outbounds) / len(outbounds)
        sorted_ob = sorted(outbounds)
        mid = len(sorted_ob) // 2
        if len(sorted_ob) % 2:
            report.median_outbound = sorted_ob[mid]
        else:
            report.median_outbound = (sorted_ob[mid - 1] + sorted_ob[mid]) / 2

    if inbounds:
        report.avg_inbound = sum(inbounds) / len(inbounds)

    # Connectivity score: weighted composite
    # avg_outbound >= 5 is good, 0 means disconnected
    norm_out = min(report.avg_outbound / 10.0, 1.0)
    # zero-inbound penalty
    zero_in_ratio = zero_in / vault.total_files if vault.total_files > 0 else 0
    report.connectivity_score = max(0.0, 0.6 * norm_out + 0.4 * (1.0 - zero_in_ratio))

    # Top 10 most connected files (by outbound + inbound)
    connected: list[tuple[str, int, int]] = []
    for rel_path, vf in vault.files.items():
        total = len(vf.wikilinks) + len(vf.inbound_links)
        if total >= 20:
            connected.append((rel_path, len(vf.wikilinks), len(vf.inbound_links)))

    connected.sort(key=lambda x: x[1] + x[2], reverse=True)
    for path, ob, ib in connected[:10]:
        report.top_connected.append({
            "path": path,
            "outbound": ob,
            "inbound": ib,
            "total": ob + ib,
        })

    return report
