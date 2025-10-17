# Chainguard Deployment Guide

This guide explains how to deploy Aeon Gateway using Chainguard's minimal, secure Python container images.

## Why Chainguard Images?

- **Zero CVEs**: Minimal vulnerability exposure through distroless design
- **Small Size**: Reduced attack surface and faster deployment
- **No Shell**: Runtime image has no shell, preventing shell-based attacks
- **Supply Chain Security**: SBOM and provenance attestations included
- **Regular Updates**: Automated patching and maintenance

## Prerequisites

- Docker with BuildKit enabled (Docker 20.10+)
- Access to Chainguard images (publicly available at `cgr.dev`)

## Quick Start

### Build the Image

```bash
cd aeon-gateway

# Build with BuildKit for optimal caching
docker build -t aeon-gateway:latest .

# Or with explicit BuildKit
DOCKER_BUILDKIT=1 docker build -t aeon-gateway:latest .
```

### Run the Container

```bash
# Basic run
docker run -p 8001:8001 aeon-gateway:latest

# With environment variables
docker run -p 8001:8001 \
  -e AGENTIC_SYSTEM_URL=http://host.docker.internal:8000 \
  aeon-gateway:latest

# With mounted .env file
docker run -p 8001:8001 \
  -v $(pwd)/.env:/opt/app/.env:ro \
  aeon-gateway:latest
```

### Verify Health

```bash
curl http://localhost:8001/health
# Expected: {"status":"healthy","service":"aeon-gateway","version":"0.1.0"}
```

## Multi-Stage Build Architecture

The Dockerfile uses a two-stage approach:

### Stage 1: Builder (python:latest-dev)
- Contains pip, setuptools, and build tools
- Creates isolated virtual environment
- Installs all Python dependencies
- Uses BuildKit cache mounts for faster builds

### Stage 2: Runner (python:latest)
- Minimal distroless image (no shell, no package manager)
- Only contains Python runtime and your application
- Copies pre-built venv from builder stage
- ~10x smaller than standard Python images

## Image Variants

Chainguard provides several Python image variants:

| Image Tag | Use Case | Size | Tools Included |
|-----------|----------|------|----------------|
| `latest` | Production runtime | ~50MB | Python 3.12 only |
| `latest-dev` | Build stage | ~200MB | pip, setuptools, gcc |

## Configuration

### Environment Variables

Set these in your `.env` file or container runtime:

```bash
# Required: URL of INDRA agentic system
AGENTIC_SYSTEM_URL=http://localhost:8000

# Optional: Enable debug logging
LOG_LEVEL=DEBUG

# Optional: Override default port
PORT=8001
```

### Docker Compose

Create `docker-compose.yml` for local development:

```yaml
version: '3.8'

services:
  aeon-gateway:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - AGENTIC_SYSTEM_URL=${AGENTIC_SYSTEM_URL:-http://indra-agent:8000}
    depends_on:
      - indra-agent
    healthcheck:
      test: ["CMD", "/venv/bin/python", "-c", "import httpx; httpx.get('http://localhost:8001/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  indra-agent:
    image: indra-agent:latest
    ports:
      - "8000:8000"
```

Run with:
```bash
docker-compose up
```

## Production Deployment

### Kubernetes Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aeon-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aeon-gateway
  template:
    metadata:
      labels:
        app: aeon-gateway
    spec:
      containers:
      - name: aeon-gateway
        image: aeon-gateway:latest
        ports:
        - containerPort: 8001
        env:
        - name: AGENTIC_SYSTEM_URL
          value: "http://indra-agent-service:8000"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        securityContext:
          runAsNonRoot: true
          runAsUser: 65532  # Chainguard nonroot user
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
---
apiVersion: v1
kind: Service
metadata:
  name: aeon-gateway-service
spec:
  selector:
    app: aeon-gateway
  ports:
  - port: 80
    targetPort: 8001
  type: LoadBalancer
```

### Cloud Run / AWS App Runner

Chainguard images are ideal for serverless container platforms:

**Google Cloud Run:**
```bash
gcloud run deploy aeon-gateway \
  --image gcr.io/your-project/aeon-gateway:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8001
```

**AWS App Runner:**
```bash
aws apprunner create-service \
  --service-name aeon-gateway \
  --source-configuration "{
    \"ImageRepository\": {
      \"ImageIdentifier\": \"your-registry/aeon-gateway:latest\",
      \"ImageRepositoryType\": \"ECR\",
      \"ImageConfiguration\": {\"Port\": \"8001\"}
    }
  }"
```

## Security Best Practices

### 1. Run as Non-Root User

Chainguard images run as user `65532` by default:

```dockerfile
# Already configured in base image
USER 65532:65532
```

### 2. Use Read-Only Root Filesystem

```yaml
# In Kubernetes pod spec
securityContext:
  readOnlyRootFilesystem: true
```

### 3. Scan for Vulnerabilities

```bash
# Use Docker Scout
docker scout cves aeon-gateway:latest

# Use Trivy
trivy image aeon-gateway:latest

# Use Grype
grype aeon-gateway:latest
```

Expected result: Zero or near-zero CVEs due to minimal base image.

### 4. Sign and Verify Images

```bash
# Sign with cosign
cosign sign --key cosign.key aeon-gateway:latest

# Verify signature
cosign verify --key cosign.pub aeon-gateway:latest
```

## Troubleshooting

### Build Fails with "pip not found"

Ensure you're using `python:latest-dev` in the builder stage:
```dockerfile
FROM cgr.dev/chainguard/python:latest-dev AS builder
```

### Health Check Fails

Check that httpx is installed in requirements.txt (used by health check):
```bash
docker run --rm aeon-gateway:latest /venv/bin/pip list | grep httpx
```

### Import Errors at Runtime

Verify that all dependencies are in requirements.txt:
```bash
# Test locally first
pip install -r requirements.txt
python -c "from src.main import app"
```

### Shell Access for Debugging

Runtime image has no shell. For debugging, override entrypoint:
```bash
# Use the -dev variant temporarily
docker run --rm -it --entrypoint /bin/sh \
  cgr.dev/chainguard/python:latest-dev
```

## Performance Optimization

### Build Cache

BuildKit automatically caches pip downloads:
```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    /opt/app/venv/bin/pip install -r requirements.txt
```

### Multi-Platform Builds

Build for both x86 and ARM:
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t aeon-gateway:latest \
  --push .
```

### Layer Optimization

Dependencies are cached separately from code:
- Change requirements.txt → rebuild dependencies layer
- Change src/ → only rebuild code layer

## Migration from Standard Images

If migrating from `python:3.12-slim`:

| Standard Image | Chainguard Equivalent |
|----------------|----------------------|
| `python:3.12` | `cgr.dev/chainguard/python:latest` |
| `python:3.12-slim` | `cgr.dev/chainguard/python:latest` |
| `python:3.12-alpine` | `cgr.dev/chainguard/python:latest` |

Key differences:
- No shell in runtime (use `-dev` for debugging)
- No apt/apk (install everything in builder stage)
- Runs as non-root by default (UID 65532)

## References

- [Chainguard Python Images](https://images.chainguard.dev/directory/image/python/overview)
- [Chainguard Academy - Python Guide](https://edu.chainguard.dev/chainguard/chainguard-images/getting-started/python/)
- [FastAPI Docker Best Practices](https://fastapi.tiangolo.com/deployment/docker/)
- [Docker BuildKit Cache Mounts](https://docs.docker.com/build/cache/)
