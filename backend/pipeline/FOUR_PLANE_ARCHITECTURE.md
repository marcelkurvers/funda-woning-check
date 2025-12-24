# 4-PLANE REPORT ARCHITECTURE

**Version: 2.0.0** | **Last Updated: 2024-12-24**

## OVERVIEW

The 4-Plane Report Architecture is a FAIL-CLOSED cognitive model for property analysis reports. Every chapter (0-12) MUST display content in exactly 4 isolated planes. No output may cross planes. EVER.

## THE 4 PLANES

### 🟦 PLANE A — VISUAL INTELLIGENCE (LEFT)

**Purpose:** Pattern recognition & pre-verbal insight  
**Answers:** "What stands out immediately?"

**ALLOWED:**
- Charts, graphs, infographics
- Trends, deltas, comparisons  
- Heatmaps, bars, timelines

**FORBIDDEN:**
- Explanatory text (no prose)
- Interpretation (no meaning)
- Conclusions (no judgments)
- KPIs with semantic meaning attached

**DATA RULE:**
- Visuals may ONLY use registry-verified data
- No AI-generated values
- No illustrative or inferred charts

---

### 🟩 PLANE B — NARRATIVE REASONING (CENTER–UPPER)

**Purpose:** Meaning, interpretation, judgment  
**Answers:** "What does this mean, and why?"

**HARD REQUIREMENTS:**
- Minimum 300 words per chapter (500-700 for Chapter 0)
- Written, continuous prose
- Analytical, reflective, explanatory

**ALLOWED:**
- Interpretation of KPIs
- Contextual reasoning
- Trade-offs
- Scenario thinking

**FORBIDDEN:**
- Raw KPIs (no numbers without context)
- Tables (structured data goes to Plane C)
- Bullet KPI dumps
- Graphs (visual goes to Plane A)
- Marcel/Petra scoring (goes to Plane D)

**AI ROLE:**
- AI operates ONLY in this plane
- AI may reason, explain, contextualize
- AI may NOT introduce new facts

---

### 🟨 PLANE C — FACTUAL ANCHOR (CENTER–LOWER)

**Purpose:** Verifiable truth & completeness  
**Answers:** "What do we actually know?"

**ALLOWED:**
- KPIs
- Parameters  
- Registry facts
- Missing data indicators
- Data provenance

**FORBIDDEN:**
- Narrative prose (goes to Plane B)
- Interpretation (goes to Plane B)
- Opinions (goes to Plane D)
- Preferences (goes to Plane D)

**STRUCTURE:**
- Structured blocks
- Tables
- Explicit "missing / unknown" markers

---

### 🟥 PLANE D — HUMAN PREFERENCE (RIGHT)

**Purpose:** Personal relevance & divergence  
**Answers:** "How does this land for Marcel vs Petra?"

**ALLOWED:**
- Marcel vs Petra comparisons
- Comfort vs strategy tensions
- Aesthetic vs technical tension  
- Match indices, mood scores

**FORBIDDEN:**
- Raw registry data (goes to Plane C)
- KPI tables (goes to Plane C)
- Narrative explanation (goes to Plane B)
- Visual analytics (goes to Plane A)

**RULE:**
- This plane consumes outputs from B & C
- It never invents facts

---

## STRUCTURAL REQUIREMENTS

### Chapter = 4 Planes (Not the Other Way Around)

A chapter is ONLY valid if:
1. Plane A exists (or is explicitly marked `not_applicable`)
2. Plane B exists AND has ≥300 words
3. Plane C exists
4. Plane D exists AND has both Marcel and Petra data

If ANY plane is missing → **chapter is invalid → output is REJECTED**

### Pipeline Contract

The pipeline spine:
1. Knows explicitly PlaneA, PlaneB, PlaneC, PlaneD
2. Validates per plane:
   - Content type
   - Minimum length
   - Forbidden content patterns
3. Refuses output that mixes planes
4. No plane-validation = pipeline fails

### AI Output Rules

AI may NEVER:
- Generate Plane B with KPIs
- Enrich Plane C with narrative text
- Use Plane D for general analysis

If AI violates these rules:
- Output is rejected
- No render
- Clear error message

### UI Layout

```
┌───────────────┬──────────────────────────────┬──────────────────────┬───────────────────────┐
│ PLANE A       │ PLANE B                      │ PLANE C              │ PLANE D               │
│ Visuals       │ Narrative (300+ words)       │ KPIs & Data          │ Marcel / Petra        │
│ (Left)        │ (Center–Upper)               │ (Center–Lower)       │ (Right)               │
└───────────────┴──────────────────────────────┴──────────────────────┴───────────────────────┘
```

The UI:
- Has fixed zones for each plane
- Shows no merged content
- Shows no chapter if any plane is missing/invalid
- PDF is secondary and may NOT weaken these rules

---

## FAIL-CLOSED ENFORCEMENT

### Validation = Fail-Closed

Plane validation happens BEFORE rendering:
- On failure: No UI output, No DB persist, Clear error status
- No test-mode escapes
- No environment flags that bypass

### Blocked Legacy Paths

The following are BLOCKED and will raise runtime errors:
- `build_chapters()` — deprecated
- `chapter.content` — deprecated  
- `fallback_text` — no fallbacks
- Any non-plane-based rendering

---

## FILE STRUCTURE

```
backend/
├── domain/
│   ├── plane_models.py       # Pydantic models for all 4 planes
│   ├── plane_validator.py    # Cross-plane validation rules
│   └── plane_generator.py    # Individual plane generators
├── pipeline/
│   ├── four_plane_backbone.py  # Main backbone generator
│   ├── chapter_generator.py    # Uses backbone for chapters
│   ├── spine.py               # Pipeline execution with validation
│   └── bridge.py              # API bridge
└── validation/
    └── gate.py                # Final validation gate

frontend/
├── src/
│   ├── components/
│   │   └── FourPlaneChapter.tsx  # 4-plane UI component
│   └── types/
│       └── planes.ts             # TypeScript types for planes
```

---

## TESTING REQUIREMENTS

Tests MUST verify:
1. ✅ Every chapter has exactly 4 planes
2. ✅ Plane B has ≥300 words (≥500 for chapter 0)
3. ✅ KPIs appear ONLY in Plane C
4. ✅ Marcel/Petra appear ONLY in Plane D
5. ✅ UI renders nothing if any plane is missing
6. ✅ No fallback paths exist
7. ✅ Validation errors are fatal

Tests that only verify "something renders" are INVALID.

---

## WHY PLANES EXIST

### Problem
Previous iterations mixed content types, leading to:
- KPIs buried in narrative text
- Marcel/Petra preferences scattered
- Visualizations with explanatory text
- Inconsistent chapter structures

### Solution
Strict cognitive separation:
- Visual processing (Plane A) uses pattern recognition
- Narrative reasoning (Plane B) uses language processing
- Factual grounding (Plane C) uses verification
- Preference mapping (Plane D) uses personal alignment

### Why Mixing is Forbidden
Mixing planes:
- Confuses the reader's cognitive processing
- Prevents targeted validation
- Makes AI output unverifiable
- Destroys report consistency

---

## VERSIONING

| Version | Date       | Changes |
|---------|------------|---------|
| 2.0.0   | 2024-12-24 | Fail-closed 4-plane backbone implementation |
| 1.0.0   | 2024-12-23 | Initial plane models and validators |
