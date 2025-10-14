# System Boundaries and Interface Contracts

## Critical Distinction: What We Build vs. What We Integrate

### Our Gateway's Responsibility
```
┌─────────────────────────────────────────────┐
│         AEON GATEWAY (Our Code)             │
│                                             │
│  1. Accept queries from UI                  │
│  2. Validate and structure requests         │
│  3. Forward to agentic system              │
│  4. Receive causal graphs                   │
│  5. Build temporal models                   │
│  6. Generate predictions                    │
│  7. Store observations                      │
│  8. Update priors                          │
│  9. Return structured responses to UI       │
└─────────────────────────────────────────────┘
```

### External Agentic System's Responsibility
```
┌─────────────────────────────────────────────┐
│     AGENTIC SYSTEM (External/Partner)       │
│                                             │
│  1. Parse health query intent               │
│  2. Query INDRA for causal paths           │
│  3. Resolve biomarker → mechanisms          │
│  4. Discover environmental factors          │
│  5. Return causal graph structure           │
└─────────────────────────────────────────────┘
```

## The Boundary: JSON-RPC Interface

### What We Own

**Endpoint**: `POST /api/gateway/query`
- Input validation (Pydantic)
- Rate limiting
- Authentication (future)
- Response caching

**Endpoint**: `POST /api/gateway/update_observation`
- Biomarker ingestion
- Temporal model updates
- Prior recalculation

**Endpoint**: `GET /api/gateway/predictions/{user_id}`
- Trajectory forecasting
- Confidence intervals
- Intervention simulations

### What They Own

**External Endpoint**: `POST https://agentic-system.example.com/api/causal_discovery`
- INDRA integration
- Biomarker resolution
- Environmental context
- Natural language understanding

## Interface Contract: Gateway → Agentic System

### Request Format

```json
{
  "request_id": "uuid-v4",
  "user_context": {
    "user_id": "sarah_chen",
    "genetics": {
      "GSTM1": "null",
      "GSTP1": "Val/Val",
      "TNF-alpha": "-308G/A"
    },
    "current_biomarkers": {
      "CRP": 0.7,
      "IL-6": 1.1
    },
    "location_history": [
      {
        "city": "San Francisco",
        "start_date": "2020-01-01",
        "end_date": "2025-08-31",
        "avg_pm25": 7.8
      },
      {
        "city": "Los Angeles",
        "start_date": "2025-09-01",
        "end_date": null,
        "avg_pm25": 34.5
      }
    ]
  },
  "query": {
    "text": "How will LA air quality affect my inflammation?",
    "intent": "prediction",  // optional hint
    "focus_biomarkers": ["CRP", "IL-6"]  // optional
  },
  "options": {
    "max_graph_depth": 4,
    "min_evidence_count": 2,
    "include_interventions": false
  }
}
```

### Response Format (Required Fields)

```json
{
  "request_id": "uuid-v4",
  "status": "success",  // or "error"
  "causal_graph": {
    "nodes": [
      {
        "id": "PM2.5",
        "type": "environmental",  // environmental | molecular | biomarker | genetic
        "label": "Particulate Matter (PM2.5)",
        "grounding": {
          "database": "MESH",
          "identifier": "D052638"
        }
      },
      {
        "id": "NFKB1",
        "type": "molecular",
        "label": "NF-κB p50",
        "grounding": {
          "database": "HGNC",
          "identifier": "7794"
        }
      },
      {
        "id": "IL6",
        "type": "molecular",
        "label": "Interleukin-6",
        "grounding": {
          "database": "HGNC",
          "identifier": "6018"
        }
      },
      {
        "id": "CRP",
        "type": "biomarker",
        "label": "C-Reactive Protein",
        "grounding": {
          "database": "HGNC",
          "identifier": "2367"
        }
      }
    ],
    "edges": [
      {
        "source": "PM2.5",
        "target": "NFKB1",
        "relationship": "activates",  // activates | inhibits | increases | decreases
        "evidence": {
          "count": 47,
          "confidence": 0.82,
          "sources": ["PMID:12345678", "PMID:23456789"],
          "summary": "Particulate matter exposure activates NF-κB signaling"
        },
        "effect_size": 0.65,  // normalized 0-1
        "temporal_lag_hours": 6  // estimated time to effect
      },
      {
        "source": "NFKB1",
        "target": "IL6",
        "relationship": "increases",
        "evidence": {
          "count": 89,
          "confidence": 0.91,
          "sources": ["PMID:34567890"],
          "summary": "NF-κB drives IL-6 transcription"
        },
        "effect_size": 0.78,
        "temporal_lag_hours": 12
      }
    ],
    "genetic_modifiers": [
      {
        "variant": "GSTM1_null",
        "affected_nodes": ["oxidative_stress"],
        "effect_type": "amplifies",
        "magnitude": 1.3
      }
    ]
  },
  "metadata": {
    "query_time_ms": 1234,
    "indra_paths_explored": 15,
    "total_evidence_papers": 136
  },
  "explanations": [
    "PM2.5 exposure activates NF-κB inflammatory signaling (47 papers)",
    "Your GSTM1 null variant amplifies oxidative stress response by 30%",
    "NF-κB drives IL-6 production, which stimulates hepatic CRP synthesis"
  ]
}
```

### Error Response Format

```json
{
  "request_id": "uuid-v4",
  "status": "error",
  "error": {
    "code": "NO_CAUSAL_PATH",  // or "TIMEOUT", "INVALID_REQUEST", etc.
    "message": "Could not find causal path from PM2.5 to CRP",
    "details": {
      "attempted_paths": 5,
      "max_depth_reached": true
    }
  },
  "partial_result": null  // or partial graph if available
}
```

## Interface Contract: Gateway → Frontend

### Query Response

```json
{
  "query_id": "uuid-v4",
  "user_id": "sarah_chen",
  "predictions": {
    "CRP": {
      "baseline": 0.7,
      "timeline": [
        {
          "day": 0,
          "mean": 0.7,
          "confidence_interval": [0.65, 0.75],
          "risk_level": "low"
        },
        {
          "day": 30,
          "mean": 1.3,
          "confidence_interval": [1.0, 1.6],
          "risk_level": "moderate"
        },
        {
          "day": 60,
          "mean": 1.9,
          "confidence_interval": [1.5, 2.3],
          "risk_level": "moderate"
        },
        {
          "day": 90,
          "mean": 2.4,
          "confidence_interval": [1.9, 2.9],
          "risk_level": "high"
        }
      ],
      "unit": "mg/L"
    }
  },
  "causal_graph": {
    "nodes": [...],  // same format as received from agentic system
    "edges": [...]
  },
  "explanations": [
    "PM2.5 increased 3.4× after moving to LA",
    "Your GSTM1 null variant increases susceptibility",
    "Expected CRP elevation to high-risk zone by day 75"
  ],
  "recommendations": [
    {
      "type": "supplement",
      "name": "N-Acetylcysteine (NAC)",
      "predicted_impact": {
        "CRP_reduction_day90": -0.8,
        "mechanism": "Boosts glutathione synthesis"
      }
    }
  ]
}
```

## Design Principles (Non-Negotiable)

### 1. Separation of Concerns

**Gateway's Core Competency**: Temporal Bayesian modeling
- We do NOT query INDRA
- We do NOT parse natural language
- We do NOT resolve biomarkers to mechanisms

**Why**: Focus on what we're uniquely good at - building personalized, updating models

### 2. Fail-Safe Defaults

```python
# If agentic system is down, return cached/simplified response
# NEVER return 500 to UI
```

### 3. Contract Testing

```python
# tests/test_contracts.py
def test_agentic_system_response_schema():
    """Ensure external system returns expected format"""
    response = mock_agentic_response()
    validate_causal_graph_schema(response)  # Pydantic validation

def test_frontend_response_schema():
    """Ensure our API returns expected format to UI"""
    response = gateway.query(mock_request())
    validate_prediction_response_schema(response)
```

### 4. Versioning

All interfaces versioned:
```
POST /api/v1/gateway/query
POST /api/v1/gateway/update_observation
```

External contract:
```
POST /api/v1/causal_discovery
```

Breaking changes require new version.

## Data Models (Pydantic)

### Our Gateway Models

```python
# models/gateway.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime

class UserContext(BaseModel):
    """User profile for contextualized queries"""
    user_id: str
    genetics: Dict[str, str]  # gene -> variant
    current_biomarkers: Dict[str, float]  # biomarker -> value
    location_history: List[Dict]

    @validator('current_biomarkers')
    def validate_positive_values(cls, v):
        for key, val in v.items():
            if val < 0:
                raise ValueError(f"{key} must be non-negative")
        return v

class QueryRequest(BaseModel):
    """Request to agentic system"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_context: UserContext
    query: Dict[str, str]  # text, intent, focus_biomarkers
    options: Optional[Dict] = Field(default_factory=dict)

class CausalNode(BaseModel):
    """Node in causal graph"""
    id: str
    type: str  # environmental | molecular | biomarker | genetic
    label: str
    grounding: Dict[str, str]  # database, identifier

class CausalEdge(BaseModel):
    """Edge in causal graph"""
    source: str
    target: str
    relationship: str  # activates | inhibits | increases | decreases
    evidence: Dict
    effect_size: float = Field(..., ge=0, le=1)
    temporal_lag_hours: int = Field(..., ge=0)

class CausalGraph(BaseModel):
    """Causal graph from agentic system"""
    nodes: List[CausalNode]
    edges: List[CausalEdge]
    genetic_modifiers: List[Dict]

class AgenticSystemResponse(BaseModel):
    """Response from external agentic system"""
    request_id: str
    status: str  # success | error
    causal_graph: Optional[CausalGraph] = None
    metadata: Dict
    explanations: List[str]

    @validator('status')
    def validate_status(cls, v):
        if v not in ['success', 'error']:
            raise ValueError("Status must be 'success' or 'error'")
        return v

class PredictionTimeline(BaseModel):
    """Prediction for a single biomarker"""
    baseline: float
    timeline: List[Dict]  # day, mean, confidence_interval, risk_level
    unit: str

class GatewayResponse(BaseModel):
    """Our response to frontend"""
    query_id: str
    user_id: str
    predictions: Dict[str, PredictionTimeline]
    causal_graph: CausalGraph
    explanations: List[str]
    recommendations: Optional[List[Dict]] = None
```

## Testability Requirements

### 1. Mock the Agentic System

```python
# tests/mocks/agentic_system.py
class MockAgenticSystem:
    """Simulates external agentic system for testing"""

    def query(self, request: QueryRequest) -> AgenticSystemResponse:
        # Return hardcoded causal graphs for known queries
        if "LA" in request.query['text'] and "inflammation" in request.query['text']:
            return self._sf_to_la_response()
        else:
            return self._generic_response()

    def _sf_to_la_response(self):
        return AgenticSystemResponse(
            request_id="test-123",
            status="success",
            causal_graph=CausalGraph(
                nodes=[
                    CausalNode(id="PM2.5", type="environmental", label="PM2.5", grounding={"database": "MESH", "identifier": "D052638"}),
                    CausalNode(id="IL6", type="molecular", label="IL-6", grounding={"database": "HGNC", "identifier": "6018"}),
                    CausalNode(id="CRP", type="biomarker", label="CRP", grounding={"database": "HGNC", "identifier": "2367"})
                ],
                edges=[
                    CausalEdge(source="PM2.5", target="IL6", relationship="increases", evidence={"count": 47, "confidence": 0.82}, effect_size=0.65, temporal_lag_hours=6),
                    CausalEdge(source="IL6", target="CRP", relationship="increases", evidence={"count": 312, "confidence": 0.98}, effect_size=0.9, temporal_lag_hours=12)
                ],
                genetic_modifiers=[
                    {"variant": "GSTM1_null", "affected_nodes": ["oxidative_stress"], "effect_type": "amplifies", "magnitude": 1.3}
                ]
            ),
            metadata={"query_time_ms": 100},
            explanations=["Test explanation"]
        )
```

### 2. Contract Tests (Verify Interface Stability)

```python
# tests/test_contracts.py
import pytest
from models.gateway import AgenticSystemResponse, CausalGraph

def test_agentic_response_has_required_fields():
    """Ensure response has all required fields"""
    response_json = {
        "request_id": "test-123",
        "status": "success",
        "causal_graph": {
            "nodes": [],
            "edges": [],
            "genetic_modifiers": []
        },
        "metadata": {},
        "explanations": []
    }

    # Should not raise ValidationError
    response = AgenticSystemResponse(**response_json)
    assert response.status == "success"

def test_agentic_response_rejects_invalid_status():
    """Ensure invalid status values are rejected"""
    response_json = {
        "request_id": "test-123",
        "status": "pending",  # Invalid
        "metadata": {},
        "explanations": []
    }

    with pytest.raises(ValueError):
        AgenticSystemResponse(**response_json)

def test_causal_edge_validates_effect_size():
    """Effect size must be 0-1"""
    with pytest.raises(ValueError):
        CausalEdge(
            source="A",
            target="B",
            relationship="activates",
            evidence={},
            effect_size=1.5,  # Invalid
            temporal_lag_hours=6
        )
```

### 3. Integration Tests (With Mock)

```python
# tests/test_gateway_integration.py
from gateway import Gateway
from tests.mocks.agentic_system import MockAgenticSystem

@pytest.fixture
def gateway():
    return Gateway(agentic_system=MockAgenticSystem())

def test_end_to_end_query(gateway):
    """Test full query flow with mocked agentic system"""
    request = QueryRequest(
        user_context=UserContext(
            user_id="sarah_chen",
            genetics={"GSTM1": "null"},
            current_biomarkers={"CRP": 0.7},
            location_history=[{"city": "Los Angeles", "avg_pm25": 34.5}]
        ),
        query={"text": "How will LA affect my inflammation?"}
    )

    response = gateway.process_query(request)

    # Verify response structure
    assert response.query_id is not None
    assert response.user_id == "sarah_chen"
    assert "CRP" in response.predictions
    assert len(response.predictions["CRP"].timeline) == 4  # 0, 30, 60, 90 days

    # Verify predictions are reasonable
    crp_timeline = response.predictions["CRP"].timeline
    assert crp_timeline[0]["mean"] == 0.7  # Baseline
    assert crp_timeline[-1]["mean"] > 0.7  # Should increase
```

## Implementation Checklist

- [ ] Define Pydantic models for all interfaces
- [ ] Create mock agentic system for testing
- [ ] Write contract tests
- [ ] Implement gateway core logic (temporal model)
- [ ] Add integration tests
- [ ] Document failure modes and fallbacks
- [ ] Version all API endpoints
- [ ] Add request/response logging
- [ ] Implement rate limiting
- [ ] Add health check endpoint

## Failure Modes & Fallbacks

| Failure | Detection | Fallback |
|---------|-----------|----------|
| Agentic system timeout | 5s timeout | Return cached graph for common queries |
| Invalid response schema | Pydantic ValidationError | Return error to UI with explanation |
| No causal path found | status="error" | Suggest alternative query or broader search |
| Prediction diverges | Confidence interval > threshold | Show warning, request new observation |

## Success Criteria

**Before demo**:
1. ✅ All contract tests pass
2. ✅ Integration test covers Sarah's SF→LA scenario
3. ✅ Mock agentic system returns valid responses
4. ✅ Gateway produces predictions from causal graph
5. ✅ Frontend can consume gateway responses

**During demo**:
1. ✅ Query completes in < 3 seconds
2. ✅ No validation errors
3. ✅ Predictions match expected values (±15%)
4. ✅ Graph renders correctly in UI

This is the contract. Ship it.
