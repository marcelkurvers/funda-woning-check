# Database Schema Verification

## Runs Table Schema
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | TEXT | NOT NULL | Primary key - UUID for run identification |
| funda_url | TEXT | NULL | URL of the Funda property listing |
| funda_html | TEXT | NULL | Raw HTML content from Funda or manual paste |
| status | TEXT | NULL | Run status: queued, running, done, error |
| steps_json | TEXT | NULL | JSON array tracking pipeline step progress |
| property_core_json | TEXT | NULL | All relevant raw fields from scraper |
| chapters_json | TEXT | NULL | Final generated chapter contents |
| kpis_json | TEXT | NULL | Computed KPIs |
| sources_json | TEXT | NULL | Info about used external sources |
| unknowns_json | TEXT | NULL | Missing data fields |
| artifacts_json | TEXT | NULL | References to PDF path, etc. |
| created_at | TEXT | NULL | Timestamp of run creation |
| updated_at | TEXT | NULL | Timestamp of last update |

## Column Check: Media URLs
- **media_urls**: MISSING (not a direct column)
  - **Storage Location**: Stored within `property_core_json` as a JSON field
  - **Evidence**: Line 354 shows `core_data = {"media_urls": inp.media_urls or [], ...}`
  - **Evidence**: Line 265 shows `core["media_urls"] = list(dict.fromkeys(initial_media + incoming_media))`

## Column Check: Parser Fields

- **asking_price_eur**: MISSING (not a direct column)
  - **Storage**: Within `property_core_json` JSON blob
  - **Evidence**: Lines 318, 324, 334 reference `core.get("asking_price_eur")`

- **living_area_m2**: MISSING (not a direct column)
  - **Storage**: Within `property_core_json` JSON blob
  - **Evidence**: Lines 318, 334 reference `core.get("living_area_m2")`

- **plot_area_m2**: MISSING (not a direct column)
  - **Storage**: Within `property_core_json` JSON blob
  - **Evidence**: Lines 318, 334 reference `core.get("plot_area_m2")`

- **build_year**: MISSING (not a direct column)
  - **Storage**: Within `property_core_json` JSON blob
  - **Evidence**: Lines 318, 334 reference `core.get("build_year")`

- **energy_label**: MISSING (not a direct column)
  - **Storage**: Within `property_core_json` JSON blob
  - **Evidence**: Lines 318, 330, 334 reference `core.get("energy_label")`

## Verdict
**SCHEMA_MISSING_COLUMNS**

## Missing Columns

All requested fields are **MISSING as dedicated database columns** but are **PRESENT as JSON fields** within the `property_core_json` TEXT column:

1. media_urls
2. asking_price_eur
3. living_area_m2
4. plot_area_m2
5. build_year
6. energy_label

## Schema Design Pattern

The database employs a **JSON document pattern**:
- Single column `property_core_json` (TEXT type) stores all property-specific data
- Fields are accessed via dictionary-style access: `core.get("field_name")`
- Provides schema flexibility but sacrifices:
  - SQL-level type enforcement
  - Efficient indexing/querying of individual fields
  - Column-level constraints

## Analysis

The current schema uses a **document-oriented design** within SQLite:
- **Pros**: Flexible schema, easy to add new fields, no migrations needed
- **Cons**: Cannot query/index individual fields efficiently, no type enforcement at DB level

The fields are accessed throughout the codebase using dictionary-style access on the parsed JSON object (e.g., `core.get("asking_price_eur")`), which confirms they are stored within the JSON blob rather than as separate columns.

## Database File Location
- **Path**: `/Users/marcelkurvers/Development/funda-app/data/local_app.db`
- **Configured via**: Environment variable `APP_DB` or default path
- **Initialization**: `init_db()` function at line 67 in `/Users/marcelkurvers/Development/funda-app/backend/main.py`
