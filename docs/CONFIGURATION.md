# AI Woning Rapport - Configuration Reference

**Version**: 2.0
**Last Updated**: 2025-12-20

This document lists all configurable values in the application, their defaults, and where they were previously hardcoded.

---

## 1. AI Configuration

| Setting | Type | Default | Env Var | Description |
|---------|------|---------|---------|-------------|
| `ai_provider` | string | `"ollama"` | `AI_PROVIDER` | Active AI provider: `ollama`, `openai`, `anthropic`, `gemini` |
| `ai_model` | string | `"llama3"` | `AI_MODEL` | Model to use for text generation |
| `ai_timeout` | int | `30` | `AI_TIMEOUT` | Request timeout in seconds |
| `ai_fallback_enabled` | bool | `true` | `AI_FALLBACK_ENABLED` | Fall back to hardcoded content if AI fails |

### API Keys

| Setting | Type | Default | Env Var | Description |
|---------|------|---------|---------|-------------|
| `ollama_base_url` | string | `null` | `OLLAMA_BASE_URL` | Ollama server URL (auto-detected if not set) |
| `openai_api_key` | string | `null` | `OPENAI_API_KEY` | OpenAI API key |
| `anthropic_api_key` | string | `null` | `ANTHROPIC_API_KEY` | Anthropic API key |
| `gemini_api_key` | string | `null` | `GEMINI_API_KEY` | Google Gemini API key |

**Previously hardcoded in:** `ollama_client.py:92` (timeout)

---

## 2. Market Configuration

| Setting | Type | Default | Previous Location | Description |
|---------|------|---------|-------------------|-------------|
| `market_avg_price_m2` | int | `5200` | `main.py:469` | Average price per m² in Dutch market |
| `energy_label_scores` | dict | See below | `main.py` | Score mapping for energy labels |

### Energy Label Scores (Default)

```json
{
  "A": 95,
  "B": 80,
  "C": 65,
  "D": 50,
  "E": 35,
  "F": 20,
  "G": 10
}
```

---

## 3. Fit Score Configuration

| Setting | Type | Default | Previous Location | Description |
|---------|------|---------|-------------------|-------------|
| `fit_score_base` | float | `0.50` | `main.py:445` | Base fit score |
| `fit_score_completeness_bonus` | float | `0.20` | `main.py:448` | Bonus for >80% data completeness |
| `fit_score_energy_bonus` | float | `0.15` | `main.py:450` | Bonus for A/B energy label |

---

## 4. Parser Validation Limits

| Setting | Type | Default | Previous Location | Description |
|---------|------|---------|-------------------|-------------|
| `max_bedrooms` | int | `15` | `parser.py` | Maximum valid bedroom count |
| `max_bathrooms` | int | `10` | `parser.py` | Maximum valid bathroom count |
| `max_total_rooms` | int | `30` | `parser.py` | Maximum valid room count |
| `min_living_area` | int | `10` | `parser.py` | Minimum valid living area (m²) |
| `max_living_area` | int | `2000` | `parser.py` | Maximum valid living area (m²) |
| `min_build_year` | int | `1500` | `parser.py` | Minimum valid build year |
| `max_build_year` | int | `2030` | `parser.py` | Maximum valid build year |

---

## 5. Pipeline Configuration

| Setting | Type | Default | Previous Location | Description |
|---------|------|---------|-------------------|-------------|
| `max_workers` | int | `2` | `main.py:180` | ThreadPoolExecutor max workers |
| `poll_interval_ms` | int | `2000` | `App.tsx:103` | Frontend status poll interval |
| `image_max_size_mb` | int | `10` | `main.py:270` | Maximum upload file size |

---

## 6. User Preferences

Stored in SQLite `kv_store` table under key `preferences`.

### Marcel Profile (Default)

```json
{
  "keywords": ["glasvezel", "zonnepanelen", "garage", "laadpaal", "1930"],
  "weights": {
    "tech": 0.4,
    "infrastructure": 0.3,
    "energy": 0.3
  },
  "hidden_priorities": ["bouwjaar", "dakisolatie"]
}
```

### Petra Profile (Default)

```json
{
  "keywords": ["karakteristiek", "sfeer", "tuin", "bad", "licht"],
  "weights": {
    "atmosphere": 0.4,
    "comfort": 0.3,
    "finish": 0.3
  },
  "hidden_priorities": ["afwerking", "badkamer"]
}
```

---

## 7. Database Configuration

| Setting | Type | Default | Env Var | Description |
|---------|------|---------|---------|-------------|
| `app_db` | string | `"data/local_app.db"` | `APP_DB` | SQLite database path |

**Special value:** Use `:memory:` for in-memory testing.

---

## 8. Chapter Titles

Currently kept in `main.py:68-82` as these are static display values.

```python
CHAPTER_TITLES = {
    "0": "Introductie & Samenvatting",
    "1": "Algemene Woningkenmerken",
    "2": "Matchanalyse Marcel & Petra",
    "3": "Bouwkundige Staat",
    "4": "Energie & Duurzaamheid",
    "5": "Indeling & Ruimtegebruik",
    "6": "Onderhoud & Afwerking",
    "7": "Tuin & Buitenruimte",
    "8": "Parkeren & Bereikbaarheid",
    "9": "Juridische Aspecten",
    "10": "Financiële Analyse",
    "11": "Marktpositie",
    "12": "Advies & Conclusie"
}
```

---

## 9. Environment Variables Summary

```bash
# Required for cloud providers (optional for local Ollama)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Optional overrides
AI_PROVIDER=ollama
AI_MODEL=llama3
AI_TIMEOUT=30
OLLAMA_BASE_URL=http://localhost:11434

# Database
APP_DB=data/local_app.db
```

---

## 10. Configuration Precedence

When a setting is requested, the system checks sources in this order:

1. **Environment variable** (highest priority)
2. **SQLite `kv_store` table** (runtime changes)
3. **`.env` file** (development defaults)
4. **`AppSettings` class default** (code fallback)

---

---

## 12. Configuration API

The application provides a comprehensive API for managing configuration at runtime. Changes made via the API are persisted to the SQLite `kv_store` table and are reloaded automatically.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/config` | Retrieve the full current configuration |
| `GET` | `/api/config/{section}` | Retrieve a specific section (e.g., `ai`, `market`) |
| `GET` | `/api/config/{section}/{key}` | Retrieve a specific value |
| `POST` | `/api/config` | Bulk update one or more sections |
| `PUT` | `/api/config/{section}/{key}` | Update a specific value |

### Persistence Mechanism

Configuration is persisted in the `kv_store` table using the following key format: `config.{section_name}`. The value is stored as a JSON-serialized dictionary of the section's settings.

**Example Database Entry:**
- **Key**: `config.ai`
- **Value**: `{"provider": "openai", "model": "gpt-4o", "timeout": 30, ...}`

### Refreshing Settings

After any update via the API, the application calls `reset_settings()`, which clears the in-memory singleton. Upon the next access, the settings are reloaded according to the precedence rules.
