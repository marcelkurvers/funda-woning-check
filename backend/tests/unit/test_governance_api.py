# TEST_REGIME: STRUCTURAL
# REQUIRES: None (governance API tests)
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app
from backend.domain.governance_state import get_governance_state, GovernanceStateManager, DeploymentEnvironment

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_governance_state():
    state = get_governance_state()
    state._current_config = None
    state._audit_log = []
    yield
    state._current_config = None

def test_get_status_returns_structure():
    response = client.get("/api/governance/status")
    assert response.status_code == 200
    data = response.json()
    assert "environment" in data
    assert "effective_truth_policy" in data
    assert "classification" in data

def test_production_rejects_apply_illegal_config():
    """Test that we cannot even create an illegal GovernanceConfig for PROD."""
    # We don't even need to mock environment here because the ApplyRequest payload 
    # explicitly specifies environment="PRODUCTION".
    # The API tries to create GovernanceConfig(environment=PRODUCTION, allow_partial=True)
    # This raises ValueError inside GovernanceConfig.__post_init__
    
    payload = {
        "environment": "PRODUCTION",
        "allow_partial_generation": True
    }
    response = client.post("/api/governance/apply", json=payload)
    assert response.status_code == 400 
    assert "Illegal Configuration" in response.text

def test_production_rejects_apply_valid_config():
    """Test that even a 'valid' config cannot be applied in PROD."""
    # Here we need to force the Runtime Environment to be PRODUCTION
    with patch.object(GovernanceStateManager, 'get_environment', return_value=DeploymentEnvironment.PRODUCTION):
        payload = {
            "environment": "PRODUCTION",
            "allow_partial_generation": False
        }
        response = client.post("/api/governance/apply", json=payload)
        assert response.status_code == 403
        assert "IMMUTABLE in PRODUCTION" in response.text

def test_dev_allows_apply():
    # Force Runtime Environment to DEVELOPMENT
    with patch.object(GovernanceStateManager, 'get_environment', return_value=DeploymentEnvironment.DEVELOPMENT):
        payload = {
            "environment": "DEVELOPMENT",
            "allow_partial_generation": True
        }
        response = client.post("/api/governance/apply", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["effective_truth_policy"]["fail_closed_narrative_generation"] == "OFF"
        assert data["current_governance_config"]["allow_partial_generation"] is True

def test_reset_works():
    # Force Runtime Environment to DEVELOPMENT
    with patch.object(GovernanceStateManager, 'get_environment', return_value=DeploymentEnvironment.DEVELOPMENT):
        # Apply first
        client.post("/api/governance/apply", json={"environment": "DEVELOPMENT", "allow_partial_generation": True})
        
        # Reset
        response = client.post("/api/governance/reset")
        assert response.status_code == 200
        data = response.json()
        assert data["current_governance_config"] is None
        assert data["effective_truth_policy"]["fail_closed_narrative_generation"] == "STRICT"
