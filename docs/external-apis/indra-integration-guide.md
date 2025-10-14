# INDRA Network Search API - Integration Guide

**For: Agentic System Team**

Based on actual INDRA API: https://network.indra.bio

---

## Overview

The agentic system queries INDRA to discover **causal paths** between environmental factors (like PM2.5) and biomarkers (like CRP). This guide explains how to use the real INDRA API.

**Key Endpoint**: `POST https://network.indra.bio/api/query`

---

## The Query Type: Shortest Path Search

For the SF→LA demo (PM2.5 → inflammation biomarkers), you need to find **shortest causal paths** between:

**Source nodes**: Environmental factors
- PM2.5 (Particulate Matter)
- O3 (Ozone)
- NO2 (Nitrogen Dioxide)

**Target nodes**: Biomarkers
- CRP (C-Reactive Protein)
- IL6 (Interleukin-6)
- TNF (Tumor Necrosis Factor)

---

## Request Format

### POST /query

**Endpoint**: `https://network.indra.bio/api/query`

**Request Body**:
```json
{
  "source": "PM2.5",           // Source node name
  "target": "CRP",             // Target node name (biomarker)
  "path_length": 5,            // Max path length (hops)
  "depth_limit": 3,            // Search depth limit
  "weighted": "belief",        // Weight by belief scores
  "belief_cutoff": 0.5,        // Minimum belief threshold
  "k_shortest": 10,            // Return top 10 shortest paths
  "stmt_filter": [],           // Optional: filter by statement types
  "filter_curated": true,      // Only curated sources
  "curated_db_only": false,    // Use all sources (not just curated DBs)
  "fplx_expand": true,         // Expand protein families
  "format": "json"
}
```

### Key Parameters Explained

| Parameter | Purpose | Recommended Value |
|-----------|---------|-------------------|
| `source` | Starting node (e.g., "PM2.5") | Environmental factor |
| `target` | Ending node (e.g., "CRP") | Biomarker name |
| `path_length` | Max hops in path | 5-7 (biological paths are short) |
| `depth_limit` | Search depth | 2-3 (limits computation) |
| `weighted` | Path scoring | "belief" (uses evidence strength) |
| `belief_cutoff` | Min confidence | 0.5-0.7 (filter weak evidence) |
| `k_shortest` | Number of paths | 10-50 (get alternatives) |
| `filter_curated` | Use curated data | true (higher quality) |
| `fplx_expand` | Expand protein families | true (finds more paths) |

---

## Response Format

### Success Response

```json
{
  "query_hash": "abc123...",
  "timed_out": false,
  "path_results": {
    "paths": {
      "PM2.5": [
        {
          "path": [
            {"name": "PM2.5", "namespace": "MESH", "id": "D052638"},
            {"name": "NFKB1", "namespace": "HGNC", "id": "7794"},
            {"name": "IL6", "namespace": "HGNC", "id": "6018"},
            {"name": "CRP", "namespace": "HGNC", "id": "2367"}
          ],
          "edges": [
            {
              "stmt_type": "Activation",
              "residue": null,
              "position": null,
              "source_counts": {"reach": 15, "sparser": 8},
              "belief": 0.85,
              "weight": 0.15,
              "z_score": 2.5,
              "corr_weight": 0.12
            },
            {
              "stmt_type": "IncreaseAmount",
              "residue": null,
              "position": null,
              "source_counts": {"reach": 42, "trips": 12},
              "belief": 0.92,
              "weight": 0.08,
              "z_score": 3.1,
              "corr_weight": 0.09
            },
            {
              "stmt_type": "Activation",
              "residue": null,
              "position": null,
              "source_counts": {"reach": 89, "medscan": 31},
              "belief": 0.98,
              "weight": 0.02,
              "z_score": 4.2,
              "corr_weight": 0.03
            }
          ]
        }
      ]
    }
  }
}
```

### Important Response Fields

| Field | Description | How to Use |
|-------|-------------|------------|
| `path` | List of nodes in order | Extract node names, IDs |
| `edges[].stmt_type` | Relationship type | Map to our relationships (activates, increases) |
| `edges[].belief` | Evidence strength | Use as `effect_size` |
| `edges[].source_counts` | Paper counts | Show evidence quality |
| `edges[].weight` | Path weight | Lower = stronger path |

---

## Mapping INDRA → Gateway Format

### Step 1: Extract Nodes

```python
def convert_indra_nodes(indra_path):
    nodes = []
    for node in indra_path['path']:
        node_type = classify_node(node['name'])  # environmental/molecular/biomarker

        nodes.append({
            "id": node['name'],
            "type": node_type,
            "label": node['name'],
            "grounding": {
                "database": node['namespace'],  # MESH, HGNC, etc.
                "identifier": node['id']
            }
        })
    return nodes
```

### Step 2: Convert Edges

```python
def convert_indra_edges(indra_path):
    edges = []
    for i, edge in enumerate(indra_path['edges']):
        source = indra_path['path'][i]['name']
        target = indra_path['path'][i+1]['name']

        # Map INDRA statement types to our relationships
        relationship = map_statement_type(edge['stmt_type'])

        edges.append({
            "source": source,
            "target": target,
            "relationship": relationship,  # activates/inhibits/increases/decreases
            "evidence": {
                "count": sum(edge['source_counts'].values()),
                "confidence": edge['belief'],
                "sources": list(edge['source_counts'].keys()),
                "summary": f"{edge['stmt_type']} relationship from INDRA"
            },
            "effect_size": edge['belief'],  # Use belief as effect size [0,1]
            "temporal_lag_hours": estimate_lag(source, target)  # Heuristic
        })
    return edges
```

### Step 3: Statement Type Mapping

```python
INDRA_TO_RELATIONSHIP = {
    "Activation": "activates",
    "Inhibition": "inhibits",
    "IncreaseAmount": "increases",
    "DecreaseAmount": "decreases",
    "Phosphorylation": "activates",  # Generally activating
    "Dephosphorylation": "inhibits",  # Generally inhibiting
    # Add more mappings as needed
}
```

---

## Example Query Flow

### 1. Query INDRA for PM2.5 → CRP

```python
import httpx

query = {
    "source": "PM2.5",
    "target": "CRP",
    "path_length": 5,
    "depth_limit": 3,
    "weighted": "belief",
    "belief_cutoff": 0.6,
    "k_shortest": 10,
    "filter_curated": True,
    "fplx_expand": True,
    "format": "json"
}

response = httpx.post(
    "https://network.indra.bio/api/query",
    json=query,
    timeout=30.0
)

result = response.json()
```

### 2. Extract Best Path

```python
# Get the shortest path with highest belief
paths = result['path_results']['paths']['PM2.5']
best_path = max(paths, key=lambda p: sum(e['belief'] for e in p['edges']))
```

### 3. Convert to Gateway Format

```python
nodes = convert_indra_nodes(best_path)
edges = convert_indra_edges(best_path)

causal_graph = {
    "nodes": nodes,
    "edges": edges,
    "genetic_modifiers": []  # Add from user genetics separately
}
```

---

## Node Name Resolution

INDRA uses **grounded names** from ontologies. You may need to search for nodes first:

### Autocomplete API

```bash
GET https://network.indra.bio/api/autocomplete?query=particulate%20matter

# Returns:
[
  {"id": "PM2.5", "name": "particulate matter", "namespace": "MESH"},
  ...
]
```

### Common Biomarker Names

| Biomarker | INDRA Name | Namespace | ID |
|-----------|------------|-----------|-----|
| C-Reactive Protein | CRP | HGNC | 2367 |
| Interleukin-6 | IL6 | HGNC | 6018 |
| Tumor Necrosis Factor | TNF | HGNC | 11892 |
| NF-κB | NFKB1 | HGNC | 7794 |

### Common Environmental Factors

| Factor | INDRA Name | Namespace | ID |
|--------|------------|-----------|-----|
| Particulate Matter | PM2.5 | MESH | D052638 |
| Ozone | O3 | CHEBI | 25812 |
| Nitrogen Dioxide | NO2 | CHEBI | 33101 |

---

## Handling Multiple Biomarkers

For Sarah's query ("inflammation markers in LA"), query INDRA **once per biomarker**:

```python
biomarkers = ["CRP", "IL6", "TNF"]
source = "PM2.5"

all_paths = {}
for biomarker in biomarkers:
    query = {"source": source, "target": biomarker, ...}
    response = httpx.post("https://network.indra.bio/api/query", json=query)
    all_paths[biomarker] = response.json()['path_results']['paths'][source]
```

Then **merge into single graph**:
- Combine unique nodes
- Combine unique edges
- Return unified causal graph

---

## Genetic Modifiers (Separate Logic)

INDRA doesn't directly handle genetic variants. Add genetic modifiers based on user genetics:

```python
genetic_modifiers = []

if user_genetics.get("GSTM1") == "null":
    genetic_modifiers.append({
        "variant": "GSTM1_null",
        "affected_nodes": ["oxidative_stress", "NFKB1"],  # Nodes to amplify
        "effect_type": "amplifies",
        "magnitude": 1.3  # 30% increase in effect
    })

if user_genetics.get("TNF") == "-308G/A":
    genetic_modifiers.append({
        "variant": "TNF-alpha_-308G/A",
        "affected_nodes": ["TNF", "IL6"],
        "effect_type": "amplifies",
        "magnitude": 1.2
    })
```

---

## Error Handling

### No Path Found

```json
{
  "path_results": {
    "paths": {}  // Empty - no path exists
  }
}
```

**Handle**: Return error or use generic inflammation path.

### Timeout

```json
{
  "timed_out": true,
  "time_limit": 30.0
}
```

**Handle**: Retry with smaller `path_length` or `depth_limit`.

### Invalid Node Name

```
422 Unprocessable Entity
```

**Handle**: Use autocomplete API to find correct name.

---

## Performance Tips

1. **Cache Results**: INDRA queries can take 5-30 seconds
2. **Parallel Queries**: Query multiple biomarkers in parallel
3. **Limit Path Length**: Start with `path_length=4`, increase if needed
4. **Filter by Belief**: Use `belief_cutoff=0.6` to reduce noise
5. **Use Curated Sources**: `filter_curated=true` for higher quality

---

## Testing Your Integration

### Test Query (Should Work)

```bash
curl -X POST https://network.indra.bio/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "source": "IL6",
    "target": "CRP",
    "path_length": 3,
    "depth_limit": 2,
    "weighted": "belief",
    "k_shortest": 5
  }'
```

**Expected**: Should return paths like IL6 → CRP (direct relationship).

### Verify Response Format

Check that response has:
- `path_results.paths` object
- Each path has `path` and `edges` arrays
- Each edge has `belief`, `stmt_type`, `source_counts`

---

## OpenAPI Spec

**Location**: `docs/external-apis/indra-openapi.json`

Use this for:
- Generating client code
- Validating requests/responses
- Understanding all available parameters

---

## Summary: What the Agentic System Does

1. **Parse User Query**: "How will LA affect my inflammation?"
2. **Identify Biomarkers**: Extract CRP, IL6 from user context
3. **Identify Environmental Change**: Detect SF→LA move, PM2.5 increase
4. **Query INDRA**: `POST /query` for PM2.5 → CRP paths
5. **Select Best Path**: Choose highest-belief shortest path
6. **Convert Format**: Map INDRA response → Gateway `CausalGraph` model
7. **Add Genetic Modifiers**: Based on user's GSTM1, TNF variants
8. **Return to Gateway**: Send structured `AgenticSystemResponse`

**Gateway then**: Builds temporal model and runs Monte Carlo simulation.

---

## References

- **API Base**: https://network.indra.bio/api
- **OpenAPI Spec**: https://network.indra.bio/api/openapi.json
- **Documentation**: https://indra.readthedocs.io/
- **Our Spec**: `docs/external-apis/indra-openapi.json`
