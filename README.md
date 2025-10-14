# Aeon Gateway

**Temporal Bayesian modeling service for personalized health predictions**

Converts causal graphs into biomarker predictions that evolve with new observations.

---

## Quick Start

### For Collaborators (First Time Setup)

**Automated setup** (recommended):
```bash
# Clone repo
git clone https://github.com/Aeon-Bio/aeon-gateway.git
cd aeon-gateway

# Run setup script
bash scripts/setup.sh  # macOS/Linux
# OR
.\scripts\setup.ps1    # Windows PowerShell

# Takes ~2 minutes, installs everything
```

**Manual setup**:
```bash
# 1. Install uv: https://github.com/astral-sh/uv
# 2. Create virtual environment
uv venv
source .venv/bin/activate  # macOS/Linux
# OR .venv\Scripts\activate  # Windows

# 3. Install dependencies
uv pip install -r requirements.txt

# 4. Verify
pytest tests/contracts/ -v
```

See **[docs/deployment/local-development.md](./docs/deployment/local-development.md)** for detailed setup guide.

### For Existing Setup

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR .venv\Scripts\activate  # Windows

# Verify setup (if needed)
python -c "from src.models.gateway import *; print('✓ Models OK')"
pytest tests/contracts/ -v
```

### Run Server

```bash
source .venv/bin/activate  # macOS/Linux
# OR .venv\Scripts\activate  # Windows

# Start gateway (accessible from your network)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Access**:
- Same machine: http://localhost:8000
- Different machine: http://YOUR_IP:8000 (e.g., http://192.168.1.100:8000)

**Endpoints**:
- Health: http://localhost:8000/health
- Interactive docs: http://localhost:8000/docs
- API reference: http://localhost:8000/redoc

### Run Tests

```bash
# All tests
pytest tests/ -v

# Contract tests only
pytest tests/contracts/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Project Structure

```
aeon-gateway/
├── docs/                          # Architecture & specs
│   ├── architecture/
│   │   ├── system-overview.md    ⭐ What we build
│   │   ├── boundaries-and-contracts.md ⭐ Interfaces
│   │   └── technology-stack.md
│   ├── api/
│   │   └── agentic-system-spec.md ⭐ For external team
│   ├── requirements/
│   │   ├── demo-scenario.md      ⭐ SF→LA demo
│   │   └── product-requirements.md
│   ├── testing/
│   │   └── testing-strategy.md   ⭐ Test plan
│   └── planning/
│       └── hackathon-timeline.md ⭐ Implementation timeline
├── src/
│   ├── models/
│   │   └── gateway.py            ✅ Pydantic models
│   ├── main.py                   ✅ FastAPI app (minimal)
│   ├── temporal_model.py         ⏳ TODO: Next priority
│   └── agentic_client.py         ⏳ TODO: After temporal model
├── tests/
│   ├── mocks/
│   │   └── agentic_system.py     ✅ Mock external system
│   ├── contracts/
│   │   └── test_interfaces.py    ✅ 13/13 passing
│   ├── integration/
│   │   └── test_gateway.py       ⏳ TODO: After temporal model
│   └── conftest.py               ✅ Fixtures
├── frontend/
│   └── index.html                  ✅ Demo/reference implementation
├── requirements.txt              ✅ Pinned dependencies
├── pytest.ini                    ✅ Test configuration
├── IMPLEMENTATION_GUIDE.md       ⭐ Step-by-step guide
└── README.md                     ⭐ This file
```

---

## Implementation Status

### ✅ Phase 1: Foundation (Complete)

- [x] Virtual environment (uv)
- [x] Dependencies installed (FastAPI, Pydantic, NetworkX, NumPy, Pandas, pytest)
- [x] Directory structure
- [x] Pydantic models (all interfaces)
- [x] Contract tests (13 passing)
- [x] Mock agentic system
- [x] FastAPI app with health check
- [x] pytest configuration

**Verification**:
```bash
pytest tests/contracts/ -v  # 13 passed ✓
curl http://localhost:8000/health  # {"status":"healthy"} ✓
```

### ⏳ Phase 2: Core Logic (Next)

Priority order:

1. **`src/temporal_model.py`** (40 min)
   - `TemporalModelEngine` class
   - `build_model()`: CausalGraph → NetworkX graph
   - `predict()`: Monte Carlo simulation
   - `_monte_carlo_step()`: Forward propagation

2. **Wire FastAPI** (20 min)
   - Update `src/main.py` `/api/v1/gateway/query` endpoint
   - Integrate MockAgenticSystem
   - Call TemporalModelEngine
   - Return predictions

3. **Integration test** (10 min)
   - `tests/integration/test_gateway.py`
   - `test_sarah_sf_to_la_query()` - MUST PASS

### ✅ Phase 3: Demo Frontend (Complete)

- [x] Reference implementation (index.html)
- [x] Chart.js timeline visualization
- [x] Risk level indicators
- [x] Causal explanations display
- [x] Wired to backend API

**Note**: `frontend/index.html` is a **demo/reference implementation** showing how to integrate with the API. Production UI should be built by your UI team following `docs/api/ui-integration-spec.md`

---

## Key Contracts

### External Agentic System → Gateway

**Endpoint**: `POST /api/v1/causal_discovery`

**Request**:
```json
{
  "request_id": "uuid",
  "user_context": {...},
  "query": {"text": "..."}
}
```

**Response**:
```json
{
  "status": "success",
  "causal_graph": {
    "nodes": [...],
    "edges": [...]
  }
}
```

**Constraints**:
- `effect_size` ∈ [0, 1]
- `temporal_lag_hours` ≥ 0
- All validated by Pydantic

### Gateway → Frontend

**Endpoint**: `POST /api/v1/gateway/query`

**Response**:
```json
{
  "query_id": "uuid",
  "predictions": {
    "CRP": {
      "baseline": 0.7,
      "timeline": [
        {"day": 0, "mean": 0.7, "confidence_interval": [0.65, 0.75], "risk_level": "low"}
      ]
    }
  },
  "causal_graph": {...},
  "explanations": [...]
}
```

---

## Testing Strategy

### Contract Tests (✅ 13 passing)

Verify interface stability:
- Pydantic validation
- Field constraints
- Type safety

**Run**: `pytest tests/contracts/ -v`

### Integration Tests (⏳ Next)

End-to-end with mocked external system:
- Sarah's SF→LA query
- Predictions in reasonable range
- Graph structure correct

**Run**: `pytest tests/integration/ -v`

### Pre-Demo Checklist

```bash
# 1. All tests pass
pytest tests/ -v
# Expected: All green ✓

# 2. Server starts
uvicorn src.main:app --reload &
sleep 2

# 3. Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy"} ✓

# 4. Demo query (after temporal model implemented)
curl -X POST http://localhost:8000/api/v1/gateway/query \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/sarah_query.json
# Expected: Predictions for CRP, IL-6 ✓

# Kill server
pkill -f uvicorn
```

---

## Next Steps

### Immediate (Phase 2)

1. **Implement `src/temporal_model.py`**
   - Copy from `docs/architecture/system-overview.md`
   - Test with manual graph building
   - Verify predictions are reasonable

2. **Wire FastAPI query endpoint**
   - Import MockAgenticSystem
   - Call TemporalModelEngine
   - Return GatewayResponse

3. **Write integration test**
   - `test_sarah_sf_to_la_query()`
   - Verify CRP: 0.7 → ~2.4
   - MUST pass before demo

### After Core Logic

4. **Frontend timeline visualization**
   - Simple HTML + Chart.js
   - Display predictions
   - Show causal graph

5. **Demo rehearsal**
   - Follow script in `docs/requirements/demo-scenario.md`
   - Time it (< 5 minutes)
   - Backup screenshots

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| API Framework | FastAPI | 0.119.0 |
| Validation | Pydantic | 2.12.2 |
| Graph Analysis | NetworkX | 3.5 |
| Numerical | NumPy | 2.3.3 |
| Time Series | Pandas | 2.3.3 |
| HTTP Client | httpx | 0.28.1 |
| Server | Uvicorn | 0.37.0 |
| Testing | pytest | 8.4.2 |
| Package Manager | uv | latest |

---

## Documentation

### For Implementation
- **[IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)** - Complete implementation guide
- **[docs/architecture/system-overview.md](./docs/architecture/system-overview.md)** - System architecture
- **[docs/architecture/boundaries-and-contracts.md](./docs/architecture/boundaries-and-contracts.md)** - Interface specs
- **[docs/testing/testing-strategy.md](./docs/testing/testing-strategy.md)** - Testing approach
- **[docs/requirements/demo-scenario.md](./docs/requirements/demo-scenario.md)** - Demo data & script

### For Integration Partners
- **[docs/api/ui-integration-spec.md](./docs/api/ui-integration-spec.md)** - ⭐ UI team spec
- **[docs/api/agentic-system-spec.md](./docs/api/agentic-system-spec.md)** - ⭐ Agentic system team spec

---

## Success Criteria

### Technical

- [x] Models defined and validated
- [x] Contract tests pass (13/13)
- [x] Server starts without errors
- [ ] Temporal model implemented
- [ ] Integration test passes
- [ ] Predictions reasonable (CRP: 0.7 → 2.4)

### Demo

- [ ] Query completes in < 3s
- [ ] Timeline visualization works
- [ ] No errors during demo
- [ ] Judges understand the innovation

---

## Contributing

This is a hackathon project. Focus on:
1. Implementing temporal model (next priority)
2. Passing integration tests
3. Shipping working demo

Don't over-engineer. Ship it. 🚀
