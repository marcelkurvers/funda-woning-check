import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest
import os
from main import build_chapters, build_kpis

class TestComprehensive(unittest.TestCase):
    def setUp(self):
        # MANDATORY: Load from test-data directory
        from tests.data_loader import load_test_data
        self.core_data = load_test_data()

    def test_all_chapters_generated(self):
        """
        Verify that all 14 chapters (0-13) are generated.
        """
        chapters = build_chapters(self.core_data)
        
        # Check we have 14 chapters (0-13)
        self.assertEqual(len(chapters), 14, f"Expected 14 chapters, got {len(chapters)}")
        
        # Verify specific content in each chapter
        for i in range(1, 14):
            str_i = str(i)
            self.assertIn(str_i, chapters, f"Chapter {i} missing")
            # Check for grid layout main content
            layout = chapters[str_i]["grid_layout"]
            if isinstance(layout, dict) and "main" in layout:
                 content = layout["main"]["content"]
            else:
                 # Legacy fallback
                 content = chapters[str_i]["blocks"][0]["data"]["text"] if chapters[str_i]["blocks"] else ""
            
            # Check for address injection
            # Note: With IntelligenceEngine, address might be in Intro
            self.assertTrue(len(content) > 10, f"Chapter {i} content too short")

            
            # Specific known placeholders checking
            if "[Adres]" in content:
                 self.fail(f"Chapter {i} contains unresolved placeholder [Adres]")

    def test_kpi_calculations_robustness(self):
        """
        Test KPI builder with various data states.
        """
        # Case 1: Perfect data
        kpis = build_kpis(self.core_data)
        comp_card = next(c for c in kpis["dashboard_cards"] if c["id"] == "completeness")
        self.assertEqual(comp_card["value"], "100%")

        # Case 2: Missing Price
        partial_data = self.core_data.copy()
        del partial_data["asking_price_eur"]
        kpis = build_kpis(partial_data)
        comp_card = next(c for c in kpis["dashboard_cards"] if c["id"] == "completeness")
        # Should be less than 100%
        self.assertNotEqual(comp_card["value"], "100%")

    def test_energy_label_logic(self):
        """
        Test that logic blocks like [IF Label matches A] working correctly.
        """
        # Label A
        data_A = self.core_data.copy()
        data_A["energy_label"] = "A"
        chapters_A = build_chapters(data_A)
        text_A = chapters_A["4"]["grid_layout"]["main"]["content"] # Checking Ch 4 (Energy)
        
        # Label G
        data_G = self.core_data.copy()
        data_G["energy_label"] = "G"
        chapters_G = build_chapters(data_G)
        text_G = chapters_G["4"]["grid_layout"]["main"]["content"]
        
        # They should differ
        self.assertNotEqual(text_A, text_G, "Dynamic logic failed to differentiate between Label A and G")

if __name__ == "__main__":
    unittest.main()
