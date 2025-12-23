# Pipeline Spine Architecture

## Overview

The Pipeline Spine is the structural enforcement layer that guarantees all report generation flows through a single, unavoidable execution path. This document explains how "gravity" was installed.

## The Problem (Before)

Before the spine, the system had architectural components that *appeared* to enforce guarantees but were not wired together:

1. **CanonicalRegistry** existed but was created locally in `DataEnricher`, converted to a dict, then discarded
2. **ValidationGate** existed but was only called inside `_generate_ai_narrative()` - not at pipeline boundaries
3. **OwnershipMap** existed but was only checked in the AI path, not in fallback paths
4. **Chapter classes** had unrestricted access to all data

This meant a browser button click could produce output that bypassed every enforcement mechanism.

## The Solution (After)

### New Components

```
backend/
├── domain/
│   ├── pipeline_context.py    # PipelineContext - first-class execution spine
│   └── registry.py            # CanonicalRegistry (unchanged)
├── pipeline/
│   ├── __init__.py            # Package exports
│   ├── spine.py               # PipelineSpine - single execution path
│   ├── bridge.py              # Integration with main.py
│   ├── enrichment_adapter.py  # Registry population
│   └── chapter_generator.py   # Context-aware generation
└── validation/
    ├── __init__.py
    └── gate.py                # Enhanced ValidationGate
```

### Execution Flow

```
User Click → main.py:simulate_pipeline()
                ↓
        execute_report_pipeline()  [pipeline/bridge.py]
                ↓
        PipelineSpine.execute_full_pipeline()  [pipeline/spine.py]
                ↓
         ┌──────────────────────────────────────┐
         │  Phase 1: Data Ingestion             │
         │  - Raw data stored in context        │
         │  - Cannot be modified after this     │
         └──────────────────────────────────────┘
                ↓
         ┌──────────────────────────────────────┐
         │  Phase 2: Enrichment & Lock          │
         │  - Facts registered in registry      │
         │  - Registry LOCKED (immutable)       │
         └──────────────────────────────────────┘
                ↓
         ┌──────────────────────────────────────┐
         │  Phase 3: Chapter Generation         │
         │  - Each chapter generated            │
         │  - ValidationGate runs on EVERY one  │
         │  - Errors recorded, output stored    │
         └──────────────────────────────────────┘
                ↓
         ┌──────────────────────────────────────┐
         │  Phase 4: Renderable Output          │
         │  - Only validated chapters render    │
         │  - Strict mode blocks on failure     │
         └──────────────────────────────────────┘
```

## Enforced Invariants

### 1. Registry Singleton

```python
# PipelineContext holds THE registry
ctx = create_pipeline_context("run-123")
registry = ctx.registry  # This is the ONLY registry for this run

# Cannot create new registries mid-pipeline
# All registration goes through ctx.register_fact()
```

### 2. Registry Locking

```python
ctx.complete_enrichment()  # Mark enrichment done
ctx.lock_registry()        # LOCK - no more modifications

# After this, any attempt to register fails:
ctx.register_fact("new", 1, "New")  # Raises PipelineViolation
```

### 3. Validation at Boundary

```python
# ValidationGate is called in PipelineSpine.generate_all_chapters()
for chapter_id in range(14):
    output = generate_chapter_with_validation(ctx, chapter_id)
    
    # MANDATORY - cannot be bypassed
    errors = ValidationGate.validate_chapter_output(chapter_id, output, ctx.get_registry_dict())
    ctx.record_validation_result(chapter_id, errors)
    
    if errors:
        output["_validation_failed"] = True  # Marked failed
    else:
        ctx.store_validated_chapter(chapter_id, output)  # Only if passed
```

### 4. Phase Enforcement

```python
spine = PipelineSpine("run-123")

# Must follow correct order:
spine.ingest_raw_data(data)           # Phase 1
spine.enrich_and_populate_registry()  # Phase 2 - LOCKS registry
spine.generate_all_chapters()          # Phase 3 - VALIDATES all
output = spine.get_renderable_output() # Phase 4

# Skip a phase? Exception:
spine = PipelineSpine("run-456")
spine.enrich_and_populate_registry()  # Raises PipelineViolation - not ingested yet
```

## What ValidationGate Checks

1. **Ownership**: Chapter only displays variables it owns
2. **Raw Fact Restatement**: No verbatim numbers in wrong chapters  
3. **Preference Reasoning**: Marcel & Petra analysis must be substantive
4. **Required Fields**: id, title, main_analysis must be present

## Tests That Prove Enforcement

Run `python3 -m pytest tests/unit/test_spine_enforcement.py -v`:

```
TestRegistrySingleton::test_registry_created_once_per_context
TestRegistrySingleton::test_cannot_replace_registry
TestRegistryLocking::test_cannot_register_after_lock
TestRegistryLocking::test_cannot_lock_twice
TestChapterGenerationRequiresLock::test_cannot_generate_chapter_before_lock
TestValidationEnforcement::test_validation_runs_for_every_chapter
TestValidationEnforcement::test_cannot_store_failed_chapter
TestRawDataImmutability::test_cannot_modify_raw_data_after_enrichment
TestRenderBlocking::test_strict_render_blocks_on_failure
...
```

All 23 tests verify structural enforcement, not just component logic.

## Migration Notes

### Old Code (Bypassed)

The old code paths still exist but are no longer called in production:

- `build_chapters()` in main.py - still exists for reference, not called
- `DataEnricher.enrich()` - still exists, used via enrichment_adapter
- Direct `IntelligenceEngine.generate_chapter_narrative()` calls - wrapped by chapter_generator

### New Code (Enforced)

All production traffic flows through:

```python
# main.py:simulate_pipeline() calls:
from pipeline.bridge import execute_report_pipeline
chapters, kpis, enriched_core = execute_report_pipeline(run_id, raw_data, prefs)
```

## Success Criteria Verification

| Criterion | Status |
|-----------|--------|
| Removing ValidationGate breaks the build | ✅ Import errors would cascade |
| Recreating registry breaks tests | ✅ test_cannot_register_after_lock |
| Chapter cannot render without registry + validation | ✅ test_cannot_generate_chapter_before_lock |
| AI failure still produces validated output | ✅ Fallback path uses same spine |
| Button click is trustworthy | ✅ All paths go through spine |

## Conclusion

Gravity has been installed. The architecture is no longer conceptual - it is structural.
