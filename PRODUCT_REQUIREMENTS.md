# Product Requirements Document (PRD)

## Overview
The **AI Woning Rapport** application generates a comprehensive, AI‑enhanced property report.  This document outlines the functional requirements for each **chapter**, the **dashboard**, supporting **underwater functions** (internal services), and the **preferences comparison & matching** feature.  It is intended for product owners, designers, and developers to ensure a shared understanding of the product scope.

---

## 1. Property Report Structure
The report is divided into **13 chapters** (0‑12).  Each chapter presents a distinct aspect of the property, combining raw data, AI‑generated insights, and visualisations.

| Chapter | Title | Core Functionality | Key UI Elements |
|---------|-------|--------------------|-----------------|
| 0 | **Cover & Summary** | Property overview, address, price, main image | Hero banner, summary card, quick‑stats grid |
| 1 | **Location & Neighborhood** | Walkability scores, transport, schools, amenities | Map view, radar chart, list of nearby POIs |
| 2 | **Price & Market** | Historical price trends, price deviation, market forecast | Line chart, deviation badge, forecast table |
| 3 | **Energy & Sustainability** | Energy label, future energy score, CO₂ footprint | Gauge, sustainability badge, comparison table |
| 4 | **Maintenance & Costs** | Maintenance intensity, yearly cost estimate | Bar chart, cost breakdown card |
| 5 | **Family Suitability** | Size, rooms, suitability for families, schools proximity | Radar chart, suitability score badge |
| 6 | **Long‑Term Quality** | Build year, renovation history, quality index | Timeline, quality index gauge |
| 7 | **Legal & Risks** | Zoning, flood risk, other legal constraints | Icon list, risk heatmap |
| 8 | **Investment Potential** | Rental yield, ROI, cash‑flow projection | ROI calculator, yield gauge |
| 9 | **Design & Layout** | Floor‑plan, interior quality, ergonomics | Interactive floor‑plan, layout score |
|10| **Community & Lifestyle** | Demographics, community vibe, lifestyle score | Demographic pie chart, lifestyle badge |
|11| **Future Development** | Planned projects, infrastructure plans | Map overlay, development timeline |
|12| **Final Recommendation** | AI‑driven advice, strengths, weaknesses, next steps | Recommendation card, action buttons |

---

## 2. Dashboard
The **Dashboard** provides a high‑level overview of the property at a glance and acts as a navigation hub.

### 2.1. Dashboard Components
- **Header** – Property address, main image, primary price.
- **Key Metrics Row** – Price deviation %, Energy Future Score, Maintenance Intensity, Family Suitability, Long‑Term Quality (the five additive metrics).
- **Quick Navigation Tiles** – Direct links to each chapter with preview icons.
- **Comparison Widget** – Side‑by‑side view of user preferences vs. property attributes.
- **Action Bar** – Buttons for **Export PDF**, **Save to Favorites**, **Share**.

### 2.2. Interaction Flow
1. User lands on the dashboard after entering a property URL.
2. Metrics animate in with subtle micro‑animations (fade‑in, count‑up).
3. Hovering a tile expands a tooltip with a short summary of the chapter.
4. Clicking a tile scrolls to the corresponding chapter section.
5. The **Preferences Comparison** widget updates in real‑time as the user tweaks their preference sliders.

---

## 3. Underwater Functions (Internal Services)
These are backend functions that are not exposed to the UI but power the report generation.

| Function | Description | Input | Output |
|----------|-------------|-------|--------|
| `fetch_property_data(url)` | Scrapes or API‑fetches raw property data from Funda. | Property URL | Raw JSON/HTML payload |
| `parse_core_data(raw)` | Extracts core fields (price, address, size, etc.). | Raw payload | `CoreProperty` dataclass |
| `enrich_with_ai(core)` | Calls the AI model to generate narrative, advice, strengths. | `CoreProperty` | `EnrichedProperty` with `interpretation`, `advice`, `strengths` |
| `calculate_metrics(enriched)` | Computes additive metrics (price deviation, energy score, …). | `EnrichedProperty` | Metric dictionary |
| `render_chapter(chapter_id, data)` | Renders HTML for a specific chapter using Jinja templates. | Chapter ID, data dict | HTML string |
| `generate_dashboard(data)` | Assembles the dashboard HTML from metric data. | Metric dict | Dashboard HTML |
| `compare_preferences(user_prefs, property_attrs)` | Calculates similarity score and highlights mismatches. | Preference dict, attribute dict | Comparison object |
| `export_pdf(html)` | Uses WeasyPrint (or Docker container) to convert HTML to PDF. | Full report HTML | PDF binary |

---

## 4. Preferences Comparison & Matching
The system lets users define personal preferences (e.g., budget, family size, sustainability focus). The **matching engine** evaluates how well a property aligns with these preferences.

### 4.1. Preference Model
```json
{
  "budget": {"min": 300000, "max": 600000},
  "familySize": 4,
  "sustainability": "high",
  "desiredRooms": 5,
  "locationScore": 8
}
```
Each field maps to one or more chapter metrics.

### 4.2. Matching Algorithm (High‑Level Steps)
1. **Normalize** both user preferences and property metrics to a 0‑1 scale.
2. **Weight** each dimension based on user‑defined importance.
3. **Compute** a weighted Euclidean distance → similarity score (0‑100%).
4. **Highlight** mismatches in the UI (red for under‑performance, green for over‑performance).
5. **Provide** actionable advice (e.g., “Consider a larger budget to meet desired rooms”).

### 4.3. UI Representation
- **Radar chart** showing user vs. property scores.
- **Slider controls** for each preference; moving a slider instantly updates the radar and similarity percentage.
- **Match Summary Card** with a headline (e.g., “Good match – 78%”) and a list of top‑3 gaps.

---

## 5. Non‑Functional Requirements
- **Performance**: Full report generation ≤ 3 seconds on typical consumer hardware.
- **Responsiveness**: UI adapts from 1280 px to 4K displays, with graceful degradation on mobile.
- **Accessibility**: WCAG 2.1 AA compliance – proper ARIA labels, keyboard navigation.
- **Scalability**: Backend services stateless; can be horizontally scaled behind a load balancer.
- **Security**: Sanitize all scraped HTML, enforce CSP, and limit external API calls.

---

## 6. Acceptance Criteria
- All 13 chapters render correctly with AI‑generated content.
- Dashboard displays the five additive metrics with animated micro‑interactions.
- Preferences comparison updates in real‑time and reflects accurate similarity scores.
- PDF export produces a paginated, styled document matching the on‑screen design.
- Unit tests cover each underwater function and UI component.

---

*Document version: 1.0 – 2025‑12‑15*
