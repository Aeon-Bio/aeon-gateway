# Technology Stack

## Stack Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  • Next.js 14 / React 18                                    │
│  • Recharts (timeline visualization)                        │
│  • D3.js / react-flow (causal graphs)                       │
│  • TailwindCSS (styling)                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API / WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                   Backend Layer                             │
│  • FastAPI (Python 3.11+)                                   │
│  • Pydantic (data validation)                               │
│  • LangGraph (agent orchestration)                          │
│  • httpx (async HTTP)                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Causal Modeling Layer                          │
│  • NetworkX (graph analysis)                                │
│  • pgmpy (Bayesian networks)                                │
│  • NumPy / SciPy (numerical computation)                    │
│  • Pandas (time series)                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 Persistence Layer                           │
│  • SQLite (hackathon)                                       │
│  • PostgreSQL (production)                                  │
│  • Redis (caching)                                          │
└─────────────────────────────────────────────────────────────┘
```

## Backend Stack

### Core Framework: FastAPI

**Version**: 0.104.1+

**Why FastAPI**:
- ✅ Automatic OpenAPI documentation
- ✅ Native async/await support (critical for INDRA API calls)
- ✅ Pydantic integration (type-safe data models)
- ✅ Fast performance (on par with Node.js, Go)
- ✅ WebSocket support (for real-time updates)

**Configuration**:
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Aeon Gateway",
    description="Personalized Causal Health Modeling API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Data Validation: Pydantic

**Version**: 2.5.0+

**Why Pydantic**:
- ✅ Runtime type checking
- ✅ JSON schema generation
- ✅ Validation error messages
- ✅ Native FastAPI integration

**Example Models**:
```python
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
from datetime import datetime

class GeneticVariant(BaseModel):
    gene: str = Field(..., description="Gene symbol (HGNC)")
    variant: str = Field(..., description="Variant identifier")
    zygosity: Optional[str] = Field(None, description="hom/het")

class UserProfile(BaseModel):
    user_id: str
    genetics: Dict[str, str]
    baseline_biomarkers: Dict[str, float]

    @validator('baseline_biomarkers')
    def validate_biomarkers(cls, v):
        # Ensure all values are positive
        for key, value in v.items():
            if value < 0:
                raise ValueError(f"{key} must be non-negative")
        return v
```

### Agent Orchestration: LangGraph

**Version**: 0.0.40+

**Why LangGraph**:
- ✅ State management for multi-agent workflows
- ✅ Conditional routing between agents
- ✅ Built-in retry logic
- ✅ Compatible with LangChain ecosystem

**Architecture**:
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    query: str
    user_profile: dict
    exposures: list
    mechanisms: list
    causal_paths: list
    graph: dict
    predictions: dict

def create_orchestrator():
    workflow = StateGraph(AgentState)

    # Add nodes (agents)
    workflow.add_node("parse_query", parse_query_agent)
    workflow.add_node("resolve_biomarkers", biomarker_resolver_agent)
    workflow.add_node("query_indra", indra_query_agent)
    workflow.add_node("construct_graph", graph_constructor_agent)
    workflow.add_node("generate_predictions", prediction_agent)

    # Define edges (flow)
    workflow.add_edge("parse_query", "resolve_biomarkers")
    workflow.add_edge("resolve_biomarkers", "query_indra")
    workflow.add_edge("query_indra", "construct_graph")
    workflow.add_edge("construct_graph", "generate_predictions")
    workflow.add_edge("generate_predictions", END)

    # Set entry point
    workflow.set_entry_point("parse_query")

    return workflow.compile()
```

### Async HTTP: httpx

**Version**: 0.25.2+

**Why httpx over requests**:
- ✅ Native async/await support
- ✅ HTTP/2 support
- ✅ Connection pooling
- ✅ Better timeout handling

**Usage for INDRA**:
```python
import httpx

class INDRAClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url="https://db.indra.bio",
            timeout=30.0,
            limits=httpx.Limits(max_connections=10)
        )

    async def query_path(self, source: str, target: str):
        response = await self.client.get(
            "/api/network/path_search",
            params={"source": source, "target": target}
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()
```

## Causal Modeling Stack

### Graph Analysis: NetworkX

**Version**: 3.2+

**Why NetworkX**:
- ✅ Comprehensive graph algorithms (betweenness, shortest path, etc.)
- ✅ Mature, well-documented
- ✅ Easy visualization with matplotlib
- ✅ Efficient for graphs < 10K nodes (our use case)

**Key Algorithms Used**:
```python
import networkx as nx

# Identify bottleneck nodes
centrality = nx.betweenness_centrality(G)

# Find shortest paths
path = nx.shortest_path(G, source="PM2.5", target="CRP")

# Topological sort for causal ordering
ordered_nodes = list(nx.topological_sort(G))

# Community detection (group related mechanisms)
communities = nx.community.greedy_modularity_communities(G)
```

### Bayesian Networks: pgmpy

**Version**: 0.1.25+

**Why pgmpy**:
- ✅ Factor graph support
- ✅ Conditional Probability Distributions (CPDs)
- ✅ Variable Elimination inference (fast, exact)
- ✅ Parameter learning from data

**Core Usage**:
```python
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

# Define structure
model = BayesianNetwork([
    ('PM25', 'OxidativeStress'),
    ('GSTM1_null', 'OxidativeStress'),
    ('OxidativeStress', 'Inflammation'),
    ('Inflammation', 'CRP')
])

# Define CPD for CRP
cpd_crp = TabularCPD(
    variable='CRP',
    variable_card=3,  # Low, Medium, High
    values=[
        [0.9, 0.5, 0.1],  # P(CRP=Low | Inflammation=Low/Med/High)
        [0.08, 0.3, 0.3],
        [0.02, 0.2, 0.6]
    ],
    evidence=['Inflammation'],
    evidence_card=[3]
)

model.add_cpds(cpd_crp)

# Inference
inference = VariableElimination(model)
result = inference.query(variables=['CRP'], evidence={'PM25': 2})  # High PM2.5
print(result)
```

**Scalability Considerations**:
- Exact inference (Variable Elimination): Fast for small graphs (<50 nodes)
- For larger graphs: Switch to approximate inference (Loopy Belief Propagation)
- Future: GPU-accelerated inference with Pyro

### Numerical Computation: NumPy + SciPy

**NumPy**: 1.26.2+
**SciPy**: 1.11.4+

**Usage**:
- Discretization of continuous biomarkers
- Statistical distributions for priors
- Linear algebra for graph operations

```python
import numpy as np
from scipy import stats

# Discretize continuous biomarker into states
def discretize_crp(value: float) -> int:
    """Convert CRP mg/L to Low/Med/High"""
    thresholds = [1.0, 3.0]
    return np.digitize(value, thresholds)

# Define prior distribution
def get_prior_distribution(mean: float, std: float):
    """Gaussian prior for biomarker baseline"""
    return stats.norm(loc=mean, scale=std)

# Sample trajectories
def monte_carlo_simulation(model, n_samples=1000):
    """Sample future trajectories from Bayesian network"""
    from pgmpy.sampling import BayesianModelSampling
    sampler = BayesianModelSampling(model)
    return sampler.forward_sample(size=n_samples)
```

### Time Series: Pandas

**Version**: 2.1.4+

**Why Pandas**:
- ✅ Time series indexing
- ✅ Resampling, interpolation
- ✅ Easy aggregation (rolling means, etc.)
- ✅ CSV/JSON export

**Usage**:
```python
import pandas as pd

# Store observations
observations = pd.DataFrame([
    {"date": "2025-07-15", "CRP": 0.7, "IL-6": 1.1},
    {"date": "2025-10-15", "CRP": 1.8, "IL-6": 2.7},
    {"date": "2025-12-15", "CRP": 1.9, "IL-6": 2.4}
])

observations['date'] = pd.to_datetime(observations['date'])
observations.set_index('date', inplace=True)

# Resample to daily (forward-fill)
daily = observations.resample('D').ffill()

# Compute rolling mean
observations['CRP_7day_avg'] = observations['CRP'].rolling(7).mean()
```

## Frontend Stack

### Framework: Next.js 14

**Version**: 14.0.0+

**Why Next.js**:
- ✅ Server-Side Rendering (SSR) for SEO
- ✅ API routes (can host some backend logic)
- ✅ Excellent developer experience
- ✅ Production-ready defaults

**Alternative for Hackathon**: Plain HTML/JS + Chart.js (faster setup)

**Project Structure**:
```
frontend/
├── app/
│   ├── page.tsx           # Home page
│   ├── query/
│   │   └── page.tsx       # Query interface
│   └── api/
│       └── proxy.ts       # Proxy to backend
├── components/
│   ├── Timeline.tsx       # Biomarker timeline
│   ├── CausalGraph.tsx    # D3/react-flow graph
│   └── Explanations.tsx   # Mechanism explanations
├── lib/
│   └── api.ts             # API client
└── public/
    └── assets/
```

### Visualization: Recharts + D3.js

**Recharts**: 2.10.0+ (for timelines)
**D3.js**: 7.8.0+ (for causal graphs)

**Why This Combo**:
- Recharts: Declarative, React-friendly, great for standard charts
- D3: Full control for custom graph layouts

**Timeline Component**:
```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export function BiomarkerTimeline({ predictions, actuals }) {
  const data = [
    { day: 0, crp_pred: 0.7, crp_actual: 0.7 },
    { day: 30, crp_pred: 1.3, crp_actual: null },
    { day: 60, crp_pred: 1.9, crp_actual: 1.8 },
    { day: 90, crp_pred: 2.4, crp_actual: null }
  ];

  return (
    <LineChart width={800} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="day" label={{ value: 'Days', position: 'bottom' }} />
      <YAxis label={{ value: 'CRP (mg/L)', angle: -90, position: 'left' }} />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="crp_pred" stroke="#ff7300" strokeDasharray="5 5" name="Predicted" />
      <Line type="monotone" dataKey="crp_actual" stroke="#ff7300" strokeWidth={0} dot={{ r: 5 }} name="Actual" />
    </LineChart>
  );
}
```

**Causal Graph Component**:
```tsx
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export function CausalGraph({ nodes, edges }) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = 600;
    const height = 400;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(edges).id(d => d.id))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Draw edges
    const link = svg.append('g')
      .selectAll('line')
      .data(edges)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-width', d => d.weight * 3);

    // Draw nodes
    const node = svg.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', 10)
      .attr('fill', d => d.type === 'genetic' ? '#4285F4' : '#34A853');

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
    });
  }, [nodes, edges]);

  return <svg ref={svgRef} />;
}
```

### Styling: TailwindCSS

**Version**: 3.4.0+

**Why Tailwind**:
- ✅ Utility-first (fast prototyping)
- ✅ Consistent design system
- ✅ Small production bundle (purged unused CSS)

**Configuration**:
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'aeon-blue': '#4285F4',
        'aeon-green': '#34A853',
        'aeon-red': '#EA4335',
      }
    }
  }
}
```

## Data Layer

### Hackathon: SQLite

**Why SQLite for Hackathon**:
- ✅ Zero configuration (no server)
- ✅ File-based (easy to inspect)
- ✅ Fast for single-user scenarios
- ✅ Sufficient for demo

**Schema**:
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE genetic_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT REFERENCES users(user_id),
    gene TEXT,
    variant TEXT,
    zygosity TEXT
);

CREATE TABLE biomarker_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT REFERENCES users(user_id),
    timestamp TIMESTAMP,
    biomarker TEXT,
    value REAL,
    unit TEXT,
    source TEXT
);

CREATE INDEX idx_biomarker_user_time ON biomarker_observations(user_id, timestamp);
```

**Python Integration**:
```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect('aeon.db')
    conn.row_factory = sqlite3.Row  # Return rows as dicts
    try:
        yield conn
    finally:
        conn.close()

def get_user_biomarkers(user_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, biomarker, value
            FROM biomarker_observations
            WHERE user_id = ?
            ORDER BY timestamp
        """, (user_id,))
        return cursor.fetchall()
```

### Production: PostgreSQL

**Version**: 15+

**Why PostgreSQL for Production**:
- ✅ ACID compliance
- ✅ JSON support (for flexible graph storage)
- ✅ Full-text search
- ✅ TimescaleDB extension for time-series

**Enhancements**:
```sql
-- Use JSONB for flexible graph storage
CREATE TABLE causal_graphs (
    id SERIAL PRIMARY KEY,
    user_id TEXT REFERENCES users(user_id),
    query TEXT,
    graph_data JSONB,  -- Store full graph structure
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_graph_data ON causal_graphs USING GIN (graph_data);

-- Use TimescaleDB for time-series
CREATE EXTENSION IF NOT EXISTS timescaledb;

SELECT create_hypertable('biomarker_observations', 'timestamp');
```

### Caching: Redis

**Version**: 7.2+

**Why Redis for Production**:
- ✅ Cache INDRA API responses (expensive queries)
- ✅ Session management
- ✅ Rate limiting

**Usage**:
```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_indra_response(query_key: str, data: dict, ttl: int = 3600):
    """Cache INDRA response for 1 hour"""
    redis_client.setex(query_key, ttl, json.dumps(data))

def get_cached_indra(query_key: str):
    """Retrieve cached INDRA response"""
    data = redis_client.get(query_key)
    return json.loads(data) if data else None
```

## Development Tools

### Dependency Management: Poetry

**Why Poetry**:
- ✅ Deterministic builds (lock file)
- ✅ Virtual environment management
- ✅ Dependency resolution

**pyproject.toml**:
```toml
[tool.poetry]
name = "aeon-gateway"
version = "0.1.0"
description = "Personalized Causal Health Modeling API"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.1"
uvicorn = "^0.24.0"
pydantic = "^2.5.0"
httpx = "^0.25.2"
networkx = "^3.2"
pgmpy = "^0.1.25"
numpy = "^1.26.2"
pandas = "^2.1.4"
langgraph = "^0.0.40"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
black = "^23.11.0"
mypy = "^1.7.0"
```

### Linting: Black + MyPy

**Black**: Code formatting (opinionated, no config)
**MyPy**: Static type checking

```bash
# Format code
black src/

# Type check
mypy src/ --strict
```

### Testing: pytest

```python
# tests/test_graph_engine.py
import pytest
from graph_engine import SimpleCausalGraph

def test_simple_prediction():
    graph = SimpleCausalGraph()
    graph.add_path(["PM2.5", "IL-6", "CRP"], weight=0.8)

    result = graph.predict({"PM2.5": 10.0})

    assert "CRP" in result
    assert result["CRP"] > 0
```

## Deployment

### Hackathon: Local Development

```bash
# Backend
uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev
```

### Production: Docker + Railway/Fly.io

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY src/ ./src/

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Railway deployment**:
```bash
railway login
railway init
railway up
```

## Monitoring & Observability

### Logging: Loguru

```python
from loguru import logger

logger.add("aeon.log", rotation="500 MB", retention="10 days")

@app.post("/api/query")
async def process_query(request: QueryRequest):
    logger.info(f"Query received: {request.query}")
    try:
        result = await orchestrator.run(request)
        logger.success(f"Query completed: {request.user_id}")
        return result
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise
```

### Metrics: Prometheus + Grafana

```python
from prometheus_client import Counter, Histogram

query_counter = Counter('aeon_queries_total', 'Total queries processed')
query_latency = Histogram('aeon_query_latency_seconds', 'Query latency')

@query_latency.time()
@app.post("/api/query")
async def process_query(request: QueryRequest):
    query_counter.inc()
    # ... process query
```

## Summary Matrix

| Layer | Hackathon | Production | Why |
|-------|-----------|------------|-----|
| **API** | FastAPI | FastAPI | Async, fast, great DX |
| **Agents** | LangGraph | LangGraph | State management |
| **Graphs** | NetworkX | NetworkX | Sufficient for scale |
| **Bayes** | pgmpy | Pyro (GPU) | Start simple, scale later |
| **HTTP** | httpx | httpx | Async-native |
| **DB** | SQLite | PostgreSQL | Zero config → Production-ready |
| **Cache** | None | Redis | INDRA responses |
| **Frontend** | HTML/JS | Next.js | Speed → Polish |
| **Charts** | Chart.js | Recharts | Quick → React integration |
| **Graphs** | D3.js | react-flow | Full control → Easier maintenance |
| **Deploy** | Local | Railway/Fly | Simple → Scalable |

**Philosophy**: Start simple, optimize when necessary. Don't over-engineer for the hackathon, but choose technologies that scale.
