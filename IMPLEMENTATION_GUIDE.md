# Aeon Gateway Implementation Guide

## What We Built: Principled Documentation

### 1. Architecture (Focused, No Fragmentation)

**File**: `docs/architecture/system-overview.md`

**What it defines**:
- Our responsibility: Temporal Bayesian modeling
- External system's responsibility: INDRA querying
- Clear interface boundary
- Complete implementation code (copy-paste ready)

**What it excludes**:
- No aspirational "multi-agent" complexity
- No agent orchestration we don't need
- No INDRA code (that's external)

### 2. Interface Contracts (Test-Driven)

**File**: `docs/architecture/boundaries-and-contracts.md`

**What it defines**:
- JSON schemas for all interfaces
- Pydantic models (type-safe)
- Required vs optional fields
- Validation rules with examples

**File**: `docs/api/agentic-system-spec.md`

**For**: External agentic system developer

**Defines**:
- Exact endpoint spec
- Request/response formats
- Field constraints (effect_size ∈ [0,1])
- Example queries

### 3. Testing Strategy (Fast Feedback)

**File**: `docs/testing/testing-strategy.md`

**Defines**:
- 10 tests in 25 minutes
- Contract tests (verify interfaces)
- Mock agentic system (hardcoded graphs)
- Integration test (Sarah's SF→LA scenario)
- Pre-demo checklist

**Philosophy**: Test boundaries, not exhaustively

### 4. Implementation Timeline

**File**: `docs/planning/hackathon-timeline.md`

**150-minute breakdown**:
- Phase 1: Foundation (30 min) - FastAPI + models
- Phase 2: Graph Engine (40 min) - NetworkX + Monte Carlo
- Phase 3: API Endpoints (20 min) - query, predict
- Phase 4: Frontend (40 min) - Timeline viz
- Phase 5: Polish (20 min) - Demo script

### 5. Product Context

**File**: `docs/requirements/product-requirements.md`

- User stories
- Competitive analysis
- TAM narrative ($350B precision medicine)
- Success metrics

**File**: `docs/requirements/demo-scenario.md`

- Sarah Chen character (GSTM1 null, GSTP1 Val/Val)
- SF→LA PM2.5 data (7.8 → 34.5 µg/m³)
- Expected predictions (CRP: 0.7 → 2.4)
- 5-minute demo script

---

## Core Principles (How We Eliminated Fragmentation)

### 1. Single Responsibility

**Gateway**: Temporal modeling only
- Input: Causal graph (from agentic system)
- Output: Biomarker predictions over time
- No NLP, no INDRA, no biomarker resolution

### 2. Clear Boundaries

```
┌─────────────────┐
│   Frontend UI   │  Our code: Timeline viz
└────────┬────────┘
         │ HTTP/JSON
┌────────▼────────┐
│  Aeon Gateway   │  Our code: Temporal model
└────────┬────────┘
         │ HTTP/JSON
┌────────▼────────┐
│ Agentic System  │  External: INDRA queries
└─────────────────┘
```

### 3. Contract-First

- Define Pydantic models BEFORE implementation
- Write contract tests BEFORE integration
- Mock external systems BEFORE they exist

### 4. Test-Driven Shipping

```
Write test → Implement → Verify → Ship
```

Not:
```
Build everything → Hope it works → Debug for hours
```

---

## Critical Files to Implement

### Priority 1: Models (15 min)

```
src/
└── models/
    └── gateway.py  # Pydantic models from boundaries-and-contracts.md
```

**Copy from**: `docs/architecture/boundaries-and-contracts.md`

**Models**:
- `UserContext`
- `QueryRequest`
- `CausalGraph`, `CausalNode`, `CausalEdge`
- `AgenticSystemResponse`
- `PredictionTimeline`
- `GatewayResponse`

### Priority 2: Mock Agentic System (10 min)

```
tests/
└── mocks/
    └── agentic_system.py  # Returns hardcoded graphs
```

**Copy from**: `docs/testing/testing-strategy.md`

**Key method**: `query(request) → AgenticSystemResponse`

### Priority 3: Temporal Model (40 min)

```
src/
└── temporal_model.py  # NetworkX + Monte Carlo simulation
```

**Copy from**: `docs/architecture/system-overview.md`

**Classes**:
- `TemporalModelEngine`
  - `build_model(graph, genetics, baseline)`
  - `predict(model, env_changes, horizon=90)`
  - `_monte_carlo_step(model, env_changes, day)`

### Priority 4: API Endpoints (20 min)

```
src/
└── main.py  # FastAPI app
```

**Endpoints**:
- `POST /api/v1/gateway/query`
- `GET /health`

### Priority 5: Contract Tests (15 min)

```
tests/
├── contracts/
│   └── test_interfaces.py  # Pydantic validation
└── integration/
    └── test_gateway.py  # End-to-end with mock
```

**Copy from**: `docs/testing/testing-strategy.md`

---

## Implementation Checklist

### Phase 1: Models & Validation (25 min)

- [ ] Create `src/models/gateway.py`
- [ ] Define all Pydantic models
- [ ] Add validators (effect_size ∈ [0,1], etc.)
- [ ] Run: `python -c "from models.gateway import *"`  # Verify imports

### Phase 2: Testing Infrastructure (25 min)

- [ ] Create `tests/mocks/agentic_system.py`
- [ ] Implement `MockAgenticSystem.query()`
- [ ] Create `tests/contracts/test_interfaces.py`
- [ ] Run: `pytest tests/contracts/ -v`  # Should pass

### Phase 3: Core Logic (40 min)

- [ ] Create `src/temporal_model.py`
- [ ] Implement `TemporalModelEngine.build_model()`
- [ ] Implement `TemporalModelEngine.predict()`
- [ ] Implement `_monte_carlo_step()`
- [ ] Test manually: Build graph, run predict, check output range

### Phase 4: API Layer (20 min)

- [ ] Create `src/main.py`
- [ ] FastAPI app with `/api/v1/gateway/query`
- [ ] Wire up: Request → Mock Agentic → Temporal Model → Response
- [ ] Test: `curl http://localhost:8000/api/v1/gateway/query`

### Phase 5: Integration Test (10 min)

- [ ] Create `tests/integration/test_gateway.py`
- [ ] Write `test_sarah_sf_to_la_query()`
- [ ] Run: `pytest tests/integration/ -v`  # MUST pass

### Phase 6: Frontend (40 min)

- [ ] Create `frontend/index.html`
- [ ] Add Chart.js for timeline
- [ ] Add D3.js for graph (optional if time tight)
- [ ] Wire to backend: `POST /api/v1/gateway/query`
- [ ] Test end-to-end in browser

### Phase 7: Demo Prep (10 min)

- [ ] Practice demo script (docs/requirements/demo-scenario.md)
- [ ] Run pre-demo checklist
- [ ] Verify all tests pass
- [ ] Take screenshots as backup

---

## Pre-Demo Checklist (Run 15 min before)

```bash
# 1. All tests pass
pytest tests/ -v
# Expected: 10 passed

# 2. Sarah's scenario works
pytest tests/integration/test_gateway.py::test_sarah_sf_to_la_query -v -s
# Expected: PASS, CRP predictions 0.7 → ~2.4

# 3. Server starts
uvicorn src.main:app --reload &
sleep 2

# 4. Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# 5. Demo query
curl -X POST http://localhost:8000/api/v1/gateway/query \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/sarah_query.json
# Expected: JSON response with predictions

# 6. Frontend loads
open http://localhost:8080
# Expected: Timeline and graph render

# Kill server
pkill -f uvicorn
```

If ANY step fails → **Fix before demo**

---

## Directory Structure (Final)

```
aeon-gateway/
├── docs/
│   ├── README.md
│   ├── architecture/
│   │   ├── system-overview.md          ⭐ Core architecture
│   │   ├── boundaries-and-contracts.md  ⭐ Interface specs
│   │   └── technology-stack.md
│   ├── api/
│   │   ├── agentic-system-spec.md      ⭐ For external team
│   │   └── indra-integration.md         (Reference only)
│   ├── requirements/
│   │   ├── product-requirements.md
│   │   └── demo-scenario.md            ⭐ Demo data
│   ├── testing/
│   │   └── testing-strategy.md         ⭐ Test plan
│   └── planning/
│       └── hackathon-timeline.md       ⭐ 150-min breakdown
├── src/
│   ├── models/
│   │   └── gateway.py                  # Pydantic models
│   ├── temporal_model.py               # Core logic
│   ├── main.py                         # FastAPI app
│   └── agentic_client.py               # HTTP client (mocked for hackathon)
├── tests/
│   ├── mocks/
│   │   └── agentic_system.py           # Hardcoded responses
│   ├── contracts/
│   │   └── test_interfaces.py          # Pydantic validation
│   ├── integration/
│   │   └── test_gateway.py             # End-to-end
│   └── conftest.py                     # Fixtures
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── requirements.txt
├── IMPLEMENTATION_GUIDE.md             ⭐ This file
└── README.md
```

---

## What Success Looks Like

### Technical Success
- ✅ 10/10 tests pass
- ✅ Sarah's query returns predictions in < 3s
- ✅ CRP prediction: 0.7 → 2.4 (±0.3) at day 90
- ✅ UI renders timeline and graph
- ✅ No errors during demo

### Demo Success
- ✅ Query completes live on stage
- ✅ Judges see causal graph with INDRA evidence
- ✅ Predictions match expected trajectory
- ✅ Explanations are clear
- ✅ TAM narrative resonates

### Post-Demo Success
- ✅ Judges ask follow-up questions
- ✅ Code is clean enough to open-source
- ✅ External agentic team can integrate using our spec
- ✅ We can iterate quickly post-hackathon

---

## Key Files Reference

| Need | File |
|------|------|
| **Architecture** | `docs/architecture/system-overview.md` |
| **Interface contracts** | `docs/architecture/boundaries-and-contracts.md` |
| **External team spec** | `docs/api/agentic-system-spec.md` |
| **Test strategy** | `docs/testing/testing-strategy.md` |
| **Demo data** | `docs/requirements/demo-scenario.md` |
| **Timeline** | `docs/planning/hackathon-timeline.md` |
| **Models (copy code)** | `docs/architecture/boundaries-and-contracts.md` |
| **Temporal engine (copy code)** | `docs/architecture/system-overview.md` |
| **Mock system (copy code)** | `docs/testing/testing-strategy.md` |

---

## Principles We Follow

### 1. Principled Architecture
- Clear responsibilities
- Single purpose per component
- No overlapping concerns

### 2. Contract-Driven Development
- Define interfaces first
- Test contracts explicitly
- Version breaking changes

### 3. Test-Driven Shipping
- Write test before code
- Run tests continuously
- Ship only when green

### 4. Pragmatic Scope
- Hackathon != Production
- Mock what's external
- Simplify where safe

---

## You Have Everything You Need

**To implement**:
- Copy Pydantic models from boundaries doc
- Copy temporal_model.py from system-overview
- Copy mock from testing-strategy
- Wire together in main.py

**To test**:
- Run contract tests (validate schemas)
- Run integration test (Sarah's scenario)
- Verify predictions reasonable

**To demo**:
- Follow demo script
- Run pre-demo checklist
- Present with confidence

**To integrate**:
- Share agentic-system-spec.md with external team
- They build to contract
- Integration is seamless

---

**This is principled, tested, shippable architecture. No fragmentation. No legacy ideas. Just clean contracts and working code.**

**Now go build it. 🚀**
