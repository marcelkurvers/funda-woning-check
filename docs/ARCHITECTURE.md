# AI Woning Rapport - System Architecture

**Version**: 5.0 (Trust & Transparency Update)
**Last Updated**: 2025-12-22

---

## 1. System Overview

AI Woning Rapport is a full-stack real estate analysis platform that transforms Dutch Funda property listings into comprehensive, AI-enriched reports. Version 5.0 introduces the **AI Trust & Transparency Architecture**, ensuring every AI claim is backed by reasoning and provenance.

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   USER CONTEXT (Chrome/Edge)                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │             MULTI-CHECK PRO LINK EXTENSION            │  │
│  │  (Data Extraction ─► Media Scraping ─► Direct Ingest) │  │
│  └──────────────┬────────────────────────────────────────┘  │
└─────────────────┼───────────────────────────────────────────┘
                  │ HTTP/REST (POST /api/extension/ingest)
┌─────────────────▼───────────────────────────────────────────┐
│                      BACKEND (FastAPI/Python)               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                       API LAYER                         ││
│  │   /api/runs  /api/extension/ingest  /api/config        ││
│  └──────────────┬──────────────────────────────────────────┘│
│                 │                                           │
│  ┌──────────────▼──────────────┐   ┌──────────────────────┐ │
│  │    PIPELINE ORCHESTRATOR    ├───►  TRUST & PROVENANCE  │ │
│  │ (Sequencing & State Mgmt)   │   │ (Confidence & Proof) │ │
│  └──────────────┬──────────────┘   └──────────┬───────────┘ │
│                 │                             │             │
│  ┌──────────────▼──────────────┐   ┌──────────▼───────────┐ │
│  │      INTELLIGENCE ENGINE    ◄───┤    DYNAMIC EXTRACTOR │ │
│  │ (Narrative & Domain Vars)   │   │ (AI Discovery Layer) │ │
│  └──────────────┬──────────────┘   └──────────────────────┘ │
└─────────────────┼───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│    SQLITE    │    │   FRONTEND   │
│ (local_app.db)│    │   (React)    │
└──────────────┘    └──────────────┘
```

---

## 2. Ingestion Multi-Strategy

The system supports three primary ways to feed data into the intelligence pipeline:

### 2.1 Multi-Check Pro Extension (Primary)
- **Context**: Runs within the user's logged-in Funda session.
- **Data**: Extracts `__NEXT_DATA__` (JSON) and high-res image URLs via DOM-traversal.
- **Benefit**: Zero-CAPTCHA, zero-proxy requirements.

### 2.2 Manual Paste (Fallback)
- **Context**: User copies HTML/Text from a listing and pastes into the dashboard.
- **Data**: Raw multi-line text input.

### 2.3 Direct URL (Legacy/Dev)
- **Context**: Server-side scraping attempting to fetch the public URL.
- **Constraint**: Often blocked by CDNs/WAFs; primarily used for internal validation.

---

## 3. Trust & Transparency Pipeline

The architecture ensures that AI is an assistant, not a black box:

1.  **Domain Variable Authority**: Each chapter is mapped to a strict set of domain-specific variables (e.g., Chapter 6 TCO includes 6 variables like `onderhoudskosten`).
2.  **Fact vs. Inference Tracking**: The system labels every data point:
    - **FACT**: Extracted directly from Funda by the parser.
    - **INFERRED**: Derived by AI with documented "Proof of Reasoning."
    - **UNKNOWN**: Explicitly flagged missing data to prevent hallucinations.
3.  **AI Provenance**: Metadata (Provider, Model, Timestamp, Confidence Score) is attached to every enrichment step and persisted in the database.
4.  **Modern Magazine v2 Rendering**: The frontend uses this metadata to render trust headers and variable grids that show the "Logic" behind the report.

---

## 4. Single Page Application (SPA) Support

The backend is configured as a Hybrid API/SPA server:
- **API Prefix**: All programmatic endpoints are mounted on `/api/*`.
- **Catch-All**: The backend serves `index.html` for any non-API route.

---

## 5. Database Schema (Enhanced)

```sql
-- Updated with Provenance and Discovery
CREATE TABLE runs (
    id TEXT PRIMARY KEY,
    funda_url TEXT,
    property_core_json TEXT, -- Now stores source_stats (Fact/Inferred)
    chapters_json TEXT,      -- Stores provenance and variables grid
    status TEXT,
    created_at TEXT
);

CREATE TABLE attribute_discovery (
    id TEXT PRIMARY KEY,
    run_id TEXT,
    namespace TEXT, 
    key TEXT,
    value TEXT,
    confidence REAL,
    source_snippet TEXT
);
```

---
*Last Updated: 2025-12-22 | Version 5.0*
