# ADR-002: Seven Epistemic Operators

**Date:** 2026-06-02
**Status:** Accepted
**Authors:** Rastislav Drahoš & Hermes Agent

## Context

Vault health je multidimenzionálny problém. Jedno číslo nestačí — potrebujeme
súbor metrík, ktoré zachytia rôzne aspekty kvality znalostného grafu.
Každá metrika musí byť interpretovateľná a mať jasný target.

## Decision

Definujeme 7 epistemic operators (inšpirované Epistemic Calculus):

| Op | Name | What It Measures | Target |
|----|------|------------------|--------|
| δ | Depth | Avg words/file, proportion deep | >60% deep |
| κ | Connectivity | Avg links/file | >5 avg |
| ρ | Recency | Files updated <30d | <30d stale |
| β | Broken | Broken link ratio | <1% |
| λ | Orphan | Zero inbound ratio | <1% |
| ω | Width | Breadth × depth balance | >20% medium |
| φ | Coherence | Cross-domain link ratio | >20% cross |

Každý operator je:
- **Samostatný modul** v `engine/` (pure Python, žiadne CLI závislosti)
- **Pure function** — `analyze(vault: Vault) -> Report`
- **Report dataclass** s metrikami + score 0.0–1.0

## Consequences

### Positive
+ Modulárna architektúra — ľahko pridať nový operator
+ Každý operator má vlastný report typ (type safety)
+ Score 0-1 umožňuje kombinovaný health index
+ Nezávislé testovanie každého operátora

### Negative
- Skórovacie funkcie sú heuristické (treba kalibráciu na reálnych data)
- Niektoré metriky (φ coherence) sú O(n) aj s optimalizáciou
- Orphan detection je citlivá na to, čo považujeme za "vault file"

### Technical Debt
- Skórovacie thresholdy (targets) su zatiaľ natvrdo v kóde
- φ používa len `domain` frontmatter — nezachytáva topic-based bridging

## Related
- ADR-001: CLI-First Architecture
- Philosophy of SW Design: Deep modules (Chapter 4)
- SE at Google: Measurability (Chapter 8)
