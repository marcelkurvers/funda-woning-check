# AI-Enhanced Reporting System Architecture

## CORE INVARIANT (ABSOLUTE)

```
If a factual value appears in a report, it MUST come from the CanonicalRegistry.
AI must never output factual values directly.
```

If this invariant is violated anywhere, the system is incorrect.

---

## Hard Role Separation

### 🧱 SYSTEM (Source of Truth)

The system:
- Parses data
- Computes metrics
- Derives KPIs
- Stores everything in a `CanonicalRegistry`
- **Locks the registry before AI runs**
- Renders all factual values in the report

### 🧠 AI (Interpreter Only)

AI:
- Reasons over registry entries
- Assesses implications
- Explains trade-offs
- Evaluates risks
- Matches against user preferences
- Highlights uncertainties

**AI must NEVER:**
- ❌ Invent facts
- ❌ Compute metrics
- ❌ Output numbers
- ❌ Introduce variables
- ❌ Restate factual values in text

---

## Mandated AI Output Contract

AI output is restricted to a fixed interpretation schema. AI may output ONLY:

```python
{
    "interpretations": [
        {
            "registry_id": "asking_price_eur",
            "assessment": "high|average|low",
            "reasoning": "Interpretive text WITHOUT facts or numbers"
        }
    ],
    "risks": [
        {
            "registry_id": "energy_label",
            "impact": "low|medium|high",
            "explanation": "Interpretive text only"
        }
    ],
    "preference_matches": [
        {
            "preference_id": "quiet_neighborhood",
            "registry_id": "road_noise_db",
            "fit": "good|neutral|poor"
        }
    ],
    "uncertainties": [
        {
            "registry_id": "maintenance_history",
            "reason": "missing|uncertain"
        }
    ],
    "title": "Chapter title",
    "summary": "Brief interpretive summary WITHOUT numbers",
    "detailed_analysis": "Extended analysis WITHOUT specific values"
}
```

### Forbidden in AI Output

| Symbol | Meaning |
|--------|---------|
| ❌ | Numbers (any numeric literal) |
| ❌ | Computed values |
| ❌ | New keys |
| ❌ | Free-form facts |
| ❌ | Derived metrics |
| ❌ | Fallback estimates |

---

## Rendering Rule (Critical)

The renderer:
1. Pulls factual values from the `CanonicalRegistry` ONLY
2. Formats them using system formatters
3. Renders AI text around facts, never containing them

### Example

```
❌ BAD: "The asking price is €500.000, which is high."

✅ GOOD: 
   System: "Vraagprijs: €500.000"
   AI: "This is considered high relative to comparable properties."
```

---

## Pipeline Enforcement

The system ensures:

1. **AI output is validated structurally** against the interpretation schema
2. **Every `registry_id` referenced by AI** must exist in the registry
3. AI output containing:
   - Unknown keys → **FAILS pipeline**
   - Numbers → **FAILS pipeline**
   - Values not backed by registry → **FAILS pipeline**
4. **Registry is locked before AI runs**
5. **Reports render only if validation passes**
6. **No fallback logic computes facts outside the registry**

---

## Architecture Components

### 1. `domain/registry.py` - Canonical Registry
- Single source of truth for all facts
- Immutable once locked
- Conflict detection on registration

### 2. `domain/ai_interpretation_schema.py` - AI Output Schema
- Defines allowed AI output structures
- Validates for numeric content
- Rejects fact patterns in text

### 3. `domain/fact_safe_renderer.py` - Fact-Safe Renderer
- Renders facts from registry only
- Formats using system formatters
- Keeps AI interpretations separate

### 4. `pipeline/ai_output_validator.py` - Validator
- Validates AI output immediately after generation
- Detects numeric literals
- Rejects unknown registry references

### 5. `pipeline/spine.py` - Pipeline Spine
- Single execution path for reports
- Enforces phase discipline
- Blocks rendering on validation failure

---

## Testing the Invariant

The end-to-end test (`tests/e2e/test_invariant_enforcement.py`) proves:

1. ✅ No AI output string contains a numeric literal
2. ✅ All facts in reports originate from CanonicalRegistry
3. ✅ Removing AI does not change factual content
4. ✅ Schema makes fact invention impossible

**If this test passes, enforcement is REAL.**

---

## Success Criteria (Binary)

You are done only when:

- [ ] AI cannot invent or restate facts
- [ ] Registry is the only factual source
- [ ] Removing AI does not change factual content
- [ ] Audits can no longer find "AI invented fact" paths
- [ ] Enforcement no longer depends on prompt compliance

---

## Key Files Changed

| File | Purpose |
|------|---------|
| `domain/ai_interpretation_schema.py` | NEW - Mandated AI output contract |
| `domain/fact_safe_renderer.py` | NEW - Registry-only fact rendering |
| `pipeline/ai_output_validator.py` | UPDATED - Numeric detection |
| `tests/e2e/test_invariant_enforcement.py` | NEW - Convergence proof |

---

## Final Note

> **Do not try to "detect" AI mistakes. Make them impossible.**

The architecture is designed so that:
- The schema has no field where facts could be injected
- Numeric patterns are detected and rejected
- Registry references are validated
- The pipeline fails closed on any violation

This is structural enforcement, not behavioral detection.
