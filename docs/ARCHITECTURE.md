# AI Woning Rapport - System Architecture

**Version**: 2.0
**Last Updated**: 2025-12-20
**Status**: Enhancement Plan

---

## 1. System Overview

AI Woning Rapport is a full-stack real estate analysis platform that transforms Dutch Funda property listings into comprehensive, AI-enriched reports with 13 analysis chapters.

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Landing   │  │   Report    │  │  Settings   │  │  Chapter Layouts    │ │
│  │    Page     │  │    View     │  │    Page     │  │  (Context-Aware)    │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                │                     │            │
│         └────────────────┴────────────────┴─────────────────────┘            │
│                                    │                                          │
│                          ┌─────────▼─────────┐                               │
│                          │  ConfigContext    │                               │
│                          │  (Global State)   │                               │
│                          └─────────┬─────────┘                               │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │ HTTP/REST
┌────────────────────────────────────▼────────────────────────────────────────┐
│                           BACKEND (FastAPI)                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                           API Layer                                      ││
│  │  /runs  /runs/{id}/start  /runs/{id}/status  /api/config  /api/ai/*     ││
│  └──────────────────────────────────┬──────────────────────────────────────┘│
│                                     │                                        │
│  ┌──────────────────────────────────▼──────────────────────────────────────┐│
│  │                        Pipeline Orchestrator                             ││
│  │  ThreadPoolExecutor (async) → scrape → parse → enrich → chapters → pdf  ││
│  └──────────────────────────────────┬──────────────────────────────────────┘│
│                                     │                                        │
│  ┌────────────┐  ┌────────────┐  ┌─▼──────────┐  ┌───────────────────────┐  │
│  │   Parser   │  │  Chapters  │  │Intelligence│  │   AI Provider Layer   │  │
│  │  (HTML→    │  │   (0-12)   │  │   Engine   │◄─┤  Ollama│OpenAI│etc.   │  │
│  │   Data)    │  │            │  │            │  │                       │  │
│  └────────────┘  └────────────┘  └────────────┘  └───────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                      Configuration System                                ││
│  │  AppSettings (Pydantic) ← .env + SQLite app_config table                ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
            ┌──────────────┐                 ┌──────────────┐
            │   SQLite     │                 │   Ollama     │
            │  local_app.db│                 │   (Local)    │
            └──────────────┘                 └──────────────┘
```

---

## 2. Component Architecture

### 2.1 Frontend Components

```
frontend/src/
├── pages/
│   ├── Landing.tsx          # New UI from zip (Hero + MediaZone)
│   ├── Report.tsx           # Report container with sidebar
│   └── Settings.tsx         # Full configuration page
├── components/
│   ├── layout/
│   │   ├── Header.tsx       # App header with nav
│   │   ├── Footer.tsx       # App footer
│   │   └── BentoLayout.tsx  # Utility grid components
│   ├── landing/
│   │   ├── Hero.tsx         # Landing hero section
│   │   ├── MediaZone.tsx    # Image paste/upload zone
│   │   └── DeepDive.tsx     # Feature showcase cards
│   ├── chapters/
│   │   ├── ChapterRenderer.tsx    # Routes chapter ID → layout
│   │   ├── DashboardLayout.tsx    # Ch 0: Executive summary
│   │   ├── MetricsLayout.tsx      # Ch 1,5,8: Metrics view
│   │   ├── MatchLayout.tsx        # Ch 2: Marcel/Petra split
│   │   ├── RiskLayout.tsx         # Ch 3,9: Risk matrix
│   │   ├── GaugeLayout.tsx        # Ch 4: Energy gauge
│   │   ├── ComparisonLayout.tsx   # Ch 6,7: Comparison view
│   │   ├── FinancialLayout.tsx    # Ch 10,11: Charts/costs
│   │   └── ConclusionLayout.tsx   # Ch 12: Recommendation
│   └── settings/
│       ├── AIProviderSettings.tsx
│       ├── MarketSettings.tsx
│       ├── ParserSettings.tsx
│       └── AppearanceSettings.tsx
├── contexts/
│   └── ConfigContext.tsx    # Global configuration state
├── services/
│   ├── configApi.ts         # Settings API client
│   └── aiApi.ts             # AI provider API client
└── types/
    └── config.ts            # Configuration types
```

### 2.2 Backend Components

```
backend/
├── main.py                  # FastAPI app, routes, pipeline
├── parser.py                # HTML → PropertyCore extraction
├── intelligence.py          # AI narrative generation
├── consistency.py           # Data validation
├── ai/
│   ├── __init__.py
│   ├── provider_interface.py    # Abstract AIProvider base
│   ├── provider_factory.py      # Factory + registry
│   └── providers/
│       ├── __init__.py
│       ├── ollama_provider.py   # Local Ollama
│       ├── openai_provider.py   # OpenAI API
│       ├── anthropic_provider.py # Anthropic Claude
│       └── gemini_provider.py   # Google Gemini
├── config/
│   ├── __init__.py
│   └── settings.py          # AppSettings (Pydantic)
├── chapters/
│   ├── base.py              # BaseChapter abstract class
│   ├── registry.py          # Chapter ID → class mapping
│   └── chapter_0.py ... chapter_12.py
├── domain/
│   └── models.py            # PropertyCore, ChapterOutput, etc.
└── tests/
    ├── unit/
    └── integration/
```

---

## 3. Data Flow

### 3.1 Report Generation Pipeline

```
1. User Input (Landing Page)
   │
   ├─► Paste HTML ─────────────────────────────────────┐
   │                                                    │
   └─► Enter Funda URL ──► Scraper ──► HTML ───────────┤
                                                        ▼
2. POST /runs                                     Create Run
   │                                              (SQLite)
   ▼
3. POST /runs/{id}/start ──► Returns immediately (non-blocking)
   │
   ▼
4. Background Pipeline (ThreadPoolExecutor)
   │
   ├─► scrape_funda()      ── Fetch HTML if URL provided
   ├─► fetch_external()    ── Additional data sources
   ├─► parse_html()        ── Parser extracts ~40 fields → PropertyCore
   ├─► compute_kpis()      ── Calculate derived metrics
   ├─► generate_chapters() ── Loop 0-12:
   │       │
   │       └─► BaseChapter.generate()
   │           │
   │           └─► IntelligenceEngine.generate_chapter_narrative()
   │               │
   │               ├─► Hardcoded fallback (if AI unavailable)
   │               │
   │               └─► AIProvider.generate() (if available)
   │                   │
   │                   └─► Ollama / OpenAI / Anthropic / Gemini
   │
   └─► render_pdf()        ── WeasyPrint PDF generation
   │
   ▼
5. Update Run (status='done', chapters_json, report_json)
   │
   ▼
6. GET /runs/{id}/status ──► Frontend polls every 2s
   │
   ▼
7. GET /runs/{id}/report ──► Frontend displays chapter content
```

### 3.2 Chapter Rendering Flow

```
ChapterRenderer.tsx
       │
       ├─► chapter.id === "0" ──► DashboardLayout
       ├─► chapter.id === "1" ──► MetricsLayout
       ├─► chapter.id === "2" ──► MatchLayout
       ├─► chapter.id === "3" ──► RiskLayout
       ├─► chapter.id === "4" ──► GaugeLayout
       ├─► chapter.id === "5" ──► MetricsLayout
       ├─► chapter.id === "6" ──► ComparisonLayout
       ├─► chapter.id === "7" ──► ComparisonLayout
       ├─► chapter.id === "8" ──► MetricsLayout
       ├─► chapter.id === "9" ──► RiskLayout
       ├─► chapter.id === "10" ──► FinancialLayout
       ├─► chapter.id === "11" ──► FinancialLayout
       └─► chapter.id === "12" ──► ConclusionLayout
```

---

## 4. AI Provider Architecture

### 4.1 Provider Interface

```python
class AIProvider(ABC):
    @abstractmethod
    async def generate(prompt, system, model, json_mode, options) -> str

    @abstractmethod
    def list_models() -> List[str]

    @abstractmethod
    def check_health() -> bool

    @property
    @abstractmethod
    def name() -> str
```

### 4.2 Provider Selection Flow

```
1. Load from settings (ai_provider = "ollama" | "openai" | "anthropic" | "gemini")
   │
   ▼
2. ProviderFactory.get_provider(settings)
   │
   ├─► Check API key availability
   ├─► Instantiate provider
   └─► Run health check
   │
   ▼
3. If health check fails and fallback_enabled:
   │
   └─► Try next provider in fallback chain
       (e.g., ollama → openai → hardcoded)
```

---

## 5. Configuration System

### 5.1 Configuration Sources (Priority Order)

1. **Environment Variables** (highest priority)
2. **SQLite `app_config` table** (runtime changes via Settings UI)
3. **`.env` file** (development defaults)
4. **`AppSettings` defaults** (hardcoded fallbacks)

### 5.2 Configuration Categories

| Category | Examples |
|----------|----------|
| AI | provider, model, timeout, API keys |
| Market | avg_price_m2, energy_scores |
| Parser | validation thresholds |
| Pipeline | max_workers, poll_interval |
| User | Marcel/Petra preferences |

---

## 6. Database Schema

### 6.1 Tables

```sql
-- Existing
CREATE TABLE runs (
    id TEXT PRIMARY KEY,
    funda_url TEXT,
    funda_html TEXT,
    status TEXT DEFAULT 'pending',
    steps_json TEXT,
    chapters_json TEXT,
    kpis_json TEXT,
    property_core_json TEXT,
    report_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE kv_store (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- New
CREATE TABLE app_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. Security Considerations

- API keys stored in environment variables, never in code
- SQLite database is local-only (no remote access)
- Image uploads validated for type and size (max 10MB)
- No user authentication (single-user local tool)

---

## 8. Performance Targets

| Metric | Target |
|--------|--------|
| Report generation | < 60 seconds |
| Status polling interval | 2 seconds |
| AI per-chapter timeout | 30 seconds |
| Frontend initial load | < 200ms |
| Image upload max size | 10MB |
