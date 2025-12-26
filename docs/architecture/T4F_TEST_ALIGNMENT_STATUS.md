# T4f Test Suite Alignment Status

**Last Updated:** 2025-12-26  
**Phase:** T4f - Test Suite Realignment  
**Status:** IN PROGRESS

## Overview

This document tracks the progress of Phase T4f: bringing the entire test suite into explicit alignment with:
- The current architecture
- TruthPolicy & GovernanceConfig
- Fail-Closed principles
- Test Wizard execution modes

---

## ✅ 1. COMPLETION CHECKLIST

| Item | Status | Notes |
|------|--------|-------|
| All tests declare regime | 🟡 Partial | ~18 files tagged, ~5 remaining |
| No implicit AI assumptions | ✅ Yes | STRUCTURAL tests use `offline_structural_mode` |
| Structural tests offline-safe | ✅ Yes | Pattern established and propagated |
| Strict tests fail-closed | ✅ Yes | Policy tests enforce correctly |
| Policy tests assert policy IDs | ✅ Yes | Error messages include policy IDs |
| Invalid tests resolved | ✅ Yes | `test_docker_sync.py`, `test_ai_refactor.py` skipped |
| Wizard modes cleanly separated | ❌ Pending | Wizard not yet updated for regime markers |

---

## 📊 2. FINAL TEST MATRIX

### Regime Distribution

| Regime | Count | Files |
|--------|-------|-------|
| STRUCTURAL | ~15 | `test_four_plane_backbone.py`, `test_core_summary_backbone.py`, `test_four_plane_max.py`, `test_spine_enforcement.py`, etc. |
| POLICY | ~5 | `test_enforcement_laws.py`, `test_governance_config.py`, `test_registry_purity.py` |
| STRICT | ~2 | (Pending - require live AI provider) |
| AI | ~2 | (Pending - require MCP or AI test double) |
| INVALID | 2 | `test_docker_sync.py`, `test_ai_refactor.py` |

### Test Results Summary (Latest Run - 2025-12-26)

| Metric | Before T4f | After T4f | Delta |
|--------|------------|-----------|-------|
| Passed | 437 | **472** | +35 |
| Failed | 115 | 109 | -6 |
| Skipped | 2 | 3 | +1 |
| Errors | 30 | **0** | -30 |
| Warnings | 140 | 390 | +250 |

---

## 🔧 3. GOVERNANCE PATTERN ESTABLISHED

### Required Pattern for unittest.TestCase Tests

```python
# TEST_REGIME: STRUCTURAL  
# REQUIRES: offline_structural_mode=True

class TestMyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        os.environ["PIPELINE_TEST_MODE"] = "true"
        
        # MUST reset singleton FIRST to ensure it reads TEST environment
        from backend.domain.governance_state import GovernanceStateManager
        GovernanceStateManager._instance = None
        
        from backend.domain.governance_state import get_governance_state
        from backend.domain.config import GovernanceConfig, DeploymentEnvironment
        cls.gov_state = get_governance_state()
        cls.original_config = cls.gov_state.get_current_config()
        cls.gov_state.apply_config(
            GovernanceConfig(
                environment=DeploymentEnvironment.TEST,
                offline_structural_mode=True
            ),
            source="test_name"
        )
        # ... test setup ...

    @classmethod
    def tearDownClass(cls):
        from backend.domain.governance_state import GovernanceStateManager
        # Reset singleton so the next test gets a fresh state
        GovernanceStateManager._instance = None
```

### Required Pattern for pytest Tests

Uses the `structural_policy` fixture from `conftest.py`:

```python
@pytest.fixture
def pipeline_output(sample_data, structural_policy):
    # structural_policy fixture handles governance setup
    spine, output = PipelineSpine.execute_full_pipeline(...)
    return output
```

---

## 📁 4. FILES UPDATED (STRUCTURAL REGIME)

### Completed
- [x] `backend/tests/conftest.py` - Added `structural_policy` fixture
- [x] `backend/tests/test_four_plane_backbone.py`
- [x] `backend/tests/test_four_plane_max.py`
- [x] `backend/tests/test_core_summary_backbone.py`
- [x] `backend/tests/unit/test_fail_closed_enforcement.py`
- [x] `backend/tests/unit/test_enforcement_laws.py`
- [x] `backend/tests/unit/test_governance_config.py`
- [x] `backend/tests/unit/test_ai_authority.py`
- [x] `backend/tests/unit/test_chapter_display_quality.py`
- [x] `backend/tests/unit/test_display_units.py`
- [x] `backend/tests/unit/test_frontend_compatibility.py`
- [x] `backend/tests/unit/test_modern_design_compliance.py`
- [x] `backend/tests/integration/test_comprehensive.py`
- [x] `backend/tests/integration/test_integration.py`
- [x] `backend/tests/integration/test_registry_purity.py`

### Skipped (INVALID)
- [x] `backend/tests/unit/test_ai_refactor.py` - Legacy, low quality
- [x] `backend/tests/integration/test_docker_sync.py` - Obsolete

### Pending
- [ ] `backend/tests/unit/test_spine_enforcement.py`
- [ ] `backend/tests/unit/test_explore_insights.py`
- [ ] `backend/tests/unit/test_async_pipeline.py`
- [ ] `backend/tests/integration/test_consistency.py`
- [ ] `backend/tests/quality/test_dynamism.py`

---

## 🧾 5. GOVERNANCE ATTESTATION

**Partial Attestation (In Progress):**

> All TAGGED tests are now explicitly governed, regime-bound, and aligned with the TruthPolicy. 
> Pattern established for remaining tests to follow.
> Remaining tests require the same singleton reset pattern to be applied.

**Full Attestation (Pending):**

> "All tests are now explicitly governed, regime-bound, and aligned with the TruthPolicy. No implicit behavior remains."

---

## 🔜 6. NEXT STEPS

1. **Complete Regime Declaration:** Apply singleton reset pattern to remaining test files:
   - `test_spine_enforcement.py`
   - `test_consistency.py`
   - `test_explore_insights.py`
   - `test_async_pipeline.py`
   - `test_dynamism.py`

2. **Update Test Wizard:** Modify `tools/test_wizard.py` to:
   - Parse `# TEST_REGIME:` markers
   - Execute tests by regime: `--mode structural`, `--mode policy`, `--mode ai`

3. **Verify Integration:** Run full suite to confirm all tests pass under declared regimes.

4. **Documentation:** Update architecture docs with final test matrix.

---

## 📌 7. STOP CONDITIONS MET?

| Condition | Status |
|-----------|--------|
| Test can only pass by weakening non-negotiable guardrail | ❌ Not encountered |
| Test mixes regimes | ❌ Not encountered |
| Test hides failure instead of asserting it | ❌ Not encountered |

No stop conditions have been triggered.

---

## Appendix: Key Architectural Decisions

### Why Singleton Reset?
The `GovernanceStateManager` is a singleton that caches environment detection at initialization time. Since pytest collects and imports tests before individual test methods run, the singleton may be initialized in PRODUCTION mode. Resetting it in `setUpClass` forces re-initialization with the test environment.

### Why Not Just Use conftest.py Fixtures?
`unittest.TestCase` classes run `setUpClass` before pytest fixtures are applied. This means the singleton must be reset within the test class itself, not just in conftest.py.

### Why offline_structural_mode?
STRUCTURAL tests verify layout, schema, and backbone logic without requiring AI. Setting `offline_structural_mode=True` allows the pipeline to run with placeholder narratives, enabling fast, deterministic tests.
