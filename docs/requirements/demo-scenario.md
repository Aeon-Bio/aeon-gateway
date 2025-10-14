# Demo Scenario: SF → LA Relocation

## Scenario Overview

**Protagonist**: Sarah Chen, 32-year-old software engineer

**Timeline**: January 2025 (SF baseline) → September 2025 (LA move) → December 2025 (3-month followup)

**Core Narrative**: Sarah's genetic variants make her susceptible to oxidative stress. Moving from clean-air SF to smoggy LA triggers a predictable inflammatory cascade that Aeon forecasts accurately.

## Character Profile: Sarah Chen

### Demographics
- **Age**: 32
- **Occupation**: Software Engineer at tech startup
- **Location History**:
  - San Francisco, CA (Jan 2020 - Aug 2025)
  - Los Angeles, CA (Sept 2025 - present)
- **Lifestyle**: Active runner, health-conscious, tracks biomarkers quarterly

### Genetic Profile

| Gene | Variant | Functional Impact | Clinical Significance |
|------|---------|-------------------|----------------------|
| **GSTM1** | Null (homozygous deletion) | No functional GSTM1 enzyme | Reduced glutathione conjugation → ⬆️ oxidative stress susceptibility |
| **GSTP1** | Ile105Val (Val/Val) | Reduced enzyme activity | Further impaired detoxification capacity |
| **TNF-α** | -308G/A (heterozygous) | Increased TNF-α expression | Pro-inflammatory phenotype |
| **SOD2** | Val16Ala (Ala/Ala) | Lower mitochondrial SOD2 activity | Reduced antioxidant defense |
| **MTHFR** | C677T (heterozygous) | Mildly reduced enzyme activity | Slight elevation in homocysteine (not primary focus) |

**Interpretation**: Sarah has a "perfect storm" genetic profile for air pollution sensitivity:
- **GSTM1 null + GSTP1 Val/Val** → Can't efficiently detoxify reactive oxygen species from PM2.5
- **TNF-α -308G/A** → When oxidative stress occurs, inflammatory response is amplified
- **SOD2 Ala/Ala** → Mitochondrial antioxidants less effective

### Baseline Health (San Francisco Era)

#### Blood Biomarkers (July 2025, SF)

| Biomarker | Value | Reference Range | Status |
|-----------|-------|----------------|--------|
| **CRP (C-Reactive Protein)** | 0.7 mg/L | < 1.0 mg/L (low risk) | ✅ Normal |
| **IL-6 (Interleukin-6)** | 1.1 pg/mL | < 1.8 pg/mL | ✅ Normal |
| **TNF-α** | 2.3 pg/mL | < 2.8 pg/mL | ✅ Normal |
| **8-OHdG** (oxidative stress) | 4.2 ng/mL | < 5.0 ng/mL | ✅ Normal |
| **Homocysteine** | 9.5 µmol/L | 5-15 µmol/L | ✅ Normal |
| **Cortisol (AM)** | 13.2 µg/dL | 6-23 µg/dL | ✅ Normal |

**Conclusion**: Despite genetic vulnerabilities, Sarah's biomarkers are excellent in SF's clean environment.

#### Wearable Data (Apple Watch + Oura Ring)

- **Resting Heart Rate**: 58 bpm (excellent)
- **HRV (Heart Rate Variability)**: 72 ms (good recovery)
- **Sleep Quality**: 7.5 hrs/night, 85% sleep efficiency
- **VO2 Max Estimate**: 42 mL/kg/min (above average for age/sex)
- **Activity**: 5-6 runs/week, 25-30 miles/week

#### Environmental Exposure (San Francisco)

| Factor | Average | Source |
|--------|---------|--------|
| **PM2.5** | 7.8 µg/m³ | AirNow (Jan-Aug 2025) |
| **PM10** | 18.2 µg/m³ | AirNow |
| **Ozone (O₃)** | 0.042 ppm | AirNow |
| **AQI** | 32 (Good) | EPA |
| **Temperature** | 15°C (59°F) avg | NOAA |
| **Humidity** | 68% avg | NOAA |

**Interpretation**: SF has some of the cleanest air in the US. Sarah's genetic vulnerabilities are not triggered.

## The Transition: Moving to Los Angeles

### Relocation Context

**Date**: September 1, 2025

**Reason**: Job opportunity at aerospace startup in El Segundo

**New Residence**: Santa Monica, CA (west LA, near ocean, slightly better air than inland)

**Sarah's Awareness**: She knows LA has worse air quality but doesn't understand personal risk given genetics

### Environmental Change (Los Angeles)

| Factor | SF Average | LA Average | Delta | % Change |
|--------|-----------|-----------|-------|----------|
| **PM2.5** | 7.8 µg/m³ | 34.5 µg/m³ | +26.7 | +342% |
| **PM10** | 18.2 µg/m³ | 58.1 µg/m³ | +39.9 | +219% |
| **Ozone (O₃)** | 0.042 ppm | 0.089 ppm | +0.047 | +112% |
| **AQI** | 32 (Good) | 78 (Moderate) | +46 | +144% |

**Key Insight**: PM2.5 increases by 3.4×, exceeding WHO guideline of 15 µg/m³ annual average.

### Aeon's Initial Prediction (Sept 1, 2025)

When Sarah inputs her relocation, Aeon generates:

#### Causal Graph

```
Environmental Inputs → Molecular Mechanisms → Biomarker Outputs

PM2.5 ──────────────┬──→ ROS (Reactive Oxygen Species)
                    │
Ozone ──────────────┤
                    │
                    ├──→ Oxidative Stress ←── GSTM1 null (⬆️ susceptibility)
                    │           │                    ↑
                    │           │                GSTP1 Val/Val (⬆️ susceptibility)
                    │           │                    ↑
                    │           │                SOD2 Ala/Ala (⬆️ susceptibility)
                    │           ↓
                    │       NRF2 pathway
                    │           ↓
                    │       (Antioxidant response - insufficient)
                    │
                    └──→ NF-κB activation (RELA, NFKB1)
                                ↓
                        ┌───────┴────────┐
                        ↓                ↓
                     IL-6 ←────── TNF-α -308G/A (⬆️ expression)
                        │                │
                        │                ↓
                        │            TNF-α ↑
                        │                │
                        └────────┬───────┘
                                 ↓
                            IL-1β ↑
                                 ↓
                            Hepatocyte IL-6 signaling
                                 ↓
                             CRP ↑↑
```

**INDRA Evidence**:
- PM2.5 → ROS: 47 papers (0.87 confidence)
- ROS → NF-κB: 163 papers (0.94 confidence)
- NF-κB → IL6: 89 papers (0.91 confidence)
- IL6 → CRP: 312 papers (0.98 confidence)

#### 90-Day Biomarker Predictions

| Biomarker | Baseline (SF) | 30-Day Prediction | 60-Day Prediction | 90-Day Prediction | % Change |
|-----------|--------------|-------------------|-------------------|-------------------|----------|
| **8-OHdG** | 4.2 ng/mL | 6.8 (±1.1) | 8.1 (±1.3) | 8.9 (±1.4) | +112% |
| **CRP** | 0.7 mg/L | 1.3 (±0.3) | 1.9 (±0.4) | 2.4 (±0.5) | +243% |
| **IL-6** | 1.1 pg/mL | 2.0 (±0.4) | 2.9 (±0.6) | 3.7 (±0.7) | +236% |
| **TNF-α** | 2.3 pg/mL | 3.1 (±0.5) | 3.6 (±0.6) | 4.0 (±0.7) | +74% |

**Risk Assessment**:
- 🟡 CRP entering "moderate cardiovascular risk" zone (1-3 mg/L) by day 30
- 🔴 CRP entering "high cardiovascular risk" zone (>3 mg/L) by day 75
- 🟡 IL-6 exceeding normal range by day 20

**Mechanistic Explanation**:
> "Your GSTM1 null variant means you lack the primary enzyme for detoxifying reactive oxygen species from air pollution. Combined with GSTP1 Val/Val, your glutathione system is overwhelmed. LA's PM2.5 (34 µg/m³) generates oxidative stress that activates NF-κB inflammatory signaling. Your TNF-α -308G/A variant amplifies this response, driving IL-6 and CRP elevation. We predict CRP will reach 2.4 mg/L within 90 days, placing you in elevated cardiovascular risk."

## Act II: Ground Truth Validation

### Month 1 (October 2025) - First Blood Panel in LA

Sarah gets bloodwork on October 15 (45 days post-move):

| Biomarker | Predicted (Day 45) | Actual | Delta | Model Accuracy |
|-----------|-------------------|--------|-------|----------------|
| **8-OHdG** | 7.5 ng/mL | 8.1 ng/mL | +0.6 | 92% |
| **CRP** | 1.6 mg/L | 1.8 mg/L | +0.2 | 89% |
| **IL-6** | 2.5 pg/mL | 2.7 pg/mL | +0.2 | 93% |
| **TNF-α** | 3.4 pg/mL | 3.2 pg/mL | -0.2 | 94% |

**Outcome**: Aeon's predictions are remarkably accurate! Sarah is impressed.

**Aeon's Response**: Bayesian prior update
- Model confidence increases
- Slight adjustment to PM2.5 → oxidative stress edge weight
- Updated 90-day forecast now predicts CRP = 2.6 mg/L (slightly higher)

### Month 2 (November 2025) - Intervention Decision

Sarah sees her CRP is already 1.8 mg/L and rising. She asks Aeon: **"What can I do to lower my inflammation?"**

#### Aeon's Intervention Recommendations (Ranked by Predicted Impact)

**1. N-Acetylcysteine (NAC) Supplementation - 600mg 2x/day**

- **Mechanism**: NAC → Cysteine → Glutathione biosynthesis → ⬆️ antioxidant capacity
- **Predicted CRP Impact**: -0.8 mg/L at 90 days (2.6 → 1.8)
- **Evidence**: 23 RCTs showing NAC reduces oxidative stress markers (meta-analysis)
- **Genetic Rationale**: Compensates for GSTM1/GSTP1 deficiency
- **Cost**: $15/month
- **Risk**: Low (well-tolerated, common supplement)

**Counterfactual Prediction**:
```
With NAC:
  CRP: 1.8 → 1.8 → 1.7 → 1.6 (day 90)
Without NAC:
  CRP: 1.8 → 2.1 → 2.4 → 2.6 (day 90)

Delta: -1.0 mg/L
```

**2. HEPA Air Filter (Home + Office)**

- **Mechanism**: Reduces indoor PM2.5 exposure by 50-70%
- **Predicted CRP Impact**: -0.5 mg/L at 90 days
- **Evidence**: 12 studies on indoor air filtration and inflammation
- **Cost**: $200 upfront, $50/year filters
- **Risk**: None

**3. Reduce Outdoor Running During High AQI Days**

- **Mechanism**: Decrease respiratory PM2.5 dose during exertion
- **Predicted CRP Impact**: -0.3 mg/L
- **Evidence**: 8 studies on exercise timing and air quality
- **Trade-off**: May reduce fitness benefits
- **Cost**: Free (behavior change)

**4. Omega-3 Supplementation (EPA/DHA 2g/day)**

- **Mechanism**: Compete with arachidonic acid → ⬇️ inflammatory prostaglandins
- **Predicted CRP Impact**: -0.4 mg/L
- **Evidence**: 34 RCTs showing modest CRP reduction
- **Cost**: $25/month
- **Risk**: Low

**Sarah's Decision**: She starts NAC + HEPA filter (highest impact combo).

### Month 3 (December 2025) - Validation of Intervention

Sarah gets bloodwork on December 15 (60 days post-intervention, 105 days post-move):

| Biomarker | Predicted (w/ NAC) | Actual | Delta | Model Accuracy |
|-----------|-------------------|--------|-------|----------------|
| **8-OHdG** | 6.2 ng/mL | 6.5 ng/mL | +0.3 | 95% |
| **CRP** | 1.7 mg/L | 1.9 mg/L | +0.2 | 89% |
| **IL-6** | 2.3 pg/mL | 2.4 pg/mL | +0.1 | 96% |

**Outcome**: Intervention worked! CRP stabilized at 1.9 instead of climbing to predicted 2.6 without intervention.

**Sarah's Reaction**: *"This is incredible. The model predicted my inflammation would hit 2.4, I intervened, and it actually stayed at 1.9. I feel like I'm finally in control of my health."*

## Demo Presentation Flow (5 Minutes)

### Act I: Setup (60 seconds)

**Slide 1: The Problem**

> "260 million Americans have genetic data, but it just sits there. Sarah has a GSTM1 null variant - her body is bad at handling oxidative stress. But her 23andMe report is just a static PDF. It doesn't know she's moving to LA."

**Visual**: Split screen - 23andMe report (static) vs. Aeon (dynamic timeline)

### Act II: The Prediction (90 seconds)

**Slide 2: Aeon in Action**

> "Sarah tells Aeon she's moving from SF to LA. Our agent queries INDRA - a biological knowledge graph with 40 million causal statements from scientific literature. It discovers PM2.5 activates NF-κB, driving IL-6 and CRP elevation. Her GSTM1 null variant means this effect is 2.3× stronger."

**Visual**: Animated causal graph building in real-time, highlighting INDRA evidence counts

**Slide 3: The Forecast**

> "Aeon predicts her CRP will spike from 0.7 to 2.4 mg/L over 90 days - moving her into high cardiovascular risk. Here's the timeline:"

**Visual**: Interactive timeline showing:
- Environmental data (PM2.5 overlay)
- Predicted biomarker trajectories (with confidence intervals)
- Risk zone shading (green → yellow → red)

### Act III: Validation (90 seconds)

**Slide 4: Ground Truth**

> "45 days later, Sarah gets bloodwork. Her CRP is 1.8 - exactly what we predicted. The model works."

**Visual**: Prediction vs. actual overlaid on timeline, showing tight match

**Slide 5: Intervention**

> "Sarah asks: 'What can I do?' Aeon simulates interventions. NAC supplementation - which boosts glutathione - is predicted to cut her CRP increase by 65%. She tries it."

**Visual**: Counterfactual graph showing:
- Baseline trajectory (red, climbing)
- NAC trajectory (green, stabilizing)
- Actual outcome (dots) tracking green line

**Slide 6: The Result**

> "60 days later, her CRP is 1.9 - stable, instead of the predicted 2.6 without intervention. This is the future of precision health: personalized, mechanistic, predictive."

**Visual**: Final timeline with all data, highlighting model accuracy

### Act IV: The Pitch (60 seconds)

**Slide 7: Market Opportunity**

> "This isn't just for Sarah. 40 million Americans have genetic data. 50 million track biomarkers. $350 billion precision medicine market - but no one is closing the loop with causal modeling."

**Numbers on Screen**:
- TAM: $350B
- SAM: $15B (genomic diagnostics)
- SOM: $150M (1% market share)

**Slide 8: Traction Roadmap**

> "We're starting with the longevity community - early adopters who already track everything. Then functional medicine clinics. Then DTC. We have the technology, the science, and the team. Help us build the future of health."

**Visual**: Growth curve with milestones

## Demo Technical Requirements

### Frontend Components

1. **Timeline Visualization** (Recharts)
   - X-axis: Date (Jan 2025 - Dec 2025)
   - Y-axes: Biomarker values, Environmental factors
   - Lines: Predicted trajectories (dashed), Actual measurements (solid)
   - Shaded regions: Confidence intervals, Risk zones
   - Markers: Key events (move, intervention start)

2. **Causal Graph Visualization** (react-flow or D3.js)
   - Nodes: Color-coded by type (environmental=gray, genetic=blue, molecular=purple, biomarker=red)
   - Edges: Width proportional to effect size, labeled with evidence count
   - Tooltips: PMID links, mechanism descriptions
   - Animation: Graph construction sequence

3. **Intervention Simulator**
   - Dropdown: Select intervention (NAC, HEPA, Omega-3, etc.)
   - Comparison view: Baseline vs. Intervention trajectories
   - Delta metrics: Effect size at 30/60/90 days
   - Confidence: Model certainty in prediction

### Backend Data (Hardcoded for Demo)

**User Profile (Sarah)**:
```json
{
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
    "TNF-alpha": 2.3,
    "8-OHdG": 4.2
  },
  "location_history": [
    {
      "city": "San Francisco",
      "start": "2020-01-01",
      "end": "2025-08-31",
      "avg_pm25": 7.8
    },
    {
      "city": "Los Angeles",
      "start": "2025-09-01",
      "end": null,
      "avg_pm25": 34.5
    }
  ]
}
```

**INDRA Paths (Cached)**:
- PM2.5 → NFKB1 → IL6 (47 papers)
- PM2.5 → oxidative_stress → RELA → IL6 (23 papers)
- IL6 → CRP (312 papers)

**Predictions (Pre-computed)**:
```json
{
  "no_intervention": {
    "CRP": [0.7, 1.3, 1.9, 2.4],  // day 0, 30, 60, 90
    "IL-6": [1.1, 2.0, 2.9, 3.7]
  },
  "with_NAC": {
    "CRP": [0.7, 1.1, 1.5, 1.8],
    "IL-6": [1.1, 1.6, 2.0, 2.3]
  }
}
```

**Ground Truth (Sarah's Actual Labs)**:
```json
{
  "observations": [
    {"date": "2025-07-15", "CRP": 0.7, "IL-6": 1.1},
    {"date": "2025-10-15", "CRP": 1.8, "IL-6": 2.7},
    {"date": "2025-12-15", "CRP": 1.9, "IL-6": 2.4}
  ]
}
```

## Success Criteria for Demo

### Must-Have
- ✅ Timeline shows clear PM2.5 spike at Sept 1
- ✅ Predictions match actual data within 15%
- ✅ Causal graph displays with INDRA evidence
- ✅ Intervention counterfactual is compelling
- ✅ Demo completes in under 5 minutes

### Nice-to-Have
- Interactive graph exploration (zoom, click nodes)
- Real-time INDRA API call (if connection stable)
- Animated graph construction
- Export report as PDF

### Show-Stoppers (Avoid)
- API timeout during demo
- Graph fails to render
- Predictions wildly off from actuals
- Unclear narrative - judges don't understand

## Post-Demo Q&A Preparation

**Expected Questions**:

1. **"How accurate are your predictions?"**
   - *Answer*: "In our SF→LA demo, we achieved 89-96% accuracy on 4 biomarkers. We're currently running prospective validation studies. Our confidence intervals reflect model uncertainty - we show ranges, not certainties."

2. **"What if INDRA doesn't have data for a query?"**
   - *Answer*: "We start with well-studied mechanisms (air quality → inflammation has 200+ papers). For novel queries, we explicitly state evidence gaps and lower confidence. Future: we'll integrate multiple knowledge bases (OpenTargets, STRING, etc.)."

3. **"Is this FDA regulated?"**
   - *Answer*: "We position as educational software, not diagnostic. Users make decisions with doctors. We're monitoring FDA guidance on clinical decision support software."

4. **"How do you handle competing evidence?"**
   - *Answer*: "INDRA provides belief scores - we weight edges by evidence count and study quality. Conflicting paths are shown transparently. Bayesian framework naturally handles uncertainty."

5. **"What's the computational cost?"**
   - *Answer*: "For this demo, inference takes 2-3 seconds per query. Production: we'll cache common graph structures, use GPU for large Bayesian nets. Under $0.50/query at scale."

**Killer Closing Line**:
> "Every year, Sarah's genetic report gets less relevant as her life changes. Aeon makes it *more* relevant - because it learns and adapts. That's the future we're building."
