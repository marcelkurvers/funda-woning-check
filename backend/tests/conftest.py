import os
import pytest

# MUST SET TEST MODE BEFORE ANY GOVERNANCE IMPORTS
os.environ["PIPELINE_TEST_MODE"] = "true"

from backend.domain.config import GovernanceConfig
from backend.domain.governance_state import get_governance_state, GovernanceStateManager


@pytest.fixture(scope="session", autouse=True)
def reset_governance_singleton():
    """
    Session-level fixture to reset the governance singleton.
    This ensures tests run in TEST environment, not PRODUCTION.
    """
    # Reset singleton to pick up updated environment
    GovernanceStateManager._instance = None
    yield
    # No cleanup needed for session scope


@pytest.fixture
def structural_policy():
    """
    T4f FIXTURE: ENABLES OFFLINE STRUCTURAL MODE.
    
    Use this fixture for STRUCTURAL regime tests that verify layout, schema,
    and backbone logic without requiring a real AI provider.
    
    Sets:
      - offline_structural_mode = True
      - require_ai_provider = STRICT (but ignored due to offline mode)
      - fail_closed_narrative_generation = STRICT (but offline mode bypasses)
    """
    import os
    # For offline structural mode, we must set TEST environment
    os.environ["PIPELINE_TEST_MODE"] = "true"
    
    # Reset singleton before use to ensure clean state
    GovernanceStateManager._instance = None
    
    state = get_governance_state()
    original_config = state.get_current_config()
    
    # Apply STRUCTURAL regime config
    from backend.domain.config import DeploymentEnvironment
    structural_config = GovernanceConfig(
        environment=DeploymentEnvironment.TEST,
        offline_structural_mode=True,
    )
    state.apply_config(structural_config, source="test_fixture")
    
    yield structural_config
    
    # Teardown: Reset singleton for clean state for next test
    GovernanceStateManager._instance = None


@pytest.fixture
def strict_policy():
    """
    T4f FIXTURE: STRICT POLICY ENFORCEMENT.
    
    Use this fixture for POLICY regime tests that verify guardrails.
    Ensures all policies are STRICT and no offline modes are allowed.
    """
    from backend.domain.guardrails import TruthPolicy, PolicyLevel
    
    policy = TruthPolicy(
        enforce_registry_immutability=PolicyLevel.STRICT,
        prevent_post_lock_registration=PolicyLevel.STRICT,
        prevent_presentation_math=PolicyLevel.STRICT,
        require_ai_provider=PolicyLevel.STRICT,
        fail_closed_narrative_generation=PolicyLevel.STRICT,
    )
    return policy


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "structural: tests that run in offline structural regime"
    )
