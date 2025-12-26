import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest
import json
import time
import os

# Set test database path before importing main
os.environ["APP_DB"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/test_integration.db"))

from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app, init_db, update_run
from intelligence import IntelligenceEngine

client = TestClient(app)

SAMPLE_HTML = """
<html>
<body>
    <div class="object-header__price">€ 950.000 k.k.</div>
    <h1 class="object-header__title">Teststraat 1, 1000 AA Amsterdam</h1>
    <dt>Woonoppervlakte</dt><dd>150 m²</dd>
    <dt>Energielabel</dt><dd>B</dd>
</body>
</html>
"""

# TEST_REGIME: STRUCTURAL
# REQUIRES: offline_structural_mode=True

class TestIntegration(unittest.TestCase):
    def setUp(self):
        import os
        os.environ["PIPELINE_TEST_MODE"] = "true"
        
        init_db()
        # Prevent init_ai_provider from running in the background thread and resetting our configuration
        self.patcher = patch('main.init_ai_provider')
        self.mock_init = self.patcher.start()
        
        # Patch Scraper to avoid network calls and timeouts
        self.patcher_scraper = patch('main.Scraper')
        self.mock_scraper = self.patcher_scraper.start()
        self.mock_scraper.return_value.derive_property_core.return_value = {}

        # Force fallback
        IntelligenceEngine.set_provider(None)
        
        # T4f: Enable Offline Structural Mode
        # MUST reset singleton FIRST to ensure it reads TEST environment
        from backend.domain.governance_state import GovernanceStateManager
        GovernanceStateManager._instance = None
        
        from backend.domain.governance_state import get_governance_state
        from backend.domain.config import GovernanceConfig, DeploymentEnvironment
        self.gov_state = get_governance_state()
        self.original_config = self.gov_state.get_current_config()
        self.gov_state.apply_config(
            GovernanceConfig(
                environment=DeploymentEnvironment.TEST,
                offline_structural_mode=True
            ),
            source="test_integration"
        )

    def tearDown(self):
        self.patcher.stop()
        self.patcher_scraper.stop()
        # Reset singleton so the next test gets a fresh state
        from backend.domain.governance_state import GovernanceStateManager
        GovernanceStateManager._instance = None

    def test_full_flow_with_paste(self):
        # 1. Start Run
        print("\n[Test] Starting Run...")
        resp = client.post("/api/runs", json={"funda_url": "https://www.funda.nl/test"})
        self.assertEqual(resp.status_code, 200)
        run_id = resp.json()["run_id"]
        
        # 2. Start Pipeline
        client.post(f"/api/runs/{run_id}/start")
        
        # Poll for completion (max 2 seconds)
        for _ in range(20):
            status_resp = client.get(f"/api/runs/{run_id}/status")
            if status_resp.json()["status"] == "done":
                break
            time.sleep(0.1)
        
        # 3. Paste HTML
        print("[Test] Pasting HTML content...")
        resp = client.post(f"/api/runs/{run_id}/paste", json={"funda_html": SAMPLE_HTML})
        self.assertEqual(resp.status_code, 200)

        # Reset status to queued so we can reliably poll for the NEXT done state
        update_run(run_id, status="queued")
        
        # Trigger Re-Run to update KPIs and Chapters with pasted data
        client.post(f"/api/runs/{run_id}/start") 
        
        # Poll for completion AGAIN
        for _ in range(20):
            status_resp = client.get(f"/api/runs/{run_id}/status")
            if status_resp.json()["status"] == "done":
                break
            time.sleep(0.1)
        
        # 4. Verify Data is updated in property_core (via Report)
        print("[Test] Fetching Report...")
        resp = client.get(f"/api/runs/{run_id}/report")
        data = resp.json()
        
        # Check if price is reflected in property_core or anywhere in data
        # In current version, price matches on "950.000"
        self.assertIn("950.000", json.dumps(data))
        
        # Chapters check
        chapters = data.get("chapters", {})
        self.assertTrue(len(chapters) > 0)
        
        # Check Chapter 0
        ch0 = chapters.get("0")
        self.assertIsNotNone(ch0)
        
        # In modern dashboard, metrics are often called 'metrics' in the grid_layout
        layout = ch0.get("grid_layout", {})
        metrics = layout.get("metrics", [])
        
        # Check KPIs
        kpi_data = data.get("kpis", {})
        kpis = kpi_data.get("dashboard_cards", [])
        
        print(f"[Test] Found {len(kpis)} top-level KPIs")
        
        # Completeness should be non-zero if tracked
        if kpis:
            completeness_card = next((c for c in kpis if c.get('id') == 'completeness'), None)
            if completeness_card:
                self.assertIsNotNone(completeness_card.get('value'))
                self.assertNotEqual(completeness_card.get('value'), "0%", "Completeness should not be 0% after paste")

if __name__ == "__main__":
    unittest.main()
