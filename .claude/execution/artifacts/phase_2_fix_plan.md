# Fix Plan

## Fix 1: Store property_core in Report State

**File**: `/Users/marcelkurvers/Development/funda-app/frontend/src/App.tsx`
**Line**: 92-96
**Change Type**: Modify

**Current Code**:
```typescript
setReport({
  runId: run_id,
  address: data.property_core?.address || "Onbekend Adres",
  chapters: data.chapters || {}
});
```

**Proposed Code**:
```typescript
setReport({
  runId: run_id,
  address: data.property_core?.address || "Onbekend Adres",
  property_core: data.property_core,
  chapters: data.chapters || {}
});
```

**Reason**: This fix stores the `property_core` object (containing `media_urls` and all parsed fields) in the report state, making it available to the header component. The backend already provides this data in the API response at `/runs/{run_id}/report` (main.py:383), so this is simply consuming data that is already available.

---

## Fix 2: Update TypeScript Type Definition

**File**: `/Users/marcelkurvers/Development/funda-app/frontend/src/types/index.ts`
**Line**: 30-35
**Change Type**: Modify

**Current Code**:
```typescript
export interface ReportData {
    runId: string;
    address: string;
    chapters: Record<string, ChapterData>;
    consistency?: ConsistencyItem[];
}
```

**Proposed Code**:
```typescript
export interface PropertyCore {
    address?: string;
    asking_price_eur?: string;
    living_area_m2?: string;
    plot_area_m2?: string;
    build_year?: string;
    energy_label?: string;
    rooms?: string;
    bedrooms?: string;
    media_urls?: string[];
    [key: string]: any; // Allow additional fields from parser
}

export interface ReportData {
    runId: string;
    address: string;
    property_core?: PropertyCore;
    chapters: Record<string, ChapterData>;
    consistency?: ConsistencyItem[];
}
```

**Reason**: This fix adds the `property_core` field to the `ReportData` interface, matching the actual API response structure. It also defines a `PropertyCore` interface to provide type safety for the fields that are accessed in the header component (App.tsx:289-320). The optional `?` modifier ensures backward compatibility if the field is missing.

---

## Fix 3: Remove Unsafe Type Casting

**File**: `/Users/marcelkurvers/Development/funda-app/frontend/src/App.tsx`
**Line**: 255
**Change Type**: Modify

**Current Code**:
```typescript
src={(report.chapters["0"] as any)?.property_core?.media_urls?.[0] ||
     (report as any).property_core?.media_urls?.[0] ||
     "https://images.unsplash.com/photo-1600596542815-27b88e360290?q=80&w=2000&auto=format&fit=crop"}
```

**Proposed Code**:
```typescript
src={report.property_core?.media_urls?.[0] ||
     report.chapters["0"]?.property_core?.media_urls?.[0] ||
     "https://images.unsplash.com/photo-1600596542815-27b88e360290?q=80&w=2000&auto=format&fit=crop"}
```

**Reason**: After Fix 1, `report.property_core` will be available and type-safe (no `as any` needed). This fix reorders the fallback chain to prefer the top-level `property_core` (which is cleaner) before falling back to `chapters["0"].property_core`. Both paths will work, but the top-level path is more direct.

---

## Fix 4: Remove Unsafe Type Casting in Parsed Data Access

**File**: `/Users/marcelkurvers/Development/funda-app/frontend/src/App.tsx`
**Line**: 289
**Change Type**: Modify

**Current Code**:
```typescript
const core = (report.chapters["0"] as any)?.property_core || (report as any).property_core || {};
```

**Proposed Code**:
```typescript
const core = report.property_core || report.chapters["0"]?.property_core || {};
```

**Reason**: After Fix 1 and Fix 2, `report.property_core` will be type-safe and available. This removes the unsafe `as any` casts and reorders the fallback chain to prefer the top-level `property_core`. The fallback logic for parsing AI summary text (lines 294-298) will still work if the fields are missing, but now the proper data will be available first.

---

## Safety Assessment

**SAFE_TO_APPLY**

**Reason**:
1. **Additive changes only**: Fix 1 adds a field to the state object without removing anything
2. **Type-safe**: Fix 2 properly types the new field, preventing runtime errors
3. **Backward compatible**: All changes use optional chaining (`?.`) and fallbacks
4. **No breaking changes**: Existing code paths remain functional
5. **Backend unchanged**: No backend modifications required (backend already provides the data)
6. **Tested pattern**: The backend already injects `property_core` into `chapters["0"]` (main.py:313), so the fallback path is proven to work

**Risk Level**: LOW

**Validation Method**:
1. **Manual test**:
   - Submit a Funda URL (e.g., https://www.funda.nl/koop/amsterdam/huis-12345/)
   - Wait for analysis to complete
   - Verify header shows:
     - First photo from the listing (not Unsplash fallback)
     - Correct asking price (not "€ N/B")
     - Correct living area (not "N/B m²")
     - Correct plot area (not "N/B m²")

2. **Console verification**:
   - Open browser DevTools
   - After analysis completes, run: `console.log(JSON.stringify(report, null, 2))`
   - Verify `property_core` field is present with `media_urls` array and parsed fields

3. **Network verification**:
   - Open browser DevTools > Network tab
   - Submit analysis and wait for completion
   - Find GET request to `/runs/{run_id}/report`
   - Verify response includes `property_core` with `media_urls` and parsed fields
   - Verify frontend state matches the response

4. **TypeScript compilation**:
   - Run: `cd frontend && npm run build`
   - Verify no TypeScript errors
   - Verify build completes successfully

---

## Alternative Approach (Not Recommended)

An alternative would be to ONLY use `chapters["0"].property_core` and not store the top-level `property_core`. This would work because the backend already injects it (main.py:313).

**Why not recommended**:
1. The backend provides BOTH paths intentionally (see "BRIDGE" comment in intelligence.py:62)
2. The top-level path is cleaner and more semantic (photos/data are property attributes, not chapter attributes)
3. Future chapters might not have `property_core`, making the top-level path more reliable
4. The current code already tries to access `report.property_core` (lines 255, 289), indicating developer intent

---

## Implementation Order

1. **Apply Fix 2 first** (types/index.ts) - Defines the interface
2. **Apply Fix 1 second** (App.tsx setReport) - Stores the data
3. **Apply Fix 3 & 4 last** (App.tsx access) - Removes unsafe casts
4. **Run validation tests** - Verify fixes work

**Estimated time**: 5 minutes
**Testing time**: 10 minutes
**Total time**: 15 minutes

---

## Rollback Plan

If fixes cause issues:
1. **Revert Fix 1**: Remove `property_core: data.property_core` line
2. **Revert Fix 2**: Remove `PropertyCore` interface and `property_core?` field
3. **Revert Fix 3 & 4**: Restore `as any` casts

The application will return to current state (photos/data missing but no errors).

---

## Post-Fix Cleanup (Optional)

After verifying fixes work, consider:
1. **Simplify fallback logic** (App.tsx:294-298) - Most cases won't need AI summary parsing
2. **Add error logging** - Log when fallbacks are used (indicates parser issues)
3. **Update tests** - Add tests for `property_core` access patterns

These are enhancements, not critical fixes.
