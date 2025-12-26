# CoreSummary Backbone Contract

## Architectural Law

**CoreSummary is the MANDATORY backbone of every report.**

This is not a feature. This is a **contractcorrectie** - a structural enforcement of what was always conceptually intended but never technically enforced.

---

## The Problem (Before)

In de oude implementatie:

- ❌ Kerngegevens bestonden wel (parsing/registry)
- ❌ Maar waren **geen verplicht top-level contractobject**
- ❌ UI scrapete data uit chapters/content
- ❌ Dashboard toonde `—` zonder verklaring
- ❌ AI-failure betekende lege dashboard

**Dit was architectonisch onacceptabel.**

---

## The Solution (Now)

### CoreSummary is:

1. **Verplicht** - Elk rapport MOET CoreSummary bevatten
2. **AI-onafhankelijk** - Gebouwd uit CanonicalRegistry, NOOIT uit AI/chapters
3. **Top-level** - Eerste-klas object in elk API response
4. **Fail-closed** - Ontbrekende data = expliciet `unknown`, nooit stil falen
5. **Single source of truth** - Dashboard leest ALLEEN uit CoreSummary

---

## What CoreSummary Contains

### Required Fields (always present):
- **asking_price** - Vraagprijs (formatted: "€ 500.000")
- **living_area** - Woonoppervlak (formatted: "120 m²")
- **location** - Locatie (human-readable summary)
- **match_score** - Match score (formatted: "75%")

### Optional Fields (if available):
- **property_type** - Woningtype
- **build_year** - Bouwjaar
- **energy_label** - Energielabel
- **plot_area** - Perceeloppervlak
- **bedrooms** - Aantal slaapkamers

### Metadata:
- **completeness_score** - Fractie van beschikbare velden (0.0-1.0)
- **registry_entry_count** - Aantal entries in registry
- **provenance** - Herkomst per veld (registry key mapping)

---

## Field Structure

Elk veld heeft:

```typescript
{
    value: string,           // Human-readable formatted value
    raw_value?: any,         // Raw value for programmatic use
    status: DataStatus,      // 'present' | 'unknown' | 'n/a'
    source: string,          // Registry key (provenance)
    unit?: string            // Display unit (e.g., "m²", "€")
}
```

---

## Pipeline Flow

```
1. Parser extracts raw data
         ↓
2. Enrichment populates CanonicalRegistry
         ↓
3. Registry is LOCKED
         ↓
4. ✨ CoreSummary is BUILT (from registry ONLY)
         ↓
5. AI/Chapter generation begins
         ↓
6. API returns report WITH CoreSummary
```

**CoreSummary is built BEFORE any AI work.**

---

## API Contract

### Response Structure:

```json
{
    "runId": "...",
    "address": "...",
    "chapters": { ... },
    "kpis": { ... },
    "core_summary": {
        "asking_price": {
            "value": "€ 500.000",
            "raw_value": "500000",
            "status": "present",
            "source": "asking_price_eur",
            "unit": "€"
        },
        "living_area": {
            "value": "120 m²",
            "raw_value": "120",
            "status": "present",
            "source": "living_area_m2",
            "unit": "m²"
        },
        "location": {
            "value": "Amsterdam",
            "status": "present",
            "source": "address"
        },
        "match_score": {
            "value": "75%",
            "raw_value": "75",
            "status": "present",
            "source": "total_match_score"
        },
        "completeness_score": 1.0,
        "registry_entry_count": 42,
        "provenance": {
            "asking_price": "asking_price_eur",
            "living_area": "living_area_m2",
            "location": "address",
            "match_score": "total_match_score"
        }
    }
}
```

### Enforcement:

- ✅ `core_summary` is **MANDATORY** in every response
- ✅ Missing CoreSummary → API returns error
- ✅ Frontend validates CoreSummary presence
- ✅ Dashboard reads **ONLY** from CoreSummary

---

## Frontend Usage

### Before (WRONG):
```typescript
// ❌ Scraping from chapters
const price = content?.variables?.asking_price?.value || '—';
```

### After (CORRECT):
```typescript
// ✅ Reading from CoreSummary
const price = report.core_summary.asking_price.value;
const status = report.core_summary.asking_price.status;

// Show status-aware UI
{status === 'unknown' && <span>Niet beschikbaar</span>}
```

---

## Invariants (NON-NEGOTIABLE)

1. **CoreSummary is ALWAYS present** after registry lock
2. **CoreSummary is built from CanonicalRegistry ONLY** (never AI/chapters)
3. **CoreSummary is constructed BEFORE AI/chapter generation**
4. **If CoreSummary is missing → report is INVALID**
5. **Dashboard KPIs come EXCLUSIVELY from CoreSummary**

---

## Tests

All invariants are enforced by tests in:
- `backend/tests/test_core_summary_backbone.py`

Tests verify:
- ✅ CoreSummary always built after registry lock
- ✅ CoreSummary fails before registry lock
- ✅ CoreSummary built from registry only
- ✅ Missing data handled gracefully (status=unknown)
- ✅ Completeness calculated correctly
- ✅ Provenance tracked
- ✅ Serialization works
- ✅ Pipeline output contains CoreSummary

---

## Absolute Verboden

❌ **Kerngegevens uit hoofdstukken halen**  
❌ **Kerngegevens uit AI halen**  
❌ **Kerngegevens impliciet laten bestaan**  
❌ **UI laten gokken waar data zit**  
❌ **"Dit was altijd al zo bedoeld" zonder afdwinging**

---

## Success Criteria

De implementatie is correct als:

✅ Het dashboard **altijd** kerngegevens toont  
✅ Ook als AI traag, uit, of fout is  
✅ Ook als chapters falen  
✅ Ook als planes leeg zijn  
✅ Je **nooit meer `—` ziet zonder verklaring**

---

## Implementation Files

### Backend:
- `backend/domain/core_summary.py` - CoreSummary domain model
- `backend/domain/pipeline_context.py` - CoreSummary storage in context
- `backend/pipeline/spine.py` - CoreSummary in output
- `backend/pipeline/bridge.py` - CoreSummary return value
- `backend/main.py` - CoreSummary in API response

### Frontend:
- `frontend/src/types/index.ts` - CoreSummary TypeScript types
- `frontend/src/App.tsx` - CoreSummary validation
- `frontend/src/components/OrientationChapter.tsx` - CoreSummary usage

### Tests:
- `backend/tests/test_core_summary_backbone.py` - Contract enforcement tests

---

## Migration Notes

### For Legacy Reports:

If a report was generated before CoreSummary was enforced:
- API builds fallback CoreSummary from `property_core`
- Fallback uses `CoreSummaryBuilder.build_from_dict()`
- Warning logged: "CoreSummary missing - legacy report"

### For New Reports:

- CoreSummary is ALWAYS built during pipeline execution
- Stored in `kpis_json` as `core_summary` field
- Returned as top-level field in API response

---

## Technical Guarantees

This is **not marketingtaal**. This is a **technical guarantee**:

> **CoreSummary is verplicht en vormt de stabiele basis van elk rapport.  
> Chapters en AI-analyse zijn verdieping, nooit fundament.**

---

**Dit is geen feature. Dit is een contractcorrectie.**

**Geïmplementeerd hard, expliciet en onmiskenbaar.**
