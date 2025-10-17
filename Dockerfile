# Multi-stage build for Aeon Gateway using Chainguard Python images
# Provides minimal attack surface, no CVEs, and distroless runtime

# =============================================================================
# Build Stage: Install dependencies in virtual environment
# =============================================================================
FROM cgr.dev/chainguard/python:latest-dev AS builder

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/app

# Create virtual environment
RUN python -m venv /opt/app/venv

# Install dependencies using cache and bind mounts for efficiency
# This approach leverages Docker's BuildKit for faster builds
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    /opt/app/venv/bin/pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Runtime Stage: Minimal distroless image with no shell
# =============================================================================
FROM cgr.dev/chainguard/python:latest AS runner

WORKDIR /opt/app

# Enable unbuffered output for real-time logs
ENV PYTHONUNBUFFERED=1

# Add venv to PATH so Python can find installed packages
ENV PATH="/venv/bin:$PATH"

# Copy virtual environment from builder
COPY --from=builder /opt/app/venv /venv

# Copy application source code
COPY src/ /opt/app/src/
COPY tests/ /opt/app/tests/

# Copy configuration files if needed
COPY pytest.ini /opt/app/pytest.ini

# Expose port 8001 (as configured in main.py)
EXPOSE 8001

# Health check to ensure service is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["/venv/bin/python", "-c", "import httpx; httpx.get('http://localhost:8001/health', timeout=5.0)"]

# Run FastAPI with uvicorn
# Using python -m uvicorn for better compatibility with venv
ENTRYPOINT ["/venv/bin/python", "-m", "uvicorn", "src.main:app"]
CMD ["--host", "0.0.0.0", "--port", "8001"]
