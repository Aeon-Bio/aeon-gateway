"""
Gateway data models - Interface contracts for Aeon Gateway

These models define:
1. Input from UI (QueryRequest)
2. Input from external agentic system (AgenticSystemResponse)
3. Output to UI (GatewayResponse)
4. Internal representations (CausalGraph, PredictionTimeline)

All models validated with Pydantic for type safety and contract enforcement.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional
from datetime import datetime
import uuid


# ============================================================================
# Input Models (From UI)
# ============================================================================

class UserContext(BaseModel):
    """User profile for contextualized queries"""
    user_id: str
    genetics: Dict[str, str]  # gene -> variant (e.g., "GSTM1": "null")
    current_biomarkers: Dict[str, float]  # biomarker -> value (e.g., "CRP": 0.7)
    location_history: List[Dict]  # [{city, start_date, end_date, avg_pm25}]

    @field_validator('current_biomarkers')
    @classmethod
    def validate_positive_values(cls, v):
        """Biomarker values must be non-negative"""
        for key, val in v.items():
            if val < 0:
                raise ValueError(f"{key} must be non-negative, got {val}")
        return v


class QueryRequest(BaseModel):
    """Request from UI to gateway"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_context: UserContext
    query: Dict[str, str]  # {text, intent, focus_biomarkers}
    options: Optional[Dict] = Field(default_factory=dict)


# ============================================================================
# Causal Graph Models (From External Agentic System)
# ============================================================================

class CausalNode(BaseModel):
    """Node in causal graph"""
    id: str
    type: str  # environmental | molecular | biomarker | genetic
    label: str
    grounding: Dict[str, str]  # {database, identifier}

    @field_validator('type')
    @classmethod
    def validate_node_type(cls, v):
        """Node type must be one of the allowed values"""
        allowed = ['environmental', 'molecular', 'biomarker', 'genetic']
        if v not in allowed:
            raise ValueError(f"Node type must be one of {allowed}, got {v}")
        return v


class CausalEdge(BaseModel):
    """Edge in causal graph"""
    source: str
    target: str
    relationship: str  # activates | inhibits | increases | decreases
    evidence: Dict  # {count, confidence, sources, summary}
    effect_size: float = Field(..., ge=0, le=1)  # MUST be [0, 1]
    temporal_lag_hours: int = Field(..., ge=0)   # MUST be >= 0

    @field_validator('relationship')
    @classmethod
    def validate_relationship(cls, v):
        """Relationship must be one of the allowed values"""
        allowed = ['activates', 'inhibits', 'increases', 'decreases']
        if v not in allowed:
            raise ValueError(f"Relationship must be one of {allowed}, got {v}")
        return v


class CausalGraph(BaseModel):
    """Causal graph from agentic system"""
    nodes: List[CausalNode]
    edges: List[CausalEdge]
    genetic_modifiers: List[Dict]  # [{variant, affected_nodes, effect_type, magnitude}]


class AgenticSystemResponse(BaseModel):
    """Response from external agentic system"""
    request_id: str
    status: str  # success | error
    causal_graph: Optional[CausalGraph] = None
    metadata: Dict
    explanations: List[str]
    error: Optional[Dict] = None  # Only present if status="error"

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Status must be 'success' or 'error'"""
        if v not in ['success', 'error']:
            raise ValueError(f"Status must be 'success' or 'error', got {v}")
        return v


# ============================================================================
# Output Models (To UI)
# ============================================================================

class PredictionTimeline(BaseModel):
    """Prediction for a single biomarker over time"""
    baseline: float
    timeline: List[Dict]  # [{day, mean, confidence_interval, risk_level}]
    unit: str

    @field_validator('timeline')
    @classmethod
    def validate_timeline_structure(cls, v):
        """Each timeline entry must have required fields"""
        required_fields = {'day', 'mean', 'confidence_interval', 'risk_level'}
        for entry in v:
            missing = required_fields - set(entry.keys())
            if missing:
                raise ValueError(f"Timeline entry missing fields: {missing}")

            # Validate confidence_interval is a 2-element list
            ci = entry.get('confidence_interval')
            if not isinstance(ci, list) or len(ci) != 2:
                raise ValueError("confidence_interval must be [lower, upper]")

            # Validate risk_level
            if entry.get('risk_level') not in ['low', 'moderate', 'high', 'unknown']:
                raise ValueError(f"Invalid risk_level: {entry.get('risk_level')}")

        return v


class GatewayResponse(BaseModel):
    """Response from gateway to UI"""
    query_id: str
    user_id: str
    predictions: Dict[str, PredictionTimeline]
    causal_graph: CausalGraph
    explanations: List[str]
    recommendations: Optional[List[Dict]] = None


# ============================================================================
# Internal Models (For Temporal Modeling)
# ============================================================================

class TemporalModel(BaseModel):
    """Internal representation of temporal causal model"""
    model_config = {"arbitrary_types_allowed": True}

    graph: object  # NetworkX DiGraph (not serializable, so object type)
    baseline: Dict[str, float]
    user_genetics: Dict[str, str]


# ============================================================================
# Demo Data Fixtures
# ============================================================================

def get_sarah_profile() -> UserContext:
    """Sarah Chen's profile for demo/testing"""
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


def get_sf_to_la_query() -> QueryRequest:
    """Sarah's SF→LA query for demo/testing"""
    return QueryRequest(
        user_context=get_sarah_profile(),
        query={
            "text": "How will LA air quality affect my inflammation?",
            "intent": "prediction",
            "focus_biomarkers": ["CRP", "IL-6"]
        },
        options={
            "max_graph_depth": 4,
            "min_evidence_count": 2
        }
    )
