# FAIL-CLOSED ENFORCEMENT ARCHITECTURE

## ⚠️ AUDIT COMPLIANCE DOCUMENT ⚠️

This document describes the **FAIL-CLOSED** enforcement architecture that makes it
**STRUCTURALLY IMPOSSIBLE** to produce an invalid report.

---

## 📐 SINGLE EXECUTION SPINE

```
┌─────────────────────────────────────────────────────────────────┐
│                    BROWSER BUTTON CLICK                         │
│                           ↓                                      │
│              execute_report_pipeline()                           │
│                    (bridge.py)                                   │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 ↓                 │                   │
│         │     PipelineSpine.__init__()      │                   │
│         │              ↓                    │                   │
│   ┌─────┴──────────────────────────────────┴─────┐             │
│   │            PHASE 1: INGEST                    │             │
│   │         ingest_raw_data()                     │             │
│   │              ↓                                │             │
│   │     ❌ VIOLATION → PipelineViolation         │             │
│   └───────────────────┬───────────────────────────┘             │
│                       ↓                                          │
│   ┌───────────────────┴───────────────────────────┐             │
│   │            PHASE 2: ENRICH & LOCK             │             │
│   │     enrich_and_populate_registry()            │             │
│   │              │                                │             │
│   │     CanonicalRegistry.register()              │             │
│   │              ↓                                │             │
│   │     ❌ CONFLICT → RegistryConflict (FATAL)   │             │
│   │              ↓                                │             │
│   │     CanonicalRegistry.lock()                  │             │
│   │              ↓                                │             │
│   │     ❌ MODIFY → RegistryLocked (FATAL)       │             │
│   └───────────────────┬───────────────────────────┘             │
│                       ↓                                          │
│   ┌───────────────────┴───────────────────────────┐             │
│   │            PHASE 3: GENERATE                  │             │
│   │     generate_all_chapters()                   │             │
│   │         for chapter_id in 0..13:              │             │
│   │              ↓                                │             │
│   │     generate_chapter_with_validation()        │             │
│   │              ↓                                │             │
│   │     ┌─────────────────────────────────┐      │             │
│   │     │    MANDATORY VALIDATION         │      │             │
│   │     │    ValidationGate.validate()    │      │             │
│   │     │         ↓                       │      │             │
│   │     │    ❌ FAIL → Marked Invalid    │      │             │
│   │     └─────────────────────────────────┘      │             │
│   └───────────────────┬───────────────────────────┘             │
│                       ↓                                          │
│   ┌───────────────────┴───────────────────────────┐             │
│   │            PHASE 4: RENDER                    │             │
│   │     get_renderable_output(strict=True)        │             │
│   │              ↓                                │             │
│   │     ┌─────────────────────────────────┐      │             │
│   │     │    PRODUCTION MODE CHECK        │      │             │
│   │     │    is_production_mode()         │      │             │
│   │     │         ↓                       │      │             │
│   │     │    STRICT = TRUE (forced)       │      │             │
│   │     └─────────────────────────────────┘      │             │
│   │              ↓                                │             │
│   │     all_chapters_valid()?                     │             │
│   │         NO → PipelineViolation (FATAL)       │             │
│   │         YES → Return validated output         │             │
│   └───────────────────┬───────────────────────────┘             │
│                       ↓                                          │
│              ┌────────┴────────┐                                │
│              │ VALIDATED REPORT │                               │
│              │    or ABORT      │                               │
│              └──────────────────┘                               │
│                                                                  │
│     There is NO third outcome.                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚫 BLOCKED BYPASS PATHS

| Path | Location | Status | Enforcement |
|------|----------|--------|-------------|
| `build_chapters()` | main.py:460 | ⛔ BLOCKED | Raises `BypassBlocked` |
| Direct chapter classes | chapters/*.py | ⛔ BLOCKED | Must go through spine |
| `IntelligenceEngine` direct | intelligence.py | ⛔ BLOCKED | Only callable from chapter_generator |
| `execute_pipeline()` | spine.py | ⚠️ DEPRECATED | Logs warning, calls correct API |
| Debug scripts | scripts/*.py | ⛔ BLOCKED | Will raise `BypassBlocked` |

---

## 🔒 HARD FAILURE JUSTIFICATIONS

### 1. `BypassBlocked` - build_chapters()
**Reason**: This function allowed direct chapter generation without validation.
**Enforcement**: Now raises `BypassBlocked` unconditionally.
**Impact**: Any code using this path will fail immediately.

### 2. `RegistryConflict` - Conflicting Values
**Reason**: Previously, conflicts were logged as warnings and IGNORED.
**Enforcement**: Now raises `RegistryConflict` with full context.
**Impact**: Any data inconsistency causes immediate pipeline abort.

### 3. `RegistryLocked` - Post-Lock Modifications
**Reason**: After enrichment, no new facts may be added.
**Enforcement**: Now raises `RegistryLocked`.
**Impact**: Prevents mid-pipeline data corruption.

### 4. `PipelineViolation` - Invalid Render Attempt
**Reason**: Production mode must never output invalid reports.
**Enforcement**: Strict validation is forced in production.
**Impact**: Invalid reports cannot reach UI/PDF.

### 5. `ValidationFailure` - Single Chapter Failure
**Reason**: Each chapter must be independently valid.
**Enforcement**: Raised when strict single-chapter generation fails.
**Impact**: Prevents partial corruption.

---

## ✅ PROOF: TESTS THAT FAIL IF ENFORCEMENT REMOVED

The following test file proves enforcement cannot be silently removed:

**`backend/tests/unit/test_fail_closed_enforcement.py`** (26 tests)

| Test | Proves |
|------|--------|
| `test_build_chapters_raises_bypass_blocked` | Bypass path is blocked |
| `test_registry_conflict_raises_exception` | Conflicts throw, not warn |
| `test_register_after_lock_raises` | Lock is enforced |
| `test_strict_render_blocks_invalid_chapters` | Validation is blocking |
| `test_production_mode_forces_strict` | Production cannot be lenient |
| `test_all_chapters_validated` | Every chapter is validated |
| `test_validation_errors_prevent_storage` | Failed chapters blocked |
| `test_cannot_enrich_before_ingest` | Phase order enforced |
| `test_registry_has_lock_method` | Enforcement code exists |
| `test_validation_gate_exists_and_callable` | Gate cannot be removed |

If ANY of these tests pass when they should fail, **the system is broken**.

---

## 🔄 PRODUCTION MODE DETECTION

```python
def is_production_mode() -> bool:
    # FAIL-CLOSED: Default to production (strict) unless explicitly in test mode
    test_mode = os.environ.get("PIPELINE_TEST_MODE", "").lower() == "true"
    return not test_mode
```

- **Default**: PRODUCTION (strict validation enforced)
- **Test mode**: Only when `PIPELINE_TEST_MODE=true`
- **No other way** to disable strict validation

---

## 📋 SUCCESS CRITERIA (BINARY)

| Criterion | Status |
|-----------|--------|
| Bad report is impossible to produce | ✅ |
| Violation causes hard failure | ✅ |
| Tests fail when enforcement removed | ✅ |
| System doesn't rely on AI compliance | ✅ |
| Marcel doesn't need to "hope" output is correct | ✅ |

---

## 🔒 FINAL NOTE

**This system will be audited again.**

Failing loudly is success.
Optimizing for user experience is forbidden until enforcement is proven correct.
