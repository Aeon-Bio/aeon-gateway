"""
Mock External Agentic System

Simulates the external agentic system that queries INDRA.
Returns hardcoded causal graphs for known queries (SF→LA demo).

For hackathon: This eliminates external dependency and ensures demo reliability.
"""
from src.models.gateway import (
    AgenticSystemResponse,
    CausalGraph,
    CausalNode,
    CausalEdge,
    QueryRequest
)


class MockAgenticSystem:
    """Simulates external agentic system for testing"""

    def query(self, request: QueryRequest) -> AgenticSystemResponse:
        """
        Route to specific response based on query

        For demo: Only handle Sarah's SF→LA query
        Other queries: Return generic/empty response
        """
        query_text = request.query.get('text', '').lower()

        # SF→LA inflammation query
        if ('la' in query_text or 'los angeles' in query_text) and 'inflammation' in query_text:
            return self._sf_to_la_response(request.request_id)

        # Generic fallback
        return self._generic_response(request.request_id)

    def _sf_to_la_response(self, request_id: str) -> AgenticSystemResponse:
        """
        Hardcoded response for Sarah's SF→LA query

        Graph: PM2.5 → NFKB1 → IL6 → CRP
        Genetic modifiers: GSTM1_null, TNF-alpha_-308G/A
        """
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
                            "sources": ["PMID:12345678", "PMID:23456789"],
                            "summary": "Particulate matter exposure activates NF-κB signaling pathway"
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
                            "sources": ["PMID:34567890"],
                            "summary": "NF-κB transcriptionally activates IL-6 gene expression"
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
                            "sources": ["PMID:45678901"],
                            "summary": "IL-6 stimulates hepatocyte CRP synthesis"
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
                    },
                    {
                        "variant": "TNF-alpha_-308G/A",
                        "affected_nodes": ["TNF", "IL6"],
                        "effect_type": "amplifies",
                        "magnitude": 1.2
                    }
                ]
            ),
            metadata={
                "query_time_ms": 150,
                "indra_paths_explored": 12,
                "total_evidence_papers": 448
            },
            explanations=[
                "PM2.5 exposure increased 3.4× after moving to LA (34.5 vs 7.8 µg/m³)",
                "Your GSTM1 null variant amplifies oxidative stress response by 30%",
                "PM2.5 activates NF-κB inflammatory signaling (47 papers, confidence: 0.82)",
                "NF-κB drives IL-6 production, which stimulates hepatic CRP synthesis",
                "Expected CRP elevation from 0.7 to ~2.4 mg/L based on environmental change"
            ]
        )

    def _generic_response(self, request_id: str) -> AgenticSystemResponse:
        """Fallback response for queries we don't specifically handle"""
        return AgenticSystemResponse(
            request_id=request_id,
            status="success",
            causal_graph=CausalGraph(
                nodes=[],
                edges=[],
                genetic_modifiers=[]
            ),
            metadata={"query_time_ms": 50},
            explanations=["Generic response - no specific causal path configured for this query"]
        )
