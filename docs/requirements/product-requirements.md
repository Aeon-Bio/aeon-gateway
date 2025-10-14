# Product Requirements Document (PRD)

## Product Vision

**Aeon** transforms static genetic data into dynamic health insights by building personalized causal models that evolve with your life. By integrating biological knowledge graphs with temporal Bayesian inference, we predict how environmental changes, lifestyle shifts, and interventions will affect your unique biomarker profile.

## Problem Statement

### Current State (Pain Points)

1. **Genomic Data is Static, Health is Dynamic**
   - Direct-to-consumer genetic tests provide risk scores that never update
   - Life changes (new city, new job, new habits) but predictions don't
   - No integration of environmental context with genetic predisposition

2. **Biomarkers Lack Mechanistic Explanation**
   - Lab results show CRP is elevated, but not *why*
   - No connection between molecular biology and clinical observations
   - Patients can't understand intervention options

3. **Fragmented Health Data**
   - Wearables, lab results, environmental data live in silos
   - No unified predictive model integrating all sources
   - Temporal relationships lost

4. **Generic Recommendations**
   - Population-level advice ignores genetic individuality
   - No personalized "what-if" scenario modeling
   - Can't evaluate intervention effectiveness before trying

### Impact

- **For Individuals**: Suboptimal health decisions, reactive rather than proactive care
- **For Clinicians**: Limited ability to provide mechanistic explanations for biomarker changes
- **For Researchers**: Difficulty translating molecular knowledge to individual-level predictions
- **For Health Systems**: Rising costs from preventable chronic disease

## Solution: Aeon Gateway

### Core Capabilities

#### 1. Dynamic Causal Modeling
**Capability**: Build personalized factor graphs that explain biomarker changes through causal mechanisms

**User Value**:
- Understand *why* inflammation increased, not just that it did
- See the causal chain from environment → molecules → biomarkers
- Genetic variants modulate causal strengths

**Technical Implementation**:
- Query INDRA biological knowledge graph
- Construct Bayesian networks with genetic modifiers
- Evidence-based edge weights from literature

#### 2. Temporal Prior Updates
**Capability**: Bayesian belief updating as new data arrives

**User Value**:
- Models get smarter over time
- Predictions improve with each new blood panel
- Historical context informs future projections

**Technical Implementation**:
- Dynamic Bayesian Networks (DBNs)
- Variable Elimination inference
- Time-series observation history

#### 3. Environmental Integration
**Capability**: Ingest location-based environmental exposures

**User Value**:
- Understand how air quality affects your health specifically
- Get alerts when environmental changes pose risks
- Quantify location-based health impacts

**Technical Implementation**:
- AirNow API for PM2.5, ozone, AQI
- OpenWeather for temperature, humidity
- Location tracking over time

#### 4. Predictive Trajectories
**Capability**: Forecast biomarker evolution over weeks/months

**User Value**:
- Anticipate health changes before symptoms appear
- Plan interventions proactively
- Track actual vs. predicted to validate model

**Technical Implementation**:
- Monte Carlo trajectory simulation
- Confidence intervals via particle filtering
- 30/60/90-day forecasts

#### 5. Intervention Simulation
**Capability**: "What if" counterfactual analysis

**User Value**:
- See predicted impact of NAC supplementation, HEPA filter, relocation
- Compare intervention options quantitatively
- Make data-driven health decisions

**Technical Implementation**:
- Do-calculus on factor graphs
- Interventional distributions
- A/B comparison visualization

## Target Users

### Primary Persona: Health-Conscious Optimizer

**Demographics**:
- Age: 28-45
- Education: College+
- Tech-savvy, early adopter
- Lives in urban environment

**Psychographics**:
- Has done 23andMe or similar genetic testing
- Tracks health metrics (wearables, periodic blood panels)
- Values data-driven decisions
- Interested in longevity optimization

**Pain Points**:
- Genetic report is just a PDF that never changes
- Doctor says "CRP is high" but doesn't explain why
- Wearable data doesn't integrate with lab results
- Wants to optimize health but unsure what to prioritize

**Use Cases**:
1. Moving to new city → predict health impact
2. Starting new supplement → see predicted biomarker changes
3. Explaining confusing lab results → understand mechanisms
4. Tracking intervention effectiveness → validate predictions

### Secondary Persona: Clinician/Health Coach

**Demographics**:
- Functional medicine practitioner
- Health coach, nutritionist
- Forward-thinking primary care

**Pain Points**:
- Patients ask "why" and generic answers don't satisfy
- Need mechanistic explanations for recommendations
- Want to show patients personalized projections
- Difficult to integrate multi-source data

**Use Cases**:
1. Show patient causal graph explaining biomarker elevation
2. Model impact of recommended interventions
3. Track patient progress vs. predictions
4. Educate patients on genetic-environment interactions

## User Stories (MVP Scope)

### Epic 1: Query & Discovery

**US-1.1**: As a user, I want to ask "How will LA air quality affect my inflammation?" and get a mechanistic answer with predictions

**Acceptance Criteria**:
- Natural language query parsed correctly
- Relevant causal mechanisms identified
- Predictions shown as timeline (30/60/90 day)
- Confidence intervals displayed

**US-1.2**: As a user, I want to see a causal graph showing how environmental factors affect my biomarkers

**Acceptance Criteria**:
- Interactive graph visualization
- Nodes labeled with names + evidence counts
- Edges show causal direction and strength
- Genetic modifiers highlighted

### Epic 2: Temporal Tracking

**US-2.1**: As a user, I want to input new biomarker results and see my model update

**Acceptance Criteria**:
- Simple form for biomarker entry (name, value, date)
- Model priors update via Bayesian inference
- Updated predictions reflect new information
- Historical observations shown on timeline

**US-2.2**: As a user, I want to track environmental changes over time (e.g., SF → LA move)

**Acceptance Criteria**:
- Location history tracking
- Environmental data automatically fetched for locations
- Timeline shows environmental transitions
- Predictions update based on new environment

### Epic 3: Intervention Planning

**US-3.1**: As a user, I want to simulate "What if I take NAC?" and see predicted biomarker changes

**Acceptance Criteria**:
- Intervention selector (supplement, air filter, relocation)
- Counterfactual trajectory shown vs. baseline
- Delta quantified (e.g., "CRP -0.5 mg/L at 60 days")
- Evidence for intervention mechanism shown

**US-3.2**: As a user, I want recommendations ranked by predicted impact

**Acceptance Criteria**:
- List of interventions with predicted effect sizes
- Sorted by magnitude of biomarker improvement
- Cost/effort considerations shown
- Evidence strength indicated

## Success Metrics

### Hackathon Demo (2.5 hours)

**Primary Goal**: Demonstrate innovation + TAM potential to judges

**Success Criteria**:
1. ✅ Live demo of SF→LA scenario with compelling narrative
2. ✅ Causal graph visualization clearly shows INDRA integration
3. ✅ Predictions match plausible biomarker trajectories
4. ✅ Articulate TAM clearly ($350B precision medicine market)
5. ✅ Judges understand the genetic-environment interaction innovation

**Metrics**:
- Demo completes without errors: **MUST**
- Judges ask follow-up questions: **GOOD**
- Judges reference our demo in deliberations: **GREAT**

### MVP Post-Hackathon (4 weeks)

**User Acquisition**:
- 100 beta users from longevity community
- 10 active users (weekly engagement)

**Product Engagement**:
- Avg 3 queries per user per week
- 80% of users input at least one biomarker update
- 60% of users explore intervention simulations

**Technical Performance**:
- Query latency p95 < 5 seconds
- INDRA API success rate > 95%
- Prediction accuracy (when ground truth available) RMSE < 20%

### Series A Readiness (12 months)

**User Growth**:
- 10,000 paying users
- $50/month subscription → $6M ARR
- 40% MoM growth

**Product-Market Fit**:
- NPS > 50
- 60% monthly retention
- 10+ case studies of health improvements

**Clinical Validation**:
- Partnership with 3 functional medicine clinics
- Prospective study showing prediction accuracy
- Publication in peer-reviewed journal

## Competitive Landscape

| Competitor | Offering | Aeon Advantage |
|-----------|----------|----------------|
| 23andMe | Static genetic reports | ✅ Dynamic, updating predictions |
| InsideTracker | Biomarker tracking + generic advice | ✅ Personalized causal models |
| Levels | Glucose monitoring + coaching | ✅ Multi-biomarker, mechanistic |
| SelfDecode | Genetic analysis + recommendations | ✅ Temporal modeling, environmental integration |
| Function Health | Comprehensive blood testing | ✅ Predictive trajectories, intervention simulation |

**Unique Value Props**:
1. **Only product integrating INDRA biological knowledge** → causal mechanisms grounded in literature
2. **Only temporal Bayesian updating** → models improve with more data
3. **Only genetic-environment interaction modeling** → personalized predictions
4. **Only counterfactual intervention simulation** → actionable "what-if" analysis

## Business Model

### Pricing Strategy

**Tier 1: Free** (Lead Gen)
- 1 query per month
- View causal graphs
- Basic predictions (30 days)
- Goal: 10,000 users

**Tier 2: Individual ($49/month)**
- Unlimited queries
- Full temporal tracking
- Intervention simulations
- Priority support
- Goal: 1,000 users → $49K MRR

**Tier 3: Professional ($199/month)** (for clinicians)
- Multi-patient management
- White-label reports
- API access
- Custom interventions
- Goal: 100 users → $20K MRR

**Enterprise**: Custom pricing for health systems

### Revenue Projections (Year 1)

| Month | Free Users | Paid Users | MRR | Cumulative Revenue |
|-------|-----------|-----------|-----|-------------------|
| 1-3   | 500       | 10        | $500 | $1,500 |
| 4-6   | 2,000     | 50        | $2,500 | $9,000 |
| 7-9   | 5,000     | 200       | $10,000 | $39,000 |
| 10-12 | 10,000    | 500       | $25,000 | $114,000 |

**Year 1 ARR**: ~$300K

## Go-to-Market Strategy

### Phase 1: Longevity Community (Months 1-3)
- Launch on Twitter, Hacker News, /r/longevity
- Partner with biohacking influencers (Peter Attia, Andrew Huberman)
- Free tier for early adopters, gather testimonials

### Phase 2: Functional Medicine (Months 4-6)
- Attend IFM conference
- Offer free pilot to 10 clinics
- Build case studies showing patient outcomes

### Phase 3: DTC Marketing (Months 7-12)
- Content marketing (blog posts on genetic-environment interactions)
- SEO for long-tail keywords ("GSTM1 null air pollution")
- Paid ads targeting 23andMe customers

## Risks & Mitigations

### Risk 1: INDRA API Reliability
**Impact**: High - core dependency
**Likelihood**: Medium
**Mitigation**:
- Cache INDRA responses aggressively
- Build fallback rules for common queries
- Contribute to INDRA project to ensure stability

### Risk 2: Prediction Accuracy
**Impact**: High - credibility risk if predictions are wrong
**Likelihood**: Medium
**Mitigation**:
- Start with well-studied relationships (air quality → CRP)
- Show confidence intervals, not point estimates
- Run prospective validation studies
- Transparent about model limitations

### Risk 3: Regulatory (FDA)
**Impact**: High - could require clinical trial
**Likelihood**: Low - informational product, not diagnostic
**Mitigation**:
- Position as "educational tool" not medical advice
- Disclaimer: "Not intended to diagnose or treat"
- Monitor FDA guidance on software as medical device

### Risk 4: User Comprehension
**Impact**: Medium - users may not understand causal graphs
**Likelihood**: High
**Mitigation**:
- Invest in UX design for complex visualizations
- Provide tooltips, tutorials, example interpretations
- Offer optional concierge onboarding

## Open Questions

1. **How to handle conflicting evidence in INDRA?**
   - Multiple paths with different effect directions
   - Weight by evidence count? Recency? Source quality?

2. **What's the right temporal resolution?**
   - Daily? Weekly? Monthly time slices?
   - Trade-off: granularity vs. computational cost

3. **How to price professional tier?**
   - Per-patient? Per-clinician? Unlimited?
   - Need to understand clinic economics

4. **Should we build our own biomarker testing?**
   - Partner with lab (Quest, Labcorp)?
   - Or remain data-agnostic platform?

## Appendix: TAM Analysis

**Total Addressable Market (TAM)**: $350B
- Global precision medicine market by 2030 (Grand View Research)

**Serviceable Addressable Market (SAM)**: $15B
- Genomic data-driven diagnostics subsegment
- US + EU markets

**Serviceable Obtainable Market (SOM)**: $150M
- 1% market share in predictive health analytics
- 300,000 users at $50/month → $180M ARR

**Bottom-Up Validation**:
- 40M Americans have done genetic testing (23andMe, Ancestry)
- 10% interested in advanced health analytics → 4M potential users
- 5% conversion → 200K paying users
- At $50/month → $120M ARR

**Wedge Strategy**: Start with early adopters (longevity community), expand to functional medicine, eventually DTC mass market.
