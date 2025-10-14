"""
Aeon Gateway - FastAPI Application

Entry point for the API gateway.
Routes requests between UI and temporal modeling engine.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.models.gateway import QueryRequest, GatewayResponse
import uvicorn

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

    For now: Returns placeholder response
    Next: Wire up temporal modeling engine
    """
    # TODO: Implement temporal modeling
    # 1. Forward to agentic system (mocked for now)
    # 2. Build temporal model from causal graph
    # 3. Generate predictions
    # 4. Return structured response

    raise HTTPException(
        status_code=501,
        detail="Query processing not yet implemented. Wire up temporal engine next."
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
