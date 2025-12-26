import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.domain.config import GovernanceConfig, DeploymentEnvironment
from backend.domain.guardrails import TruthPolicy, CURRENT_POLICY

logger = logging.getLogger(__name__)

class GovernanceStateManager:
    """
    Manages the runtime lifecycle of GovernanceConfig.
    
    Responsibilities:
    1. Detects current DeploymentEnvironment
    2. Stores the currently applied GovernanceConfig (if any)
    3. Derives the Effective TruthPolicy
    4. Audits all changes
    """
    
    _instance = None
    
    def __init__(self):
        self._current_config: Optional[GovernanceConfig] = None
        self._audit_log: List[Dict[str, Any]] = []
        
        # Initial audit entry
        self._audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "environment": self.get_environment().value,
            "action": "INIT",
            "details": "GovernanceStateManager initialized"
        })

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GovernanceStateManager()
        return cls._instance

    def get_environment(self) -> DeploymentEnvironment:
        """
        Detects the current environment.
        
        Logic matches PipelineSpine.is_production_mode():
        - Default is PRODUCTION (Safe/Fail-Closed)
        - PIPELINE_TEST_MODE="true" -> TEST
        - PIPELINE_DEV_MODE="true" -> DEVELOPMENT (Future proofing, treating as Test for now)
        """
        # Specific overrides
        if os.environ.get("PIPELINE_DEV_MODE", "false").lower() == "true":
            return DeploymentEnvironment.DEVELOPMENT
            
        if os.environ.get("PIPELINE_TEST_MODE", "false").lower() == "true":
            return DeploymentEnvironment.TEST
            
        return DeploymentEnvironment.PRODUCTION

    def get_effective_policy(self) -> TruthPolicy:
        """
        Returns the policy that should be enforced RIGHT NOW.
        
        If a config is applied, it builds the policy from it.
        Otherwise, it returns the default strict TruthPolicy.
        """
        if self._current_config:
            return self._current_config.to_truth_policy()
        
        # Default fallback: Strict TruthPolicy
        # We ensure environment awareness even without a config object
        # (Though TruthPolicy defaults are already strict)
        return TruthPolicy()

    def get_current_config(self) -> Optional[GovernanceConfig]:
        return self._current_config

    def apply_config(self, config: GovernanceConfig, source: str = "api") -> TruthPolicy:
        """
        Applies a new governance configuration.
        
        STRICTLY FORBIDDEN IN PRODUCTION.
        """
        current_env = self.get_environment()
        
        # 1. Environment Guard (Redundant with config validation but critical)
        if current_env == DeploymentEnvironment.PRODUCTION:
            self._log_audit("ATTEMPT_JURISDICTION_VIOLATION", f"Attempted to apply config in PRODUCTION from {source}")
            raise ValueError("Governance Configuration is IMMUTABLE in PRODUCTION.")
            
        # 2. Config-Environment Mismatch Guard
        if config.environment != current_env:
            raise ValueError(f"Config environment ({config.environment}) does not match runtime environment ({current_env})")

        # 3. Apply
        self._current_config = config
        
        # 4. Audit
        self._log_audit("APPLY_CONFIG", f"Applied new config from {source}", config.__dict__)
        
        logger.warning(f"Governance Policy OVERRIDDEN by {source}. Env: {current_env}. Config: {config}")
        
        return self.get_effective_policy()

    def reset(self, source: str = "api") -> TruthPolicy:
        """
        Resets to default strict policy.
        """
        current_env = self.get_environment()
        
        if current_env == DeploymentEnvironment.PRODUCTION:
             self._log_audit("ATTEMPT_JURISDICTION_VIOLATION", f"Attempted reset in PRODUCTION from {source}")
             raise ValueError("Governance Configuration is IMMUTABLE in PRODUCTION.")

        self._current_config = None
        self._log_audit("RESET_CONFIG", f"Reset to default strict policy from {source}")
        
        return self.get_effective_policy()

    def get_audit_log(self) -> List[Dict[str, Any]]:
        return self._audit_log

    def _log_audit(self, action: str, details: str, payload: Optional[Dict] = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "environment": self.get_environment().value,
            "action": action,
            "details": details,
            "payload": str(payload) if payload else None
        }
        self._audit_log.append(entry)
        # Keep log size manageable in memory
        if len(self._audit_log) > 1000:
            self._audit_log.pop(0)

# Global Accessor
def get_governance_state() -> GovernanceStateManager:
    return GovernanceStateManager.get_instance()
