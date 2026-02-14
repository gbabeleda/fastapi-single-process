# syntax=docker/dockerfile:1
# Enable BuildKit features (cache mounts, bind mounts) for faster and cleaner builds

# Build Stage: Resolve dependencies and build wheel
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# uv configuration:
# - compile bytecode for faster startup
# - avoid hardlinks across layers
# - exclude development dependencies
# - rely on system python provided by base image
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0

# Change the working directory to the app directory
WORKDIR /app

# Install dependencies in a dedicated layer before copying source code.
# This maximizes Docker layer cache reuse since dependency definitions
# change far less frequently than application code.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy application source after dependencies to avoid cache invalidation
COPY . .

# Build a wheel for the application
# The wheel is installed in the runtime image to keep it minimal
RUN uv build --wheel --out-dir /dist

# Runtime Stage: Minimal production image
FROM python:3.13-slim-bookworm

# Create non-root user for security
RUN groupadd --system --gid 999 appuser && \
    useradd --system --gid 999 --uid 999 --create-home appuser

WORKDIR /app

# Install only the pre-built wheel using system pip.
# This avoids shipping build tools and uv in the final image.
COPY --from=builder /dist/*.whl .
RUN pip install --no-cache-dir *.whl && rm *.whl

# Drop privileges for runtime
USER appuser

# Expose port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "fastapi_single_process.main:app", "--host", "0.0.0.0", "--port", "8000"]
