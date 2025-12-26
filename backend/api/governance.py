from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.domain.governance_state import get_governance_state, GovernanceStateManager
from backend.domain.config import GovernanceConfig, DeploymentEnvironment
from backend.domain.guardrails import PolicyLevel

router = APIRouter(prefix="/api/governance", tags=["governance"])

# === Response Models ===

class ClassificationEntry(BaseModel):
    guardrail_id: str
    name: str
    category: str  # NON-NEGOTIABLE, etc.
    allowed_scope: str

class GovernanceStatus(BaseModel):
    environment: str
    effective_truth_policy: Dict[str, str]
    classification: List[ClassificationEntry]
    config_candidates: List[str]
    current_governance_config: Optional[Dict[str, Any]]
    last_audit: Optional[Dict[str, Any]]

# === Hardcoded Classification (from T4a) ===
# This should ideally come from the Classification Meta-Model if we had one in code,
# but for now we hardcode the "Constitution".
GOVERNANCE_CLASSIFICATION = [
    ClassificationEntry(guardrail_id="GR-NAR-001", name="fail_closed_narrative_generation", category="CONDITIONALLY CONFIGURABLE", allowed_scope="DEV_ONLY, TEST_ONLY"),
    ClassificationEntry(guardrail_id="GR-NAR-002", name="require_ai_provider", category="CONDITIONALLY CONFIGURABLE", allowed_scope="DEV_ONLY, TEST_ONLY"),
    ClassificationEntry(guardrail_id="GR-REG-001", name="enforce_registry_immutability", category="NON-NEGOTIABLE", allowed_scope="NEVER"),
    ClassificationEntry(guardrail_id="GR-REG-002", name="prevent_post_lock_registration", category="NON-NEGOTIABLE", allowed_scope="NEVER"),
    ClassificationEntry(guardrail_id="GR-REG-003", name="fail_on_registry_conflict", category="NON-NEGOTIABLE", allowed_scope="NEVER"),
    ClassificationEntry(guardrail_id="GR-PIP-001", name="enforce_production_strictness", category="ENVIRONMENT-BOUND", allowed_scope="PROD (Strict), NON-PROD (Flexible)"),
    ClassificationEntry(guardrail_id="GR-PIP-002", name="prevent_test_mode_leakage", category="NON-NEGOTIABLE", allowed_scope="NEVER"),
    ClassificationEntry(guardrail_id="GR-PLA-001", name="enforce_four_plane_structure", category="NON-NEGOTIABLE", allowed_scope="NEVER"),
    ClassificationEntry(guardrail_id="GR-PLA-002", name="fail_on_missing_planes", category="NON-NEGOTIABLE", allowed_scope="NEVER"),
    ClassificationEntry(guardrail_id="GR-AUT-001", name="enforce_authority_model_selection", category="NON-NEGOTIABLE", allowed_scope="NEVER"),
    ClassificationEntry(guardrail_id="GR-PRE-001", name="prevent_presentation_math", category="NON-NEGOTIABLE", allowed_scope="NEVER"),
]

WHITELISTED_CANDIDATES = [
    "allow_partial_generation",
    "offline_structural_mode"
]

@router.get("/status", response_model=GovernanceStatus)
def get_status():
    state = get_governance_state()
    
    current_config = state.get_current_config()
    current_config_dict = current_config.__dict__ if current_config else None
    if current_config_dict:
        # Convert Enum to string for JSON serialization
        current_config_dict['environment'] = current_config_dict['environment'].value
        
    audit_log = state.get_audit_log()
    last_audit = audit_log[-1] if audit_log else None
    
    return GovernanceStatus(
        environment=state.get_environment().value,
        effective_truth_policy=state.get_effective_policy().to_dict(),
        classification=GOVERNANCE_CLASSIFICATION,
        config_candidates=WHITELISTED_CANDIDATES,
        current_governance_config=current_config_dict,
        last_audit=last_audit
    )

class ApplyRequest(BaseModel):
    environment: str
    allow_partial_generation: bool = False
    offline_structural_mode: bool = False

@router.post("/apply", response_model=GovernanceStatus)
def apply_governance(req: ApplyRequest):
    state = get_governance_state()
    
    # 1. Map string env to Enum
    try:
        target_env = DeploymentEnvironment(req.environment)
    except ValueError:
        raise HTTPException(400, f"Invalid environment: {req.environment}")
    
    # 2. Build GovernanceConfig (this enforces T4a/T4b rules)
    try:
        config = GovernanceConfig(
            environment=target_env,
            allow_partial_generation=req.allow_partial_generation,
            offline_structural_mode=req.offline_structural_mode
        )
    except ValueError as e:
        raise HTTPException(400, f"Illegal Configuration: {str(e)}")
        
    # 3. Apply to State Manager (this enforces Production Protection)
    try:
        state.apply_config(config, source="api")
    except ValueError as e:
        raise HTTPException(403, str(e))
        
    return get_status()

@router.post("/reset", response_model=GovernanceStatus)
def reset_governance():
    state = get_governance_state()
    try:
        state.reset(source="api")
    except ValueError as e:
        raise HTTPException(403, str(e))
        
    return get_status()
