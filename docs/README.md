# Aeon Gateway Documentation

## Overview

The Aeon Gateway is an intelligent API gateway that integrates personalized health data with causal biological modeling to provide predictive health insights. The system bridges clinical biomarkers, environmental factors, and genetic variants with mechanistic biological knowledge from INDRA (Integrated Network and Dynamical Reasoning Assembler).

## Core Value Proposition

**"Personalized causal health models that evolve with your life"**

Dynamically build factor graphs from biological literature to predict how environmental changes affect individual biomarkers based on personal genetics and evolving priors.

## Documentation Structure

```
docs/
├── README.md                           # This file
├── architecture/
│   ├── system-overview.md             # High-level architecture
│   ├── agent-architecture.md          # Multi-agent system design
│   ├── temporal-graph-model.md        # Causal graph representation
│   └── technology-stack.md            # Stack decisions and rationale
├── api/
│   ├── gateway-api.md                 # REST API specification
│   ├── data-models.md                 # Pydantic models and schemas
│   └── indra-integration.md           # INDRA API integration details
├── requirements/
│   ├── product-requirements.md        # PRD and user stories
│   ├── demo-scenario.md               # SF→LA demo specifications
│   └── success-metrics.md             # KPIs and demo success criteria
└── planning/
    ├── hackathon-timeline.md          # 2.5hr implementation plan
    ├── mvp-scope.md                   # Minimal viable features
    └── future-roadmap.md              # Post-hackathon enhancements
```

## Quick Links

- [System Architecture](./architecture/system-overview.md)
- [Agent Design](./architecture/agent-architecture.md)
- [API Specification](./api/gateway-api.md)
- [Product Requirements](./requirements/product-requirements.md)
- [Demo Scenario](./requirements/demo-scenario.md)
- [Implementation Timeline](./planning/hackathon-timeline.md)

## Key Innovations

1. **Semantic Bridging**: Automated mapping from clinical biomarkers to molecular mechanisms
2. **Multi-Strategy INDRA Querying**: Path search + neighborhood expansion for comprehensive coverage
3. **Evidence-Based Graph Pruning**: Network analysis to identify critical causal bottlenecks
4. **Genetic Contextualization**: Variant-specific edge weights in factor graphs
5. **Temporal Bayesian Updates**: Dynamic priors that evolve with new observations

## Target Audience

- Hackathon judges evaluating innovation and TAM potential
- Engineers implementing the gateway
- Product stakeholders defining scope and priorities
- Research collaborators understanding the biological modeling approach

## Getting Started

1. Review [Product Requirements](./requirements/product-requirements.md) for context
2. Understand the [System Architecture](./architecture/system-overview.md)
3. Explore the [Demo Scenario](./requirements/demo-scenario.md)
4. Follow the [Implementation Timeline](./planning/hackathon-timeline.md)
