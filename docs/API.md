# AI Woning Rapport - API Specification

**Version**: 5.1 (Bug Fixes & Documentation Update)
**Last Updated**: 2025-12-27
**Base URL**: `http://localhost:8000/api`

---

## 1. Run Management

### 1.1 Create Run
Creates a new analysis run.

```http
POST /api/runs
Content-Type: application/json

{
  "funda_url": "https://www.funda.nl/koop/amsterdam/...",
  "funda_html": null,
  "media_urls": [],
  "extra_facts": ""
}
```

### 1.2 Extension Ingest (User-Mediated)
Preferred route for browser extension ingestion. Directly triggers the full pipeline.

```http
POST /api/extension/ingest
Content-Type: application/json

{
  "url": "https://www.funda.nl/koop/...",
  "html": "<html>...</html>",
  "photos": [
    { "url": "...", "caption": "Living room", "order": 0 }
  ]
}
```

### 1.3 Start Processing
Triggers background pipeline processing for manually created runs.

```http
POST /api/runs/{run_id}/start
```

### 1.4 Update HTML (Paste Mode)
Allows manual submission of Funda HTML content for an existing run.

```http
POST /api/runs/{run_id}/paste
Content-Type: application/json

{
  "funda_html": "<html>...</html>"
}
```

### 1.5 Get Status
Polls current processing status and progress.

```http
GET /api/runs/{run_id}/status
```

**Response:**
```json
{
  "run_id": "uuid-string",
  "status": "processing",
  "steps": {
     "scrape_funda": "done",
     "dynamic_extraction": "running",
     "compute_kpis": "pending",
     "generate_chapters": "pending",
     "render_pdf": "pending"
  },
  "progress": {
    "current": 2,
    "total": 5,
    "percent": 40
  }
}
```

### 1.6 Get Report
Fetches completed report data, including dynamically discovered attributes and AI provenance.

```http
GET /api/runs/{run_id}/report
```

**Response Structure:**
```json
{
  "runId": "uuid-string",
  "address": "Street 123, Amsterdam",
  "property_core": {
    "asking_price_eur": 500000,
    "living_area_m2": 100,
    "plot_area_m2": 150,
    "build_year": 1995,
    "energy_label": "B",
    "rooms": 4,
    "bedrooms": 3
  },
  "chapters": {
    "0": { /* Dashboard */ },
    "1": { /* Chapter 1 */ },
    ...
    "12": { /* Chapter 12 */ }
  },
  "kpis": {
    "dashboard_cards": [
      {
        "id": "fit",
        "title": "Match Score",
        "value": "75%",
        "trend": "up",
        "desc": "Match Marcel & Petra"
      }
    ],
    "completeness": 0.85,
    "fit_score": 0.75,
    "validation_passed": true,
    "registry_entry_count": 42,
    "core_summary": { /* See below */ }
  },
  "discovery": [
    {
      "namespace": "property_features",
      "key": "balcony_size_m2",
      "value": "8",
      "confidence": 0.9,
      "source": "AI extraction"
    }
  ],
  "media_from_db": [
    {
      "url": "https://cloud.funda.nl/...",
      "caption": "Living room",
      "order": 0
    }
  ],
  "core_summary": {
    "completeness_score": 0.85,
    "field_count": 42,
    "missing_fields": ["energy_bill", "parking"],
    "validation_status": "passed"
  }
}
```

**Chapter Provenance Structure:**
Each chapter includes AI provenance metadata:
```json
{
  "provenance": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "timestamp": "2025-12-27T10:30:00Z",
    "confidence": "high",
    "inferred_variables": ["risk_factor"],
    "factual_variables": ["m2_price"]
  },
  "missing_critical_data": ["energy_bill"]
}
```

### 1.7 Download PDF
Generates and downloads PDF report with Trust Header.

```http
GET /api/runs/{run_id}/pdf
```

### 1.8 Get Active Run
Returns the most recent active run (for resuming analysis).

```http
GET /api/runs/active
```

**Response:**
```json
{
  "run_id": "uuid-string",
  "status": "running",
  "created_at": "2025-12-27T..."
}
```

---

## 2. Configuration & AI

### 2.1 Get Configuration
Returns full application configuration across all sections.

```http
GET /api/config
```

**Response:**
```json
{
  "ai": {
    "provider": "openai",
    "model": "gpt-4o-mini"
  },
  "market": {
    "avg_price_m2": 6000
  },
  "validation": {
    "max_bedrooms": 20
  },
  "pipeline": { ... },
  "database_url": "..."
}
```

### 2.2 Get Configuration Section
Returns a specific configuration section.

```http
GET /api/config/{section}
```

Example: `GET /api/config/ai` returns only AI configuration.

### 2.3 Get Configuration Value
Returns a specific key within a section.

```http
GET /api/config/{section}/{key}
```

Example: `GET /api/config/ai/provider` returns `{"provider": "openai"}`

### 2.4 Update Configuration
Updates configuration values (bulk update).

```http
POST /api/config
Content-Type: application/json

{
  "ai": {
    "provider": "openai",
    "model": "gpt-4o-mini"
  }
}
```

### 2.5 List AI Providers
Returns available AI providers and their capabilities.

```http
GET /api/ai/providers
```

**Response:**
```json
{
  "providers": ["openai", "anthropic", "google", "ollama"],
  "default": "openai"
}
```

### 2.6 Check AI Status (Legacy)
Legacy endpoint for basic AI provider status.

```http
GET /api/ai/status
```

### 2.7 AI Runtime Status (Unified)
Returns comprehensive AI provider runtime status including provider hierarchy, operational status, and available models.

```http
GET /api/ai/runtime-status
```

**Response:**
```json
{
  "active_provider": "openai",
  "active_model": "gpt-4o-mini",
  "provider_status": {
    "openai": {
      "status": "AVAILABLE",
      "category": "IMPLEMENTATION_VALID",
      "models": ["gpt-4o-mini", "gpt-4o"]
    },
    "anthropic": {
      "status": "NOT_CONFIGURED",
      "category": "IMPLEMENTATION_INVALID"
    }
  },
  "decision_record": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "reason": "Primary provider configured and operational"
  }
}
```

### 2.8 Invalidate AI Cache
Forces re-evaluation of AI provider status and configuration.

```http
POST /api/ai/invalidate-cache
```

---

## 3. Preferences

### 3.1 Get Preferences
Returns user preferences (Marcel & Petra profiles).

```http
GET /api/preferences
```

**Response:**
```json
{
  "ai_provider": "openai",
  "ai_model": "gpt-4o-mini",
  "preferences": {
    "marcel": { ... },
    "petra": { ... }
  }
}
```

### 3.2 Update Preferences
Updates user preferences and AI provider/model selection.

```http
POST /api/preferences
Content-Type: application/json

{
  "provider": "openai",
  "model": "gpt-4o-mini"
}
```

---

## 4. Governance & Policy

### 4.1 Get Governance Status
Returns current governance state, policies, and enforcement rules.

```http
GET /api/governance/status
```

**Response:**
```json
{
  "environment": "production",
  "effective_truth_policy": "fail_closed",
  "classification": "T4gE",
  "policies": {
    "fail_closed_narrative_generation": true,
    "strict_validation": true
  }
}
```

---

## 5. Image Upload (Local)
`POST /api/upload/image` (Multipart)

---

## 6. Single Page Application (SPA)
The backend includes a catch-all route that serves the React frontend for any non-API path.
Example: Navigating to `http://localhost:8000/runs/{id}/status` will serve the UI, which then internally calls `/api/runs/{id}/status`.
