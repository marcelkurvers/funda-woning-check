# AI Woning Rapport - AI Intelligence Guide

## 1. Executive Summary
The **AI Woning Rapport** uses a sophisticated "Dual-Layer Narrative Engine" to generate property reports. It combines a **Rule-Based Heuristic Layer** (deterministic logic) with an **AI Enhancement Layer** (probabilistic LLM generation). This ensures that reports are accurate and grounded in data, but also insightful, professional, and deeply personalized for the users, **Marcel & Petra**.

---

## 2. The Intelligence Pipeline

When a report is generated, the `IntelligenceEngine` processes property data through the following stages:

### A. Data Normalization
The engine extracts and cleans core metrics (KPIs) from the `PropertyCore` model:
- **Financials**: Asking price and price per m².
- **Dimensions**: Living area, plot size, and volume.
- **Temporals**: Build year and renovation history.
- **Sustainability**: Energy labels and heating types.

### B. Rule-Based Heuristic Layer (The Foundation)
Before any AI is called, the engine runs deterministic Python logic to build a "Draft Narrative". This layer ensures that even if the AI provider is offline, the report remains functional.
- **Categorization**: Houses are grouped into segments (e.g., "Historic < 1940" or "Top-segment > €1M").
- **Risk Detection**: Automatic flagging of age-related risks (asbestos pre-1994, lead pipes pre-1960).
- **KPI Analysis**: Calculates density ratios (building/plot) and space efficiency.

### C. AI Enhancement Layer (The "Soul")
If an AI provider (Ollama, OpenAI, Claude, or Gemini) is active, the engine sends the draft narrative and raw data to the LLM.

#### **Technical Implementation**
- **System Prompt**: Defines the persona ("Senior Strategic Real Estate Consultant") and the target audience (Marcel & Petra).
- **JSON Mode**: Forces the AI to return a specific data structure:
  ```json
  {
    "title": "Normalized Title",
    "intro": "Executive summary...",
    "main_analysis": "Detailed technical breakdown...",
    "interpretation": "Personal match for Marcel & Petra...",
    "advice": "Actionable next steps...",
    "conclusion": "Final verdict...",
    "strengths": ["Royaal Wonen", "Tech-Ready"]
  }
  ```
- **Async Execution**: The AI call is handled asynchronously with a fallback mechanism and automated event loop bridging (`nest_asyncio`).

---

## 3. Personality & Personalization (Marcel & Petra)

A unique feature of the AI engine is its obsession with the users' specific profiles.

| Persona | Focus Areas | AI Interpretation Logic |
|---------|-------------|-------------------------|
| **Marcel** | Tech, Infrastructure, Energy | Scans for: CAT6 cabling, fiber optics, solar panels, EV charging, smart home readiness. |
| **Petra** | Atmosphere, Comfort, Finish | Scans for: Character, natural light, high-end materials, ergonomic flow, garden aesthetics. |

**The "Killer Feature":** The AI explicitly mentions Marcel and Petra by name in every chapter's `interpretation` section, explaining *why* a specific piece of data matters to them (e.g., "Marcel, let op de meterkast voor de gewenste laadpaal" vs "Petra, de lichtinval in de keuken matcht jouw voorkeur").

---

## 4. Chapter-Specific AI Insights

The engine generates 13 unique chapters, each with specialized AI logic:

1.  **Ch 0: Executive Summary**: High-level impact assessment.
2.  **Ch 1: General Features**: Urban vs. Rural density analysis. Special focus on NEN2580 measurement compliance.
3.  **Ch 2: Personal Match**: Detailed hit/miss analysis of Marcel & Petra's JSON preferences.
4.  **Ch 3: Technical State**: Heuristic risk assessment based on construction periods.
5.  **Ch 4: Energy & Sustainability**: ROI calculation for "A" label migration paths.
6.  **Ch 10: Financial Analysis**: Market vs. Asking price deviation using the `market_avg_price_m2` setting.
7.  **Ch 12: Final Recommendation**: Weighted scoring (1-10) to determine "KOOPWAARDIG" (Buy-worthy) status.

---

## 5. Fallback & Reliability

To ensure the "Zero Regression Policy," the AI engine follows this health chain:
1.  **Configured AI Provider**: (e.g., OpenAI GPT-4o).
2.  **Local Fallback**: (Ollama Llama3).
3.  **Heuristic Fallback**: High-quality rule-based Dutch text (no AI required).
4.  **Error Handling**: If AI returns malformed JSON, the system regex-cleans the output (stripping markdown blocks) before failing back to heuristics.

---
*Generated: 2025-12-20 | Version 2.0*
