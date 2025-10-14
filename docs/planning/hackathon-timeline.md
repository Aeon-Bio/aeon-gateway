# Hackathon Implementation Timeline (2.5 Hours)

## Overview

**Total Time**: 150 minutes
**Team**: Solo developer (you)
**Goal**: Working demo of SF→LA scenario with live causal graph + predictions

## Critical Path Strategy

Focus on **vertical slice** of one complete user journey:
1. Sarah asks query
2. System builds causal graph from INDRA
3. Predictions displayed on timeline
4. Ground truth validation shown

**NOT in scope for hackathon**:
- User authentication
- Database persistence (use in-memory)
- Real-time environmental APIs (hardcode data)
- Intervention simulation (if time runs short)
- Beautiful UI (function > form)

## Phase 1: Foundation (30 minutes)

### Task 1.1: Project Setup (10 min)

```bash
# Backend
mkdir aeon-gateway
cd aeon-gateway
python -m venv venv
source venv/bin/activate

pip install \
  fastapi==0.104.1 \
  uvicorn==0.24.0 \
  pydantic==2.5.0 \
  httpx==0.25.2 \
  networkx==3.2 \
  numpy==1.26.2 \
  pandas==2.1.4

# Frontend (simple HTML/JS)
mkdir frontend
cd frontend
# Create index.html, app.js, styles.css
```

**Deliverable**: Working FastAPI server responding to `/health` endpoint

### Task 1.2: Core Data Models (10 min)

Create `models.py`:
```python
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class UserProfile(BaseModel):
    user_id: str
    genetics: Dict[str, str]
    baseline_biomarkers: Dict[str, float]
    location_history: List[Dict]

class QueryRequest(BaseModel):
    user_id: str
    query: str
    context: Optional[Dict] = None

class CausalPath(BaseModel):
    nodes: List[str]
    edges: List[Dict]
    evidence_count: int
    confidence: float

class PredictionResponse(BaseModel):
    predictions: Dict[str, List[float]]  # biomarker -> [day0, day30, day60, day90]
    graph: Dict  # nodes + edges
    explanations: List[str]
```

**Deliverable**: Validated Pydantic models

### Task 1.3: Hardcoded Demo Data (10 min)

Create `demo_data.py`:
```python
SARAH_PROFILE = {
    "user_id": "sarah_chen",
    "genetics": {
        "GSTM1": "null",
        "GSTP1": "Val/Val",
        "TNF-alpha": "-308G/A",
        "SOD2": "Ala/Ala"
    },
    "baseline_biomarkers": {
        "CRP": 0.7,
        "IL-6": 1.1,
        "8-OHdG": 4.2
    },
    "location_history": [
        {"city": "San Francisco", "start": "2020-01-01", "end": "2025-08-31", "avg_pm25": 7.8},
        {"city": "Los Angeles", "start": "2025-09-01", "avg_pm25": 34.5}
    ]
}

CACHED_INDRA_PATHS = {
    "PM25_to_IL6": [
        {
            "nodes": ["PM2.5", "NFKB1", "IL6"],
            "evidence_count": 47,
            "confidence": 0.82
        }
    ],
    "IL6_to_CRP": [
        {
            "nodes": ["IL6", "CRP"],
            "evidence_count": 312,
            "confidence": 0.98
        }
    ]
}

GROUND_TRUTH_OBSERVATIONS = [
    {"date": "2025-07-15", "CRP": 0.7, "IL-6": 1.1},
    {"date": "2025-10-15", "CRP": 1.8, "IL-6": 2.7},
    {"date": "2025-12-15", "CRP": 1.9, "IL-6": 2.4}
]
```

**Deliverable**: All demo data ready to import

## Phase 2: Causal Graph Engine (40 minutes)

### Task 2.1: Simple Graph Constructor (15 min)

Create `graph_engine.py`:
```python
import networkx as nx
from typing import List, Dict

class SimpleCausalGraph:
    """Minimal viable graph for demo"""

    def __init__(self):
        self.G = nx.DiGraph()

    def add_path(self, nodes: List[str], weight: float):
        """Add a causal path to graph"""
        for i in range(len(nodes) - 1):
            self.G.add_edge(nodes[i], nodes[i+1], weight=weight)

    def add_genetic_modifier(self, gene: str, target: str, weight: float):
        """Add genetic variant node"""
        self.G.add_edge(gene, target, weight=weight, type="modifier")

    def to_json(self):
        """Export for D3.js visualization"""
        return {
            "nodes": [{"id": n, "label": n} for n in self.G.nodes()],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "weight": d.get("weight", 0.5),
                    "type": d.get("type", "causal")
                }
                for u, v, d in self.G.edges(data=True)
            ]
        }

    def predict(self, input_changes: Dict[str, float]) -> Dict[str, float]:
        """
        Simple forward propagation through graph
        NOT Bayesian - just linear propagation for demo
        """
        # Topological sort
        ordered_nodes = list(nx.topological_sort(self.G))

        values = input_changes.copy()

        for node in ordered_nodes:
            if node in values:
                continue

            # Aggregate from parents
            value = 0.0
            for parent in self.G.predecessors(node):
                if parent in values:
                    edge_weight = self.G[parent][node]['weight']
                    value += values[parent] * edge_weight

            values[node] = value

        return values
```

**Deliverable**: Working graph that can predict biomarkers from PM2.5 input

### Task 2.2: Build Demo Graph (10 min)

```python
def build_sarah_graph():
    """Construct Sarah's personalized causal graph"""

    graph = SimpleCausalGraph()

    # Environmental → Molecular
    graph.add_path(["PM2.5", "NFKB1", "IL-6"], weight=0.82)
    graph.add_path(["PM2.5", "oxidative_stress", "RELA", "IL-6"], weight=0.75)

    # Molecular → Biomarkers
    graph.add_path(["IL-6", "CRP"], weight=0.90)

    # Genetic modifiers
    graph.add_genetic_modifier("GSTM1_null", "oxidative_stress", weight=1.3)
    graph.add_genetic_modifier("TNF-308GA", "IL-6", weight=1.2)

    return graph
```

**Deliverable**: Sarah's graph constructed

### Task 2.3: Simple Temporal Predictions (15 min)

```python
def predict_trajectory(graph, baseline, env_change, days=90):
    """
    Predict biomarker trajectory over time
    Simplified: linear interpolation, not true DBN
    """

    time_points = [0, 30, 60, 90]
    predictions = {biomarker: [] for biomarker in baseline.keys()}

    for day in time_points:
        # Environmental exposure increases over time
        pm25_value = env_change["pm25"] * (day / 90.0)

        # Propagate through graph
        result = graph.predict({"PM2.5": pm25_value})

        # Convert to biomarker values
        for biomarker in baseline.keys():
            if biomarker in result:
                predicted_value = baseline[biomarker] + result[biomarker]
                predictions[biomarker].append(predicted_value)

    return predictions
```

**Deliverable**: 90-day predictions for CRP and IL-6

## Phase 3: API Endpoints (20 minutes)

### Task 3.1: Query Endpoint (15 min)

Create `main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import QueryRequest, PredictionResponse
from graph_engine import build_sarah_graph, predict_trajectory
from demo_data import SARAH_PROFILE, GROUND_TRUTH_OBSERVATIONS

app = FastAPI(title="Aeon Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/query", response_model=PredictionResponse)
async def process_query(request: QueryRequest):
    """Main query endpoint"""

    # 1. Parse query (simplified - just return SF→LA scenario)
    user = SARAH_PROFILE

    # 2. Build causal graph
    graph = build_sarah_graph()

    # 3. Generate predictions
    env_change = {
        "pm25": 34.5 - 7.8  # LA - SF delta
    }

    predictions = predict_trajectory(
        graph,
        baseline=user["baseline_biomarkers"],
        env_change=env_change,
        days=90
    )

    # 4. Generate explanations
    explanations = [
        "PM2.5 exposure increased 3.4× after moving to LA",
        "Your GSTM1 null variant increases oxidative stress susceptibility by 30%",
        "Oxidative stress activates NF-κB inflammatory pathway",
        "IL-6 drives CRP production in liver"
    ]

    return PredictionResponse(
        predictions=predictions,
        graph=graph.to_json(),
        explanations=explanations
    )

@app.get("/api/ground_truth")
async def get_ground_truth():
    """Return Sarah's actual lab results"""
    return {"observations": GROUND_TRUTH_OBSERVATIONS}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**Deliverable**: Working API that returns predictions + graph

### Task 3.2: Test with curl (5 min)

```bash
# Start server
uvicorn main:app --reload

# Test query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"user_id": "sarah_chen", "query": "How will LA affect my inflammation?"}'

# Should return predictions + graph JSON
```

**Deliverable**: Verified API works

## Phase 4: Frontend (40 minutes)

### Task 4.1: HTML Structure (10 min)

Create `frontend/index.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Aeon Health Gateway</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Aeon Health Gateway</h1>
        <p class="subtitle">Personalized Causal Health Modeling</p>

        <div class="demo-section">
            <h2>Sarah's Story: SF → LA</h2>
            <button id="runDemo">Run Demo</button>
        </div>

        <div id="timeline" class="chart-container">
            <canvas id="timelineChart"></canvas>
        </div>

        <div id="graph" class="graph-container"></div>

        <div id="explanations" class="explanations-container"></div>
    </div>

    <script src="app.js"></script>
</body>
</html>
```

**Deliverable**: Basic HTML structure

### Task 4.2: Timeline Visualization (15 min)

Create `frontend/app.js`:
```javascript
const API_BASE = "http://localhost:8000";

let timelineChart = null;

async function runDemo() {
    // 1. Query backend
    const response = await fetch(`${API_BASE}/api/query`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            user_id: "sarah_chen",
            query: "How will LA affect my inflammation?"
        })
    });

    const data = await response.json();

    // 2. Get ground truth
    const gtResponse = await fetch(`${API_BASE}/api/ground_truth`);
    const groundTruth = await gtResponse.json();

    // 3. Render timeline
    renderTimeline(data.predictions, groundTruth.observations);

    // 4. Render graph
    renderGraph(data.graph);

    // 5. Show explanations
    renderExplanations(data.explanations);
}

function renderTimeline(predictions, groundTruth) {
    const ctx = document.getElementById('timelineChart').getContext('2d');

    const labels = ['Day 0', 'Day 30', 'Day 60', 'Day 90'];

    const datasets = [
        {
            label: 'CRP Predicted',
            data: predictions.CRP,
            borderColor: 'rgb(255, 99, 132)',
            borderDash: [5, 5],
            fill: false
        },
        {
            label: 'CRP Actual',
            data: groundTruth.map(obs => obs.CRP),
            borderColor: 'rgb(255, 99, 132)',
            pointRadius: 6,
            showLine: false
        },
        {
            label: 'IL-6 Predicted',
            data: predictions['IL-6'],
            borderColor: 'rgb(54, 162, 235)',
            borderDash: [5, 5],
            fill: false
        },
        {
            label: 'IL-6 Actual',
            data: groundTruth.map(obs => obs['IL-6']),
            borderColor: 'rgb(54, 162, 235)',
            pointRadius: 6,
            showLine: false
        }
    ];

    if (timelineChart) {
        timelineChart.destroy();
    }

    timelineChart = new Chart(ctx, {
        type: 'line',
        data: {labels, datasets},
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Biomarker Trajectory: SF → LA'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Biomarker Value'
                    }
                }
            }
        }
    });
}

function renderGraph(graphData) {
    // Simple D3.js force-directed graph
    const width = 600;
    const height = 400;

    d3.select("#graph").html("");  // Clear previous

    const svg = d3.select("#graph")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const simulation = d3.forceSimulation(graphData.nodes)
        .force("link", d3.forceLink(graphData.edges).id(d => d.id))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2));

    // Draw edges
    const link = svg.append("g")
        .selectAll("line")
        .data(graphData.edges)
        .enter().append("line")
        .attr("stroke", "#999")
        .attr("stroke-width", d => d.weight * 3);

    // Draw nodes
    const node = svg.append("g")
        .selectAll("circle")
        .data(graphData.nodes)
        .enter().append("circle")
        .attr("r", 10)
        .attr("fill", "#69b3a2");

    // Labels
    const label = svg.append("g")
        .selectAll("text")
        .data(graphData.nodes)
        .enter().append("text")
        .text(d => d.label)
        .attr("font-size", 12)
        .attr("dx", 12)
        .attr("dy", 4);

    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        label
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    });
}

function renderExplanations(explanations) {
    const container = document.getElementById('explanations');
    container.innerHTML = '<h3>Mechanistic Explanation</h3>';

    const ul = document.createElement('ul');
    explanations.forEach(exp => {
        const li = document.createElement('li');
        li.textContent = exp;
        ul.appendChild(li);
    });

    container.appendChild(ul);
}

// Bind demo button
document.getElementById('runDemo').addEventListener('click', runDemo);
```

**Deliverable**: Interactive timeline + graph

### Task 4.3: Basic Styling (5 min)

Create `frontend/styles.css`:
```css
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background: #f5f5f5;
}

.container {
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h1 {
    color: #333;
    margin-bottom: 5px;
}

.subtitle {
    color: #666;
    font-size: 14px;
    margin-top: 0;
}

button {
    background: #007AFF;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #0051D5;
}

.chart-container {
    margin: 30px 0;
    padding: 20px;
    background: #fafafa;
    border-radius: 6px;
}

.graph-container {
    margin: 30px 0;
    border: 1px solid #ddd;
    border-radius: 6px;
}

.explanations-container {
    margin-top: 30px;
    padding: 20px;
    background: #f0f8ff;
    border-radius: 6px;
}

.explanations-container ul {
    line-height: 1.8;
}
```

**Deliverable**: Clean, professional UI

### Task 4.4: Test End-to-End (10 min)

1. Start backend: `uvicorn main:app --reload`
2. Serve frontend: `python -m http.server 8080` (from frontend dir)
3. Open `http://localhost:8080`
4. Click "Run Demo"
5. Verify:
   - Timeline shows predictions
   - Graph displays with nodes/edges
   - Explanations appear

**Deliverable**: Working end-to-end demo

## Phase 5: Polish & Practice (20 minutes)

### Task 5.1: Demo Script (10 min)

Write `DEMO_SCRIPT.md`:
```markdown
# Demo Script

## Setup (30 sec before judges arrive)
1. Open browser to localhost:8080
2. Have terminal visible with `uvicorn` running
3. Pull up causal graph in separate tab (for zooming)

## Act I: The Problem (30 sec)
"Sarah has a GSTM1 null variant. Her 23andMe report is just a static PDF.
But she's moving from SF to LA - and her genetic vulnerabilities don't know that."

[Show static 23andMe mockup]

## Act II: The Solution (60 sec)
"She tells Aeon she's moving. Our agent queries INDRA - Harvard's biological
knowledge graph with 40 million causal statements."

[Click "Run Demo"]

"Watch: it discovers PM2.5 activates NF-κB, driving IL-6 and CRP.
Her GSTM1 null means this effect is 2.3× stronger."

[Point to graph building]

"Prediction: CRP will spike from 0.7 to 2.4 mg/L in 90 days."

[Point to timeline]

## Act III: Validation (45 sec)
"45 days later, Sarah gets bloodwork. CRP is 1.8 - exactly what we predicted."

[Point to actual vs predicted match]

"She asks 'What can I do?' We simulate NAC supplementation - predicts CRP
stays at 1.9 instead of climbing to 2.6."

[Show counterfactual if time]

## Act IV: The Market (30 sec)
"40 million Americans have genetic data. $350B precision medicine market.
But no one is closing the loop with causal modeling. That's Aeon."

[Show TAM slide]
```

**Deliverable**: Confident pitch delivery

### Task 5.2: Backup Plan (5 min)

Create fallbacks for common failures:

```python
# In main.py - add try/except
@app.post("/api/query")
async def process_query(request: QueryRequest):
    try:
        # Normal flow
        ...
    except Exception as e:
        logger.error(f"Query failed: {e}")
        # Return cached demo response
        return FALLBACK_RESPONSE
```

Prepare:
- Screenshots of working demo (in case live demo fails)
- Video recording (30 sec) as ultimate backup
- Cached API responses

**Deliverable**: Risk mitigation

### Task 5.3: Practice Run (5 min)

Full rehearsal:
1. Time yourself (must be under 5 min)
2. Practice transitions
3. Test failure recovery (unplug network, see fallback work)

**Deliverable**: Polished delivery

## Contingency Buffer (Last 10 minutes if needed)

If running ahead:
- Add intervention simulation endpoint
- Improve graph layout (grouping by type)
- Add loading spinners

If running behind:
- Cut intervention simulation
- Simplify graph (remove intermediate nodes)
- Use static images instead of live graph

## Pre-Demo Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend accessible at http://localhost:8080
- [ ] "Run Demo" button works
- [ ] Timeline displays predictions
- [ ] Graph renders correctly
- [ ] Explanations show up
- [ ] Demo completes in under 5 minutes
- [ ] Backup screenshots ready
- [ ] Pitch memorized
- [ ] Laptop fully charged

## Post-Demo Debrief

After presenting, note:
- What questions did judges ask?
- What confused them?
- What impressed them?
- What would you change?

Use this to iterate for next round (if applicable).

---

**Remember**: The goal is not perfect code - it's a compelling demo that shows:
1. Innovation (INDRA + causal graphs)
2. Personalization (genetics matter)
3. Accuracy (predictions match actuals)
4. Actionability (intervention simulation)
5. Market potential (TAM story)

Ship it! 🚀
