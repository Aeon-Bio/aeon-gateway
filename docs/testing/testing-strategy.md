# Testing Strategy: Fast Feedback for Demo Shipping

## Philosophy

**Goal**: Ship a working demo in 2.5 hours
**Constraint**: Every line of code must work
**Strategy**: Test-driven boundaries, not exhaustive coverage

### What We Test

1. **Interface contracts** - External boundaries (agentic system, frontend)
2. **Core logic** - Temporal model predictions
3. **Data validation** - Pydantic models catch bad input
4. **Integration** - End-to-end with mocks

### What We DON'T Test (For Hackathon)

1. ~~Edge cases~~ - Focus on happy path (Sarah's scenario)
2. ~~Performance~~ - If it works in < 5s, ship it
3. ~~Security~~ - No auth for demo
4. ~~Error recovery~~ - Simple fallbacks, not comprehensive

## Test Pyramid (Hackathon Edition)

```
        ┌─────────┐
        │  E2E    │  1 test (Sarah's SF→LA)
        │  (5min) │
        └─────────┘
      ┌─────────────┐
      │ Integration │  3 tests (query, predict, update)
      │   (10min)   │
      └─────────────┘
    ┌─────────────────┐
    │  Unit/Contract  │  10 tests (models, contracts)
    │     (10min)     │
    └─────────────────┘
```

**Total test writing time**: 25 minutes
**Test execution time**: < 10 seconds

## Test Files Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── mocks/
│   ├── __init__.py
│   └── agentic_system.py    # Mock external agentic system
├── unit/
│   ├── test_models.py       # Pydantic validation
│   └── test_temporal_model.py  # Prediction logic
├── contracts/
│   └── test_interfaces.py   # Contract validation
└── integration/
    └── test_gateway.py      # End-to-end with mocks
```

## Critical Test: Contract Validation

**File**: `tests/contracts/test_interfaces.py`

```python
"""
Contract tests: Verify external interface stability
These MUST pass before demo - they ensure agentic system contract
"""
import pytest
from pydantic import ValidationError
from models.gateway import (
    AgenticSystemResponse,
    CausalGraph,
    CausalNode,
    CausalEdge,
    GatewayResponse,
    PredictionTimeline
)

class TestAgenticSystemContract:
    """Verify external agentic system response format"""

    def test_minimal_valid_response(self):
        """Agentic system must return these fields at minimum"""
        response_json = {
            "request_id": "test-123",
            "status": "success",
            "causal_graph": {
                "nodes": [
                    {
                        "id": "PM2.5",
                        "type": "environmental",
                        "label": "PM2.5",
                        "grounding": {"database": "MESH", "identifier": "D052638"}
                    }
                ],
                "edges": [],
                "genetic_modifiers": []
            },
            "metadata": {"query_time_ms": 100},
            "explanations": ["Test"]
        }

        # Should NOT raise ValidationError
        response = AgenticSystemResponse(**response_json)
        assert response.status == "success"
        assert len(response.causal_graph.nodes) == 1

    def test_rejects_invalid_status(self):
        """Status must be 'success' or 'error'"""
        response_json = {
            "request_id": "test-123",
            "status": "pending",  # INVALID
            "metadata": {},
            "explanations": []
        }

        with pytest.raises(ValidationError) as exc_info:
            AgenticSystemResponse(**response_json)

        assert "status" in str(exc_info.value)

    def test_causal_edge_requires_all_fields(self):
        """Every edge must have source, target, relationship, evidence, effect_size, temporal_lag"""
        with pytest.raises(ValidationError):
            CausalEdge(
                source="A",
                target="B"
                # Missing required fields
            )

    def test_effect_size_bounded_0_to_1(self):
        """Effect size must be between 0 and 1"""
        with pytest.raises(ValidationError):
            CausalEdge(
                source="A",
                target="B",
                relationship="activates",
                evidence={"count": 10, "confidence": 0.8},
                effect_size=1.5,  # INVALID
                temporal_lag_hours=6
            )

    def test_temporal_lag_non_negative(self):
        """Temporal lag cannot be negative"""
        with pytest.raises(ValidationError):
            CausalEdge(
                source="A",
                target="B",
                relationship="activates",
                evidence={"count": 10, "confidence": 0.8},
                effect_size=0.7,
                temporal_lag_hours=-5  # INVALID
            )


class TestFrontendContract:
    """Verify our gateway response format for UI"""

    def test_prediction_timeline_format(self):
        """Frontend expects timeline with specific structure"""
        timeline = PredictionTimeline(
            baseline=0.7,
            timeline=[
                {"day": 0, "mean": 0.7, "confidence_interval": [0.65, 0.75], "risk_level": "low"},
                {"day": 30, "mean": 1.3, "confidence_interval": [1.0, 1.6], "risk_level": "moderate"}
            ],
            unit="mg/L"
        )

        assert timeline.baseline == 0.7
        assert len(timeline.timeline) == 2
        assert timeline.timeline[0]["day"] == 0

    def test_gateway_response_has_all_required_fields(self):
        """UI depends on these fields"""
        response_json = {
            "query_id": "test-123",
            "user_id": "sarah_chen",
            "predictions": {
                "CRP": {
                    "baseline": 0.7,
                    "timeline": [{"day": 0, "mean": 0.7, "confidence_interval": [0.65, 0.75], "risk_level": "low"}],
                    "unit": "mg/L"
                }
            },
            "causal_graph": {
                "nodes": [{"id": "CRP", "type": "biomarker", "label": "CRP", "grounding": {"database": "HGNC", "identifier": "2367"}}],
                "edges": [],
                "genetic_modifiers": []
            },
            "explanations": ["Test explanation"]
        }

        response = GatewayResponse(**response_json)
        assert response.user_id == "sarah_chen"
        assert "CRP" in response.predictions
```

## Critical Test: Mock Agentic System

**File**: `tests/mocks/agentic_system.py`

```python
"""
Mock external agentic system for testing
Returns hardcoded causal graphs for known queries
"""
from models.gateway import (
    AgenticSystemResponse,
    CausalGraph,
    CausalNode,
    CausalEdge
)


class MockAgenticSystem:
    """Simulates external agentic system"""

    def query(self, request) -> AgenticSystemResponse:
        """
        Route to specific response based on query
        For demo: only handle Sarah's SF→LA query
        """
        query_text = request.query.get('text', '').lower()

        if 'la' in query_text and 'inflammation' in query_text:
            return self._sf_to_la_response(request.request_id)
        else:
            return self._generic_response(request.request_id)

    def _sf_to_la_response(self, request_id: str) -> AgenticSystemResponse:
        """Hardcoded response for Sarah's SF→LA query"""
        return AgenticSystemResponse(
            request_id=request_id,
            status="success",
            causal_graph=CausalGraph(
                nodes=[
                    CausalNode(
                        id="PM2.5",
                        type="environmental",
                        label="Particulate Matter (PM2.5)",
                        grounding={"database": "MESH", "identifier": "D052638"}
                    ),
                    CausalNode(
                        id="NFKB1",
                        type="molecular",
                        label="NF-κB p50",
                        grounding={"database": "HGNC", "identifier": "7794"}
                    ),
                    CausalNode(
                        id="IL6",
                        type="molecular",
                        label="Interleukin-6",
                        grounding={"database": "HGNC", "identifier": "6018"}
                    ),
                    CausalNode(
                        id="CRP",
                        type="biomarker",
                        label="C-Reactive Protein",
                        grounding={"database": "HGNC", "identifier": "2367"}
                    )
                ],
                edges=[
                    CausalEdge(
                        source="PM2.5",
                        target="NFKB1",
                        relationship="activates",
                        evidence={
                            "count": 47,
                            "confidence": 0.82,
                            "sources": ["PMID:12345678"],
                            "summary": "PM2.5 activates NF-κB signaling"
                        },
                        effect_size=0.65,
                        temporal_lag_hours=6
                    ),
                    CausalEdge(
                        source="NFKB1",
                        target="IL6",
                        relationship="increases",
                        evidence={
                            "count": 89,
                            "confidence": 0.91,
                            "sources": ["PMID:23456789"],
                            "summary": "NF-κB drives IL-6 transcription"
                        },
                        effect_size=0.78,
                        temporal_lag_hours=12
                    ),
                    CausalEdge(
                        source="IL6",
                        target="CRP",
                        relationship="increases",
                        evidence={
                            "count": 312,
                            "confidence": 0.98,
                            "sources": ["PMID:34567890"],
                            "summary": "IL-6 stimulates hepatic CRP synthesis"
                        },
                        effect_size=0.90,
                        temporal_lag_hours=24
                    )
                ],
                genetic_modifiers=[
                    {
                        "variant": "GSTM1_null",
                        "affected_nodes": ["oxidative_stress"],
                        "effect_type": "amplifies",
                        "magnitude": 1.3
                    }
                ]
            ),
            metadata={
                "query_time_ms": 150,
                "indra_paths_explored": 12,
                "total_evidence_papers": 448
            },
            explanations=[
                "PM2.5 increased 3.4× after moving to LA",
                "Your GSTM1 null variant amplifies oxidative stress by 30%",
                "NF-κB activation drives IL-6 and CRP elevation"
            ]
        )

    def _generic_response(self, request_id: str) -> AgenticSystemResponse:
        """Fallback response for other queries"""
        return AgenticSystemResponse(
            request_id=request_id,
            status="success",
            causal_graph=CausalGraph(
                nodes=[],
                edges=[],
                genetic_modifiers=[]
            ),
            metadata={"query_time_ms": 50},
            explanations=["Generic response - no specific causal path found"]
        )
```

## Critical Test: Integration

**File**: `tests/integration/test_gateway.py`

```python
"""
Integration tests: End-to-end with mocked agentic system
"""
import pytest
from gateway import Gateway
from models.gateway import QueryRequest, UserContext
from tests.mocks.agentic_system import MockAgenticSystem


@pytest.fixture
def gateway():
    """Gateway instance with mocked agentic system"""
    return Gateway(agentic_system=MockAgenticSystem())


class TestGatewayIntegration:
    """Test full query → prediction flow"""

    def test_sarah_sf_to_la_query(self, gateway):
        """
        CRITICAL TEST: Sarah's demo scenario
        This MUST pass before demo
        """
        # Arrange
        request = QueryRequest(
            user_context=UserContext(
                user_id="sarah_chen",
                genetics={"GSTM1": "null", "GSTP1": "Val/Val"},
                current_biomarkers={"CRP": 0.7, "IL-6": 1.1},
                location_history=[
                    {
                        "city": "San Francisco",
                        "start_date": "2020-01-01",
                        "end_date": "2025-08-31",
                        "avg_pm25": 7.8
                    },
                    {
                        "city": "Los Angeles",
                        "start_date": "2025-09-01",
                        "end_date": None,
                        "avg_pm25": 34.5
                    }
                ]
            ),
            query={
                "text": "How will LA air quality affect my inflammation?",
                "focus_biomarkers": ["CRP", "IL-6"]
            }
        )

        # Act
        response = gateway.process_query(request)

        # Assert: Response structure
        assert response.query_id is not None
        assert response.user_id == "sarah_chen"
        assert len(response.explanations) > 0

        # Assert: Predictions exist
        assert "CRP" in response.predictions
        crp_pred = response.predictions["CRP"]
        assert crp_pred.baseline == 0.7
        assert len(crp_pred.timeline) == 4  # 0, 30, 60, 90 days

        # Assert: Predictions are reasonable
        timeline = crp_pred.timeline
        assert timeline[0]["day"] == 0
        assert timeline[0]["mean"] == 0.7  # Baseline

        assert timeline[1]["day"] == 30
        assert 1.0 <= timeline[1]["mean"] <= 1.5  # Moderate increase

        assert timeline[2]["day"] == 60
        assert 1.5 <= timeline[2]["mean"] <= 2.2

        assert timeline[3]["day"] == 90
        assert 2.0 <= timeline[3]["mean"] <= 2.8  # High risk zone

        # Assert: Risk levels escalate
        assert timeline[0]["risk_level"] == "low"
        assert timeline[3]["risk_level"] in ["moderate", "high"]

        # Assert: Causal graph structure
        graph = response.causal_graph
        assert len(graph.nodes) >= 3  # At least PM2.5, IL6, CRP
        assert len(graph.edges) >= 2  # At least PM2.5→IL6→CRP

        # Assert: Graph contains expected nodes
        node_ids = [n.id for n in graph.nodes]
        assert "PM2.5" in node_ids
        assert "CRP" in node_ids

    def test_update_observation_refines_prediction(self, gateway):
        """
        Test Bayesian prior update when new data arrives
        """
        # Initial query
        request = QueryRequest(
            user_context=UserContext(
                user_id="sarah_chen",
                genetics={"GSTM1": "null"},
                current_biomarkers={"CRP": 0.7},
                location_history=[{"city": "Los Angeles", "avg_pm25": 34.5}]
            ),
            query={"text": "Predict my CRP"}
        )

        initial_response = gateway.process_query(request)
        initial_day90 = initial_response.predictions["CRP"].timeline[3]["mean"]

        # New observation at day 45
        gateway.update_observation(
            user_id="sarah_chen",
            observation={"CRP": 1.8},  # Slightly higher than predicted
            day=45
        )

        # Query again
        updated_response = gateway.process_query(request)
        updated_day90 = updated_response.predictions["CRP"].timeline[3]["mean"]

        # Prediction should adjust upward
        assert updated_day90 > initial_day90

    def test_handles_missing_biomarker(self, gateway):
        """
        If agentic system returns graph without requested biomarker,
        gateway should gracefully handle it
        """
        request = QueryRequest(
            user_context=UserContext(
                user_id="test_user",
                genetics={},
                current_biomarkers={},
                location_history=[]
            ),
            query={"text": "Random query with no biomarkers"}
        )

        # Should not crash
        response = gateway.process_query(request)
        assert response.query_id is not None
        # Predictions may be empty, but response should be valid
```

## Test Fixtures

**File**: `tests/conftest.py`

```python
"""
Shared test fixtures
"""
import pytest
from models.gateway import UserContext, QueryRequest


@pytest.fixture
def sarah_profile():
    """Sarah's user profile for testing"""
    return UserContext(
        user_id="sarah_chen",
        genetics={
            "GSTM1": "null",
            "GSTP1": "Val/Val",
            "TNF-alpha": "-308G/A",
            "SOD2": "Ala/Ala"
        },
        current_biomarkers={
            "CRP": 0.7,
            "IL-6": 1.1,
            "8-OHdG": 4.2
        },
        location_history=[
            {
                "city": "San Francisco",
                "start_date": "2020-01-01",
                "end_date": "2025-08-31",
                "avg_pm25": 7.8
            },
            {
                "city": "Los Angeles",
                "start_date": "2025-09-01",
                "end_date": None,
                "avg_pm25": 34.5
            }
        ]
    )


@pytest.fixture
def sf_to_la_query(sarah_profile):
    """Sarah's SF→LA query for testing"""
    return QueryRequest(
        user_context=sarah_profile,
        query={
            "text": "How will LA air quality affect my inflammation?",
            "focus_biomarkers": ["CRP", "IL-6"]
        }
    )
```

## Test Execution Workflow

### During Development (TDD)

```bash
# 1. Write failing test
pytest tests/contracts/test_interfaces.py::test_minimal_valid_response -v

# 2. Implement minimum code to pass
# ... edit models/gateway.py ...

# 3. Verify test passes
pytest tests/contracts/test_interfaces.py::test_minimal_valid_response -v

# 4. Repeat for next test
```

### Before Demo

```bash
# Run all tests
pytest tests/ -v

# Expected output:
# tests/contracts/test_interfaces.py ✓✓✓✓✓ (5 tests)
# tests/mocks/test_agentic_system.py ✓✓ (2 tests)
# tests/integration/test_gateway.py ✓✓✓ (3 tests)
# =========================== 10 passed in 2.34s ===========================

# If ANY test fails, DO NOT demo
```

### Fast Feedback Loop

```bash
# Watch mode (re-run on file change)
pytest-watch tests/ -- -v

# Or use pytest-xdist for parallel execution
pytest tests/ -n auto
```

## Test Coverage Goals

**Hackathon**: 80% coverage on critical paths
- ✅ 100% coverage on interface contracts
- ✅ 100% coverage on gateway.process_query()
- ✅ 80% coverage on temporal model
- ❌ No coverage on error recovery (use simple fallbacks)

**Post-Hackathon**: 90%+ comprehensive coverage

## Pre-Demo Checklist

Run this checklist 15 minutes before demo:

```bash
# 1. All tests pass
pytest tests/ -v
# ✓ Must show: 10 passed

# 2. Mock agentic system works
pytest tests/integration/test_gateway.py::test_sarah_sf_to_la_query -v
# ✓ Must pass

# 3. Predictions are reasonable
pytest tests/integration/test_gateway.py::test_sarah_sf_to_la_query -v -s
# ✓ Check output: CRP should go from 0.7 → ~2.4

# 4. No import errors
python -c "from gateway import Gateway; from models.gateway import *"
# ✓ Must run without errors

# 5. Startup test
uvicorn main:app --reload &
sleep 2
curl http://localhost:8000/health
# ✓ Must return: {"status": "healthy"}
pkill -f uvicorn
```

If ANY step fails, **fix before demo**.

## Success Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Tests written | 10 | ___ |
| Tests passing | 10/10 (100%) | ___ |
| Contract coverage | 100% | ___ |
| Integration coverage | 100% | ___ |
| Test execution time | < 10s | ___ |
| Sarah's query test | PASS | ___ |

**Ship criteria**: All targets met.
