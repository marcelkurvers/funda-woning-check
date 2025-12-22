# AI Woning Rapport - API Specification

**Version**: 5.0 (Trust & Transparency Update)
**Last Updated**: 2025-12-22
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

**Response Fields:**
| Field | Description |
|-------|-------------|
| `property_core`| Core extracted fields (Price, Area, etc.) |
| `chapters`     | AI chapters with `provenance` and `variables` grid |
| `discovery`    | List of AI-discovered namespaced attributes |
| `media_from_db`| Managed media items with provenance |

**Chapter Provenance Structure:**
```json
{
  "provenance": {
    "provider": "ollama",
    "model": "llama3",
    "timestamp": "2025-12-22T...",
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

---

## 2. Configuration & AI

### 2.1 Get Configuration
`GET /api/config`

### 2.2 List AI Providers
`GET /api/ai/providers`

### 2.3 Check AI Status
`GET /api/ai/status`

---

## 3. Image Upload (Local)
`POST /api/upload/image` (Multipart)

---

## 4. Single Page Application (SPA)
The backend includes a catch-all route that serves the React frontend for any non-API path.
Example: Navigating to `http://localhost:8000/runs/{id}/status` will serve the UI, which then internally calls `/api/runs/{id}/status`.
