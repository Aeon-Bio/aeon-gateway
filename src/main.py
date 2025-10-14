"""
Aeon Gateway - FastAPI Application

Entry point for the API gateway.
Routes requests between UI and temporal modeling engine.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.models.gateway import QueryRequest, GatewayResponse
import uvicorn
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Aeon Gateway",
    description="Temporal Bayesian modeling service for personalized health predictions",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "aeon-gateway",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "Aeon Gateway",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "query": "POST /api/v1/gateway/query",
            "docs": "/docs"
        }
    }


@app.post("/api/v1/gateway/query", response_model=GatewayResponse)
async def process_query(request: QueryRequest):
    """
    Main query endpoint

    Accepts user context + query, returns predictions.

    Flow:
    1. Forward query to agentic system (mocked)
    2. Build temporal model from causal graph
    3. Generate predictions via Monte Carlo simulation
    4. Return structured response
    """
    from src.temporal_model import TemporalModelEngine
    from src.agentic_client import AgenticSystemClientSync
    from tests.mocks.agentic_system import MockAgenticSystem
    import uuid

    # Get agentic system URL from environment
    agentic_url = os.getenv("AGENTIC_SYSTEM_URL")

    try:
        # Step 1: Query agentic system
        if agentic_url:
            # Production: Use real agentic system
            logger.info(f"Using real agentic system: {agentic_url}")
            agentic_system = AgenticSystemClientSync(base_url=agentic_url)
            agentic_response = agentic_system.query(request)
            agentic_system.close()
        else:
            # Development: Use mock
            logger.info("Using mock agentic system (set AGENTIC_SYSTEM_URL to use real system)")
            agentic_system = MockAgenticSystem()
            agentic_response = agentic_system.query(request)

        if agentic_response.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Agentic system error: {agentic_response.error}"
            )

        # Check if causal graph is present
        if not agentic_response.causal_graph:
            raise HTTPException(
                status_code=500,
                detail="Agentic system returned no causal graph"
            )

        # Step 2: Build temporal model
        engine = TemporalModelEngine(n_simulations=1000)
        model = engine.build_model(
            causal_graph=agentic_response.causal_graph,
            user_genetics=request.user_context.genetics,
            baseline_biomarkers=request.user_context.current_biomarkers
        )

        # Step 3: Detect environmental changes from location history
        environmental_changes = _infer_environmental_changes(request.user_context)

        # Step 4: Generate predictions
        predictions = engine.predict(
            model=model,
            environmental_changes=environmental_changes,
            horizon_days=90
        )

        # Step 5: Return structured response
        return GatewayResponse(
            query_id=str(uuid.uuid4()),
            user_id=request.user_context.user_id,
            predictions=predictions,
            causal_graph=agentic_response.causal_graph,
            explanations=agentic_response.explanations
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


def _infer_environmental_changes(user_context: "UserContext") -> dict:
    """
    Infer environmental changes from location history.

    For demo: SF → LA means PM2.5 increases by 1.8x
    """
    from src.models.gateway import UserContext

    # Check location history
    location_history = user_context.location_history
    if not location_history:
        return {}

    # Simple heuristic: If last location contains "LA" or "Los Angeles"
    if location_history:
        last_location = location_history[-1].get('city', '').lower()
        if 'los angeles' in last_location or 'la' in last_location:
            # LA has ~1.8x higher PM2.5 than SF
            return {"PM2.5": 1.8}

    return {}


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
