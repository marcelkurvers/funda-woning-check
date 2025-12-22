# AI Woning Rapport - AI Intelligence Guide

## 1. Executive Summary
The **AI Woning Rapport** uses a sophisticated "Trust-First Narrative Engine". It combines deterministic data parsing with high-level AI reasoning that is strictly bound by a **Domain Variable Model**. This ensures every AI-generated claim is auditable, transparent, and grounded in either **Fact** or clear **Inference**.

---

## 2. The Intelligence Pipeline

### A. Data Normalization
Core metrics are extracted from Funda and validated:
- **Financials**: Asking price and price per m².
- **Dimensions**: Living area, plot size.
- **Temporals**: Build year and construction period categorization.

### B. Domain Variable Authority
The engine targets specific variables for each of the 14 report chapters.
- **Dynamic Variable Grid**: The AI must populate a predefined JSON map for each chapter.
- **Fact/Inference Labeling**: Each variable is tagged as `fact` (from data), `inferred` (AI interpretation), or `unknown`.
- **Reasoning Snippets**: For every inference (e.g., "Inferred safety risk"), the AI must provide a 1-sentence proof of reasoning.

### C. AI Provenance Tracking
Every report section is signed with an **AI Signature**:
- **Metadata**: Attach provider (e.g., OpenAI), model (e.g., GPT-4o), and precise timestamp.
- **Confidence Rating**: AI self-assesses its analysis as `high`, `medium`, or `low` based on data availability.

---

## 3. The "Lead AI" Refactor (v3.0)

The v3.0 logic introduced in Dec 2025 focuses on **Transparency and Trust**:

#### **Authoritative variable sets by Chapter:**
- **Ch 1 (Features)**: Location, Build Year, Type, m², Energy Label, Heating, Insulation.
- **Ch 6 (Costs)**: Purchase fees, Utility estimates, Maintenance buffer, Renovation impact, TCO 10y.
- **Ch 10 (Value)**: Asking price, WOZ indicator, Market benchmark, Deviation %, Negotiation margin.

#### **JSON Mode Evolution**
The system now demands an enriched JSON structure:
```json
{
  "title": "...",
  "variables": {
    "build_year": { "value": "1935", "status": "fact", "reasoning": "Direct from Funda metadata" },
    "asbestos_risk": { "value": "Moderate", "status": "inferred", "reasoning": "Built between 1940-1994 without remediation proof" }
  },
  "metadata": {
    "confidence": "high",
    "inferred_vars": ["asbestos_risk"],
    "missing_vars": ["maintenance_state"]
  }
}
```

---

## 4. Personality & Personalization (Marcel & Petra)

| Persona | Focus Areas | AI Strategy |
|---------|-------------|-------------|
| **Marcel** | ROI, Infrastructure, TCO | Focuses on technical scalability, internet speeds, and long-term financial feasibility. |
| **Petra** | Atmosphere, Ergonomics, Flow | Focuses on light-quality, character, space usability, and immediate comfort. |

---

## 5. Fallback & Reliability

The engine follows a strict health chain:
1.  **Cloud AI**: GPT-4o / Claude 3.5 (configured in settings).
2.  **Edge/Local AI**: Ollama Llama3 (fallback if cloud is unstable).
3.  **Heuristic Logic**: Dutch rule-based generation (if all AI is offline).

---
*Generated: 2025-12-22 | Version 3.0 (Lead AI Standard)*
