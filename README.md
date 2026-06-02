# vault-health

Epistemic Calculus CLI — measure and improve your knowledge vault health.

## Installation

```bash
pip install vault-health
```

## Usage

```bash
# Scan a vault and see health report
vault-health scan --path ~/my-obsidian-vault/

# JSON output for piping
vault-health scan --path ~/my-obsidian-vault/ --json
```

## Architecture

```
src/vault_health/
├── cli/         # CLI commands (Typer)
├── engine/      # 7 epistemic operators (pure Python)
├── core/        # Vault scanner, graph builder
└── output/      # Formatters (terminal, JSON)
```

## Development

```bash
uv sync --dev
uv run pytest
uv run vault-health scan --path ~/my-vault/
```

## Books

Built on principles from:
- **The Pragmatic Programmer** — DRY, Tracer Bullets, Decoupling
- **A Philosophy of Software Design** — Deep modules, Info hiding
- **Software Engineering at Google** — Code review, Testing, CI/CD
- **Software Architecture: The Hard Parts** — ADR, Trade-off analysis