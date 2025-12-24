

import sys
import os
import unittest
import json
import uuid
from unittest.mock import patch, MagicMock


# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi.testclient import TestClient

# Mock WeasyPrint BEFORE importing main to avoid OSError due to missing system libs (pango/cairo)
# This allows us to test the Application Logic (HTML generation, Formatting) without needing the physical PDF engine working.
sys.modules["weasyprint"] = MagicMock()
sys.modules["weasyprint.HTML"] = MagicMock()

import main

class TestPDFExport(unittest.TestCase):
    def setUp(self):
        self.test_db_path = f"test_{uuid.uuid4()}.db"
        # Patch the DB_PATH in main module
        self.db_patcher = patch("main.DB_PATH", self.test_db_path)
        self.db_patcher.start()
        
        # Initialize the DB
        main.init_db()
        
        # Force WeasyPrint available to True for testing logic
        main.WEASYPRINT_AVAILABLE = True
        if not hasattr(main, "HTML"):
            main.HTML = MagicMock()
        
        self.client = TestClient(main.app)

    def tearDown(self):
        self.db_patcher.stop()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_pdf_export_functionality(self):
        """
        Requirements:
        1. Check Export PDF function is working (Status 200, PDF content).
        2. Check result is formatted (Inspect HTML sent to WeasyPrint).
        3. Check at least 10 pages (Implied by content length/chapters).
        4. Check professional front page (Cover section in HTML).
        """
        
        # 1. Setup Data: Create a Run
        run_id = str(uuid.uuid4())
        
        # Create Dummy Chapters (0-12)
        # To ensure > 10 pages, we ensure every chapter has some content.
        chapters = {}
        for i in range(13):
            chapters[str(i)] = {
                "title": f"Hoofdstuk {i} - Test Title",
                "grid_layout": {
                    "layout_type": "modern_dashboard",
                    "metrics": [
                        {"id": f"m{i}", "label": "Test Metric", "value": "100", "color": "blue"}
                    ],
                    "main": {
                        "title": f"Main Content {i}",
                        "content": f"<p>This is the detailed content for chapter {i}. " * 20 + "</p>"
                    },
                    "sidebar": [
                        {"type": "advisor_card", "title": "Advice", "content": "Some advice here."}
                    ]
                }
            }
            
        core = {
            "address": "Teststraat 123, 1234 AB Teststad",
            "asking_price_eur": "€ 450.000",
            "living_area_m2": "120 m²"
        }

        # Insert directly into DB
        con = main.db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO runs (id, funda_url, funda_html, status, steps_json, property_core_json, chapters_json, kpis_json, sources_json, unknowns_json, artifacts_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                run_id, 
                "http://test.url", 
                None, 
                "done", 
                json.dumps(main.default_steps()), 
                json.dumps(core), 
                json.dumps(chapters), 
                "{}", "[]", "[]", "{}", 
                main.now(), main.now()
            )
        )
        con.commit()
        con.close()

        # 2. Mock WeasyPrint HTML Class to inspect HTML and return dummy PDF
        # Note: We mocked the module 'weasyprint' at the top, so we need to set behavior on that mock.
        
        captured_html = []
        
        # Setup the mock to return a write_pdf result
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4 Mock PDF Content"
        
        # The HTML class constructor should return this instance
        # main.HTML is actually weasyprint.HTML imported.
        # Check if main.HTML is already our mock.
        
        def side_effect_HTML(string=None, **kwargs):
            if string:
                captured_html.append(string)
            return mock_html_instance

        # We assume main.HTML is our mocked object because of sys.modules hack.
        # But main.py did 'from weasyprint import HTML', so main.HTML refers to the object in weasyprint module at import time.
        # If we reload or if patch worked, it should be fine.
        # To be safe, we patch main.HTML directly here.
        
        with patch("main.HTML", side_effect=side_effect_HTML):
            response = self.client.get(f"/api/runs/{run_id}/pdf")

        # 3. Validation
        
        # A. Status and Content Type
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got {response.status_code}")
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"), "Response does not start with %PDF marker")

        # B. Check Formatting & Front Page (via Captured HTML)
        self.assertTrue(len(captured_html) > 0, "HTML was not passed to WeasyPrint")
        html_content = captured_html[0]
        
        # Check Front Page
        self.assertIn('<div class="page cover-page">', html_content, "Magazine Front Page (cover-page class) not found")
        self.assertIn("Teststraat 123", html_content, "Address not found on cover")
        
        # Check Chapters & Page Breaks
        self.assertIn('<div class="page">', html_content)
        count_titles = html_content.count('class="chapter-title"')
        self.assertGreaterEqual(count_titles, 13, "Expected at least 13 chapter titles")

        # Check Modern Layout usage
        self.assertIn('class="mag-v3-kpi-grid"', html_content, "Magazine V3 KPI Grid not found")
        self.assertIn('KURVERS PROPERTY CONSULTING', html_content, "Branding not found")

        print("Test PDF Export Logic Passed (Mocked Engine).")

if __name__ == "__main__":
    unittest.main()
