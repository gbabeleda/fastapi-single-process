# fastapi-single-process

A blueprint for production-grade backend engineering using FastAPI. This repository serves as a living document of architectural decisions and engineering best practices.

## Development Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- [Docker & Docker Compose](https://docs.docker.com/get-started/get-docker/)

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

## Running the Application

This project supports multiple deployment patterns depending on the development context.

### Local Development

Best for rapid iteration and debugging

```bash
# Start the development server
uv run uvicorn fastapi_single_process.main:app --reload
```

- **Interactive Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/health`

### Docker Compose

Best for testing the containerized environment

```bash
# Start services using latest version of the image
docker compose up --build

# Stop all services
docker compose down
```

### Production Build (Manual)

Best for validating image size and security

```bash
# Build the production image
docker build -t fastapi-single-process-latest .

# Run the container
docker run -p 8000:8000 fastapi-single-process:latest

# Stop the container
docker ps # Find the container ID
docker stop <container-id>
```

## Docker Architecture

### Multi-Stage Build Strategy

The `Dockerfile` implements a two-stage process to ensure the production image is lean and secure

1. **Builder Stage**: Uses `ghcr.io/astral-sh/uv` to resolve dependencies and build a Python wheel. This stage contains build tools and compilers that are **not** needed at runtime.
2. **Runtime Stage**: A minimal`python:slim` image that only installs the pre-built wheel.

### Key Benefits

- **Security**: No build tools are present in the final image, reducing the attack surface.
- Size: Final image is ~300 MB vs ~1GB+ for a standard single-stage build.
- Non-Root User: The application runs as `appuser` rather than `root` to prevent privilege escalation.

### Build Context & Optimization

A strict `.dockerignore` strategy ensures that only necessary source code is sent to the Docker daemon. We exclude `.git`, `tests/`, and local dev artifacts to keep build times fast and prevent secret leakage.

## Database

### Setup

**First time setup:**

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Start database
docker compose up -d --build

# 3. Run migrations
uv run alembic upgrade head
```

**Health check:**

```bash
curl http://localhost:8000/api/v1/health
# {"status":"healthy","database":"connected","last_check":"2026-02-18T..."}
```

### Daily Workflow

**Creating a new model:**

1. Add model to `src/invested_fastapi/db/models/`
2. Re-export in `src/invested_fastapi/db/models/__init__.py`
3. Generate migration:

```bash
   uv run alembic revision --autogenerate -m "add user table"
```

4. Review the generated file in `alembic/versions/`
5. Apply migration:

```bash
   uv run alembic upgrade head
```

**Common commands:**

```bash
# Check current migration
uv run alembic current

# View migration history
uv run alembic history

# Rollback one migration
uv run alembic downgrade -1

# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up postgres -d
uv run alembic upgrade head
```

### Troubleshooting

**"Connection refused" error:**

- Ensure postgres is running: `docker compose ps`
- Check `APP_ENVIRONMENT=docker` is set in `docker-compose.yaml`

**"Table does not exist" error:**

- Run migrations: `uv run alembic upgrade head`
- Check current state: `uv run alembic current`

**Migration conflicts:**

- Check pending migrations: `uv run alembic history`
- Coordinate with team before running `downgrade`

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

### Application Skeleton & Infrastructure

This phase transforms the repository from a configuration scaffold into a functional API with a production-ready directory structure.

- **Configuration**:
  - Implemented a `Settings` singleton using `BaseSettings` for robust environment and variable validation.
  - Used `@cache` to ensure settings are loaded once, preventing unnecessary I/O during the app lifecycle.
- **Modular Routing & Versioning**:
  - Adopted a versioned routing strategy `api/v1/router.py` to allow for breaking changes in the future without disrupting existing clients.
  - Included `/health` endpoint to support infrastructure health checks.
- **Domain Layering**:
  - Scaffolding was created to enforce a clean separation between database, data validation, and business logic
  - The `main.py` entrypoint remains "thin", focusing solely on app initialization and mounting routers

### Containerization & Orchestration

Established a production-grade container strategy focused on security and build efficiency.

- **Multi-Stage Dockerfile**: Implemented a builder/runtime split to produce a minimal production artifact.
- **Docker Compose**: Provided a standardized development entry point
- **Security Hardening**: Configured the runtime to use a non-privileged `appuser` and strictly ignored sensitive local files via `.dockeringore`

### Database Layer

This project uses async SQLAlchemy 2.0 with Alembic migrations, configured entirely through `pyproject.toml` following modern Python packaging standards (PEP 621).

**Key Features:**

- Async-first architecture for optimal FastAPI concurrency
- Timezone-aware datetime fields by default
- Environment-aware database URL handling (Docker vs host execution)
- Connection pooling with configurable parameters
- Pure `pyproject.toml` configuration (no `alembic.ini`)

#### Environment-Aware Configuration

The database URL automatically adjusts based on execution context:

| Environment  | Database URL     | Use Case                           |
| ------------ | ---------------- | ---------------------------------- |
| `local`      | `localhost:5445` | Running Alembic migrations on host |
| `docker`     | `postgres:5432`  | FastAPI app in container           |
| `production` | `postgres:5432`  | Production deployment              |

**How it works:**

The `adjust_db_url()` model validator in `config.py` detects the execution environment and modifies the connection URL accordingly. This allows the same configuration to work seamlessly across different contexts without manual URL changes.

**Port mapping:** Docker Compose maps `5445:5432` so host machines can access the containerized database at `localhost:5445` while containers use internal networking at `postgres:5432`.

#### Why pyproject.toml Over alembic.ini?

**Modern Python packaging (PEP 621)** consolidates all project configuration in `pyproject.toml`. Using `alembic.ini` scatters configuration across files and requires maintaining multiple sources of truth.

**Benefits:**

- Single configuration file for the entire project
- Version control is simpler (one file to track)
- No confusion about which config file to edit
- Follows Python ecosystem direction

**Trade-off:** Slightly less common (most Alembic tutorials use `alembic.ini`), but the pattern is well-documented and future-proof.

#### Why Environment-Based URL Adjustment?

**The problem:** Docker service names (`postgres:5432`) only resolve inside containers. Host machines can't use them directly.

**The solution:** Detect execution context and adjust URLs automatically:

- Host machine (running Alembic): Use `localhost:5445`
- Docker container (running app): Use `postgres:5432`

**Alternative considered:** Maintain separate config files for Docker vs host. **Rejected because:** Manual switching is error-prone and violates DRY principles.
