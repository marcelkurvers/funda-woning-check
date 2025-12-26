# TEST_REGIME: POLICY
# REQUIRES: none (tests guardrail enforcement itself)
import pytest
from backend.domain.config import GovernanceConfig, DeploymentEnvironment
from backend.domain.guardrails import PolicyLevel, TruthPolicy

class TestGovernanceConfig:
    """
    Validates that GovernanceConfig correctly enforces:
    1. Production Invariants
    2. Non-Negotiable Rules (by omission)
    3. Conditional Overrides
    """
    
    def test_production_defaults_are_strict(self):
        """Production environment should yield a fully STRICT policy by default."""
        config = GovernanceConfig(environment=DeploymentEnvironment.PRODUCTION)
        policy = config.to_truth_policy()
        
        # Check Critical Invariants
        assert policy.enforce_registry_immutability == PolicyLevel.STRICT
        assert policy.fail_closed_narrative_generation == PolicyLevel.STRICT
        assert policy.require_ai_provider == PolicyLevel.STRICT
        assert policy.enforce_production_strictness == PolicyLevel.STRICT

    def test_production_rejects_partial_generation(self):
        """Production MUST NOT allow allow_partial_generation."""
        with pytest.raises(ValueError, match="ILLEGAL CONFIGURATION"):
            GovernanceConfig(
                environment=DeploymentEnvironment.PRODUCTION,
                allow_partial_generation=True
            )

    def test_production_rejects_offline_mode(self):
        """Production MUST NOT allow offline_structural_mode."""
        with pytest.raises(ValueError, match="ILLEGAL CONFIGURATION"):
            GovernanceConfig(
                environment=DeploymentEnvironment.PRODUCTION,
                offline_structural_mode=True
            )

    def test_dev_can_enable_partial_generation(self):
        """Development environment CAN enable partial generation."""
        config = GovernanceConfig(
            environment=DeploymentEnvironment.DEVELOPMENT,
            allow_partial_generation=True
        )
        policy = config.to_truth_policy()
        
        # Should be OFF/WARN
        assert policy.fail_closed_narrative_generation == PolicyLevel.OFF
        
        # But other invariants must remain STRICT
        assert policy.enforce_registry_immutability == PolicyLevel.STRICT
        assert policy.prevent_post_lock_registration == PolicyLevel.STRICT

    def test_test_can_enable_offline_mode(self):
        """Test environment CAN enable offline mode."""
        config = GovernanceConfig(
            environment=DeploymentEnvironment.TEST,
            offline_structural_mode=True
        )
        policy = config.to_truth_policy()
        
        # Should be OFF
        assert policy.require_ai_provider == PolicyLevel.OFF
        
        # Ideally, this config implies we might not have a provider, 
        # so check if require_ai_provider is indeed OFF. 
        # (It is mapped in the to_truth_policy method)
        
    def test_non_negotiable_rules_are_unchangeable(self):
        """
        Verify that even in DEV with all flags on, 
        Non-Negotiable rules remain STRICT.
        """
        config = GovernanceConfig(
            environment=DeploymentEnvironment.DEVELOPMENT,
            allow_partial_generation=True,
            offline_structural_mode=True
        )
        policy = config.to_truth_policy()
        
        # Overrides applied
        assert policy.fail_closed_narrative_generation == PolicyLevel.OFF
        assert policy.require_ai_provider == PolicyLevel.OFF
        
        # INVARIANTS MUST HOLD
        assert policy.enforce_registry_immutability == PolicyLevel.STRICT
        assert policy.prevent_post_lock_registration == PolicyLevel.STRICT
        assert policy.fail_on_registry_conflict == PolicyLevel.STRICT
        assert policy.enforce_four_plane_structure == PolicyLevel.STRICT
        assert policy.fail_on_missing_planes == PolicyLevel.STRICT
        assert policy.enforce_authority_model_selection == PolicyLevel.STRICT
        assert policy.prevent_presentation_math == PolicyLevel.STRICT
        assert policy.prevent_test_mode_leakage == PolicyLevel.STRICT
