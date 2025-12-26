# Architectural Guardrails & Policy Contract

**Governance Level:** PHASE T3a  
**Status:** DEFINED (Not yet fully wired)  
**Authority:** Policy Architect

---

## 1. Policy Contract Statement

### The "Fail-Closed" Truth Guarantee

This system operates under a strict **Fail-Closed** architecture. This means that **no output is better than incorrect output.**

If any component of the system cannot guarantee the integrity, provenance, or structural correctness of its data, it **must** halt execution immediately. It is explicitly forbidden to:
*   Degrade gracefully by showing "unknown" data without explicit flags.
*   Fall back to templates when AI analysis fails.
*   Invent data to fill gaps in the UI.
*   Serve outputs that failed internal validation checks.
*   Perform calculations in the presentation layer.

**We guarantee that:**
1.  **Truth is Immutable:** Once data is enriched and registered, it never changes for the duration of the request.
2.  **Logic is Centralized:** All business logic lives in the Enrichment Layer (Python), never in the Presentation Layer (Jinja/React).
3.  **AI is Leashed:** AI generates narrative *interpretation* only, never factual *data*.
4.  **Structure is Enforced:** Every chapter complies with the Four-Plane standard, or it does not exist.

---

## 2. Guardrail Inventory

These guardrails define the non-negotiable rules of the system.

### Domain: Narrative Integrity
| ID | Name | Intent | Risk of Violation |
| :--- | :--- | :--- | :--- |
| **GR-NAR-001** | `fail_closed_narrative_generation` | Abort if AI cannot generate narrative. | Hallucinated or quality-compromised content; misleading users. |
| **GR-NAR-002** | `require_ai_provider` | Prevent execution without a configured AI brain. | Invalid/Empty analysis; unauthenticated API calls. |

### Domain: Registry & Data Truth
| ID | Name | Intent | Risk of Violation |
| :--- | :--- | :--- | :--- |
| **GR-REG-001** | `enforce_registry_immutability` | Lock data after enrichment phase. | "Magic" data appearing later; hallucinations mismatching facts. |
| **GR-REG-002** | `prevent_post_lock_registration` | Block new keys after lock. | Hidden data channels bypassing governance. |
| **GR-REG-003** | `fail_on_registry_conflict` | Fatal error on value redefinition. | Split-brain truth (e.g., showing two different prices). |

### Domain: Pipeline Integrity
| ID | Name | Intent | Risk of Violation |
| :--- | :--- | :--- | :--- |
| **GR-PIP-001** | `enforce_production_strictness` | Mandatory validation in PROD. | Serving broken/incomplete reports to paying users. |
| **GR-PIP-002** | `prevent_test_mode_leakage` | Isolate test outputs clearly. | Test/Mock data viewed by real users; cache poisoning. |

### Domain: Four-Plane Structure
| ID | Name | Intent | Risk of Violation |
| :--- | :--- | :--- | :--- |
| **GR-PLA-001** | `enforce_four_plane_structure` | Output must match schema. | Frontend crashes; UI degradation. |
| **GR-PLA-002** | `fail_on_missing_planes` | All 4 planes required. | Incomplete cognitive model presented as truth. |

### Domain: AI Authority
| ID | Name | Intent | Risk of Violation |
| :--- | :--- | :--- | :--- |
| **GR-AUT-001** | `enforce_authority_model_selection` | Models chosen centrally. | Shadow IT; cost explosions; using deprecated models. |

### Domain: Presentation
| ID | Name | Intent | Risk of Violation |
| :--- | :--- | :--- | :--- |
| **GR-PRE-001** | `prevent_presentation_math` | Logic in Enrichment only. | Hidden business logic; calculation errors in UI. |

---

## 3. Policy-to-System Mapping

This table proves that these policies are **already implicit** in the codebase. Phase T3b will make them explicitly referenced.

| Guardrail ID | Policy Name | Current Enforcement Location | Mechanism |
| :--- | :--- | :--- | :--- |
| **GR-NAR-001** | `fail_closed_narrative_generation` | `backend.domain.narrative_generator.NarrativeGenerator` | `try/except` -> Re-raise Exception (T2a) |
| **GR-NAR-002** | `require_ai_provider` | `backend.intelligence.intelligence.IntelligenceEngine` | `__init__` Check |
| **GR-REG-001** | `enforce_registry_immutability` | `backend.domain.registry.CanonicalRegistry` | `register()` raises `RegistryLocked` |
| **GR-REG-002** | `prevent_post_lock_registration` | `backend.domain.registry.CanonicalRegistry` | `register()` raises `RegistryLocked` |
| **GR-REG-003** | `fail_on_registry_conflict` | `backend.domain.registry.CanonicalRegistry` | `register()` raises `RegistryConflict` |
| **GR-PIP-001** | `enforce_production_strictness` | `backend.pipeline.spine.PipelineSpine` | `get_renderable_output(strict=True)` |
| **GR-PIP-002** | `prevent_test_mode_leakage` | `backend.pipeline.spine.mark_test_output` | Metadata Injection |
| **GR-PLA-001** | `enforce_four_plane_structure` | `backend.pipeline.four_plane_backbone` | `BackboneEnforcementError` |
| **GR-PLA-002** | `fail_on_missing_planes` | `backend.validation.gate.ValidationGate` | Validator Logic |
| **GR-AUT-001** | `enforce_authority_model_selection` | `backend.ai.ai_authority.AIAuthority` | `get_model_for_provider()` |
| **GR-PRE-001** | `prevent_presentation_math` | `backend.domain.registry_proxy.RegistryValue` | `__add__`, `__sub__`, etc. raise Exception |

---

## 4. Configuration & Override Policy

*   **Production Environment:** All policies are `STRICT`. No overrides allowed.
*   **Test Environment:** Policies may be temporarily lowered to `WARN` or `OFF` strictly for specific test cases (e.g., testing failure modes), but default to `STRICT`.
*   **Future (Governance UI):** Admin users may toggle `WARN` for specific non-critical guardrails during system degradation, but core Truth Guardrails (`GR-REG-*`) are permanently `STRICT`.
