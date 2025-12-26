# Guardrail Classification & Governance Matrix

**Governance Level:** PHASE T4a  
**Status:** RATIFIED  
**Authority:** Governance Architect  
**Date:** 2025-12-26  

---

## 1. Governance Rules Statement

1.  **Constitutional Invariants (The "Never" List):**  
    Rules classified as **NON-NEGOTIABLE** are the "Constitution" of the system. They guarantee data integrity, truthful provenance, and architectural stability. These rules must **never** be exposed to configuration, toggles, or runtime overrides. Disabling them is equivalent to system corruption.

2.  **Operational Flexibility (The "Sometimes" List):**  
    Rules classified as **CONDITIONALLY CONFIGURABLE** represent operational constraints (e.g., "AI must be available"). These may be relaxed **strictly** in non-production environments (Dev/Test) to facilitate debugging, structural testing, or offline development. They remain **STRICT** in Production.

3.  **Environment awareness:**  
    Rules classified as **ENVIRONMENT-BOUND** are inherently tied to the deployment context (e.g., "Is this Production?"). Their enforcement is automatic based on the environment detection, not user preference.

4.  **Configuration Scope:**  
    "Configurable" means *administratively* adjustable in restricted environments using authenticated tools. It does **not** mean user-facing settings. No end-user may ever disable a guardrail.

---

## 2. Guardrail Classification Matrix

| Guardrail ID | Name | Category | Allowed Scope | Rationale | Risk if Misused |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GR-NAR-001** | `fail_closed_narrative_generation` | **CONDITIONALLY CONFIGURABLE** | DEV_ONLY, TEST_ONLY | In local dev, seeing a partial report (without AI) is useful for layout debugging. | In Prod: Users receive incomplete reports thinking they are complete. |
| **GR-NAR-002** | `require_ai_provider` | **CONDITIONALLY CONFIGURABLE** | DEV_ONLY, TEST_ONLY | CI pipelines must verify backbone structure without needing live AI keys/costs. | In Prod: Execution starts but fails mid-way; security bypass possible. |
| **GR-REG-001** | `enforce_registry_immutability` | **NON-NEGOTIABLE** | **NEVER** | Data MUST stay consistent between enrichment and render. | Output hallucinates values that contradict the factual record. |
| **GR-REG-002** | `prevent_post_lock_registration` | **NON-NEGOTIABLE** | **NEVER** | Ensures all data passes through the enrichment gate. | "Hidden" data paths bypass validation and audit logs. |
| **GR-REG-003** | `fail_on_registry_conflict` | **NON-NEGOTIABLE** | **NEVER** | A fact cannot have two values simultaneously. | Split-brain truth; user mistrust; liability. |
| **GR-PIP-001** | `enforce_production_strictness` | **ENVIRONMENT-BOUND** | PROD (Strict), NON-PROD (Flexible) | Validates that Prod runs enforce all checks. | Production incidents allowed to propagate to users. |
| **GR-PIP-002** | `prevent_test_mode_leakage` | **NON-NEGOTIABLE** | **NEVER** (Always Active if Test Mode) | Test artifacts must NEVER look like real reports. | Cache poisoning; User confusing mock data for real valuation. |
| **GR-PLA-001** | `enforce_four_plane_structure` | **NON-NEGOTIABLE** | **NEVER** | This is the public contract of the system output. | Frontend rendering crashes; Broken data pipelining. |
| **GR-PLA-002** | `fail_on_missing_planes` | **NON-NEGOTIABLE** | **NEVER** | Partial cognitive models are invalid models. | Users make decisions based on missing context. |
| **GR-AUT-001** | `enforce_authority_model_selection` | **NON-NEGOTIABLE** | **NEVER** | Centralized control of AI costs and models. | Shadow IT; Cost explosions; Security leaks. |
| **GR-PRE-001** | `prevent_presentation_math` | **NON-NEGOTIABLE** | **NEVER** | Business logic must be auditable (Enrichment only). | Hidden logic errors; pricing mistakes in UI. |

---

## 3. Future Configuration Candidates (T4b Scope)

Only the following guardrails are eligible for exposure in any future configuration system (e.g., `dev_config.yml` or Admin UI):

1.  **Narrative Soft-Fail Mode (`GR-NAR-001` override)**
    *   **Toggle:** `allow_partial_generation`
    *   **Constraint:** Allowed ONLY if `ENV != PRODUCTION`.
    *   **Use Case:** Local UI development; "Dry run" testing.

2.  **Offline Mode (`GR-NAR-002` override)**
    *   **Toggle:** `offline_structural_mode`
    *   **Constraint:** Allowed ONLY if `ENV != PRODUCTION`.
    *   **Use Case:** CI/CD structure verification; Local development without internet/API keys.

**ALL OTHER GUARDRAILS ARE LOCKED.** 
Attempts to make them configurable will be rejected by Code Review and CI Policy Tests.
