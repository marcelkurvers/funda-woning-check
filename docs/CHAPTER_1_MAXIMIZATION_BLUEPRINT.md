# CHAPTER 1 MAXIMIZATION BLUEPRINT

**Version:** 1.0  
**Date:** 2025-12-25  
**Status:** Contract-Bound Implementation Specification  
**Classification:** Four-Plane Backbone Constraint Document

---

## OPERATING ASSUMPTIONS

This blueprint assumes the following are immutable:

1. `FourPlaneBackbone` in `four_plane_backbone.py` — sole gate for chapter output
2. `FourPlaneMaxExtractor` in `four_plane_extractors.py` — sole extraction logic
3. `PLANE_A_CHART_CATALOG[1]` — defines permitted Chapter 1 visuals
4. `PLANE_C_KPI_CATALOG[1]` — defines permitted Chapter 1 KPIs
5. `CanonicalRegistry` — locked before chapter generation; unmodifiable
6. `BackboneEnforcementError` — hard failure; no recovery path

Any maximalization strategy that conflicts with these components is invalid.

---

## 1. PLANE-BY-PLANE MAXIMALIZATION STRATEGY

### 🟦 PLANE A — VISUAL INTELLIGENCE

#### What "Maximum Useful Value" Means in Practice

Plane A is maximized when:

| Condition | Measurement |
|-----------|-------------|
| All 4 Chapter 1 catalog charts are generated | `charts_generated == 4` |
| Each chart references ≥1 registry key | `len(data_source_ids) >= 4` |
| No chart has a title > 50 characters | Validated by `PlaneAVisualModel` |
| Missing charts have explicit fallback reasons | `len(charts_missing_reasons) == (4 - charts_generated)` |

**Maximum useful bound = 4 charts**. Beyond this, the contract does not define additional visuals for Chapter 1.

#### Contract Limits That Apply

Per `PLANE_A_CHART_CATALOG[1]`:

| Chart ID | Chart Type | Required Registry Keys | Fallback If Missing |
|----------|------------|------------------------|---------------------|
| `ch1_area_scale` | comparison | `living_area_m2` | "Woonoppervlak onbekend - schaal niet bepaalbaar" |
| `ch1_plot_ratio` | bar | `living_area_m2`, `plot_area_m2` | "Perceel of woonoppervlak onbekend" |
| `ch1_rooms_distribution` | bar | `rooms`, `bedrooms` | "Kamerindeling onbekend" |
| `ch1_build_period` | gauge | `build_year` | "Bouwjaar onbekend" |

No additional charts may be invented. No substitutes exist.

#### Mandatory, Optional, and Conditionally Applicable Elements

| Element | Status | Condition |
|---------|--------|-----------|
| `ch1_area_scale` | Mandatory if data exists | `living_area_m2` in registry |
| `ch1_plot_ratio` | Conditional | Both `living_area_m2` AND `plot_area_m2` in registry |
| `ch1_rooms_distribution` | Conditional | Both `rooms` AND `bedrooms` in registry |
| `ch1_build_period` | Mandatory if data exists | `build_year` in registry |
| `data_source_ids` | Mandatory always | Must reflect actual registry keys used |
| `not_applicable_reason` | Mandatory if `charts == []` | Cannot be empty string |

#### What Must Be Shown When Maximalization Is Not Achievable

If fewer than 4 charts are generated:

```python
PlaneAVisualModel(
    charts=[...generated...],
    data_source_ids=[...used keys...],
    not_applicable=True if len(charts) == 0 else False,
    not_applicable_reason="<fallback_if_missing from each failed ChartSpec>"
)
```

The `charts_missing_reasons` list must contain exactly the `fallback_if_missing` string for each chart that could not be generated. No paraphrasing. No omission.

---

### 🟩 PLANE B — NARRATIVE REASONING (AI)

#### What "Maximum Useful Value" Means in Practice

Plane B is maximized when:

| Condition | Measurement |
|-----------|-------------|
| Word count ≥ 300 | `word_count >= 300` |
| Word count ≤ 500 | Beyond 500 adds diminishing value; risks padding |
| References ≥ 3 Plane C KPIs by logical name | Manual audit or NLP check |
| Contains 4 structural sections | Opening, Interpretation, Gaps, Forward Orientation |
| Zero raw KPI dumps | No "Label: Value" patterns |
| Zero persona references | No "Marcel" or "Petra" mentions |

**Maximum useful bound = 450-500 words** of substantive, non-repetitive prose.

#### Contract Limits That Apply

Per `DEFAULT_NARRATIVE_CONTRACT`:

```python
NarrativeRequirement(
    min_words=300,
    required_sections=[
        "Wat we zeker weten (feitelijk)",
        "Wat dit betekent (interpretatie)",
        "Risico's & onbekenden",
        "Acties / Vervolgvragen"
    ],
    required_references={"plane_c_kpi": 2, "plane_d_persona": 1, "plane_a_visual": 1}
)
```

Note: `plane_d_persona: 1` is a contract requirement but **must not be satisfied by naming "Marcel" or "Petra" directly**. The narrative may reference "the preference analysis" or "buyer priorities" without naming personas.

#### Mandatory, Optional, and Conditionally Applicable Elements

| Element | Status | Condition |
|---------|--------|-----------|
| `narrative_text` | Mandatory always | Cannot be empty; min_length=100 chars |
| `word_count >= 300` | Mandatory | Hard failure if violated |
| `ai_generated=True` | Mandatory | Must be True for Plane B |
| `ai_provider`, `ai_model` | Mandatory if available | From provenance |
| `not_applicable` | Fixed: `False` | Narrative is never "not applicable" |

#### What Must Be Shown When Maximalization Is Not Achievable

**Plane B cannot be "not maximized" — it must always reach 300 words or the chapter fails.**

If the AI generates < 300 words, `BackboneEnforcementError` is raised:

```python
BackboneViolation(
    chapter_id=1,
    plane="B",
    violation_type=BackboneViolationType.PLANE_B_INSUFFICIENT_WORDS,
    message=f"Narrative has {word_count} words, minimum is 300"
)
```

There is no "partial" Plane B. There is no fallback.

---

### 🟨 PLANE C — FACTUAL ANCHORS

#### What "Maximum Useful Value" Means in Practice

Plane C is maximized when:

| Condition | Measurement |
|-----------|-------------|
| All 9 Chapter 1 catalog KPIs extracted or explicitly missing | `len(kpis) == 9` |
| ≥ 5 KPIs have `completeness=True` | Contract minimum threshold |
| Each missing KPI has `missing_reason` populated | No `None` reasons |
| Derived metrics computed where possible | `price_per_m2`, `building_ratio` in parameters |
| `data_sources` includes "registry", "extractor" | Always |

**Maximum useful bound = 9 KPIs** per `PLANE_C_KPI_CATALOG[1]`.

#### Contract Limits That Apply

Per `PLANE_C_KPI_CATALOG[1]`:

| KPI ID | Label | Registry Key | Unit | Format | Derived? |
|--------|-------|--------------|------|--------|----------|
| `ch1_price` | Vraagprijs | `asking_price_eur` | € | currency | No |
| `ch1_area` | Woonoppervlak | `living_area_m2` | m² | — | No |
| `ch1_plot` | Perceeloppervlak | `plot_area_m2` | m² | — | No |
| `ch1_rooms` | Kamers | `rooms` | — | — | No |
| `ch1_beds` | Slaapkamers | `bedrooms` | — | — | No |
| `ch1_year` | Bouwjaar | `build_year` | — | — | No |
| `ch1_energy` | Energielabel | `energy_label` | — | — | No |
| `ch1_volume` | Inhoud | `volume_m3` | m³ | — | No |
| `ch1_price_m2` | Prijs/m² | — | €/m² | — | Yes: `asking_price_eur`, `living_area_m2` |

**Minimum threshold for diagnostics (not hard failure): 5 KPIs with `completeness=True`**

Per `PLANE_C_MIN_KPIS[1] = 5`.

#### Mandatory, Optional, and Conditionally Applicable Elements

| Element | Status | Condition |
|---------|--------|-----------|
| `kpis` list | Mandatory | Must contain all catalog entries (complete or incomplete) |
| `provenance` per KPI | Mandatory | `"fact"`, `"derived"`, or `"unknown"` |
| `missing_reason` | Mandatory if `value=None` | Exact wording per extractor |
| `parameters` | Mandatory | Derived metrics dictionary |
| `data_sources` | Mandatory | Always `["registry", "extractor"]` minimum |
| `not_applicable` | Fixed: `False` | Facts are never "not applicable" |

#### What Must Be Shown When Maximalization Is Not Achievable

Each KPI that cannot be extracted appears as:

```python
FactualKPI(
    key="ch1_volume",
    label="Inhoud",
    value=None,
    unit="m³",
    provenance="unknown",
    registry_id="volume_m3",
    completeness=False,
    missing_reason="'volume_m3' niet in registry"
)
```

The `missing_reason` must follow the exact format: `"'{registry_key}' niet in registry"`.

The chapter does not fail if KPIs are missing. The chapter fails only if Plane B is insufficient.

---

### 🟥 PLANE D — HUMAN PREFERENCE ANALYSIS

#### What "Maximum Useful Value" Means in Practice

Plane D is maximized when:

| Condition | Measurement |
|-----------|-------------|
| Marcel has ≥ 3 `key_values` and ≥ 2 `concerns` | `len(marcel.key_values) >= 3` |
| Petra has ≥ 3 `key_values` and ≥ 2 `concerns` | `len(petra.key_values) >= 3` |
| Marcel and Petra have ≥ 2 non-overlapping concerns | Set difference ≥ 2 |
| ≥ 1 tension point | `len(tensions) >= 1` |
| ≥ 1 overlap point | `len(overlaps) >= 1` |
| ≥ 3 comparisons | Per chapter comparison aspects |
| `joint_synthesis` ≤ 500 chars (if present) | Only for Chapter 0 |

**Maximum useful bound:**
- 5 key_values per persona
- 5 concerns per persona
- 3 comparisons per chapter
- 3 tensions, 3 overlaps

#### Contract Limits That Apply

Per `DEFAULT_PLANE_D_CONTRACT`:

```python
PlaneDContract(
    marcel=PersonaRequirement(min_positives=3, min_concerns=3, require_tradeoff_text=True),
    petra=PersonaRequirement(min_positives=3, min_concerns=3, require_tradeoff_text=True),
    require_tensions=True,
    require_overlap=True,
    min_tension_count=1,
    min_overlap_count=1
)
```

Note: Chapter 1 does not include `joint_synthesis` (that is Chapter 0 only).

#### Mandatory, Optional, and Conditionally Applicable Elements

| Element | Status | Source |
|---------|--------|--------|
| `marcel.key_values` | Mandatory | From `_generate_positives("marcel", 1)` |
| `marcel.concerns` | Mandatory | From `_generate_concerns("marcel", 1)` |
| `petra.key_values` | Mandatory | From `_generate_positives("petra", 1)` |
| `petra.concerns` | Mandatory | From `_generate_concerns("petra", 1)` |
| `comparisons` | Mandatory | From `aspects[1]`: ["Ruimte", "Prijs", "Bouwjaar"] |
| `tension_points` | Mandatory | At least 1 |
| `overlap_points` | Mandatory | At least 1 |
| `match_score` | Optional | From `chapter_data.get("marcel_match_score")` |
| `mood` | Derived | From score or summary |
| `not_applicable` | Fixed: `False` | Preferences are never "not applicable" |

#### What Must Be Shown When Maximalization Is Not Achievable

Plane D cannot fail to generate content — the extractor uses chapter-specific defaults:

```python
marcel_positives[1] = ["Objectgegevens volledig", "Bouwjaar traceerbaar", "Oppervlaktes gedocumenteerd"]
marcel_concerns[1] = ["Sommige basisdata ontbreekt", "Verificatie tijdens bezichtiging nodig"]
```

If external persona data is missing, these defaults are used. There is no empty Plane D.

---

## 2. REGISTRY DEPENDENCY MAP (CRITICAL)

### Plane A Registry Dependencies

| Chart | Required Keys | Common Missing Status | Absence Surfacing |
|-------|---------------|----------------------|-------------------|
| `ch1_area_scale` | `living_area_m2` | Rare (usually present) | "Woonoppervlak onbekend - schaal niet bepaalbaar" |
| `ch1_plot_ratio` | `living_area_m2`, `plot_area_m2` | Common (`plot_area_m2` often missing for apartments) | "Perceel of woonoppervlak onbekend" |
| `ch1_rooms_distribution` | `rooms`, `bedrooms` | Moderate (sometimes only total rooms) | "Kamerindeling onbekend" |
| `ch1_build_period` | `build_year` | Moderate | "Bouwjaar onbekend" |

**If registry value is absent:** Chart is not generated. Fallback string from `ChartSpec.fallback_if_missing` is added to `charts_missing_reasons`.

### Plane C Registry Dependencies

| KPI | Registry Key | Common Missing Status | Absence Surfacing |
|-----|--------------|----------------------|-------------------|
| `ch1_price` | `asking_price_eur` | Rare | `"'asking_price_eur' niet in registry"` |
| `ch1_area` | `living_area_m2` | Rare | `"'living_area_m2' niet in registry"` |
| `ch1_plot` | `plot_area_m2` | Common (apartments) | `"'plot_area_m2' niet in registry"` |
| `ch1_rooms` | `rooms` | Moderate | `"'rooms' niet in registry"` |
| `ch1_beds` | `bedrooms` | Moderate | `"'bedrooms' niet in registry"` |
| `ch1_year` | `build_year` | Moderate | `"'build_year' niet in registry"` |
| `ch1_energy` | `energy_label` | Moderate | `"'energy_label' niet in registry"` |
| `ch1_volume` | `volume_m3` | Common | `"'volume_m3' niet in registry"` |
| `ch1_price_m2` | — (derived) | Depends on sources | `"Bron 'asking_price_eur' ontbreekt voor berekening"` |

**If registry value is absent:** KPI is still included in list with `value=None`, `completeness=False`, `missing_reason` populated.

### Plane D Registry Dependencies

| Data Point | Registry Key | Common Missing Status | Absence Surfacing |
|------------|--------------|----------------------|-------------------|
| `marcel_match_score` | `marcel_match_score` | Common (not always computed) | Default to `None`, mood defaults to `"neutral"` |
| `petra_match_score` | `petra_match_score` | Common | Default to `None`, mood defaults to `"neutral"` |

**If registry value is absent:** Extractor uses chapter-specific positives/concerns from `marcel_positives[1]` and `petra_concerns[1]`. Mood defaults to `"neutral"`.

### Elements That Cannot Be Registry-Derived

| Element | Plane | Why Not Registry-Derivable | How Handled |
|---------|-------|---------------------------|-------------|
| `narrative_text` | B | AI-generated interpretation | Generated by AI, not extracted |
| `ai_provider`, `ai_model` | B | Runtime metadata | From `chapter_data.get("provenance")` |
| Comparison `marcel_view`, `petra_view` | D | Synthesized from persona profiles | Generated by extractor, not registry |

---

## 3. AI DISCIPLINE RULES (PLANE B ONLY)

### How Plane B Can Reference A and C Without Inventing

**Permitted reference patterns:**

| Pattern | Example | Why Valid |
|---------|---------|-----------|
| Logical name reference | "The living area of 142 m² exceeds the regional average..." | References `ch1_area` by interpretation |
| Comparison reference | "As the scale comparison shows..." | References `ch1_area_scale` chart |
| Proportional reasoning | "With nearly 40% of the plot covered by the building..." | Derived from `building_ratio` parameter |
| Gap acknowledgment | "The absence of volume data limits our assessment..." | References `ch1_volume` missing |

**Prohibited patterns:**

| Pattern | Example | Why Invalid |
|---------|---------|-------------|
| Raw KPI dump | "Vraagprijs: €495.000, Woonoppervlak: 142 m²" | This is Plane C content |
| Invented fact | "The property likely has a garage" | Not in registry |
| Persona attribution | "Marcel would value the room count" | This is Plane D content |
| Comparative invention | "Similar properties in the area..." | No registry data for comparables |

### How Uncertainty Must Be Worded

| Registry State | Required Wording Pattern |
|----------------|-------------------------|
| KPI present but low confidence | "The [label] is recorded as [value], though verification is recommended" |
| KPI missing | "Data for [label] is not available; this limits our assessment of [aspect]" |
| Derived metric | "Based on the available data, [metric] suggests [interpretation]" |
| Multiple gaps | "Several data points remain unconfirmed: [list]. These gaps introduce uncertainty around [aspect]" |

**Prohibited uncertainty phrasings:**

- "We estimate..." (introduces speculation)
- "It is likely that..." (probabilistic claim without basis)
- "Based on typical properties..." (invents comparison set)

### What Narrative Depth Looks Like Without Padding

**Depth indicators:**

| Indicator | Example |
|-----------|---------|
| Causal reasoning | "Because the property was built in 1987, you should anticipate..." |
| Implication chain | "The C energy label, combined with the 142 m² area, suggests monthly energy costs that may warrant..." |
| Forward orientation | "This raises the question of whether renovation budgets should..." |
| Trade-off articulation | "While the price per m² appears competitive, the plot ratio limits..." |

**Padding indicators (to avoid):**

| Indicator | Example |
|-----------|---------|
| Repetition with synonyms | "The area is spacious. The space is generous. There is ample room." |
| Filler phrases | "It is important to note that..." / "One should consider that..." |
| Obvious statements | "A larger living area means more space" |
| Generic advice | "Always consult a professional before purchasing" |

### Phrases and Structures That Must Be Avoided

**Prohibited phrases:**

| Phrase | Reason |
|--------|--------|
| "This stunning property..." | Marketing language |
| "An excellent opportunity..." | Promotional tone |
| "Marcel and Petra both feel..." | Crosses into Plane D |
| "Looking at the data, we can see..." | Filler, no insight |
| "As everyone knows..." | Unsourced claim |
| "Based on market trends..." | Invents external data |

**Prohibited structures:**

| Structure | Reason |
|-----------|--------|
| Bulleted KPI list within narrative | Plane C format in Plane B |
| Table of values | Plane C format in Plane B |
| Chart description with embedded values | Plane A format in Plane B |
| Direct persona quotes | Plane D format in Plane B |

---

## 4. CONTRACT-AWARE FAILURE HANDLING

### What the System Must Show When a Plane Cannot Be Maximized

#### Plane A: Fewer Than 4 Charts

```json
{
  "plane_a": {
    "charts": [...generated charts...],
    "not_applicable": false,
    "not_applicable_reason": null,
    "data_source_ids": [...used registry keys...]
  }
}
```

Additionally, `diagnostics.charts_missing_reasons` contains:
```
["Perceel of woonoppervlak onbekend", "Kamerindeling onbekend"]
```

The UI should render available charts and may optionally show missing reasons in a diagnostic panel. The plane is NOT marked `not_applicable` unless `charts == []`.

#### Plane A: Zero Charts

```json
{
  "plane_a": {
    "charts": [],
    "not_applicable": true,
    "not_applicable_reason": "Geen visuele data beschikbaar: Woonoppervlak onbekend - schaal niet bepaalbaar; Perceel of woonoppervlak onbekend; Kamerindeling onbekend; Bouwjaar onbekend",
    "data_source_ids": []
  }
}
```

The UI must display the `not_applicable_reason` instead of an empty space.

#### Plane B: Insufficient Words (Hard Failure)

This is NOT a graceful degradation. The pipeline throws:

```python
BackboneEnforcementError([
    BackboneViolation(
        chapter_id=1,
        plane="B",
        violation_type=BackboneViolationType.PLANE_B_INSUFFICIENT_WORDS,
        message="Narrative has 247 words, minimum is 300"
    )
])
```

The chapter is NOT generated. The report is NOT rendered.

**There is no partial Plane B. There is no fallback narrative.**

#### Plane C: Fewer Than 5 Complete KPIs

```json
{
  "plane_c": {
    "kpis": [
      {"key": "ch1_price", "value": "€ 495.000", "completeness": true, ...},
      {"key": "ch1_area", "value": "142", "completeness": true, ...},
      {"key": "ch1_plot", "value": null, "completeness": false, "missing_reason": "'plot_area_m2' niet in registry"},
      ...
    ],
    "missing_data": ["Perceeloppervlak", "Inhoud", ...],
    "not_applicable": false
  }
}
```

The UI renders all KPIs, showing a `—` or "Onbekend" for incomplete ones with the `missing_reason` as tooltip.

**Diagnostics flag:** `kpis_generated < PLANE_C_MIN_KPIS[1]` (i.e., < 5) triggers a diagnostic warning, NOT a hard failure.

#### Plane D: Match Scores Missing

```json
{
  "plane_d": {
    "marcel": {
      "match_score": null,
      "mood": "neutral",
      "key_values": ["Objectgegevens volledig", "Bouwjaar traceerbaar", "Oppervlaktes gedocumenteerd"],
      "concerns": ["Sommige basisdata ontbreekt", "Verificatie tijdens bezichtiging nodig"],
      "summary": null
    },
    ...
  }
}
```

The UI renders the persona card without a score gauge, showing key_values and concerns only.

### How This Preserves Trust and Value

| Scenario | Trust Preservation Mechanism |
|----------|------------------------------|
| Missing chart | Explicit reason shown; user understands data gap |
| Missing KPI | Row present with "Onbekend" and reason; user sees what's missing |
| No match score | Persona still shows preferences; score gauge hidden |
| Narrative references gap | Narrative explicitly discusses limitations |

**Principle: No silent degradation. Every gap is named.**

---

## 5. MAXIMALIZATION STOP RULES

### When Maximalization Must STOP

| Plane | Stop Condition | Reason |
|-------|----------------|--------|
| A | 4 charts generated | Contract defines exactly 4 charts for Chapter 1 |
| A | All registry keys exhausted | No additional charts can be derived |
| B | 500 words reached | Diminishing returns; risk of padding |
| B | All required sections covered | Structural completeness achieved |
| C | All 9 catalog KPIs extracted | No additional KPIs defined |
| C | All derived metrics computed | No additional formulas defined |
| D | 5 key_values + 5 concerns per persona | Contract maximum |
| D | 3 comparisons, 3 tensions, 3 overlaps | Contract maximum |

### What Would Be Considered Overreach

| Overreach | Why It Violates Contract |
|-----------|-------------------------|
| Adding a 5th chart | Not in `PLANE_A_CHART_CATALOG[1]` |
| Adding a 10th KPI | Not in `PLANE_C_KPI_CATALOG[1]` |
| Narrative > 600 words | Likely contains padding or cross-plane content |
| Persona with 8 concerns | Exceeds presentation utility; likely repetitive |
| Comparing to external properties | No registry data for comparables |
| Adding market trend chart | Requires external data not in registry |

### What Looks "Richer" But Actually Violates the Contract

| Seeming Enrichment | Violation |
|-------------------|-----------|
| "I'll add estimated renovation costs" | Invented fact not in registry |
| "I'll include a neighborhood score gauge" | Not in Chapter 1 catalog |
| "I'll make the narrative 700 words for depth" | Likely padding or plane crossing |
| "I'll add Marcel's detailed life story" | Plane D is analytical, not biographical |
| "I'll show a price trend over time" | No registry historical data |
| "I'll compare to 5 similar listings" | No registry comparison data |

**Rule: If it's not in the catalog, it cannot appear.**

---

## 6. SELF-AUDIT CHECKLIST (MANDATORY)

Before any Chapter 1 output is considered valid, verify:

### Structural Validation

| Check | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| `plane_a.charts` count ≤ 4 | Yes | | |
| `plane_a.data_source_ids` non-empty if charts exist | Yes | | |
| `plane_a.not_applicable_reason` populated if charts empty | Yes | | |
| `plane_b.word_count` ≥ 300 | Yes | | |
| `plane_b.narrative_text` length ≥ 100 chars | Yes | | |
| `plane_b.not_applicable` == False | Yes | | |
| `plane_c.kpis` count == 9 | Yes | | |
| `plane_c.missing_reason` populated for incomplete KPIs | Yes | | |
| `plane_c.not_applicable` == False | Yes | | |
| `plane_d.marcel.key_values` count ≥ 3 | Yes | | |
| `plane_d.petra.concerns` count ≥ 2 | Yes | | |
| `plane_d.tension_points` count ≥ 1 | Yes | | |
| `plane_d.not_applicable` == False | Yes | | |

### Content Validation

| Check | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| Plane A titles all ≤ 50 characters | Yes | | |
| Plane B contains no KPI tables | Yes | | |
| Plane B contains no "Marcel" or "Petra" names | Yes | | |
| Plane B references ≥ 3 Plane C KPIs by logical name | Yes | | |
| Plane C KPI values match exactly registry values | Yes | | |
| Plane D Marcel ≠ Petra (at least 2 distinct concerns) | Yes | | |

### Registry Traceability

| Check | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| Every `data_source_id` exists in locked registry | Yes | | |
| Every `registry_id` in KPIs exists or is documented missing | Yes | | |
| No value appears that is not registry-sourced or formula-derived | Yes | | |
| Removing any registry key would break exactly the dependent outputs | Yes | | |

### Final Gate Questions

| Question | Required Answer |
|----------|-----------------|
| Would this output render under strict validation? | **Yes** |
| Is every element contract-anchored? | **Yes** |
| Is any value implied that cannot be proven from registry? | **No** |
| Would removing a registry field break exactly the dependent outputs (no silent fallback)? | **Yes** |

**If any answer differs from the required answer, the design is invalid and must be revised.**

---

## APPENDIX: REGISTRY KEYS USED BY CHAPTER 1

For reference, the complete set of registry keys that Chapter 1 may access:

| Key | Type | Used By |
|-----|------|---------|
| `living_area_m2` | FACT | A:area_scale, A:plot_ratio, C:ch1_area, C:ch1_price_m2 |
| `plot_area_m2` | FACT | A:plot_ratio, C:ch1_plot |
| `rooms` | FACT | A:rooms_distribution, C:ch1_rooms |
| `bedrooms` | FACT | A:rooms_distribution, C:ch1_beds |
| `build_year` | FACT | A:build_period, C:ch1_year |
| `asking_price_eur` | FACT | C:ch1_price, C:ch1_price_m2 |
| `energy_label` | FACT | C:ch1_energy |
| `volume_m3` | FACT | C:ch1_volume |
| `marcel_match_score` | KPI | D:marcel.match_score |
| `petra_match_score` | KPI | D:petra.match_score |

No other registry keys are used by Chapter 1 extractors.

---

*End of Chapter 1 Maximization Blueprint*
