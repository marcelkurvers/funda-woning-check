# AI Woning Rapport - API Specification

**Version**: 2.0
**Last Updated**: 2025-12-20
**Base URL**: `http://localhost:8001` (Docker) or `http://localhost:8000` (local)

---

## 1. Run Management

### 1.1 Create Run

Creates a new analysis run.

```http
POST /runs
Content-Type: application/json

{
  "funda_url": "https://www.funda.nl/koop/amsterdam/...",
  "funda_html": null,
  "media_urls": [],
  "extra_facts": ""
}
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `funda_url` | string | Yes | Funda URL or `"manual-paste"` |
| `funda_html` | string | No | Raw HTML content (for paste mode) |
| `media_urls` | string[] | No | Uploaded image URLs |
| `extra_facts` | string | No | Additional context |

**Response:**
```json
{
  "run_id": "uuid-string"
}
```

### 1.2 Start Processing

Triggers background pipeline processing.

```http
POST /runs/{run_id}/start
```

**Response:**
```json
{
  "status": "processing"
}
```

### 1.3 Get Status

Polls current processing status.

```http
GET /runs/{run_id}/status
```

**Response:**
```json
{
  "status": "pending" | "processing" | "done" | "failed",
  "progress": {
    "current_step": "generate_chapters",
    "percent": 65,
    "message": "Generating Chapter 8..."
  }
}
```

### 1.4 Get Report

Fetches completed report data.

```http
GET /runs/{run_id}/report
```

**Response:**
```json
{
  "property_core": {
    "address": "Herengracht 100, Amsterdam",
    "asking_price_eur": 495000,
    "living_area_m2": 85,
    "energy_label": "C",
    "build_year": 1920,
    "...": "..."
  },
  "chapters": {
    "0": {
      "id": "0",
      "title": "Executive Summary",
      "chapter_data": {
        "intro": "...",
        "interpretation": "...",
        "main_analysis": "...",
        "conclusion": "...",
        "metrics": [...],
        "sidebar_items": [...]
      }
    },
    "1": { "..." },
    "...": "..."
  },
  "kpis": {...},
  "consistency": {...}
}
```

### 1.5 Download PDF

Generates and downloads PDF report.

```http
GET /runs/{run_id}/pdf
```

**Response:** PDF file download

---

## 2. Configuration API

### 2.1 Get All Configuration

Returns the current application configuration.

```http
GET /api/config
```

**Response:**
```json
{
  "ai": {
    "provider": "ollama",
    "model": "llama3",
    "timeout": 30,
    "fallback_enabled": true,
    ...
  },
  "market": {
    "avg_price_m2": 5200,
    "energy_label_scores": {...}
  },
  "preferences": {...},
  "validation": {...},
  "pipeline": {...},
  "database_url": "data/local_app.db"
}
```

### 2.2 Bulk Update Configuration

Partially update one or more configuration sections. Changes are persisted to the database.

```http
POST /api/config
Content-Type: application/json

{
  "ai": {
    "provider": "openai",
    "model": "gpt-4"
  },
  "market": {
    "avg_price_m2": 5500
  }
}
```

**Response:**
```json
{
  "status": "updated",
  "sections": ["ai", "market"]
}
```

### 2.3 Get Configuration Section

```http
GET /api/config/{section}
```

**Example:** `GET /api/config/ai`

### 2.4 Get Specific Configuration Value

```http
GET /api/config/{section}/{key}
```

**Example:** `GET /api/config/ai/provider` -> `{"provider": "ollama"}`

### 2.5 Update Specific Configuration Value

```http
PUT /api/config/{section}/{key}
Content-Type: application/json

50
```

**Response:**
```json
{
  "status": "updated",
  "section": "ai",
  "key": "timeout",
  "new_value": 50
}
```

---

## 3. AI Provider API

### 3.1 List Available Providers

```http
GET /api/ai/providers
```

**Response:**
```json
{
  "providers": [
    {
      "name": "ollama",
      "display_name": "Ollama (Local)",
      "available": true,
      "requires_api_key": false
    },
    {
      "name": "openai",
      "display_name": "OpenAI",
      "available": true,
      "requires_api_key": true
    },
    {
      "name": "anthropic",
      "display_name": "Anthropic Claude",
      "available": false,
      "requires_api_key": true
    },
    {
      "name": "gemini",
      "display_name": "Google Gemini",
      "available": false,
      "requires_api_key": true
    }
  ]
}
```

### 3.2 List Models for Provider

```http
GET /api/ai/providers/{provider_name}/models
```

**Response:**
```json
{
  "provider": "ollama",
  "models": [
    {
      "id": "llama3",
      "name": "Llama 3",
      "context_length": 8192
    },
    {
      "id": "qwen2.5-coder:7b",
      "name": "Qwen 2.5 Coder 7B",
      "context_length": 32768
    }
  ]
}
```

### 3.3 Test Provider Connection

```http
POST /api/ai/providers/{provider_name}/test
Content-Type: application/json

{
  "api_key": "sk-..." // Optional, for cloud providers
}
```

**Response:**
```json
{
  "status": "success" | "failed",
  "message": "Connected successfully",
  "latency_ms": 234
}
```

---

## 4. Image Upload API

### 4.1 Upload Image

```http
POST /api/upload/image
Content-Type: multipart/form-data

file: <binary image data>
```

**Response:**
```json
{
  "url": "/uploads/abc123-uuid.jpg",
  "filename": "abc123-uuid.jpg",
  "size": 245678,
  "mime_type": "image/jpeg"
}
```

**Constraints:**
- Max file size: 10MB
- Allowed types: image/jpeg, image/png, image/webp, image/gif

---

## 5. Preferences API

### 5.1 Get Preferences

```http
GET /api/preferences
```

**Response:**
```json
{
  "marcel": {
    "keywords": ["glasvezel", "zonnepanelen", "garage"],
    "weights": {"tech": 0.4, "infrastructure": 0.3, "energy": 0.3}
  },
  "petra": {
    "keywords": ["karakteristiek", "sfeer", "tuin"],
    "weights": {"atmosphere": 0.4, "comfort": 0.3, "finish": 0.3}
  }
}
```

### 5.2 Update Preferences

```http
PUT /api/preferences
Content-Type: application/json

{
  "marcel": {
    "keywords": ["glasvezel", "zonnepanelen", "garage", "laadpaal"]
  }
}
```

---

## 6. Health & Status

### 6.1 Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "ai_provider": {
    "name": "ollama",
    "healthy": true
  },
  "database": {
    "healthy": true
  }
}
```

---

## 7. Error Responses

All endpoints return errors in this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid provider name",
    "details": {...}
  }
}
```

**Error Codes:**
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `PROVIDER_ERROR` | 502 | AI provider unavailable |
| `PROCESSING_ERROR` | 500 | Pipeline processing failed |
| `TIMEOUT` | 504 | AI generation timed out |
