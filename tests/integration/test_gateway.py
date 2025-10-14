"""
Integration Tests: End-to-End Query Flow

Tests the complete flow:
1. User query → Gateway
2. Gateway → Agentic system (mocked)
3. Temporal model building
4. Monte Carlo prediction
5. Structured response

MUST PASS: Sarah's SF→LA scenario
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


class TestGatewayIntegration:
    """End-to-end integration tests"""

    def test_sarah_sf_to_la_query(self):
        """
        Sarah Chen moves from SF to LA.

        Expected:
        - CRP baseline: 0.7 mg/L
        - CRP after 90 days: ~2.4 mg/L (due to higher PM2.5 in LA)
        - Predictions include timeline with confidence intervals
        - Risk level escalates from 'low' to 'moderate' or 'high'
        """
        # Build request matching demo scenario
        request_data = {
            "user_context": {
                "user_id": "sarah_chen",
                "genetics": {
                    "APOE": "e3/e3",  # No high-risk variant
                    "IL6": "GG"       # Standard inflammatory response
                },
                "current_biomarkers": {
                    "CRP": 0.7,   # Baseline: low inflammation
                    "IL6": 1.2    # Baseline: normal
                },
                "location_history": [
                    {"city": "San Francisco", "state": "CA", "start_date": "2023-01-01", "end_date": "2024-01-01"},
                    {"city": "Los Angeles", "state": "CA", "start_date": "2024-01-01", "end_date": None}
                ]
            },
            "query": {
                "text": "How will my inflammation markers change in LA?"
            }
        }

        # Send request to gateway
        response = client.post("/api/v1/gateway/query", json=request_data)

        # Assert response structure
        assert response.status_code == 200
        data = response.json()

        assert "query_id" in data
        assert data["user_id"] == "sarah_chen"
        assert "predictions" in data
        assert "causal_graph" in data
        assert "explanations" in data

        # Verify CRP predictions
        assert "CRP" in data["predictions"]
        crp_prediction = data["predictions"]["CRP"]

        assert crp_prediction["baseline"] == 0.7
        assert crp_prediction["unit"] == "mg/L"
        assert len(crp_prediction["timeline"]) > 0

        # Find day 90 prediction
        day_90 = next((point for point in crp_prediction["timeline"] if point["day"] == 90), None)
        assert day_90 is not None, "Should have prediction for day 90"

        # Verify CRP increases
        crp_final = day_90["mean"]
        assert crp_final > 0.7, f"CRP should increase from baseline, got {crp_final}"

        # Should be in reasonable range (not too extreme)
        assert 1.3 < crp_final < 4.5, f"CRP at day 90 should increase significantly (1.3-4.5 mg/L), got {crp_final}"

        # Verify risk level escalates
        day_0_risk = crp_prediction["timeline"][0]["risk_level"]
        day_90_risk = day_90["risk_level"]

        assert day_0_risk == "low", f"Baseline risk should be 'low', got {day_0_risk}"
        assert day_90_risk in ["moderate", "high"], f"Day 90 risk should escalate, got {day_90_risk}"

        # Verify confidence intervals exist
        assert "confidence_interval" in day_90
        ci = day_90["confidence_interval"]
        assert len(ci) == 2
        assert ci[0] < crp_final < ci[1], "Mean should be within confidence interval"

        # Verify causal graph structure
        graph = data["causal_graph"]
        assert "nodes" in graph
        assert "edges" in graph

        # Should have PM2.5 → ... → CRP pathway
        node_ids = [node["id"] for node in graph["nodes"]]
        assert "PM2.5" in node_ids, "Should have PM2.5 environmental node"
        assert "CRP" in node_ids, "Should have CRP biomarker node"

        # Verify explanations
        assert len(data["explanations"]) > 0
        explanations_text = " ".join(data["explanations"]).lower()
        assert "pm2.5" in explanations_text or "pollution" in explanations_text

    def test_generic_query_without_location_change(self):
        """
        Test query without environmental changes.

        Biomarkers should remain stable (no significant change).
        """
        request_data = {
            "user_context": {
                "user_id": "john_doe",
                "genetics": {},
                "current_biomarkers": {"CRP": 1.0},
                "location_history": [
                    {"city": "San Francisco", "state": "CA", "start_date": "2023-01-01", "end_date": None}
                ]
            },
            "query": {
                "text": "What are my inflammation markers?"
            }
        }

        response = client.post("/api/v1/gateway/query", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "CRP" in data["predictions"]

        crp_prediction = data["predictions"]["CRP"]
        day_90 = next((point for point in crp_prediction["timeline"] if point["day"] == 90), None)

        # Without environmental changes, CRP should stay relatively stable
        assert day_90 is not None
        # Allow some variation but should not increase as much as with environmental changes
        assert 0.8 < day_90["mean"] < 2.5

    def test_query_validation(self):
        """Test that invalid queries are rejected"""
        # Missing required field
        invalid_request = {
            "user_context": {
                "user_id": "test",
                "genetics": {},
                "current_biomarkers": {},
                "location_history": []
            }
            # Missing 'query' field
        }

        response = client.post("/api/v1/gateway/query", json=invalid_request)
        assert response.status_code == 422  # Validation error

    def test_negative_biomarker_rejected(self):
        """Biomarkers must be non-negative"""
        invalid_request = {
            "user_context": {
                "user_id": "test",
                "genetics": {},
                "current_biomarkers": {"CRP": -0.5},  # INVALID
                "location_history": []
            },
            "query": {
                "text": "test"
            }
        }

        response = client.post("/api/v1/gateway/query", json=invalid_request)
        assert response.status_code == 422
