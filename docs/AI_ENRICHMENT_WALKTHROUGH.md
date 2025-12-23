# AI Enrichment & Trust Architecture: Implementation Walkthrough

## Summary
We have transformed the AI report from a static narrative into a dynamic, transparent advisory system. The report now "proves" its insights by surfacing domain variables, reasoning, and provenance.

## Key Accomplishments
1.  **AI Provenance Header**: Every chapter now clearly displays which AI model generated the content, the timestamp, and a confidence score.
2.  **Domain Variable Grid**: We implemented a structured variable check (14 variables per chapter) that distinguishes between **Fact** (extracted from Funda), **Inferred** (derived by AI), and **Unknown**.
3.  **Proof of Reasoning**: For every inferred variable, the AI now provides a "reasoning" snippet explaining *why* it reached that conclusion.
4.  **Automatic Missing Data Detection**: Fields that are truly missing from the source are explicitly flagged as "Onbekend", alerting the user to perform manual inspection during a viewing.

## Detailed Changes
- **Backend Model**: Added `AIProvenance` and `source_stats` to the core data models.
- **Intelligence Engine**: Refactored the prompt system to use an authoritative domain model. The AI now returns structured metadata for each chapter.
- **Dynamic Key Resolution**: Implemented `_smart_get` in `EditorialEngine` to robustness against varying data keys (e.g., `price` vs `asking_price_eur`), eliminating brittle upstream normalization.
- **Base Rendering**: The `BaseChapter` now generates a "Modern Magazine v2" layout which includes the provenance header and the variable grid.
- **Frontend Integration**: Updated `App.tsx` to surface the global AI status bar for every chapter.

## Verification
- Checked Chapter 0 and 1: They now display the new Variable Grid and Provenance Header.
- Verified AI fallback: Chapters 2-12 automatically benefit from the new structured prompt and rendering logic.
- Confidence scoring: AI now assigns confidence levels to its analysis.
