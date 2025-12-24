# Release Notes v7.1.0

**Date:** 2025-12-24
**Version:** 7.1.0

## 🚀 New Features

### Enhanced Page Narrative Generation
- Implemented `PAGE_NARRATIVE_SYSTEM_PROMPT` for generating high-quality, editorial-style narratives for property reports.
- **Role-Based Analysis**: The AI now acts as an "Analytisch Redacteur" (Analytical Editor), providing deep insights rather than just summarizing data.
- **Strict Validations**: Output enforced to be at least 300 words, strictly JSON formatted, and free of marketing fluff.
- **Context-Aware**: Narratives are generated using a specific subset of "Relevant Variables" and "KPIs" per chapter, ensuring focused content.

## 🛠 System Improvements

- **IntelligenceEngine V2**: 
  - Complete overhaul of `_generate_ai_narrative` to support the new prompt structure.
  - Enforced `json_mode=True` for robust AI responses.
  - Improved mapping of AI text to `main_analysis` fields in the report.

## 📦 Components
- `backend/intelligence.py`: Updated with new prompt and generation logic.
- `backend/domain/ownership.py`: Verified for data scoping compliance.

## 📝 Notes
- This release deprecates the old "summary-style" AI generation in favor of the new "editorial analysis" model.
- Cross-page dashboard narrative generation is prepared but scheduled for a subsequent pipeline update.
