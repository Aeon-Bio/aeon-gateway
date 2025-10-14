# System Architecture Overview

## What We Build

**Aeon Gateway**: A temporal Bayesian modeling service that converts causal graphs into personalized health predictions.

### Core Responsibility

```
Input:  Causal graph (from external agentic system) + User observations
Output: Biomarker predictions over time with confidence intervals
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (UI)                        │
│  • Timeline visualization (Recharts)                    │
│  • Causal graph display (D3.js)                         │
│  • User queries and observation input                   │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP/JSON
                        ▼
┌─────────────────────────────────────────────────────────┐
│             AEON GATEWAY (Our System)                   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  FastAPI Layer                                   │  │
│  │  • POST /api/v1/gateway/query                    │  │
│  │  • POST /api/v1/gateway/update_observation       │  │
│  │  • GET  /api/v1/gateway/predictions/:user_id     │  │
│  └────────┬───────────────────────────────┬─────────┘  │
│           │                               │            │
│  ┌────────▼───────────────────────────────▼─────────┐  │
│  │  Temporal Modeling Engine                        │  │
│  │  • Build Dynamic Bayesian Network from graph     │  │
│  │  • Update priors with new observations          │  │
│  │  • Monte Carlo trajectory simulation            │  │
│  │  • Risk stratification                          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Data Layer (SQLite)                             │  │
│  │  • User profiles & genetics                      │  │
│  │  • Observation history (time series)             │  │
│  │  • Cached predictions                            │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTP/JSON
                    ▼
┌─────────────────────────────────────────────────────────┐
│        External Agentic System (Not Our Code)           │
│  • Query INDRA for causal paths                         │
│  • Resolve biomarkers → molecular mechanisms            │
│  • Parse natural language queries                       │
│  • Return structured causal graphs                      │
└─────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### FastAPI Layer (Our Code)

**Responsibility**: API endpoints, validation, orchestration

**Endpoints**:

1. **POST /api/v1/gateway/query**
   - Input: User context + query text
   - Forwards to agentic system for causal graph
   - Builds temporal model from graph
   - Returns predictions

2. **POST /api/v1/gateway/update_observation**
   - Input: New biomarker measurements
   - Updates Bayesian priors
   - Recalculates predictions

3. **GET /api/v1/gateway/predictions/:user_id**
   - Returns cached predictions for user
   - Includes confidence intervals

**Implementation**:
```python
# main.py
from fastapi import FastAPI
from models.gateway import QueryRequest, GatewayResponse
from temporal_model import TemporalModelEngine
from agentic_client import AgenticSystemClient

app = FastAPI(title="Aeon Gateway", version="0.1.0")

temporal_engine = TemporalModelEngine()
agentic_client = AgenticSystemClient(base_url="http://agentic-system.example.com")

@app.post("/api/v1/gateway/query", response_model=GatewayResponse)
async def query(request: QueryRequest):
    # 1. Forward to agentic system
    causal_graph = await agentic_client.get_causal_graph(request)

    # 2. Build temporal model
    model = temporal_engine.build_model(
        graph=causal_graph,
        user_genetics=request.user_context.genetics,
        baseline_biomarkers=request.user_context.current_biomarkers
    )

    # 3. Generate predictions
    predictions = temporal_engine.predict(
        model=model,
        environmental_changes=extract_env_changes(request.user_context),
        horizon_days=90
    )

    # 4. Return to UI
    return GatewayResponse(
        query_id=str(uuid.uuid4()),
        user_id=request.user_context.user_id,
        predictions=predictions,
        causal_graph=causal_graph,
        explanations=causal_graph.explanations
    )
```

### Temporal Modeling Engine (Our Code)

**Responsibility**: Convert causal graphs to predictive models

**Core Operations**:

1. **build_model()**: CausalGraph → DynamicBayesianNetwork
   - Parse nodes and edges
   - Create time-sliced representation
   - Add genetic modifiers as static nodes
   - Initialize priors from baseline

2. **predict()**: DBN → Biomarker trajectories
   - Monte Carlo simulation (1000 samples)
   - Forward propagate through graph
   - Aggregate to mean + 95% CI
   - Discretize to risk levels

3. **update_priors()**: New observation → Updated DBN
   - Bayesian update of node distributions
   - Store observation in history
   - Recalculate predictions

**Implementation**:
```python
# temporal_model.py
import networkx as nx
import numpy as np
from typing import Dict, List

class TemporalModelEngine:
    """Builds and runs temporal causal models"""

    def build_model(self, graph, user_genetics, baseline_biomarkers):
        """
        Convert causal graph to executable model

        Args:
            graph: CausalGraph from agentic system
            user_genetics: Dict[gene, variant]
            baseline_biomarkers: Dict[biomarker, value]

        Returns:
            TemporalModel ready for prediction
        """
        # Build NetworkX graph
        G = nx.DiGraph()

        for node in graph.nodes:
            G.add_node(node.id, type=node.type, label=node.label)

        for edge in graph.edges:
            G.add_edge(
                edge.source,
                edge.target,
                weight=edge.effect_size,
                lag_hours=edge.temporal_lag_hours
            )

        # Add genetic modifiers
        for modifier in graph.genetic_modifiers:
            variant_node = modifier['variant']
            G.add_node(variant_node, type='genetic')

            for affected_node in modifier['affected_nodes']:
                if G.has_node(affected_node):
                    G.add_edge(
                        variant_node,
                        affected_node,
                        weight=modifier['magnitude'],
                        lag_hours=0
                    )

        return TemporalModel(
            graph=G,
            baseline=baseline_biomarkers,
            user_genetics=user_genetics
        )

    def predict(self, model, environmental_changes, horizon_days=90):
        """
        Generate biomarker predictions

        Args:
            model: TemporalModel
            environmental_changes: Dict[env_factor, value]
            horizon_days: Prediction horizon

        Returns:
            Dict[biomarker, PredictionTimeline]
        """
        time_points = [0, 30, 60, 90]
        predictions = {}

        # Get biomarker nodes
        biomarker_nodes = [
            n for n, d in model.graph.nodes(data=True)
            if d.get('type') == 'biomarker'
        ]

        for biomarker in biomarker_nodes:
            timeline = []

            for day in time_points:
                # Run Monte Carlo simulation
                samples = self._monte_carlo_step(
                    model, environmental_changes, day
                )

                # Extract this biomarker's values
                biomarker_samples = [s.get(biomarker, 0) for s in samples]

                # Compute statistics
                mean = np.mean(biomarker_samples)
                ci_lower = np.percentile(biomarker_samples, 2.5)
                ci_upper = np.percentile(biomarker_samples, 97.5)
                risk_level = self._discretize_risk(biomarker, mean)

                timeline.append({
                    "day": day,
                    "mean": float(mean),
                    "confidence_interval": [float(ci_lower), float(ci_upper)],
                    "risk_level": risk_level
                })

            predictions[biomarker] = PredictionTimeline(
                baseline=model.baseline.get(biomarker, 0),
                timeline=timeline,
                unit="mg/L"  # TODO: get from metadata
            )

        return predictions

    def _monte_carlo_step(self, model, env_changes, day):
        """Run Monte Carlo simulation for a specific day"""
        samples = []
        n_samples = 1000

        for _ in range(n_samples):
            # Initialize with environmental changes scaled by day
            state = {
                env: value * (day / 90.0)
                for env, value in env_changes.items()
            }

            # Forward propagate through graph (topological order)
            for node in nx.topological_sort(model.graph):
                if node in state:
                    continue

                # Aggregate from parents
                value = 0.0
                for parent in model.graph.predecessors(node):
                    if parent in state:
                        edge_data = model.graph[parent][node]
                        weight = edge_data.get('weight', 0.5)
                        value += state[parent] * weight

                # Add baseline if biomarker
                node_data = model.graph.nodes[node]
                if node_data.get('type') == 'biomarker':
                    baseline = model.baseline.get(node, 0)
                    value += baseline

                # Add noise
                value += np.random.normal(0, value * 0.1)

                state[node] = max(0, value)  # Non-negative

            samples.append(state)

        return samples

    def _discretize_risk(self, biomarker, value):
        """Convert continuous value to risk level"""
        # Hardcoded thresholds for demo
        thresholds = {
            "CRP": [(1.0, "low"), (3.0, "moderate"), (float('inf'), "high")],
            "IL-6": [(1.8, "low"), (5.0, "moderate"), (float('inf'), "high")]
        }

        if biomarker not in thresholds:
            return "unknown"

        for threshold, level in thresholds[biomarker]:
            if value < threshold:
                return level

        return "high"
```

### Data Models (Our Code)

See [boundaries-and-contracts.md](./boundaries-and-contracts.md) for complete Pydantic models.

**Key Models**:
- `QueryRequest`: Input from UI
- `AgenticSystemResponse`: Input from agentic system
- `GatewayResponse`: Output to UI
- `CausalGraph`: Internal representation
- `PredictionTimeline`: Biomarker forecast

### External Agentic System (Not Our Code)

**Responsibility**: Query INDRA, resolve biomarkers, return causal graphs

**Interface**: See [boundaries-and-contracts.md](./boundaries-and-contracts.md)

**We Do NOT implement**:
- INDRA API calls
- Natural language understanding
- Biomarker → mechanism resolution
- Environmental data fetching

**For hackathon**: Mock this system entirely (see [testing-strategy.md](../testing/testing-strategy.md))

## Data Flow: End-to-End

```
1. User enters query in UI
   ↓
2. UI → POST /api/v1/gateway/query
   {
     user_context: {genetics, biomarkers, location_history},
     query: "How will LA affect my inflammation?"
   }
   ↓
3. Gateway → External agentic system
   Request causal graph
   ↓
4. Agentic system → INDRA
   Query PM2.5 → IL6 → CRP paths
   ↓
5. Agentic system → Gateway
   Return CausalGraph (nodes, edges, evidence)
   ↓
6. Gateway builds TemporalModel
   - NetworkX graph from nodes/edges
   - Add genetic modifiers
   - Initialize priors from baseline
   ↓
7. Gateway runs predictions
   - Monte Carlo simulation (1000 samples)
   - Forward propagate to day 90
   - Compute mean + 95% CI
   ↓
8. Gateway → UI
   Return GatewayResponse {predictions, graph, explanations}
   ↓
9. UI renders
   - Timeline (Recharts)
   - Causal graph (D3)
   - Explanations (list)
```

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| API Framework | FastAPI | Async, fast, auto-docs |
| Graph Library | NetworkX | Mature, sufficient for scale |
| Numerical | NumPy | Standard for array operations |
| Validation | Pydantic | Type-safe models |
| Database | SQLite | Zero-config for hackathon |
| Testing | pytest | Industry standard |
| HTTP Client | httpx | Async-native for agentic calls |

## Deployment

### Hackathon: Local

```bash
uvicorn main:app --reload --port 8000
```

### Production: Docker

```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Success Criteria

**Before demo**:
- ✅ All contract tests pass
- ✅ Sarah's SF→LA query returns predictions
- ✅ Predictions reasonable (CRP: 0.7 → 2.4 over 90 days)
- ✅ UI can render response

**During demo**:
- ✅ Query completes in < 3 seconds
- ✅ No errors
- ✅ Predictions match expected trajectory

## What We DON'T Build (Hackathon)

- ❌ INDRA integration (external system handles this)
- ❌ Natural language parsing (external system)
- ❌ Environmental data APIs (hardcoded in demo data)
- ❌ User authentication (single demo user)
- ❌ True Bayesian inference (simplified Monte Carlo)

## Future Enhancements (Post-Hackathon)

1. **True Bayesian Inference**: Replace Monte Carlo with pgmpy Variable Elimination
2. **GPU Acceleration**: Use Pyro for large graphs
3. **Real-time Updates**: WebSocket for streaming predictions
4. **Multi-user**: Add auth, per-user data isolation
5. **Intervention Simulation**: Do-calculus for counterfactuals

---

**This is the architecture we ship. Focus on temporal modeling - that's our unique value.**
