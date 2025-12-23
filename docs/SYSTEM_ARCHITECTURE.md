# System Architecture: The 4-Layer Enforcement Model

To guarantee report consistency, non-duplication, and high-quality AI reasoning, the system enforces a strict 4-Layer Architecture. This is not just a guideline; it is enforced by code.

## Layer 1: Canonical Knowledge Registry
**Goal**: Single Source of Truth.
- **Role**: Ingests raw parsed data and normalizes it into a strictly typed Registry.
- **Types**: `FACT` (Raw data), `VARIABLE` (Derived), `KPI` (Calculated), `UNCERTAINTY`.
- **Enforcement**: Before any AI reasoning begins, the `CanonicalRegistry` must be locked.
- **Location**: `backend/domain/registry.py` & `backend/enrichment.py`

## Layer 2: Ownership & Scope Resolution
**Goal**: Data Firewalling.
- **Role**: Determines exactly which variables each Chapter is allowed to "own" (display) or "see" (reason over).
- **Rule**: Chapter 7 (Garden) physically cannot see specific data like "Asking Price" (Chapter 0). This prevents the AI from hallucinating or duplicating facts across pages.
- **Location**: `backend/domain/ownership.py`

## Layer 3: AI Reasoning & Enrichment
**Goal**: Interpretive Logic (No Recording).
- **Role**: The AI (IntelligenceEngine) acts as an Analyst, not a Recorder.
- **Constraint**: It receives only the Scoped Context from Layer 2. Its job is to interpret implications, not restate numbers.
- **Location**: `backend/intelligence.py`

## Layer 4: Validation Gate
**Goal**: The Button-Click Guarantee.
- **Role**: Inspects the AI output before rendering.
- **Checks**:
    1.  **Ownership Violation**: Did the AI invent a variable not allowed in this chapter?
    2.  **Preference Materiality**: Did the AI provide specific reasoning for Marcel & Petra?
    3.  **Restatement**: Did the AI parrot raw facts instead of interpreting them?
- **Behavior**: If validation fails, the rendering overrides the page with an Explicit Error Block, preventing silent quality regression.
- **Location**: `backend/validation/gate.py`

## Verification
The architecture is verified by a dedicated invariant test suite:
- `backend/tests/quality/test_system_invariants.py`
- `backend/tests/quality/test_real_data_architecture.py`
