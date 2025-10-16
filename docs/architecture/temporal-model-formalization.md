# Temporal Model Formalization

This note translates the current Aeon Gateway temporal causal engine into GitHub-friendly notation, highlights the behaviour we actually ship, and records the main shortcomings relative to standard causal inference practice.

## 1. System Context

Inputs:
- Causal graph `G = (V, E)` from the external agentic system.
- Baseline biomarker values `b[v]` for biomarker nodes.
- Environmental change multipliers `delta[v]` for environmental nodes.
- User genetics `g[gene] = variant`.

Node metadata:
- `type(v)` is one of `environmental`, `molecular`, `biomarker`, `genetic`.
- Edges carry `effect_size` in `[0, 1]`, `temporal_lag_hours` (integer hours), and a label such as `activates` or `inhibits`.
- Genetic modifiers arrive as dictionaries that are meant to scale edge effects when the user has a matching variant.

`src/temporal_model.py` converts this into a NetworkX directed graph and performs a Monte Carlo forward simulation to produce biomarker timelines.

## 2. Simulation Formalization

Notation:
- Prediction horizon: `T = 90` days (configurable).
- Number of Monte Carlo particles: `N = 1000`.
- `X_s[v][t]` is the simulated value for node `v` on day `t` in particle `s`.

### 2.1 Edge Re-weighting

For each edge `e = (u -> v)` with base weight `w_e`:

```
tilde_w_e = w_e * product over modifiers m that target e (gamma_m)
```

Today no modifiers fire because the code expects a field named `affects_edge` while the mock data uses `affected_nodes`.

### 2.2 Initial Conditions

```
X_s[v][0] = b[v]            if v is a biomarker
X_s[v][0] = 1.0            otherwise (implicit in code)
```

Environmental multipliers are applied separately and do not rely on day-zero values.

### 2.3 Environmental Nodes

For day `t >= 1`:

```
noise ~ Normal(0, 0.05)
X_s[v][t] = delta.get(v, 1.0) * (1 + noise)
```

### 2.4 Molecular Nodes

Let `parents(v)` be the incoming neighbours and `lag_days(e) = floor(temporal_lag_hours / 24)`.

```
if parents(v) is empty:
    X_s[v][t] = 1 + Normal(0, 0.1)
else:
    total = 0
    for each edge (u -> v):
        if t >= lag_days:
            source_value = X_s[u][t - lag_days] (clamped to day 0)
        else:
            source_value = 1.0
        total += tilde_w_e * source_value
    X_s[v][t] = total * (1 + Normal(0, 0.1))
```

If the graph is cyclic, the engine abandons topological ordering and processes nodes in arbitrary order.

### 2.5 Biomarker Nodes

For biomarker `v`:

```
previous = X_s[v][t - 1]
increment = 0
for each parent edge (u -> v):
    if t >= lag_days:
        source_value = X_s[u][t - lag_days]
    else:
        source_value = 1.0
    increment += tilde_w_e * source_value
X_s[v][t] = previous + 0.02 * increment * (1 + Normal(0, 0.1))
```

There is no negative effect handling; all `effect_size` values are treated as positive contributions.

### 2.6 Trajectory Aggregation

After running the loop for `t = 1..T`, the engine samples days `{0, 30, 60, 90} intersect [0, T]` and reports:

```
mean[v][t]      = average over particles X_s[v][t]
ci_lower[v][t]  = 2.5th percentile over particles
ci_upper[v][t]  = 97.5th percentile over particles
```

Risk levels:
- For CRP: `low` if mean < 1.0 mg/L, `moderate` if mean < 3.0 mg/L, else `high`.
- For other biomarkers: compare fold-change vs baseline (thresholds 1.5 and 2.5).

## 3. Delivered Capabilities

- **Scenario simulation**: Small DAGs, an environmental multiplier, and baseline biomarker values yield a 90-day trajectory.
- **Uncertainty heuristics**: Particle means and empirical 95% intervals respond to stochastic noise.
- **Risk bucketing**: Outputs coarse risk categories for messaging.
- **Extension scaffolding**: Hooks exist for genetic modulation and additional node types once contracts align.

## 4. Observed Flaws and Limitations

1. **Genetic modifiers never apply** (`src/temporal_model.py:118` vs `tests/mocks/agentic_system.py:71`): schema mismatch means genetics have no quantitative effect.
2. **Edge labels ignored** (`src/temporal_model.py:52`): inhibitory edges cannot exert negative influence because weights are confined to `[0, 1]`.
3. **Heuristic dynamics** (`src/temporal_model.py:179`): the 0.02 factor and Gaussian noise are ad hoc and uncalibrated.
4. **Temporal lag truncation** (`src/temporal_model.py:154`): hourly lags become whole days, erasing sub-day structure.
5. **Cycle handling** (`src/temporal_model.py:141`): cycles break causal semantics; processing order becomes arbitrary.
6. **Environmental baselines missing**: absolute concentrations (e.g., 34.5 ug/m^3) are not propagated, only multiplicative changes.
7. **No posterior updates**: `update_priors` is unimplemented, so new observations never adjust trajectories.
8. **Unit handling brittle**: defaults to `"mg/L"`, `"pg/mL"`, or `"units"`, risking mislabelled outputs as the graph expands.

These issues leave the engine closer to a bespoke simulator than to a principled temporal causal model.

## 5. Methods That Resonate in the Field

- **Dynamic Bayesian networks**: define conditional distributions per time slice and run particle filtering or variational inference (Pyro, PyMC, pgmpy).
- **Structural causal models with time indices**: encode structural equations `X_v(t) = f_v(parents, noise)` and leverage do-calculus for interventions (Pearl).
- **State-space / Kalman models**: linear-Gaussian models for biomarker dynamics with explicit process and measurement noise.
- **Causal impact frameworks**: combine SCM structure with counterfactual estimation (synthetic control, Bayesian structural time series).
- **Time-varying coefficient models**: estimate effect sizes as functions of modifiers (genetics, lifestyle) instead of hard-coded multipliers.

Each alternative offers identifiable parameters, explainable uncertainty, and principled updating with new evidence.

## 6. Follow-up Questions

1. Should the data contract expose edge-level modifier targets so genetics can modulate effects?
2. Do we allow negative weights so inhibitory edges actually suppress downstream nodes?
3. What empirical data can calibrate noise levels and growth factors?
4. Which inference upgrade (particle filter, variational DBN, Kalman smoother) fits demo constraints while improving causal validity?

Clarifying these points will determine whether the temporal engine remains a demo heuristic or evolves into a defensible causal forecasting system.
