# Features List - AI Woning Rapport

This document tracks the implemented features across the frontend and backend of the AI Woning Rapport.

## 📥 Data Ingestion & Parsing
- [x] **Universal Input**: Support for Funda URLs.
- [x] **Paste Mode**: Support for raw HTML/Text pasting to bypass anti-scraping measures.
- [x] **Robust Regex Parsing**: Handles currency symbols, "m²" suffixes, and localized number formats without corruption.
- [x] **Deep Attribute Extraction**: Captures ~100 fields including isolation, energy label, garden orientation, and VvE details.

## 🧠 Intelligence Engine
- [x] **Contextual Narratives**: Dynamic text generation based on physical property attributes.
- [x] **Safety Logic**: Automatic risk flagging for Asbestos (pre-1994) and Lead (pre-1960).
- [x] **Preference Matching**: Keyword-based scoring for Marcel (Tech/Garage) and Petra (Atmosphere/Garden).
- [x] **Renovation Estimation**: Estimated budgets for upgrading energy labels (F/G -> B/C).
- [x] **Financial Analysis**: Accurate price per m² calculation and market segmentation.

## 💻 Dashboard & UI
- [x] **Bento Grid Layout**: Optimized 5-column grid for high-density information display.
- [x] **Split-View Navigation**: Integrated narrative flow on the left with supporting visuals on the right.
- [x] **Live Progress (SSE)**: Real-time updates as the analysis pipeline completes each stage.
- [x] **Semantic Color System**: Standardized Green/Orange/Red status indicators for all KPIs.
- [x] **4K Optimization**: Fully responsive layout that performs on large professional monitors.

## 📄 Reporting & Export
- [x] **13 Unique Chapters**: Spanning from Executive Summary to final Investment Advice.
- [x] **Interactive Charts**: Visual representation of price comparisons and energy scores.
- [x] **High-Quality PDF**: Professional PDF export via WeasyPrint, mirroring the web dashboard's styling.
- [x] **AI Usage Disclaimer**: Transparency on where AI-driven heuristics are used.

## ⚙️ Backend & Infrastructure
- [x] **FastAPI Architecture**: High-performance asynchronous API handles concurrent runs.
- [x] **Local Persistence**: SQLite database for storing analysis results and user settings.
- [x] **Dockerized Stack**: One-command setup for both frontend and backend using Docker Compose.
- [x] **Zero Regression Suite**: Comprehensive pytest suite covering unit and integration scenarios.
