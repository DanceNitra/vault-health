# vault-health

[![CI](https://github.com/DanceNitra/vault-health/actions/workflows/ci.yml/badge.svg)](https://github.com/DanceNitra/vault-health/actions/workflows/ci.yml)

**Epistemic Calculus CLI** — measure and improve your knowledge vault health.

Built as a Tracer Bullet from 4 software engineering books.

## Installation

```bash
pip install vault-health
```

## Usage

```bash
# Scan a vault and see health report
vh --path ~/my-obsidian-vault/

# JSON output for piping
vh --path ~/my-obsidian-vault/ --json
```

## Architecture

```
src/vault_health/
├── cli/         # CLI commands (Typer)
├── engine/      # 7 epistemic operators (pure Python)
├── core/        # Vault scanner, graph builder
└── output/      # Formatters (terminal, JSON)
```

## Operators

| Operator | Metric | Target |
|----------|--------|--------|
| 🟢 δ | Depth (avg words/file) | >60% deep |
| 🔵 κ | Connectivity (links/file) | >5 avg |
| 🟡 ρ | Recency (updated files) | <30d |
| 🔴 β | Broken link ratio | <1% |
| 🟣 λ | Orphan ratio | <1% |
| 🟠 ω | Width (breadth/depth balance) | >40% |
| ⚪ φ | Coherence (bridge quality) | >0.8 |

## Development

```bash
uv sync --dev
uv run pytest
vh --path ~/my-vault/
```

Built on principles from:
- **The Pragmatic Programmer** — DRY, Tracer Bullets, Decoupling
- **A Philosophy of Software Design** — Deep modules, Info hiding
- **Software Engineering at Google** — Code review, Testing, CI/CD
- **Software Architecture: The Hard Parts** — ADR, Trade-off analysis
