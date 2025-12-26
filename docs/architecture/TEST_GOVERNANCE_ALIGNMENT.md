# Test Governance Alignment Matrix

This document tracks the classification and governance status of all tests in the suite.
It ensures that the test suite itself is aligned with the `TruthPolicy` and `GovernanceConfig` system.

## Classification Legend

| Category | Name | Definition | Requirement |
|---|---|---|---|
| **A** | **GOVERNANCE-ENFORCING** | Directly asserts guardrail rules, policy levels, or API restrictions. | Must cite guardrail IDs. Must assert defaults. |
| **B** | **POLICY-DEPENDENT** | Relies on the system working (which implies Strict Policy). | Must pass under Strict Policy. Must fail if policy violated. |
| **C** | **GOVERNANCE-AGNOSTIC** | Unit tests for logic independent of policy. | Must not mutate governance. |
| **D** | **LEGACY / QUARANTINED** | Deprecated or incompatible. | Must be refactored or excluded. |

## Test Inventory & Status

### 1. Root Tests (`backend/tests/`)

| File | Category | Purpose | Status | Notes |
|---|---|---|---|---|
| `test_ai_preference_matching.py` | **B** | Match logic | ⏳ Pending Audit | |
| `test_capability_manager.py` | **B** | AI Capability | ⏳ Pending Audit | |
| `test_core_summary_backbone.py` | **B** | Core Summary | ⏳ Pending Audit | |
| `test_dynamic_editorial.py` | **B** | Editorial logic | ⏳ Pending Audit | |
| `test_explicit_config_ux.py` | **A** | Config UX | ⏳ Pending Audit | |
| `test_four_plane_backbone.py` | **B** | 4-Plane structure | ✅ Verified | Enforces correct structure |
| `test_four_plane_max.py` | **B** | Content max | ⏳ Pending Audit | |
| `test_four_plane_model.py` | **C** | Data models | ⏳ Pending Audit | |
| `test_page1_maximalization.py` | **B** | Page 1 | ⏳ Pending Audit | |
| `test_plane_a2_infographic.py` | **B** | Visuals | ⏳ Pending Audit | |
| `test_verify_consistency.py` | **B** | Consistency | ⏳ Pending Audit | |
| `test_worldclass_editorial.py` | **B** | Editorial | ⏳ Pending Audit | |

### 2. Unit Tests (`backend/tests/unit/`)

| File | Category | Purpose | Status | Notes |
|---|---|---|---|---|
| `test_ai_authority.py` | **B** | AI keys/models | ⏳ Pending Audit | |
| `test_ai_contracts.py` | **A** | LLM outputs | ⏳ Pending Audit | |
| `test_ai_interpretation.py` | **B** | Logic | ⏳ Pending Audit | |
| `test_ai_refactor.py` | **D** | Refactor check | ⏳ Pending Audit | Likely legacy |
| `test_ai_routing.py` | **B** | Routing | ⏳ Pending Audit | |
| `test_ai_schema.py` | **C** | Schema | ⏳ Pending Audit | |
| `test_api_endpoints.py` | **B** | API | ⏳ Pending Audit | |
| `test_async_pipeline.py` | **B** | Pipeline | ⏳ Pending Audit | |
| `test_chapter_display_quality.py` | **C** | Display | ⏳ Pending Audit | |
| `test_complex_parsing.py` | **C** | Parsing | ⏳ Pending Audit | |
| `test_config_api.py` | **A** | Config | ⏳ Pending Audit | |
| `test_display_units.py` | **C** | Formatting | ⏳ Pending Audit | |
| `test_domain_models.py` | **C** | Models | ⏳ Pending Audit | |
| `test_enforcement_laws.py` | **A** | Guardrails | ✅ Verified | Updated to check NarrativeGenerator |
| `test_explore_insights.py` | **C** | Logic | ⏳ Pending Audit | |
| `test_fail_closed_enforcement.py` | **A** | Fail-Closed | ✅ Verified | Refactored to use Gov Fixtures |
| `test_frontend_compatibility.py` | **C** | Schema | ⏳ Pending Audit | |
| `test_governance_api.py` | **A** | Gov API | ✅ Verified | T4c work |
| `test_governance_config.py` | **A** | Gov Config | ✅ Verified | T4b work |
| `test_image_upload.py` | **C** | Uploads | ⏳ Pending Audit | |
| `test_intelligence.py` | **B** | Intel Engine | ✅ Verified | Uses Offline Mode |
| `test_modern_design_compliance.py` | **C** | CSS/Design | ⏳ Pending Audit | |
| `test_narrative_enforcement.py` | **A** | Narrative | ⏳ Pending Audit | |
| `test_narrative_quality.py` | **B** | Quality | ⏳ Pending Audit | |
| `test_ollama_integration.py` | **B** | AI | ⏳ Pending Audit | |
| `test_parser.py` | **C** | Parsing | ⏳ Pending Audit | |
| `test_parser_edge_cases*.py` | **C** | Parsing | ⏳ Pending Audit | |
| `test_preferences_compliance.py` | **B** | Preferences | ⏳ Pending Audit | |
| `test_preferenties_vergelijking.py` | **B** | Logic | ⏳ Pending Audit | |
| `test_provider_factory.py` | **B** | AI providers | ⏳ Pending Audit | |
| `test_providers.py` | **B** | AI providers | ⏳ Pending Audit | |
| `test_spine_enforcement.py` | **A** | Spine | ⏳ Pending Audit | |
| `test_system_architecture.py` | **A** | Arch | ⏳ Pending Audit | |
| `test_utils.py` | **C** | Utils | ⏳ Pending Audit | |
| `test_variable_strategy.py` | **C** | Logic | ⏳ Pending Audit | |

### 3. Integration Tests (`backend/tests/integration/`)

| File | Category | Purpose | Status | Notes |
|---|---|---|---|---|
| `test_comprehensive.py` | **B** | Full flow | ⏳ Pending Audit | |
| `test_consistency.py` | **B** | Data | ⏳ Pending Audit | |
| `test_docker_sync.py` | **D** | Docker | ⏳ Pending Audit | Sync check? |
| `test_integration.py` | **B** | Flow | ⏳ Pending Audit | |
| `test_integration_fixtures.py` | **C** | Fixtures | ⏳ Pending Audit | |
| `test_registry_purity.py` | **A** | Registry | ⏳ Pending Audit | |

### 4. E2E Tests (`backend/tests/e2e/`)

| File | Category | Purpose | Status | Notes |
|---|---|---|---|---|
| `test_frontend.py` | **B** | Frontend | ⏳ Pending Audit | |
| `test_invariant_enforcement.py` | **A** | Invariants | ⏳ Pending Audit | |
| `test_pdf_export.py` | **B** | PDF | ⏳ Pending Audit | |
| `test_strict_narrative.py` | **A** | Narrative | ⏳ Pending Audit | |

### 5. Quality Tests (`backend/tests/quality/`)

| File | Category | Purpose | Status | Notes |
|---|---|---|---|---|
| `test_audit_codebase.py` | **D** | Audit | ⏳ Pending Audit | |
| `test_dynamism.py` | **B** | Logic | ⏳ Pending Audit | |
| `test_real_data_architecture.py` | **B** | Data | ⏳ Pending Audit | |
| `test_system_invariants.py` | **A** | Invariants | ⏳ Pending Audit | |

