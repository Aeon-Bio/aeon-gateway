# UI Integration Specification

## For: Frontend/UI Team

**Audience**: Team building the user-facing application
**Purpose**: Define how your UI integrates with the Aeon Gateway API

---

## Overview

The Aeon Gateway provides a REST API that accepts health queries and returns temporal predictions for biomarkers. Your UI is responsible for:

1. **User Input**: Collecting user context (genetics, current biomarkers, location history)
2. **Query Submission**: Sending queries to gateway
3. **Visualization**: Displaying prediction timelines, risk levels, and causal explanations
4. **Observation Updates**: Sending new biomarker measurements to update models

**You OWN**: User authentication, data entry, visualization, UX
**We OWN**: Temporal modeling, predictions, causal graph processing

---

## Required API Integration

### Base URL

```
Development: http://localhost:8000
Production: https://api.aeon.bio  (TBD)
```

### Authentication (Future)

Not implemented in MVP. Future versions will require:
```
Authorization: Bearer <jwt_token>
```

---

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if gateway is online.

**Response**:
```json
{
  "status": "healthy",
  "service": "aeon-gateway",
  "version": "0.1.0"
}
```

**When to use**:
- On app startup
- Before critical operations
- Health dashboard

---

### 2. Submit Query (Primary Endpoint)

**POST** `/api/v1/gateway/query`

Submit a health query and receive biomarker predictions.

#### Request Format

**Minimum Required Fields** (what you should send):

```json
{
  "user_context": {
    "user_id": "sarah_chen",
    "genetics": {
      "APOE": "e3/e3",
      "IL6": "GG"
    },
    "current_biomarkers": {
      "CRP": 0.7,
      "IL6": 1.2
    },
    "location_history": [
      {
        "city": "San Francisco",
        "state": "CA",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01"
      },
      {
        "city": "Los Angeles",
        "state": "CA",
        "start_date": "2024-01-01",
        "end_date": null
      }
    ]
  },
  "query": {
    "text": "How will my inflammation markers change in LA?"
  }
}
```

**Full Format with Optional Fields**:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",  // OPTIONAL: Auto-generated if missing
  "user_context": {
    "user_id": "string",                                 // REQUIRED: unique user identifier
    "genetics": {                                        // REQUIRED: genetic variants (can be empty {})
      "GSTM1": "null",
      "APOE": "e3/e4",
      "IL6": "GG"
    },
    "current_biomarkers": {                             // REQUIRED: baseline measurements
      "CRP": 0.7,                                       // C-Reactive Protein (mg/L)
      "IL6": 1.2                                        // Interleukin-6 (pg/mL)
    },
    "location_history": [                               // REQUIRED: environmental context
      {
        "city": "San Francisco",
        "state": "CA",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01"                        // null if current
      },
      {
        "city": "Los Angeles",
        "state": "CA",
        "start_date": "2024-01-01",
        "end_date": null
      }
    ]
  },
  "query": {
    "text": "How will my inflammation markers change in LA?",   // REQUIRED: user's question
    "intent": "prediction",                             // OPTIONAL: Not used currently
    "focus_biomarkers": ["CRP", "IL6"]                  // OPTIONAL: Not used currently
  },
  "options": {                                          // OPTIONAL: Future use
    "horizon_days": 90,
    "n_simulations": 1000
  }
}
```

**Field Descriptions**:

| Field | Required? | Default | Description |
|-------|-----------|---------|-------------|
| `request_id` | No | Auto-generated UUID | Request tracking ID |
| `user_context.user_id` | **Yes** | - | Unique user identifier |
| `user_context.genetics` | **Yes** | - | Genetic variants (can be `{}`) |
| `user_context.current_biomarkers` | **Yes** | - | Baseline biomarker values |
| `user_context.location_history` | **Yes** | - | Location history (can be `[]`) |
| `query.text` | **Yes** | - | User's natural language query |
| `query.intent` | No | - | Query intent (not used) |
| `query.focus_biomarkers` | No | - | Target biomarkers (not used) |
| `options` | No | `{}` | Future configuration options |

#### Response Format

```json
{
  "query_id": "uuid-v4",           // For tracking/logging
  "user_id": "sarah_chen",
  "predictions": {
    "CRP": {
      "baseline": 0.7,             // Current value
      "timeline": [
        {
          "day": 0,                // Days from now
          "mean": 0.7,             // Predicted mean value
          "confidence_interval": [0.65, 0.75],  // 95% CI [lower, upper]
          "risk_level": "low"      // low | moderate | high | unknown
        },
        {
          "day": 30,
          "mean": 1.19,
          "confidence_interval": [1.16, 1.23],
          "risk_level": "moderate"
        },
        {
          "day": 60,
          "mean": 1.69,
          "confidence_interval": [1.64, 1.73],
          "risk_level": "moderate"
        },
        {
          "day": 90,
          "mean": 2.18,
          "confidence_interval": [2.12, 2.23],
          "risk_level": "moderate"
        }
      ],
      "unit": "mg/L"               // Units for this biomarker
    },
    "IL6": {
      // Same structure as CRP
    }
  },
  "causal_graph": {
    "nodes": [
      {
        "id": "PM2.5",
        "type": "environmental",   // environmental | molecular | biomarker | genetic
        "label": "Particulate Matter (PM2.5)",
        "grounding": {
          "database": "MESH",
          "identifier": "D052638"
        }
      }
      // ... more nodes
    ],
    "edges": [
      {
        "source": "PM2.5",
        "target": "NFKB1",
        "relationship": "activates",  // activates | inhibits | increases | decreases
        "evidence": {
          "count": 47,
          "confidence": 0.82,
          "sources": ["PMID:12345678"],
          "summary": "PM2.5 activates NF-κB signaling"
        },
        "effect_size": 0.65,        // [0, 1] scale
        "temporal_lag_hours": 6     // How long before effect manifests
      }
      // ... more edges
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
  "explanations": [
    "PM2.5 exposure increased 3.4× after moving to LA",
    "Your GSTM1 null variant amplifies oxidative stress response by 30%",
    "Expected CRP elevation from 0.7 to ~2.4 mg/L"
  ]
}
```

#### Error Responses

**422 Validation Error** - Invalid request format
```json
{
  "detail": [
    {
      "loc": ["body", "user_context", "current_biomarkers", "CRP"],
      "msg": "CRP must be non-negative, got -0.5",
      "type": "value_error"
    }
  ]
}
```

**500 Internal Server Error** - Processing failed
```json
{
  "detail": "Query processing failed: <error message>"
}
```

---

## UI Integration Patterns

### Pattern 1: Query Form

**User Flow**:
1. User enters query: "How will LA affect my inflammation?"
2. UI submits to `/api/v1/gateway/query` with user context
3. Display loading state (predictions take 0.5-3s)
4. Render timeline visualization on success

**Code Example** (JavaScript):
```javascript
async function submitQuery(userContext, queryText) {
  const response = await fetch('http://localhost:8000/api/v1/gateway/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_context: userContext,
      query: { text: queryText }
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
}
```

### Pattern 2: Timeline Visualization

**Requirements**:
- X-axis: Days (0, 30, 60, 90)
- Y-axis: Biomarker value with units
- Line: Mean prediction
- Shaded area: 95% confidence interval
- Color coding: Risk levels (green=low, yellow=moderate, red=high)

**Recommended Libraries**:
- Chart.js (simple, demo-ready)
- D3.js (complex, customizable)
- Plotly (interactive)

**Example** (Chart.js):
```javascript
function renderTimeline(biomarker, prediction) {
  const ctx = document.getElementById('chart').getContext('2d');

  const days = prediction.timeline.map(p => p.day);
  const means = prediction.timeline.map(p => p.mean);
  const lowerCI = prediction.timeline.map(p => p.confidence_interval[0]);
  const upperCI = prediction.timeline.map(p => p.confidence_interval[1]);

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: days,
      datasets: [
        {
          label: `${biomarker} (Mean)`,
          data: means,
          borderColor: '#667eea',
          borderWidth: 3
        },
        {
          label: '95% CI',
          data: lowerCI.map((lower, i) => [lower, upperCI[i]]),
          backgroundColor: 'rgba(102, 126, 234, 0.2)',
          fill: true
        }
      ]
    }
  });
}
```

### Pattern 3: Causal Graph Display

**Requirements**:
- Nodes: Show label and type (environmental vs biomarker)
- Edges: Show relationship and effect size
- Interactive: Click to see evidence summaries

**Optional**: Use D3.js force-directed graph or Cytoscape.js

### Pattern 4: Risk Indicators

**Risk Levels**:
- `"low"`: Green badge, "Low Risk"
- `"moderate"`: Yellow badge, "Moderate Risk"
- `"high"`: Red badge, "High Risk"
- `"unknown"`: Gray badge, "Unknown Risk"

**UI Pattern**:
```jsx
function RiskBadge({ level }) {
  const colors = {
    low: 'bg-green-100 text-green-800',
    moderate: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800',
    unknown: 'bg-gray-100 text-gray-800'
  };

  return (
    <span className={`px-3 py-1 rounded-full ${colors[level]}`}>
      {level.toUpperCase()} RISK
    </span>
  );
}
```

---

## Data Requirements from Users

To submit a query, your UI must collect:

### 1. Genetic Information (Optional but Recommended)

**How to collect**:
- File upload (23andMe, Ancestry.com raw data)
- Manual entry for key variants
- Skip if unavailable (empty `{}`)

**Key variants to prioritize**:
- `GSTM1`: null or present (oxidative stress)
- `APOE`: e2/e3/e4 variants (inflammation)
- `IL6`: SNPs affecting IL-6 response
- `TNF-alpha`: -308G/A (TNF response)

**Example**:
```json
{
  "GSTM1": "null",
  "APOE": "e3/e3",
  "IL6": "GG"
}
```

### 2. Current Biomarkers (Required)

**How to collect**:
- Import from lab results (PDF/CSV parsing)
- Manual entry with date
- Connect to health APIs (Apple Health, wearables)

**Common biomarkers**:
- `CRP`: C-Reactive Protein (mg/L) - inflammation
- `IL6`: Interleukin-6 (pg/mL) - inflammation
- `HbA1c`: Hemoglobin A1c (%) - glucose control
- `LDL`: LDL Cholesterol (mg/dL)

**Validation**:
- All values must be **non-negative**
- Include units for user clarity
- Show reference ranges

**Example**:
```json
{
  "CRP": 0.7,
  "IL6": 1.2,
  "HbA1c": 5.4
}
```

### 3. Location History (Required)

**How to collect**:
- Current location + move date
- Historical addresses with date ranges
- Pull from user profile

**Example**:
```json
[
  {
    "city": "San Francisco",
    "state": "CA",
    "start_date": "2020-01-01",
    "end_date": "2024-08-31"
  },
  {
    "city": "Los Angeles",
    "state": "CA",
    "start_date": "2024-09-01",
    "end_date": null  // Current location
  }
]
```

---

## UI States to Handle

### Loading State
```
⏳ Analyzing causal pathways and simulating trajectories...
Expected time: 2-3 seconds
```

### Success State
- Display predictions timeline
- Show risk badges
- Render causal graph (optional)
- List explanations

### Error States

**Validation Error (422)**:
```
❌ Invalid input: CRP value must be non-negative
Please check your biomarker values and try again.
```

**Server Error (500)**:
```
❌ Unable to process query
Please try again or contact support if the issue persists.
```

**Network Error**:
```
❌ Connection failed
Check your internet connection and try again.
```

---

## Performance Expectations

| Operation | Expected Time | Max Time |
|-----------|--------------|----------|
| `/health` check | <50ms | 200ms |
| Simple query | 500ms-1s | 3s |
| Complex query (many biomarkers) | 1-2s | 5s |

**Recommendations**:
- Show loading state after 300ms
- Timeout queries after 10s
- Cache responses for repeated queries

---

## Testing Your Integration

### 1. Use the Demo Frontend

We provide a reference implementation:
```bash
open frontend/index.html
```

This shows:
- How to structure requests
- How to render timelines
- How to display risk levels

### 2. Test with Mock Data

Sarah's SF→LA scenario (guaranteed to work):
```json
{
  "user_context": {
    "user_id": "test_user",
    "genetics": {"APOE": "e3/e3", "IL6": "GG"},
    "current_biomarkers": {"CRP": 0.7, "IL6": 1.2},
    "location_history": [
      {"city": "San Francisco", "state": "CA", "start_date": "2023-01-01", "end_date": "2024-01-01"},
      {"city": "Los Angeles", "state": "CA", "start_date": "2024-01-01", "end_date": null}
    ]
  },
  "query": {
    "text": "How will my inflammation markers change in LA?"
  }
}
```

### 3. Validate Responses

Check that responses have:
- `predictions` with at least one biomarker
- `timeline` with 4 data points (days 0, 30, 60, 90)
- `confidence_interval` as 2-element array
- `risk_level` in valid set

---

## Integration Checklist

- [ ] Health check on app startup
- [ ] Form to collect user context
- [ ] Validation for biomarker values (non-negative)
- [ ] Loading state during query (2-3s)
- [ ] Timeline visualization with confidence intervals
- [ ] Risk level badges (color-coded)
- [ ] Display causal explanations
- [ ] Error handling (422, 500, network)
- [ ] Responsive design for mobile
- [ ] Accessibility (ARIA labels, keyboard nav)

---

## FAQ

**Q: What if user doesn't have genetic data?**
A: Send empty object: `"genetics": {}`

**Q: What if user only has one biomarker?**
A: That's fine - predictions will focus on that biomarker

**Q: How do I handle multiple biomarkers?**
A: Response includes `predictions` object with one entry per biomarker. Render separate charts or tabs.

**Q: What units should I display?**
A: Use `unit` field from response (e.g., "mg/L", "pg/mL")

**Q: Can I customize prediction horizon?**
A: Not in MVP (fixed 90 days). Future versions will support this.

**Q: How do I update the model with new measurements?**
A: Future endpoint: `POST /api/v1/gateway/update_observation` (not yet implemented)

---

## Contact

For integration questions:
- API issues: Check `/health` endpoint
- Schema questions: See `src/models/gateway.py` for Pydantic models
- Demo reference: `frontend/index.html`

---

## Version History

- **v0.1.0** (Current): Initial MVP with `/api/v1/gateway/query`
- **v0.2.0** (Planned): Add `/update_observation` endpoint
- **v0.3.0** (Planned): Add authentication
