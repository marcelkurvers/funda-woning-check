# Media URL Flow Verification

## Data Flow Trace

### 1. POST /runs (main.py:347-363) - receives media_urls: **YES**
- **Line 176**: `RunInput` model defines `media_urls: Optional[List[str]] = []`
- **Line 182**: `PasteIn` model defines `media_urls: Optional[List[str]] = []`
- **Line 348**: `create_run(inp: RunInput)` accepts the input
- **Line 354**: `media_urls` is extracted and stored in `core_data` dict: `"media_urls": inp.media_urls or []`

### 2. Database save (main.py:358-359) - stores media_urls: **YES**
- **Line 358-359**: Data is saved to database via `property_core_json` column:
  ```python
  cur.execute(
      "INSERT INTO runs (..., property_core_json, ...) VALUES (...)",
      (..., json.dumps(core_data), ...)
  )
  ```
- `core_data` contains `media_urls` from line 354
- **Database schema (line 78)**: `property_core_json TEXT` column exists in the runs table

### 3. GET /runs/{id}/report (main.py:376-386) - retrieves media_urls: **YES**
- **Line 378**: Row fetched from database: `row = get_run_row(run_id)`
- **Line 383**: `property_core` is extracted: `"property_core": json.loads(row["property_core_json"])`
- The `property_core_json` contains the full `core_data` including `media_urls`

### 4. Context construction (main.py:287-298) - passes to intelligence.py: **YES**
- **Line 238-239**: In `simulate_pipeline`, core data is loaded from database:
  ```python
  core = json.loads(row["property_core_json"])
  ```
- **Line 298**: Core (including `media_urls`) is passed to intelligence engine:
  ```python
  output = IntelligenceEngine.generate_chapter_narrative(i, core)
  ```

### 5. Intelligence consumption (intelligence.py:29-56) - uses media_urls: **YES**
- **Line 55**: `media_urls` is extracted from context and added to data dict:
  ```python
  "media_urls": ctx.get('media_urls', [])
  ```
- **Line 120**: Vision audit triggered when images present:
  ```python
  if chapter_id == 0 and data.get("media_urls") and IntelligenceEngine._provider:
  ```
- **Line 159**: Vision processing retrieves media_urls:
  ```python
  media_urls = property_data.get('media_urls', [])
  ```

### 6. Additional merge logic (main.py:258-265) - preserves media_urls: **YES**
- During HTML parsing in pipeline, there's smart merge logic:
  ```python
  incoming_media = p.get("media_urls", [])
  initial_media = core.get("media_urls", [])
  core["media_urls"] = list(dict.fromkeys(initial_media + incoming_media))
  ```
- This ensures user-uploaded media URLs are preserved and merged with parsed URLs

## Missing Links

**NONE DETECTED**

The data flow is complete and unbroken:
- ✅ Input model accepts `media_urls`
- ✅ Data is stored in database via `property_core_json`
- ✅ Data is retrieved from database in report endpoint
- ✅ Data is passed through pipeline to intelligence engine
- ✅ Intelligence engine consumes `media_urls` for vision audit (Chapter 0)
- ✅ Smart merge logic preserves user uploads during HTML parsing

## Additional Observations

### Positive findings:
1. **Consistent naming**: `media_urls` is used consistently throughout the codebase
2. **Defensive programming**: Uses `.get('media_urls', [])` with fallback to empty list
3. **Deduplication**: Uses `list(dict.fromkeys(...))` to remove duplicates while preserving order
4. **Vision integration**: Connected to multimodal vision audit feature in Chapter 0 (line 120-137)
5. **Test coverage**: Unit tests exist (`test_image_upload.py:175-202`) validating the flow

### Architecture notes:
- The `property_core_json` column serves as a flexible JSON store for all property data
- Media URLs are treated as first-class property data, not separate entities
- The flow supports both uploaded images (`/uploads/...`) and external URLs
- Vision audit processes up to 10 images with local path resolution (intelligence.py:181-192)

## Verdict

**FLOW_COMPLETE**

The `media_urls` parameter flows correctly through all stages:
1. API input (POST /runs)
2. Database persistence (property_core_json)
3. Data retrieval (GET /runs/{id}/report)
4. Pipeline processing (simulate_pipeline)
5. Intelligence consumption (generate_chapter_narrative)
6. Vision processing (process_visuals for Chapter 0)

No breaks or missing links detected in the data flow chain.
