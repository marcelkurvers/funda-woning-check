# GOLDEN REFERENCE: CHAPTER 1 — KERNGEGEVENS

**Version:** 1.0  
**Date:** 2025-12-25  
**Status:** Authoritative Design Specification  
**Classification:** Four-Plane System Compliance Standard

---

## 1. CHAPTER INTENT (WHY THIS CHAPTER EXISTS)

### Key Question Chapter 1 Answers

> "What is this property, objectively?"

Chapter 1 answers the foundational question every buyer must resolve before any deeper analysis: **What are the measurable, verifiable facts about this property?** This is not interpretation. This is not preference. This is the immutable factual ground truth upon which all subsequent reasoning depends.

### Why This Chapter Matters Early in the Report

Chapter 1 occupies the **second position** (after the Executive Dashboard) because:

1. **Calibration Function** — Before Marcel and Petra can evaluate whether the property matches their needs, they must first understand what the property *is*. Without this baseline, all subsequent opinions are untethered.

2. **Registry Demonstration** — This chapter serves as the first full demonstration that the system operates on verified, sourced facts. It establishes trust: "This report knows what it knows, and admits what it doesn't."

3. **Decision Pre-filtering** — Certain core facts (price, area, rooms) immediately answer binary questions: "Does this property fall within our search parameters?" If the answer is no, the reader may not need to proceed further.

4. **Plane Architecture Proof** — Chapter 1 is the system's clearest example of proper plane separation. The facts are unambiguous (Plane C), the visuals demonstrate proportions (Plane A), the narrative explains implications (Plane B), and preferences reveal divergence (Plane D).

### Decision Confidence This Chapter Must Create

After reading Chapter 1, Marcel and Petra should be able to state with confidence:

- "We know the objective specifications of this property"
- "We understand where data is missing and why"
- "We see how the property compares to reference benchmarks"
- "We recognize where we agree and disagree on foundational priorities"

If the reader cannot make these four statements, Chapter 1 has failed.

---

## 2. GOLDEN UI WALKTHROUGH (WHAT THE USER SEES)

When Marcel and Petra open Chapter 1 in the UI, they encounter a **four-panel layout** that reads like a comprehensive property identity document.

### Initial Visual Scan (0-5 seconds)

The eye is immediately drawn to **Plane A (left)**, where 3-4 data visualizations create instant pattern recognition. A comparison bar chart shows the property's living area against a regional average—immediately signaling whether this is a large, medium, or small property. Below it, a gauge chart places the build year in historical context (1900-2024 scale). The visuals communicate scale and age *before* any text is read.

Simultaneously, the right margin displays **Plane D**, where two compact persona cards for Marcel and Petra show distinct mood indicators (positive/neutral/negative icons) and brief bullet lists of their key values and concerns for this chapter. This creates immediate awareness: "two people are evaluating this together, and they don't see it identically."

### Conscious Reading (5-30 seconds)

The eye moves to **Plane B (center-upper)**, where a flowing narrative of 300-400 words explains *what the core data means*. The narrative references specific facts from Plane C but does not repeat them as raw values—it contextualizes them:

> "The 142 m² living area positions this property above the regional average of 125 m², offering room for a growing family without the premium of villa-segment properties. However, the 1987 construction year places it in a generation of homes often characterized by dated electrical systems and limited insulation—factors that will surface in later chapters."

The tone is analytical but accessible. No marketing language. No enthusiasm. Just reasoned interpretation of facts that the reader can verify in Plane C below.

### Verification and Grounding (30-60 seconds)

The reader's eye drops to **Plane C (center-lower)**, a compact structured block displaying 6-9 KPIs:

| Label | Value | Status |
|-------|-------|--------|
| Vraagprijs | €495.000 | ✓ fact |
| Woonoppervlak | 142 m² | ✓ fact |
| Perceeloppervlak | 380 m² | ✓ fact |
| Kamers | 5 | ✓ fact |
| Slaapkamers | 3 | ✓ fact |
| Bouwjaar | 1987 | ✓ fact |
| Energielabel | C | ✓ fact |
| Prijs/m² | €3.486/m² | ○ derived |
| Garage | — | ⚠ unknown |

Each row has a provenance indicator. Missing data is explicitly marked with a reason ("Data niet in listing" or "Funda vermeldt dit niet"). This block is dense but scannable—designed for reference, not reading.

### Preference Synthesis (60-90 seconds)

Finally, the reader examines **Plane D (right)** in detail. Marcel's card shows a match score (e.g., 72%) with key values ("Price within budget", "Good room count") and concerns ("Energy label needs improvement", "Garage unclear"). Petra's card shows her score (e.g., 68%) with her own priorities ("Space for home office", "Garden potential") and concerns ("1987 construction feels dated", "Kitchen likely needs renovation").

Below the persona cards, a brief "Overlap & Tension" section notes:
- **Overlap:** Both value the room count and outdoor space
- **Tension:** Marcel prioritizes price efficiency; Petra prioritizes modernization potential

This completes the four-plane circuit. The reader has absorbed a visual impression, read an interpretive narrative, verified the underlying facts, and understood how two real humans react differently to the same property.

### What Feels "Rich"

- Plane A charts that show *relative* position, not just raw values
- Plane B narrative that explains *why* a fact matters, not just what it is
- Plane C with 6+ KPIs and explicit missing-data markers
- Plane D with distinct (not mirrored) persona concerns

### What Feels "Empty but Honest"

- Plane A showing 1-2 charts when data is limited, with clear "Not applicable: [reason]" labels
- Plane C with honest "Data missing — reason explained" entries
- Plane D with "Neutral" mood when the property neither excites nor concerns a persona

---

## 3. PLANE-BY-PLANE GOLDEN DEFINITION

### 🟦 PLANE A — VISUAL INTELLIGENCE

**Purpose in Chapter 1:**  
Plane A provides immediate pre-cognitive pattern recognition. Before the reader processes any text, they should *see* what kind of property this is in relative terms.

**Types of Charts/Visuals That MAY Appear:**

1. **Comparison Bar: Living Area vs Average** — Shows property m² against regional average (e.g., 125 m² for vrijstaande woningen). Single bar with reference line.

2. **Gauge: Build Year Position** — Positions the construction year on a 1900-2024 timeline. Communicates "old/medium/new" instantly.

3. **Bar Chart: Room Distribution** — Shows total rooms, bedrooms, bathrooms as stacked or grouped bars.

4. **Ratio Chart: Plot Coverage** — Living area as percentage of plot area. Reveals density vs. outdoor space balance.

**Maximum Reasonable Number of Visuals:**  
4 charts. Beyond this, Chapter 1 becomes visually cluttered and the impact of individual charts diminishes.

**When "Not Applicable" Is Acceptable:**

- If `living_area_m2` is missing, the comparison chart cannot be generated → "Niet toepasbaar: Woonoppervlak onbekend"
- If both `living_area_m2` and `plot_area_m2` are missing, the ratio chart cannot appear
- "Not applicable" is never acceptable for *all* visuals. If Chapter 1 has zero charts, the chapter should flag a diagnostic warning.

**What Would Be Considered a Failure for Plane A:**

- **Narrative text appearing in chart titles** — Titles must be brief labels (max 50 characters)
- **Charts without data source IDs** — Every chart must reference registry keys
- **Illustrative or decorative charts** — No charts based on estimated or invented values
- **More than 4 charts** — Visual overload indicates failure to filter for relevance

---

### 🟩 PLANE B — NARRATIVE REASONING (AI)

**Narrative Role in Chapter 1:**  
Plane B transforms raw facts into meaning. The AI's task is to answer: "Given these specifications, what should Marcel and Petra *understand* about this property before they proceed?"

**Required Structure:**

The narrative should flow through four implicit sections (not necessarily labeled):

1. **Opening Synthesis (50-80 words)** — What type of property is this? How does it position within the market segment?

2. **Factual Interpretation (100-150 words)** — What do the key metrics (area, price, build year) imply? The narrative must reference at least 3 KPIs from Plane C without repeating raw values as bullet points.

3. **Data Gaps & Uncertainties (50-80 words)** — What is missing and why does it matter? Honest acknowledgment of limits.

4. **Forward Orientation (50-80 words)** — What questions does this chapter raise that later chapters will address?

**Minimum Word Count:** 300 words (enforced by backbone)

**How It References Insights from Planes A and C:**

The narrative may state:
> "As the area comparison [Plane A reference] shows, this property exceeds the regional average by 14%. This positions it [reasoning] in the upper-middle segment [interpretation], which the price point [Plane C: asking_price_eur] confirms."

The narrative must NEVER:
- Invent facts not in the registry
- State raw KPIs without interpretation ("The area is 142 m²" alone is prohibited)
- Include Marcel/Petra opinions (those belong in Plane D)

**What "Excellent" Narrative Depth Looks Like:**

- Every key fact is *explained*, not just stated
- The narrative anticipates reader questions ("You may wonder why the price/m² seems high—the explanation lies in the plot size...")
- Clear causal reasoning ("Because the build year is 1987, you should expect...")
- Explicit acknowledgment of uncertainty ("Without garage data, we cannot assess...")

**What Would FAIL Validation or Expectations:**

- **Less than 300 words** → Hard failure (BackboneEnforcementError)
- **Bullet-point KPI dumps** → Plane violation (content belongs in Plane C)
- **Marcel/Petra references** → Plane violation (content belongs in Plane D)
- **Charts or graphs** → Plane violation (content belongs in Plane A)
- **Marketing language** ("Stunning opportunity!") → Tone violation
- **Speculation presented as fact** → Integrity violation

---

### 🟨 PLANE C — FACTUAL ANCHORS

**Categories of KPIs/Parameters Expected in Chapter 1:**

| Category | KPIs | Registry Keys |
|----------|------|---------------|
| **Price** | Vraagprijs, Prijs/m² | `asking_price_eur`, `price_per_m2` |
| **Size** | Woonoppervlak, Perceeloppervlak, Inhoud | `living_area_m2`, `plot_area_m2`, `volume_m3` |
| **Structure** | Kamers, Slaapkamers, Badkamers | `rooms`, `bedrooms`, `bathrooms` |
| **Context** | Bouwjaar, Energielabel | `build_year`, `energy_label` |

**Typical Range of Number of KPIs:**  
- Minimum: 5 (below this, the chapter is diagnostically "thin")
- Target: 7-9
- Maximum: 12 (beyond this, consider moving lower-priority items to later chapters)

**How Missing Data Must Be Explained:**

Every expected KPI that cannot be retrieved must appear with:
- A `missing_reason` field (e.g., "Niet vermeld in Funda-listing", "Scraping mislukt", "Niet-standaard veld")
- The provenance field set to `"unknown"`

Example:
```
{ key: "garage", label: "Garage", value: null, provenance: "unknown", missing_reason: "Funda vermeldt dit niet" }
```

Silent gaps are prohibited. If a KPI is expected but absent, the system must explain why.

**How Plane C Grounds Plane B:**

Plane B may only interpret values that Plane C explicitly contains. If Plane B references "the energy label" in its narrative, Plane C must contain the `energy_label` KPI. This is a hard constraint: narrative without anchor is rejected.

**What Would Be Considered "Too Thin":**

- Fewer than 5 KPIs in Chapter 1 (unless data genuinely does not exist)
- All KPIs with provenance `"unknown"` (indicates scraping or registry failure)
- No missing_reason explanations for absent data

**What Would Be Considered "Misleading":**

- Values marked as `"fact"` that are actually derived or inferred
- Computed values (like age from build_year) presented as raw registry facts
- Missing KPIs silently omitted rather than explicitly marked

---

### 🟥 PLANE D — HUMAN PREFERENCE ANALYSIS

**Dimensions of Preference Relevant in Chapter 1:**

Chapter 1 focuses on **foundational priorities**—how Marcel and Petra each weight core property characteristics:

| Dimension | Marcel Tendency | Petra Tendency |
|-----------|----------------|----------------|
| Price Efficiency | Prioritizes €/m² value | Weighs against renovation potential |
| Living Space | Focuses on functional m² | Considers natural light, flow |
| Room Count | Evaluates against family needs | Considers flex-use potential |
| Build Year | Sees as maintenance predictor | Sees as style/character indicator |
| Energy Label | Views as future-cost signal | Views as environmental alignment |

**How Marcel vs Petra Differences Should Appear:**

Each persona is represented by a `PersonaScore` with:
- `match_score`: 0-100 (based on how well core facts align with stated preferences)
- `mood`: positive / neutral / negative / mixed
- `key_values`: 3-5 bullet points of what this persona likes about the core data
- `concerns`: 3-5 bullet points of what gives this persona pause

The two personas must NOT mirror each other. If Marcel's concerns are identical to Petra's, the plane has failed to capture genuine divergence.

**How Neutrality or Alignment Is Shown:**

- **Aligned:** Both personas have the same concern or value → shown in `overlap_points` list
- **Neutral:** A persona has no strong opinion on an aspect → the aspect is not listed in either key_values or concerns
- **Tension:** Personas disagree → shown in `tension_points` list

**What Makes This Plane Valuable (Not Decorative):**

Plane D is valuable when it reveals information that Marcel and Petra *cannot easily articulate themselves*:
- "I didn't realize my partner cared so much about the garage"
- "We actually agree on price efficiency more than I thought"
- "The tension on energy labels is something we should discuss"

If Plane D merely restates obvious facts or presents generic preferences, it is decorative.

**What Failure Looks Like:**

- **Vague prose** instead of structured scores and bullets
- **Forced conflict** that doesn't reflect genuine preference differences
- **Copy-paste personas** where Marcel and Petra have identical content
- **Opinion on interpretation** (e.g., "Marcel thinks the narrative overstates risk") — personas react to *facts*, not to Plane B content
- **Invented preferences** not grounded in declared persona profiles

---

## 4. CROSS-PLANE QUALITY SIGNALS

### Signals That Indicate This Chapter Is High-Value

| Signal | Description |
|--------|-------------|
| **A↔C Alignment** | Every chart in Plane A has corresponding KPIs in Plane C with matching registry IDs |
| **B→C Grounding** | Plane B narrative references at least 3 specific KPIs by logical name |
| **C Completeness** | 7+ KPIs with `provenance: "fact"`, explicit missing_reason for gaps |
| **D Divergence** | Marcel and Petra have at least 2 distinct concerns (not shared) |
| **B→D Separation** | Plane B contains zero persona references; all persona content is in Plane D |
| **Visual Clarity** | Plane A has 2-4 charts, all under 50-character titles |
| **Narrative Depth** | Plane B exceeds 350 words with causal reasoning visible |

### Signals That Indicate the Chapter Is Structurally Valid but Weak

| Signal | Description |
|--------|-------------|
| **Thin KPIs** | Only 5 KPIs in Plane C, all expected but minimal |
| **Generic Narrative** | Plane B reaches 300 words but repeats observations without insight |
| **Identical Personas** | Marcel and Petra have 80%+ overlap in key_values and concerns |
| **Missing Visuals** | Only 1 chart in Plane A, others marked "Not applicable" |
| **No Tensions** | Plane D shows alignment on all dimensions (plausible but suspicious) |

### Signals That Indicate the Chapter Should Fail Diagnostics

| Signal | Failure Type |
|--------|--------------|
| **< 300 words in Plane B** | BackboneEnforcementError — HARD FAIL |
| **Zero charts in Plane A with no explanation** | Diagnostic violation |
| **KPIs with narrative-length values (>200 chars)** | Plane C violation — content belongs in Plane B |
| **Plane B contains raw KPI dumps** | Plane B validation fails |
| **Plane D joint_synthesis > 500 chars** | Plane D violation — extended narrative belongs in Plane B |
| **Registry key referenced in chart but not in registry** | Data integrity failure |
| **Empty Plane D (no persona data at all)** | Structural incompleteness |

---

## 5. ANTI-PATTERNS (CRITICAL)

### Things Previous AI Attempts Often Got Wrong

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| **"The property has 142 m² of living space, 5 rooms, and costs €495.000..."** | Bullet-dump masquerading as narrative. This is Plane C content in Plane B. | Interpret: "The 142 m² positions this property in the upper-middle segment, explaining the €3.486/m² price point." |
| **Generating charts without registry backing** | Visuals must reference actual data. "Illustrative" charts violate the backbone. | Only generate charts for registry keys that exist and have values. |
| **"Marcel zegt: 'Dit huis is perfect!'"** | Invented dialogue. Personas are analytical profiles, not characters. | Use structured PersonaScore with key_values and concerns, not quotes. |
| **Leaving `missing_reason` empty** | Silent gaps are prohibited. | Always explain why data is missing. |
| **Word-padding to reach 300** | Repeating the same point with different wording is detectable and valueless. | Add causal reasoning, implications, forward-looking questions. |

### Tempting but Invalid Shortcuts

| Shortcut | Why It Fails |
|----------|--------------|
| **Using a single template for all chapters** | Each chapter has a distinct chart catalog, KPI set, and narrative focus. Chapter 1 ≠ Chapter 4. |
| **Setting all persona scores to 75%** | Arbitrary scores without registry backing. Scores must derive from stated preference alignment. |
| **Omitting Plane D because "there's no preference data"** | Plane D is mandatory. If preferences are unknown, show default persona profiles with neutral moods. |
| **Merging Plane B and Plane C into one block** | Violates the fundamental architecture. Narrative and facts are separate cognitive functions. |

### Content That Looks Good But Violates the Backbone Philosophy

| Content | Superficial Appearance | Why It Violates |
|---------|------------------------|-----------------|
| **"This beautiful home offers excellent value..."** | Sounds professional | Marketing language is prohibited. Narrative must be analytical, not promotional. |
| **Chart titled "Expected Value Increase Over 10 Years"** | Looks data-driven | Chart is speculative. No registry data supports future projections. |
| **Plane C showing "Estimated Annual Costs: €4.200"** | Appears factual | Derived/estimated values must be clearly marked as such, not presented as registry facts. |
| **Plane D showing "Marcel: 92%, Petra: 91%"** | High alignment seems positive | Suspiciously similar scores suggest copy-paste or formula error. Real divergence is expected. |
| **Narrative that says "As the data shows..." without citing specific KPIs** | Sounds grounded | Vague attribution. Must reference specific Plane C entries by name. |

---

## 6. SUMMARY ACCEPTANCE CRITERIA

**Chapter 1 is considered Golden when:**

1. ☐ Plane A contains 2-4 registry-backed charts with titles < 50 characters
2. ☐ Plane B contains ≥ 300 words of interpretive narrative that references ≥ 3 Plane C KPIs
3. ☐ Plane B contains zero raw KPI dumps, zero persona references, zero charts
4. ☐ Plane C contains ≥ 5 KPIs with correct provenance markers
5. ☐ Plane C explicitly marks missing data with `missing_reason` explanations
6. ☐ Plane D contains distinct Marcel and Petra profiles with ≥ 2 non-overlapping concerns
7. ☐ Plane D contains ≥ 1 tension point and ≥ 1 overlap point
8. ☐ All cross-plane references are validated (chart registry keys exist, narrative KPI references exist)
9. ☐ No plane violates another plane's content rules
10. ☐ Diagnostics show `is_maximized: true`

---

**When someone reads this chapter in the UI, they should say:**

> "This report knows exactly what the property is, admits what it doesn't know, and shows me how two real people see it differently. I trust this foundation."

If that reaction is not achieved, Chapter 1 has failed its purpose.

---

*End of Golden Reference Document*
