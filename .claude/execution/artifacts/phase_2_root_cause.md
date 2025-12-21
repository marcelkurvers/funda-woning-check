# Root Cause Analysis

## Issue 1: Photos Not Appearing in Header

### Expected Behavior
The first photo from `media_urls` array should be displayed in the header thumbnail (line 254-261 in App.tsx).

### Actual Behavior
The photo does not appear, and the fallback Unsplash image is shown instead.

### Root Cause
**Frontend data structure mismatch - `property_core` is NOT stored in the `report` state object.**

**File**: `/Users/marcelkurvers/Development/funda-app/frontend/src/App.tsx`
**Line**: 92-96

The backend API response at `/runs/{run_id}/report` includes:
```json
{
  "runId": "...",
  "address": "...",
  "property_core": { "media_urls": [...], ... },  // ← THIS IS PROVIDED
  "chapters": { "0": { "property_core": {...} } }
}
```

However, `setReport` at line 92-96 ONLY stores:
```typescript
setReport({
  runId: run_id,
  address: data.property_core?.address || "Onbekend Adres",
  chapters: data.chapters || {}
  // ← property_core is NEVER stored!
});
```

At line 255, the photo access code tries:
```typescript
src={(report.chapters["0"] as any)?.property_core?.media_urls?.[0] ||
     (report as any).property_core?.media_urls?.[0] ||
     "fallback"}
```

Both paths fail because:
1. `report.chapters["0"].property_core` exists (backend injects it at main.py:313)
2. BUT `report.property_core` does NOT exist (frontend never stores it)
3. The TypeScript type definition (`ReportData` at types/index.ts:30-35) does not include `property_core` field

### Evidence

**Backend main.py:376-386** (GET /runs/{run_id}/report):
```python
return {
    "runId": row["id"],
    "address": json.loads(row["property_core_json"]).get("address", "Onbekend"),
    "property_core": json.loads(row["property_core_json"]),  # ← Provided
    "chapters": json.loads(row["chapters_json"]),
    "kpis": json.loads(row["kpis_json"])
}
```

**Backend main.py:313** (Chapter 0 includes property_core):
```python
chapters[chapter_id] = {
    "id": chapter_id,
    "title": title,
    "intro": output.get("intro"),
    "main_analysis": output.get("main_analysis"),
    "interpretation": output.get("interpretation"),
    "advice": output.get("advice", []),
    "strengths": output.get("strengths", []),
    "chapter_data": output,
    "property_core": output.get("property_core")  # ← Chapter 0 has this
}
```

**Backend intelligence.py:60-63** (Chapter 0 injection):
```python
if chapter_id == 0:
    result = IntelligenceEngine._narrative_ch0(data)
    # BRIDGE: Inject core data into Chapter 0 for the frontend dashboard header
    result["property_core"] = data  # ← Backend injects property_core with media_urls
```

**Frontend App.tsx:92-96** (Data loss):
```typescript
setReport({
  runId: run_id,
  address: data.property_core?.address || "Onbekend Adres",
  chapters: data.chapters || {}
  // ← data.property_core is discarded!
});
```

**Frontend types/index.ts:30-35** (Type definition):
```typescript
export interface ReportData {
    runId: string;
    address: string;
    chapters: Record<string, ChapterData>;
    consistency?: ConsistencyItem[];
    // ← No property_core field defined
}
```

**Frontend App.tsx:255** (Access attempt):
```typescript
src={(report.chapters["0"] as any)?.property_core?.media_urls?.[0] ||
     (report as any).property_core?.media_urls?.[0] ||
     "fallback"}
```
- First path: `report.chapters["0"].property_core.media_urls[0]` - Should work (backend provides it)
- Second path: `report.property_core.media_urls[0]` - Fails (frontend never stored it)

---

## Issue 2: Parsed Data Not Appearing in Header

### Expected Behavior
The header should display:
- Asking price (`asking_price_eur`)
- Living area (`living_area_m2`)
- Plot area (`plot_area_m2`)
- Other parsed fields from the Funda listing

### Actual Behavior
The header shows "€ N/B" and missing values, requiring fallback logic to parse AI-generated summary text.

### Root Cause
**Identical to Issue 1 - Frontend discards `property_core` containing all parsed fields.**

**File**: `/Users/marcelkurvers/Development/funda-app/frontend/src/App.tsx`
**Line**: 92-96

The same `setReport` call that discards `media_urls` also discards all parsed fields:
- `asking_price_eur`
- `living_area_m2`
- `plot_area_m2`
- `build_year`
- `energy_label`
- `rooms`
- `bedrooms`
- etc.

At line 289-298, the code attempts to access these fields:
```typescript
const core = (report.chapters["0"] as any)?.property_core ||
             (report as any).property_core || {};

let price = core.asking_price_eur;
if (!price || price === "€ N/B" || price === "€ TBD") {
  // Fallback: Parse from AI summary
  const m = summary.match(/€\s?([\d.,]+)/);
  if (m) price = `€ ${m[1]}`;
  else price = "€ N/B";
}
```

The first path (`report.chapters["0"].property_core`) should work because the backend includes it.
The second path (`report.property_core`) fails because the frontend never stored it.

### Evidence

**Backend main.py:270** (Parser data stored):
```python
# Store parsed data
core = parser_result.model_dump()
property_core_json = json.dumps(core, ensure_ascii=False)
```

**Backend main.py:383** (API response includes all parser fields):
```python
"property_core": json.loads(row["property_core_json"]),
```

**Frontend App.tsx:289** (Data access):
```typescript
const core = (report.chapters["0"] as any)?.property_core ||
             (report as any).property_core || {};
```
- The code tries both paths but relies on unsafe type casting `(report as any).property_core`
- This indicates the developer knew the type definition was wrong

**Frontend App.tsx:293-298** (Fallback logic):
```typescript
let price = core.asking_price_eur;
if (!price || price === "€ N/B" || price === "€ TBD") {
  const m = summary.match(/€\s?([\d.,]+)/);
  if (m) price = `€ ${m[1]}`;
  else price = "€ N/B";
}
```
- The code has extensive fallback logic to parse AI-generated text
- This wouldn't be needed if `property_core` was properly stored

---

## Additional Findings

### Finding 1: Type Definition is Incomplete

**File**: `/Users/marcelkurvers/Development/funda-app/frontend/src/types/index.ts`
**Line**: 30-35

The `ReportData` interface does not include `property_core`:
```typescript
export interface ReportData {
    runId: string;
    address: string;
    chapters: Record<string, ChapterData>;
    consistency?: ConsistencyItem[];
}
```

This should include:
```typescript
export interface ReportData {
    runId: string;
    address: string;
    property_core?: PropertyCore;  // ← Missing
    chapters: Record<string, ChapterData>;
    consistency?: ConsistencyItem[];
}
```

### Finding 2: Backend Already Provides TWO Paths

The backend is smart - it provides `property_core` in TWO locations:
1. **Top-level**: `data.property_core` (via main.py:383)
2. **Chapter 0**: `data.chapters["0"].property_core` (via main.py:313)

This redundancy was likely added as a "bridge" to support both access patterns. The frontend only needs to store ONE of these paths.

### Finding 3: Code Comments Confirm Intent

**Backend intelligence.py:62**:
```python
# BRIDGE: Inject core data into Chapter 0 for the frontend dashboard header
result["property_core"] = data
```

**Backend main.py:312**:
```python
"chapter_data": output, # Legacy/Bridge compatibility
```

The comments indicate this was a deliberate "bridge" to fix this exact issue. However, the frontend was never updated to consume it.

---

## Summary

**Root Cause**: The frontend receives `property_core` from the backend but discards it when storing the report state (App.tsx:92-96). This causes both photos and parsed data to be unavailable in the header.

**Scope**: Single-file fix in `/Users/marcelkurvers/Development/funda-app/frontend/src/App.tsx`

**Impact**: HIGH - Core feature (photos + parsed data) is completely broken

**Complexity**: LOW - Only need to add one line to `setReport` and update TypeScript type

**Backend Status**: WORKING CORRECTLY - No backend changes required
