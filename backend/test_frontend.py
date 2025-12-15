import unittest
from bs4 import BeautifulSoup
import os

class TestFrontendStructure(unittest.TestCase):
    def setUp(self):
        self.static_dir = os.path.join(os.path.dirname(__file__), "static")

    def test_01_index_html_structure(self):
        """
        Validates the structure of the new Premium UI in index.html.
        """
        html_path = os.path.join(self.static_dir, "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        
        # 1. Check Hero
        hero = soup.find(id="start-screen")
        self.assertIsNotNone(hero, "Hero section #start-screen missing")
        self.assertIn("AI ANALYSE 2.0", hero.get_text())
        
        # 2. Check Dashboard Section (should be hidden by default)
        dash = soup.find(id="dashboard-screen")
        self.assertIsNotNone(dash, "Dashboard section #dashboard-screen missing")
        self.assertIn("hidden", dash.get("class", []))
        
        # 3. Check Critical Components
        self.assertIn("DOMContentLoaded", str(soup))
        # Ensure fallback paste area exists
        self.assertIsNotNone(soup.find(id="paste-area"), "Paste area missing")
        self.assertIsNotNone(soup.find(id="toggle-paste"), "Paste Toggle missing")
        
        # 4. Check Dashboard Containers (Targeted by JS)
        self.assertIsNotNone(soup.find(id="btn-download-pdf"), "PDF Download button missing")
        self.assertIsNotNone(soup.find(id="d-address"), "Address display container missing")
        self.assertIsNotNone(soup.find(id="kpi-area"), "KPI Grid container missing")
        self.assertIsNotNone(soup.find(id="advisor-area"), "Advisor Panel container missing")
        self.assertIsNotNone(soup.find(id="chapter-nav"), "Sidebar Navigation container missing")
        self.assertIsNotNone(soup.find(id="report-content"), "Report Content container missing")

        # 5. Check Script Logic (Now Inline)
        # Verify that the main logic variables are present in the inline script
        inline_scripts = [s.get_text() for s in soup.find_all("script") if not s.get("src")]
        found_logic = False
        for s in inline_scripts:
            if "let currentRunId" in s:
                found_logic = True
                break
        self.assertTrue(found_logic, "Inline script logic (currentRunId) missing in index.html")
        
        # Verify switchTab is present
        found_switch = False
        for s in inline_scripts:
            if "function switchTab(key)" in s:
                found_switch = True
                break
        self.assertTrue(found_switch, "switchTab function missing in index.html")

        # Verify modern grid rendering logic
        found_grid = False
        for s in inline_scripts:
            if "ch.grid_layout" in s and "chapter-grid" in s:
                found_grid = True
                break
        self.assertTrue(found_grid, "Modern grid layout rendering logic missing in index.html")

    def test_02_preferences_html_structure(self):
        """
        Validates structure of preferences.html
        """
        html_path = os.path.join(self.static_dir, "preferences.html")
        if not os.path.exists(html_path):
            self.fail("preferences.html does not exist")

        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            
        self.assertIn("Voorkeuren", soup.title.string)
        self.assertIsNotNone(soup.find(id="btn-save"), "Save button missing")
        self.assertIsNotNone(soup.find(id="shared-budget"), "Preferences input missing")

if __name__ == "__main__":
    unittest.main()
