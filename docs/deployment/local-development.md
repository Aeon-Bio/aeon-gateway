# Local Development Setup

## For: Collaborators (UI Team, Agentic System Team)

**Purpose**: Get the Aeon Gateway running locally to develop and test your integration

---

## Quick Start (5 minutes)

### Prerequisites

- Python 3.10+ ([download](https://www.python.org/downloads/))
- Git ([download](https://git-scm.com/downloads))
- `uv` package manager ([install](https://github.com/astral-sh/uv))

**Install uv** (if not already installed):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/Aeon-Bio/aeon-gateway.git
cd aeon-gateway

# 2. Create virtual environment
uv venv

# 3. Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# 4. Install dependencies
uv pip install -r requirements.txt

# 5. Verify installation
python -c "from src.models.gateway import *; print('✓ Setup complete')"
pytest tests/contracts/ -v
# Expected: 13 passed ✓

# 6. Start the server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Test It Works

Open a new terminal:
```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"aeon-gateway","version":"0.1.0"}
```

**Gateway is now running!** 🚀

---

## Accessing from Your Application

### Same Machine

Your app connects to:
```
http://localhost:8000
```

### Different Machine (Same Network)

**On gateway machine**, find IP address:
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig

# Example output: 192.168.1.100
```

**On your app machine**, connect to:
```
http://192.168.1.100:8000
```

**Note**: Gateway must be started with `--host 0.0.0.0` (not `127.0.0.1`)

---

## Testing Your Integration

### 1. For UI Developers

**Test query endpoint**:
```bash
curl -X POST http://localhost:8000/api/v1/gateway/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_context": {
      "user_id": "test_user",
      "genetics": {"APOE": "e3/e3"},
      "current_biomarkers": {"CRP": 0.7},
      "location_history": [
        {"city": "San Francisco", "state": "CA", "start_date": "2023-01-01", "end_date": "2024-01-01"},
        {"city": "Los Angeles", "state": "CA", "start_date": "2024-01-01", "end_date": null}
      ]
    },
    "query": {
      "text": "How will my inflammation markers change in LA?"
    }
  }'
```

**Expected**: JSON response with predictions, timeline, and risk levels

**View demo UI**:
```bash
open frontend/index.html
# Click "Run Prediction" button
```

See `docs/api/ui-integration-spec.md` for full API reference.

### 2. For Agentic System Developers

Currently, the gateway uses a **mock agentic system** (`tests/mocks/agentic_system.py`).

**To integrate your real system**:

1. **Deploy your agentic system** on accessible URL (e.g., `http://localhost:8001`)

2. **Create client** (`src/agentic_client.py`):
```python
import httpx
from src.models.gateway import AgenticSystemResponse, QueryRequest

class AgenticSystemClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def query(self, request: QueryRequest) -> AgenticSystemResponse:
        response = await self.client.post(
            f"{self.base_url}/api/v1/causal_discovery",
            json=request.model_dump()
        )
        response.raise_for_status()
        return AgenticSystemResponse(**response.json())
```

3. **Update gateway** (`src/main.py` line 74):
```python
# BEFORE (mock):
from tests.mocks.agentic_system import MockAgenticSystem
agentic_system = MockAgenticSystem()

# AFTER (real):
from src.agentic_client import AgenticSystemClient
import os
agentic_system = AgenticSystemClient(
    base_url=os.getenv("AGENTIC_SYSTEM_URL", "http://localhost:8001")
)
```

4. **Set environment variable**:
```bash
export AGENTIC_SYSTEM_URL=http://localhost:8001
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Test your integration**:
```bash
# Gateway should now forward requests to your system
curl -X POST http://localhost:8000/api/v1/gateway/query \
  -H "Content-Type: application/json" \
  -d '{"user_context": {...}, "query": {...}}'
```

See `docs/api/agentic-system-spec.md` for required endpoint spec.

---

## Development Workflow

### Running Tests

```bash
# All tests (13 contract + 4 integration)
pytest tests/ -v

# Only contract tests (fast, no integration)
pytest tests/contracts/ -v

# Only integration tests
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing
```

**All tests should pass before integrating!**

### Auto-Reload

The server automatically reloads when you change code (via `--reload` flag).

**Files that trigger reload**:
- `src/*.py` (gateway code)
- `tests/*.py` (test code)

**Files that DON'T reload**:
- `frontend/index.html`
- `docs/*.md`
- `requirements.txt`

### Logs

**View server logs**:
```bash
# Terminal where uvicorn is running shows all requests
INFO:     127.0.0.1:54321 - "POST /api/v1/gateway/query HTTP/1.1" 200 OK
```

**Increase verbosity**:
```bash
uvicorn src.main:app --reload --log-level debug
```

### Stopping the Server

```bash
# Press Ctrl+C in terminal
^C
INFO:     Shutting down
INFO:     Finished server process
```

---

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'src'`

**Solution**: Activate virtual environment
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Issue: `Address already in use`

**Solution**: Port 8000 is taken
```bash
# Option 1: Find and kill process using port 8000
lsof -ti:8000 | xargs kill  # macOS/Linux
netstat -ano | findstr :8000  # Windows (then kill PID)

# Option 2: Use different port
uvicorn src.main:app --reload --port 8001
```

### Issue: `CORS error` from browser

**Solution**: Gateway has CORS enabled for all origins (line 22-28 in `src/main.py`)

If still blocked, check browser console and ensure:
- Using correct URL (`http://localhost:8000`, not `https`)
- Gateway is running
- Request has `Content-Type: application/json` header

### Issue: Tests fail with import errors

**Solution**: Install test dependencies
```bash
uv pip install -r requirements.txt
```

### Issue: `422 Validation Error` when calling API

**Solution**: Check request format

Common mistakes:
- Negative biomarker values (must be ≥ 0)
- Missing required fields (`user_context`, `query`)
- Incorrect field types (string vs number)

**Debug**:
```bash
curl -X POST http://localhost:8000/api/v1/gateway/query \
  -H "Content-Type: application/json" \
  -d '{...}' | python -m json.tool
```

---

## Docker Setup (Alternative)

**Create Dockerfile**:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy source
COPY src/ src/
COPY tests/ tests/

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run**:
```bash
# Build image
docker build -t aeon-gateway .

# Run container
docker run -p 8000:8000 aeon-gateway

# Access at http://localhost:8000
```

**With environment variables**:
```bash
docker run -p 8000:8000 \
  -e AGENTIC_SYSTEM_URL=http://host.docker.internal:8001 \
  aeon-gateway
```

---

## Network Configuration

### Firewall Rules

If collaborators can't connect, ensure port 8000 is open:

**macOS**:
```bash
# Check firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Allow Python (if blocked)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/python3
```

**Linux (ufw)**:
```bash
sudo ufw allow 8000/tcp
```

**Windows**:
```powershell
# Add firewall rule
New-NetFirewallRule -DisplayName "Aeon Gateway" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Cloud Deployment (Optional)

For remote collaboration, deploy to cloud:

**Render.com** (Free tier):
1. Fork repo to your GitHub
2. Go to [render.com](https://render.com)
3. New Web Service → Connect repo
4. Build command: `pip install uv && uv pip install -r requirements.txt`
5. Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
6. Get public URL: `https://aeon-gateway-xyz.onrender.com`

**Railway.app** (Free tier):
1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Auto-detects Python, uses `requirements.txt`
4. Get public URL

**Fly.io**:
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy

# Get URL
fly status
```

---

## Environment Variables

Create `.env` file (optional):
```bash
# Agentic system URL
AGENTIC_SYSTEM_URL=http://localhost:8001

# Server config
PORT=8000
LOG_LEVEL=info

# Future: Auth
# JWT_SECRET=your-secret-key
```

**Load with**:
```bash
pip install python-dotenv

# In src/main.py:
from dotenv import load_dotenv
load_dotenv()
```

---

## API Documentation

Once server is running, view interactive docs:

**Swagger UI**: http://localhost:8000/docs
- Interactive API explorer
- Try requests in browser
- See request/response schemas

**ReDoc**: http://localhost:8000/redoc
- Cleaner documentation view
- Easier to read

---

## Performance Monitoring

**Check response times**:
```bash
# Using httpie (pip install httpie)
http POST localhost:8000/api/v1/gateway/query < test_query.json

# Shows request time at bottom
```

**Expected performance**:
- Health check: <50ms
- Query endpoint: 500ms - 2s (depends on mock vs real agentic system)

**Add timing logs** (optional):
```python
# In src/main.py
import time

@app.post("/api/v1/gateway/query")
async def process_query(request: QueryRequest):
    start = time.time()
    # ... process request ...
    duration = time.time() - start
    print(f"Query processed in {duration:.2f}s")
    return response
```

---

## Getting Help

**Gateway issues**:
1. Check logs in terminal where uvicorn is running
2. Run tests: `pytest tests/ -v`
3. Check `/health` endpoint: `curl localhost:8000/health`

**Integration issues**:
- UI Team: See `docs/api/ui-integration-spec.md`
- Agentic System Team: See `docs/api/agentic-system-spec.md`

**GitHub Issues**: https://github.com/Aeon-Bio/aeon-gateway/issues

---

## Checklist for Collaborators

### UI Developers
- [ ] Gateway running on `http://localhost:8000`
- [ ] Can access `/health` endpoint
- [ ] Can POST to `/api/v1/gateway/query`
- [ ] Receive JSON response with predictions
- [ ] Demo frontend works (`frontend/index.html`)

### Agentic System Developers
- [ ] Gateway running and accessible
- [ ] Understand required endpoint: `POST /api/v1/causal_discovery`
- [ ] Reviewed `docs/api/agentic-system-spec.md`
- [ ] Contract tests pass: `pytest tests/contracts/ -v`
- [ ] Can send test request to gateway

### Both Teams
- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed (`uv pip install -r requirements.txt`)
- [ ] All tests passing (17/17)
- [ ] Can make requests to gateway from your code

---

## Version Info

**Current Version**: 0.1.0

**What's implemented**:
- ✅ `/health` - Health check
- ✅ `/api/v1/gateway/query` - Query predictions
- ❌ `/api/v1/gateway/update_observation` - Not yet (v0.2.0)
- ❌ Authentication - Not yet (v0.3.0)

**Dependencies**:
- FastAPI 0.119.0
- Pydantic 2.12.2
- NetworkX 3.5
- NumPy 2.3.3
- Pandas 2.3.3

See `requirements.txt` for full list.

---

## Next Steps

1. **UI Team**: Follow `docs/api/ui-integration-spec.md` to build your interface
2. **Agentic System Team**: Follow `docs/api/agentic-system-spec.md` to implement your endpoint
3. **Both**: Test integration end-to-end with real data

**Questions?** Open an issue on GitHub.
