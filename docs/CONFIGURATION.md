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
2. **SQLite `app_config` table** (runtime changes)
3. **`.env` file** (development defaults)
4. **`AppSettings` class default** (code fallback)

---

## 11. Migrating from Hardcoded Values

To migrate existing hardcoded values:

1. Identify the value in the codebase
2. Add to `AppSettings` class in `backend/config/settings.py`
3. Replace hardcoded usage with `settings.value_name`
4. Add to Settings UI if user-configurable
5. Update this documentation

**Example migration:**

```python
# Before (hardcoded)
market_avg = 5200

# After (configurable)
from config.settings import get_settings
settings = get_settings()
market_avg = settings.market_avg_price_m2
```
