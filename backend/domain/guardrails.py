"""
Guardrail Policy Model - The Single Source of Architectural Law

This module defines the explicit policy model for the system.
It separates the definition of rules (Policy) from their enforcement (Code).

Phase T3a: Definition Only.
This model is not yet connected to the runtime enforcement points.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any

class PolicyLevel(Enum):
    """
    Defines the enforcement level for a specific guardrail.
    """
    STRICT = "STRICT"    # Violation results in immediate hard failure (Exception)
    WARN = "WARN"        # Violation is allowed but logged/flagged
    OFF = "OFF"          # Guardrail is disabled (Legacy/Debug/Migration only)

@dataclass
class TruthPolicy:
    """
    The Single Source of Truth for System Invariants.
    
    This policy object defines behavior. Code enforces it.
    Changing a value here changes the system's "rule of law".
    
    Defaults match the current PROVEN production behavior.
    """
    
    # === NARRATIVE GUARDRAILS ===
    
    fail_closed_narrative_generation: PolicyLevel = PolicyLevel.STRICT
    """
    If AI fails or is unavailable, the pipeline must abort.
    Fallbacks to templates or static text are FORBIDDEN.
    Risk: Hallucinated or low-quality content masking system failure.
    """
    
    require_ai_provider: PolicyLevel = PolicyLevel.STRICT
    """
    The IntelligenceEngine must have a valid provider configured to start.
    Risk: Silent failure or unauthed execution.
    """
    
    # === REGISTRY & DATA GUARDRAILS ===
    
    enforce_registry_immutability: PolicyLevel = PolicyLevel.STRICT
    """
    Once the Registry is locked (post-enrichment), no modifications are allowed.
    Risk: Data tampering during narrative generation (hallucination).
    """
    
    prevent_post_lock_registration: PolicyLevel = PolicyLevel.STRICT
    """
    No new keys can be added to the registry after locking.
    Risk: Hidden data channels bypassing validation.
    """
    
    fail_on_registry_conflict: PolicyLevel = PolicyLevel.STRICT
    """
    Attempting to register a key that already exists with a different value is FATAL.
    Risk: Split-brain truth (two different prices for the same house).
    """
    
    # === PIPELINE INTEGRITY GUARDRAILS ===
    
    enforce_production_strictness: PolicyLevel = PolicyLevel.STRICT
    """
    In Production Mode, all validations must be STRICT.
    Risk: Serving invalid/broken reports to users.
    """
    
    prevent_test_mode_leakage: PolicyLevel = PolicyLevel.STRICT
    """
    Outputs generated in Test Mode must be strictly isolated/marked.
    Risk: Test data leaking into production storage/cache.
    """
    
    # === FOUR-PLANE STRUCTURE GUARDRAILS ===
    
    enforce_four_plane_structure: PolicyLevel = PolicyLevel.STRICT
    """
    All Chapter outputs must strictly adhere to the Four-Plane Schema.
    Risk: Frontend rendering crashes or degraded UX.
    """
    
    fail_on_missing_planes: PolicyLevel = PolicyLevel.STRICT
    """
    A Chapter output is INVALID if any Plane (A, B, C, D) is missing.
    Risk: Incomplete analysis presented as complete.
    """
    
    # === AI AUTHORITY GUARDRAILS ===
    
    enforce_authority_model_selection: PolicyLevel = PolicyLevel.STRICT
    """
    Providers MUST use the Model defined by the AI Authority.
    Direct model string injection is FORBIDDEN.
    Risk: Uncontrolled costs, deprecated model usage, untracked performance.
    """

    # === PRESENTATION GUARDRAILS ===
    
    prevent_presentation_math: PolicyLevel = PolicyLevel.STRICT
    """
    Presentation components (UI, Templates) cannot perform arithmetic.
    Logic must exist in Enrichment layer only.
    Risk: Hidden business logic, "off-by-one" pricing errors in UI.
    """

    def to_dict(self) -> Dict[str, str]:
        """Serialize policy state for logging/auditing."""
        return {k: v.value for k, v in self.__dict__.items() if isinstance(v, PolicyLevel)}

# Singleton Instance representing the current Law of the Land
# In future phases, this can be loaded from config/env
CURRENT_POLICY = TruthPolicy()
