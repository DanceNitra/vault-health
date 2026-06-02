# ADR-001: CLI-First Architecture

**Date:** 2026-06-02
**Status:** Accepted
**Authors:** Rastislav Drahoš & Hermes Agent

## Context
Potrebujeme nástroj na health-check markdown vaultov (Obsidian, Logseq, custom).
Cieľ: čo najrýchlejšie overiť, či je o túto funkcionalitu záujem.

## Decision
CLI-first, web dashboard v Phase 2.

- **engine/** je samostatná knižnica (žiadne CLI závislosti)
- **CLI** je tenká vrstva nad enginom
- **backend** a **frontend** (Phase 2) budú v tom istom monorepe

## Consequences

### Positive
+ Rýchlejší time-to-market (týždne, nie mesiace)
+ Žiadne serverové náklady v Phase 1
+ API design overený na reálnych používateľoch pred web buildom
+ Jednoduché testovanie (lokálne, bez infraštruktúry)

### Negative
- Web bude vyžadovať definovanie API kontraktu medzi CLI a backendom
- CLI distribúcia (PyPI) je menej známa ako web
- Niektorí používatelia uprednostnia web UI pred terminálom

## Related
- [[Build Plan — SBaaS MVP v1]]
- [[Software Development Roadmap — 4 knižné princípy v praxi]]
- Pragmatic Programmer: Tracer Bullets (Topic 12)
- Architecture Hard Parts: Single Quantum (Chapter 2)
