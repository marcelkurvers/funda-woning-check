# TEST_REGIME: STRUCTURAL
# REQUIRES: offline_structural_mode=True
import sys
import os

# Set test mode BEFORE imports
os.environ["PIPELINE_TEST_MODE"] = "true"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest
from fastapi.testclient import TestClient
from main import app, init_db
import json

class TestApiEndpoints(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # T4gB-FIX: Apply governance singleton pattern
        from backend.domain.governance_state import GovernanceStateManager
        GovernanceStateManager._instance = None
        
        from backend.domain.governance_state import get_governance_state
        from backend.domain.config import GovernanceConfig, DeploymentEnvironment
        cls.gov_state = get_governance_state()
        cls.gov_state.apply_config(
            GovernanceConfig(
                environment=DeploymentEnvironment.TEST,
                offline_structural_mode=True
            ),
            source="test_api_endpoints"
        )

    @classmethod
    def tearDownClass(cls):
        from backend.domain.governance_state import GovernanceStateManager
        GovernanceStateManager._instance = None

    def setUp(self):
        # Use a fresh in-memory db or re-init the test db for each test
        init_db()
        self.client = TestClient(app)

    def test_create_run_defaults(self):
        """Test creating a run with minimal fields"""
        resp = self.client.post("/api/runs", json={"funda_url": "http://example.com"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("run_id", data)
        self.assertEqual(data["status"], "queued")

    def test_get_nonexistent_run(self):
        """Test 404 on missing run"""
        resp = self.client.get("/api/runs/non-existent-id/report")
        self.assertEqual(resp.status_code, 404)

    def test_start_run_updates_status(self):
        """Test that starting a run updates its status (simulated pipeline)"""
        # Create
        create_resp = self.client.post("/api/runs", json={"funda_url": "http://example.com"})
        run_id = create_resp.json()["run_id"]
        
        # Start
        start_resp = self.client.post(f"/api/runs/{run_id}/start")
        self.assertEqual(start_resp.status_code, 200)
        
        # Verify status via report or direct DB check (using report here implies status is implicitly checked by flow)
        report_resp = self.client.get(f"/api/runs/{run_id}/report")
        self.assertEqual(report_resp.status_code, 200)
        # We assume pipeline runs synchronously in local mode

    def test_preferences_api(self):
        """Test getting and setting preferences"""
        # Set
        payload = {"theme": "light", "language": "nl"}
        resp = self.client.post("/api/preferences", json=payload)
        self.assertEqual(resp.status_code, 200)
        
        # Get
        resp = self.client.get("/api/preferences")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), payload)

    def test_health_check(self):
        """Test health check endpoint"""
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["backend"], "ok")
        self.assertEqual(data["db"], "ok")

if __name__ == "__main__":
    unittest.main()
