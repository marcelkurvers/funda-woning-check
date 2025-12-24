# 4-PLANE ENFORCED ANALYTICAL REPORT SYSTEM

## Implementation Complete ✅

This document summarizes the implementation of the 4-Plane Cognitive Model as specified.

---

## 🎯 SYSTEM CONTRACT

**Core Principle**: This system operates on a 4-Plane Cognitive Model. Each plane has exclusive responsibility. No output may cross planes. **Ever.**

If output crosses planes → it **MUST** be rejected.

---

## 📐 THE 4-PLANE MODEL

```
┌───────────────┬──────────────────────────────┬──────────────────────┬───────────────────────┐
│ PLANE A       │ PLANE B                      │ PLANE C              │ PLANE D               │
│ Visuals       │ Narrative (300+ words)       │ KPIs & Data          │ Marcel / Petra        │
│ (Left)        │ (Center–Upper)               │ (Center–Lower)       │ (Right)               │
│ 🟦 Blue       │ 🟩 Green                     │ 🟨 Amber             │ 🟥 Red                │
└───────────────┴──────────────────────────────┴──────────────────────┴───────────────────────┘
```

### 🟦 PLANE A — VISUAL INTELLIGENCE PLANE (LEFT)

**Purpose**: Pattern recognition & pre-verbal insight  
**Answers**: "What stands out immediately?"

| Allowed | Forbidden |
|---------|-----------|
| Charts, graphs, infographics | Explanatory text |
| Trends, deltas, comparisons | Interpretation |
| Heatmaps, bars, timelines | Conclusions |
| | KPIs with meaning |

**Data Rule**: Visuals may ONLY use registry-verified data. No AI-generated values.

### 🟩 PLANE B — NARRATIVE REASONING PLANE (CENTER–UPPER)

**Purpose**: Meaning, interpretation, judgment  
**Answers**: "What does this mean, and why?"

| Allowed | Forbidden |
|---------|-----------|
| Interpretation of KPIs | Raw KPIs |
| Contextual reasoning | Tables |
| Trade-offs | Bullet KPI dumps |
| Scenario thinking | Graphs |
| | Marcel/Petra scoring |

**Hard Requirements**:
- Minimum 300 words per chapter (500-700 for Chapter 0)
- Written, continuous prose
- Analytical, reflective, explanatory

**AI Role**: AI operates ONLY in this plane. AI may reason, explain, contextualize. AI may NOT introduce new facts.

### 🟨 PLANE C — FACTUAL ANCHOR PLANE (CENTER–LOWER)

**Purpose**: Verifiable truth & completeness  
**Answers**: "What do we actually know?"

| Allowed | Forbidden |
|---------|-----------|
| KPIs, parameters | Narrative prose |
| Registry facts | Interpretation |
| Missing data indicators | Opinions |
| Data provenance | Preferences |

**Structure**: Structured blocks, tables, explicit "missing / unknown" markers.

### 🟥 PLANE D — HUMAN PREFERENCE PLANE (RIGHT)

**Purpose**: Personal relevance & divergence  
**Answers**: "How does this land for Marcel vs Petra?"

| Allowed | Forbidden |
|---------|-----------|
| Marcel vs Petra comparisons | Raw registry data |
| Comfort vs strategy | KPI tables |
| Match indices, mood scores | Narrative explanation |
| Aesthetic vs technical tension | Visual analytics |

**Rule**: This plane consumes outputs from B & C. It never invents facts.

---

## 📁 FILE STRUCTURE

### Backend (Python)

```
backend/domain/
├── plane_models.py          # 🔵 PlaneAVisualModel, PlaneBNarrativeModel, 
│                            #    PlaneCFactModel, PlaneDPreferenceModel
├── plane_validator.py       # 🔵 PlaneValidator, PlaneViolationError
├── plane_generator.py       # 🔵 generate_four_plane_chapter()
```

### Frontend (TypeScript/React)

```
frontend/src/
├── types/
│   ├── planes.ts            # 🔵 TypeScript plane type definitions
│   └── index.ts             # Re-exports plane types
├── components/
│   └── FourPlaneChapter.tsx # 🔵 4-column layout component
└── index.css                # 🔵 4-plane CSS styling
```

### Tests

```
backend/tests/
└── test_four_plane_model.py # ✅ 19 passing tests
```

---

## 🏗️ CODEBASE NAMING (MANDATORY)

These names exist in code, not just comments:

- `PlaneAVisualModel`
- `PlaneBNarrativeModel`
- `PlaneCFactModel`
- `PlaneDPreferenceModel`
- `ChapterPlaneComposition`
- `PlaneViolationError`
- `PlaneValidator`

---

## ⛔ ENFORCEMENT & REFUSAL RULES

### Hard Refusal Conditions

The system **MUST** reject output if:

1. KPIs appear in Plane B
2. Narrative appears in Plane C
3. Visuals appear outside Plane A
4. Preferences leak into narrative
5. A chapter has <300 words narrative
6. AI invents data not in registry

### Error Message (Mandatory)

```
PLANE VIOLATION ERROR:
Output attempted to cross cognitive planes.
Refactor required. Output rejected.
```

---

## 📋 PER-CHAPTER PLANE COMPOSITION

### Chapter 0 — Executive Summary
- **A**: High-level market visuals
- **B**: Strategic narrative (500–700 words)
- **C**: Key KPIs summary
- **D**: Joint Marcel/Petra synthesis

### Chapters 1–10 (Core Analysis)
- **A**: Chapter-specific visuals (optional but encouraged)
- **B**: Minimum 300 words narrative
- **C**: Full KPI & parameter set
- **D**: Explicit Marcel vs Petra interpretation

### Chapter 11 — Market Positioning
- **A**: Comparative visuals **mandatory**
- **B**: Strategy narrative
- **C**: Price, comps, ranges
- **D**: Risk appetite divergence

### Chapter 12 — Advice & Conclusion
- **A**: Scenario visuals
- **B**: Final reasoning narrative
- **C**: Decision KPIs
- **D**: Final alignment / tension

---

## 🤖 PLANE-AWARE AI PROMPTING

The AI system prompt for Plane B narrative generation:

```
You are generating Plane B output ONLY.

You are forbidden from:
- listing KPIs
- showing tables
- mentioning raw values
- creating visuals
- scoring preferences

You must:
- write a minimum of 300 words
- interpret existing registry data
- explain implications, risks, and meaning
- assume KPIs are shown elsewhere

If you cannot meet these rules, return an error.
```

---

## ✅ TEST COVERAGE

All 19 tests pass:

| Test Category | Tests | Status |
|--------------|-------|--------|
| PlaneAVisualModel | 3 | ✅ |
| PlaneBNarrativeModel | 4 | ✅ |
| PlaneCFactModel | 3 | ✅ |
| PlaneDPreferenceModel | 2 | ✅ |
| PlaneValidator | 3 | ✅ |
| ChapterPlaneComposition | 2 | ✅ |
| CreateValidatedChapter | 2 | ✅ |

---

## 🚀 USAGE

### Backend: Generate a 4-Plane Chapter

```python
from backend.domain.plane_generator import generate_four_plane_chapter
from backend.domain.pipeline_context import PipelineContext

# Generate chapter with validation
chapter = generate_four_plane_chapter(
    chapter_id=5,
    ctx=pipeline_context,
    chapter_data=raw_chapter_data,
    ai_narrative=generated_narrative,
    validate=True  # Will raise PlaneViolationError on failure
)
```

### Frontend: Render a 4-Plane Chapter

```tsx
import { FourPlaneChapter } from './components/FourPlaneChapter';

<FourPlaneChapter 
    chapter={chapterData}
    chapterIndex={5}
    media={mediaItems}
/>
```

---

## 🎨 UI PREVIEW

The 4-Plane layout provides:

1. **Color-coded headers** for cognitive clarity
2. **Responsive grid** (12-column system)
3. **Synchronized scroll behavior**
4. **Plane violation error states**
5. **Radar, bar, and gauge charts** for Plane A
6. **Rich prose formatting** for Plane B
7. **KPI cards with provenance** for Plane C
8. **Persona comparison cards** for Plane D

---

## VERSION

Implementation Date: December 24, 2024
