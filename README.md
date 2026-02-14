# fastapi-single-process

A blueprint for production-grade backend engineering using FastAPI. This repository serves as a living document of architectural decisions and engineering best practices.

## Development Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Quick Start

1. **Clone and install dependencies:**

```bash
   git clone <repo-url>
   cd fastapi-single-process
   uv sync --group dev
```

2. **Install pre-commit hooks:**

```bash
   uv run pre-commit install
```

3. **Verify setup:**

```bash
   uv run pre-commit run --all-files
```

### IDE Setup

**VS Code (Recommended):**

- Install recommended extensions (prompt appears on first open)
- Workspace settings configure format-on-save and Ruff integration automatically

**Note:** `.vscode/settings.json` contains workspace standards only. Personal preferences (themes, fonts, UI) belong in your User Settings.

**Other IDEs:**

- Use Ruff for formatting and linting
- Line length: 100
- Format on save: Recommended

### Quality Gates

This project uses automated quality enforcement:

- **Ruff** (linting + formatting): Catches bugs, enforces style, modernizes syntax
- **Pre-commit hooks**: Run automatically on `git commit` to block quality issues

**Manual commands:**

```bash
# Run all pre-commit checks
uv run pre-commit run --all-files

# Run specific check
uv run ruff check .
uv run ruff format .

# Skip hooks (use sparingly)
git commit --no-verify
```

## Repository Evolution

We treat the repository history as a narrative, documenting each phase of the setup to maintain a clear trail of architectural intent.

### Initial Setup

The goal was to establish a modern Python environment with deterministic builds.

- **Tooling**: `uv` was chosen for its performance and its ability to replace `pip`, `pip-compile`, and `virtualenv` in a single tool.

- **Initialization**:

```bash
uv init --package --python 3.13 --build-backend hatch
```

### Quality Gates & Defense in Depth

Before a single line of business logic is written, we establish the "rules of engagement." This "shifts left" the burden of code quality, catching errors at the IDE and commit level rather than in CI.

- **Linter/Formatter**: `ruff`(The industry standard for speed and consolidated rulesets).

- **Pre-commit**: Ensures that no "messy" code ever leaves the local environment.

- **IDE Config**: Standardized `.vscode` settings to ensure the team (or your future self) uses the same ruler to measure the code.

```bash
# Add dev dependencies
uv add --group dev pre-commit ruff

# Initialize hooks
uv run pre-commit install
```
