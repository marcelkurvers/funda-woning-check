from enum import Enum
from dataclasses import dataclass, field
from backend.domain.guardrails import TruthPolicy, PolicyLevel

class DeploymentEnvironment(Enum):
    PRODUCTION = "PRODUCTION"
    DEVELOPMENT = "DEVELOPMENT"
    TEST = "TEST"
    
@dataclass
class GovernanceConfig:
    """
    Validated Configuration Model for System Guardrails.
    
    This is the ONLY authorized way to modify the TruthPolicy.
    It enforces:
    1. Production Invariants (No overrides in Prod)
    2. Non-Negotiable Rules (Cannot be overridden anywhere)
    3. Conditionally Configurable Rules (Overrides must map securely)
    """
    
    environment: DeploymentEnvironment
    
    # === ALLOWED CONFIGURATION TOGGLES ===
    # These map ONLY to the "Conditionally Configurable" guardrails
    # identified in GUARDRAIL_CLASSIFICATION.md
    
    allow_partial_generation: bool = False
    """
    If True, sets fail_closed_narrative_generation = OFF/WARN.
    Allows testing UI layouts without full AI generation.
    """
    
    offline_structural_mode: bool = False
    """
    If True, sets require_ai_provider = OFF.
    Allows CI pipelines to verify backbone structure without API keys.
    """
    
    def __post_init__(self):
        """Validate configuration constraints immediately involved in construction."""
        if self.environment == DeploymentEnvironment.PRODUCTION:
            if self.allow_partial_generation:
                raise ValueError("ILLEGAL CONFIGURATION: allow_partial_generation MUST be False in PRODUCTION.")
            if self.offline_structural_mode:
                raise ValueError("ILLEGAL CONFIGURATION: offline_structural_mode MUST be False in PRODUCTION.")

    def to_truth_policy(self) -> TruthPolicy:
        """
        Derive the authoritative TruthPolicy from this validated config.
        """
        # Start with default STRICT policy
        policy = TruthPolicy()
        
        # 1. Apply Environment-Bound Rules
        if self.environment == DeploymentEnvironment.PRODUCTION:
            policy.enforce_production_strictness = PolicyLevel.STRICT
        else:
            # In Non-Prod, we allow relaxed strictness if needed (though TruthPolicy defaults to STRICT)
            # The classification said: PROD (Strict), NON-PROD (Flexible).
            # For now, let's keep it STRICT by default unless we add a flag, 
            # OR we can relax it to WARN for dev convenience if needed.
            # However, the classification matrix said "Flexible", but didn't explicitly demand a toggle.
            # Best practice: Default strict, relax only via explicit intent.
            # For now, we leave it STRICT unless we add a `strict_pipeline_checks` toggle.
            pass

        # 2. Apply Conditional Overrides
        if self.allow_partial_generation:
            # Only allowed in Non-Prod (enforced by __post_init__)
            policy.fail_closed_narrative_generation = PolicyLevel.OFF
            
        if self.offline_structural_mode:
            # Only allowed in Non-Prod (enforced by __post_init__)
            policy.require_ai_provider = PolicyLevel.OFF
            
        return policy
