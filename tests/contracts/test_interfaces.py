"""
Contract Tests: Verify Interface Stability

These tests ensure:
1. External agentic system response format is valid
2. Our gateway response format is valid
3. Pydantic validation catches invalid data
4. Field constraints are enforced

These MUST pass before demo.
"""
import pytest
from pydantic import ValidationError
from src.models.gateway import (
    AgenticSystemResponse,
    CausalGraph,
    CausalNode,
    CausalEdge,
    GatewayResponse,
    PredictionTimeline,
    UserContext
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

        assert "status" in str(exc_info.value).lower()

    def test_causal_edge_requires_all_fields(self):
        """Every edge must have required fields"""
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
                evidence={"count": 10, "confidence": 0.8, "sources": [], "summary": "test"},
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
                evidence={"count": 10, "confidence": 0.8, "sources": [], "summary": "test"},
                effect_size=0.7,
                temporal_lag_hours=-5  # INVALID
            )

    def test_node_type_validation(self):
        """Node type must be one of allowed values"""
        with pytest.raises(ValidationError):
            CausalNode(
                id="test",
                type="invalid_type",  # INVALID
                label="Test",
                grounding={"database": "MESH", "identifier": "D000001"}
            )

    def test_relationship_validation(self):
        """Relationship must be one of allowed values"""
        with pytest.raises(ValidationError):
            CausalEdge(
                source="A",
                target="B",
                relationship="causes",  # INVALID
                evidence={"count": 10, "confidence": 0.8, "sources": [], "summary": "test"},
                effect_size=0.7,
                temporal_lag_hours=6
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

    def test_timeline_validation_missing_fields(self):
        """Timeline entry missing required fields should fail"""
        with pytest.raises(ValidationError):
            PredictionTimeline(
                baseline=0.7,
                timeline=[
                    {"day": 0, "mean": 0.7}  # Missing confidence_interval, risk_level
                ],
                unit="mg/L"
            )

    def test_timeline_validation_invalid_ci(self):
        """Confidence interval must be [lower, upper]"""
        with pytest.raises(ValidationError):
            PredictionTimeline(
                baseline=0.7,
                timeline=[
                    {"day": 0, "mean": 0.7, "confidence_interval": [0.65], "risk_level": "low"}  # Only 1 element
                ],
                unit="mg/L"
            )

    def test_timeline_validation_invalid_risk_level(self):
        """Risk level must be one of allowed values"""
        with pytest.raises(ValidationError):
            PredictionTimeline(
                baseline=0.7,
                timeline=[
                    {"day": 0, "mean": 0.7, "confidence_interval": [0.65, 0.75], "risk_level": "very_high"}  # INVALID
                ],
                unit="mg/L"
            )

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

    def test_user_context_validates_biomarkers(self):
        """Biomarkers must be non-negative"""
        with pytest.raises(ValidationError):
            UserContext(
                user_id="test",
                genetics={},
                current_biomarkers={"CRP": -0.5},  # INVALID
                location_history=[]
            )
