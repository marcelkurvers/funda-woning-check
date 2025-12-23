# Future-Proof System Test Strategy
## Canonical Consistency & Render Safety

This document outlines the testing strategy to enforce system invariants for the AI-assisted reporting system. The goal is to ensure long-term architectural integrity where duplication is impossible and AI reasoning is strictly bounded.

### Core Philosophy
Tests validate **invariants** and **contracts**, not implementation details.
- **Invariant**: A condition that must always be true for the system to be valid.
- **Contract**: A formal agreement between layers (e.g., Ownership Layout).

---

### Taxonomy of Tests

#### 1. Registry Integrity Tests
**Goal**: Ensure the "Single Source of Truth" (Layer 1) is immutable and distinct.
- **Uniqueness**: Verify no two registry entries share an ID.
- **Completeness**: Verify all entries have source, type, and confidence.
- **Typing**: Verify strict typing (FACT vs VARIABLE vs KPI).
- **No Orphans**: Verify no "Unknown" derived values exist without a parent source.

#### 2. Ownership & Scope Tests
**Goal**: Enforce "Data Firewalling" (Layer 2).
- **Single Owner**: assert every variable in the Registry maps to exactly one Chapter.
- **Leakage Prevention**: Verify that requesting Context for Chapter X *never* returns variables owned by Chapter Y.
- **No Restatement**: Verify that non-owning pages cannot display raw variables in their primary grid.

#### 3. AI Output Classification Tests
**Goal**: Verify AI acts as an Analyst, not a Recorder (Layer 3).
- **Value Scanning**: Regex scan AI text outputs against Registry values.
- **Fail Condition**: If AI text matches a Registry FACT value verbatim (e.g. "€450.000"), FAIL.
- **Pass Condition**: AI text describes *implications* ("The price is market-conform").

#### 4. Page-Level Value Tests
**Goal**: Ensure every page adds unique value (Layer 4).
- **Variable Uniqueness**: The set of variables displayed across all chapters must have 0% overlap.
- **Insight Presence**: Every chapter must contain at least one "Interpretation" or "Advice" block.

#### 5. Render Gate Enforcement
**Goal**: The "Button-Click Guarantee".
- **Gated Rendering**: Simulate a validation failure (e.g. duplicate fact). Assert the renderer returns an Error Block, not the rendered page.
- **Panic Check**: System must fail loudly (Explicit Error) rather than silently swallowing invalid data.

---

### Failure Handling
- **Invariant Violations**: Treat as critical system failures. Block deployment.
- **Messaging**: Error messages must indicate *which* invariant was broken (e.g. "Invariant 3 Violation: Chapter 7 attempted to display excluded variable 'price'").

---

### Future-Proofing
These tests rely on the *presence* of the Registry and Ownership Map, not their specific contents. If new chapters or variables are added, these tests automatically cover them without code changes.
