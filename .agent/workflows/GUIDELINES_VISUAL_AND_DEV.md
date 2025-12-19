---
description: Mandatory Visual Design & Development Rules for AI Woning Rapport
---

# Mandatory Visual Design & Development Rules

This document outlines the strict rules (non-negotiable) for visual design and development practices within the project. Failure to adhere to these rules constitutes a violation of the project charter.

## 1. Development Process Rules (Mandatory)

1.  **NO Cutting Corners**: Every solution must be robust, scalable, and complete. Hacky fixes or partial implementations are strictly forbidden.
2.  **Container Management**: After ANY change to functionality, configuration, dependencies, or static assets, the Docker container MUST be fully rebuilt to ensure the development environment matches the runtime environment.
    *   Command: `docker-compose down -v --remove-orphans && docker-compose build --no-cache && docker-compose up -d`
3.  **Strict Linting**: Code must adhere to the project's linting rules (ESLint/Prettier). No unused variables, no `any` types unless absolutely necessary (and documented), and consistent formatting.
4.  **Error Handling**: All user-facing features must have graceful error handling (Fallbacks). never show a raw error stack trace to the user.

## 2. Visual Design & User Experience (Mandatory)

### Objective
Every visual element must serve one of three purposes:
1.  **Accelerate Understanding** (Functional)
2.  **Increase Trust** (Professionalism)
3.  **Support Action/Decision** (Conversion)

"Just beautiful" is NOT enough. "Ugly" or "Dark/Gloomy" is forbidden.

### Core Principles
*   **Data vs. Atmosphere**: STRICTLY SEPARATE factual data (charts, maps, tables) from atmospheric elements (artwork, icons, backgrounds). Do not mix them in a way that compromises data integrity.
*   **Consistency**:
    *   **ONE Icon Set**: Use `Lucide React` exclusively.
    *   **ONE Color Palette**: Use the predefined `Tailwind` palette (Slate/Blue/Emerald/Rose/Amber) consistently.
    *   **ONE Typography Set**: Sans-serif, clean, legible.
*   **Performance**: Animate responsibly. Micro-interactions (< 250ms) for UI feedback. Skeleton loaders instead of spinners for content loading.

### Visual Components Standards

#### 1. Hero Section (Web/App)
*   **Layout**: Dedicated "Hero" area separate from the header.
*   **Content**: High-quality photo (with fallback) + Key Address + Premium Badge.
*   **Style**: Vivid, bright, inviting. NO solid black blocks. Use gradients, glassmorphism (`backdrop-blur`), and white/light cards with subtle shadows.

#### 2. KPI Tiles
*   **Composition**: Icon + Big Score/Value + Short Interpretation (1 line).
*   **Color Logic**:
    *   **Green (Emerald)**: Positive / Good / Compliant.
    *   **Orange (Amber)**: Warning / Average / Check needed.
    *   **Red (Rose)**: Negative / Critical / Bad.
    *   **Blue/Slate**: Neutral / Informational.
*   **Interaction**: Hover effects (lift/shadow) to indicate interactivity.

#### 3. Charts & Graphs
*   **Waterfall**: Used for Financial/TCO breakdown (Purchase -> Reno -> Energy -> Monthly).
*   **Heatmap**: Used as a 3x3 Matrix for Risk Analysis (Probability x Impact).
*   **Sparklines**: Minimalist line charts for trends inside cards.
*   **Tool**: Recharts (React).

#### 4. Fallbacks
*   **Images**: If a media URL fails, show a high-quality, generic architectural placeholder. NEVER show a broken image icon.
*   **Data**: If a KPI is missing (`None`/`Null`), display "N/B" or "?" with a neutral style, do NOT crash the component.

#### 5. Typography
*   **Headings**: Bold, clear hierarchy (H1 -> H2 -> H3).
*   **Body**: Legible contrast (Slate-600/700 on White), never pure black on pure white.
*   **Numbers**: Monospaced tabular nums for financial tables for alignment.

## 3. Implementation Checklist (Pre-Push)

- [ ] Does the UI feel "Premium" (White/Glass/Light, not heavy dark blocks)?
- [ ] Are all metrics parsed correctly? (No "NaN" or "undefined" visible).
- [ ] Is the Docker container rebuilt?
- [ ] Are fallbacks in place for missing images/data?
- [ ] Is the copy-paste flow robust against bad input?
