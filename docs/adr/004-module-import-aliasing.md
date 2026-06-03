# ADR-004: Module Import Aliasing for CLI Commands

**Date:** 2026-06-02
**Status:** Accepted
**Authors:** Rastislav Drahoš & Hermes Agent

## Context

Pri pridávaní CLI commandov pre β (broken) a λ (orphan) operátory sme narazili
na Python import konflikt: command funkcia `broken()` shadowovala modul `broken.py`.
Rovnaký problém by nastal pre `orphan()`.

```python
# Problem: broken je funkcia AJ modul
from ..engine import broken       # ✅ modul
from ..engine import broken as _   # ❌ neexistuje v čase definície

@app.command()
def broken(path): ...              # shadows modul broken
report_obj = broken.analyze(vault) # AttributeError: 'function' object has no attribute 'analyze'
```

## Decision

Importovať enginy s aliasom na module úrovni:

```python
from ..engine import broken as broken_engine
from ..engine import orphan as orphan_engine
```

**Nie** inline importy (PEP 8: imports at top), **nie** renaming command funkcií
(CLI API by bolo menej konzistentné), **nie** `importlib` (zbytočne komplexné).

## Consequences

### Positive
+ Jasné oddelenie CLI vrstvy od engine vrstvy
+ Konzistentný pattern pre všetkých 7 operátorov
+ type checker (mypy, pyright) správne rozpozná modul vs function

### Negative
- Mená sú dlhšie (`broken_engine.analyze()` namiesto `broken.analyze()`)
- Potenciálne mätúce pre nových prispievateľov

### Not Considered
- Zmena názvu modulov (broken → broken_op) — zbytočne komplikuje adresárovú štruktúru

## Related
- ADR-002: Seven Epistemic Operators
- Pragmatic Programmer: DRY (Topic 11) — opak, toto je zámerné pomenovanie
- Python PEP 8: Imports
