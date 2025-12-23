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
from main import app, init_db

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

class TestIntegration(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_full_flow_with_paste(self):
        # 1. Start Run
        print("\n[Test] Starting Run...")
        resp = client.post("/api/runs", json={"funda_url": "https://www.funda.nl/test"})
        self.assertEqual(resp.status_code, 200)
        run_id = resp.json()["run_id"]
        
        # 2. Start Pipeline
        client.post(f"/api/runs/{run_id}/start")
        
        # Wait for "scrape" to finish (simulated)
        time.sleep(1)
        
        # 3. Paste HTML
        print("[Test] Pasting HTML content...")
        resp = client.post(f"/api/runs/{run_id}/paste", json={"funda_html": SAMPLE_HTML})
        self.assertEqual(resp.status_code, 200)
        
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
