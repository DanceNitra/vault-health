# ADR-003: Tracer Bullet Development Strategy

**Date:** 2026-06-02
**Status:** Accepted
**Authors:** Rastislav Drahoš & Hermes Agent

## Context

Začíname nový projekt s neistým dopytom. Potrebujeme overiť architektúru
a funkcionalitu čo najrýchlejšie, bez prepadnutia sa do analýzy paralysis.
Štandardný waterfall alebo big-design-up-front by oddialil spätnú väzbu.

## Decision

Použiť **Tracer Bullet** development podľa Pragmatic Programmer (Topic 12):

1. **End-to-end skeleton** — jeden operátor (δ depth) prejde celým stackom:
   `CLI → vault scanner → engine → output`
   - Funkčný za 1 session
   - Overí: CLI framework, scanner výkonnosť, output formátovanie

2. **Iteratívne portovať** zvyšné operátory jeden po druhom:
   - Každý operátor je nezávislý modul
   - Každý má vlastný report typ
   - Pridanie commandu = 3 riadky v CLI

3. **Testy písať súbežne** — nie po fáze, ale paralelne
   - Unit testy pre scanner
   - Smoke test pre CLI

4. **Pre-commit od začiatku** — Google SE princíp:
   - Ruff (lint + format)
   - MyPy (type safety)
   - Základné hooks (whitespace, YAML, large files)

5. **CI od začiatku** — GitHub Actions:
   - Matrix: 3.11, 3.12
   - Stages: ruff → mypy → pytest → smoke

## Consequences

### Positive
+ Funkčný produkt po 1. sessions (Tracer Bullet overený)
+ Architektúra overená na reálnych dátach (6,670 files, 77K wikilinks)
+ Každý commit je potenciálne releasovatelný (continuous delivery)
+ Testy chytili regression pred commitom

### Negative
- Prvý operátor (δ depth) je najjednoduchší — riziko, že komplexnejšie
  operátory odhalia architektonické problémy
- Niektoré rozhodnutia (skórovacie funkcie) sú ad-hoc a budú sa meniť
- Súbežné písanie testov spomaľuje initial prototyping

## Related
- ADR-001: CLI-First Architecture
- ADR-002: Seven Epistemic Operators
- Pragmatic Programmer: Tracer Bullets (Topic 12), DRY (Topic 11)
- Software Engineering at Google: Testing Culture (Chapter 11)
