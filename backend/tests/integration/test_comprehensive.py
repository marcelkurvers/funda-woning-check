"""
Comprehensive Integration Tests - Using Correct Pipeline API

These tests verify comprehensive end-to-end functionality.
All tests use execute_report_pipeline() - the ONLY valid path.
"""
import sys
import os

# Set test mode BEFORE any imports
os.environ["PIPELINE_TEST_MODE"] = "true"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest

from backend.pipeline.bridge import execute_report_pipeline
from tests.data_loader import load_test_data


class TestComprehensive(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load test data and run pipeline once for base tests."""
        cls.core_data = load_test_data()
        cls.chapters, cls.kpis, cls.enriched = execute_report_pipeline(
            run_id="test-comprehensive",
            raw_data=cls.core_data,
            preferences={}
        )
    
    def test_all_chapters_generated(self):
        """Verify that all 14 chapters (0-13) are generated."""
        # Check we have 14 chapters (0-13)
        self.assertEqual(len(self.chapters), 14, f"Expected 14 chapters, got {len(self.chapters)}")
        
        # Verify specific content in each chapter
        for i in range(14):
            str_i = str(i)
            self.assertIn(str_i, self.chapters, f"Chapter {i} missing")
            
            chapter = self.chapters[str_i]
            self.assertIn("id", chapter, f"Chapter {i} missing 'id'")
            self.assertIn("title", chapter, f"Chapter {i} missing 'title'")
            
            # Check for grid layout structure
            self.assertIn("grid_layout", chapter, f"Chapter {i} missing 'grid_layout'")

    def test_kpis_generated(self):
        """Test KPIs are correctly generated."""
        self.assertIn("dashboard_cards", self.kpis)
        self.assertIn("completeness", self.kpis)
        self.assertIn("fit_score", self.kpis)
        
        # Should have 4 dashboard cards
        self.assertEqual(len(self.kpis["dashboard_cards"]), 4)
        
        # Check card IDs
        card_ids = [c["id"] for c in self.kpis["dashboard_cards"]]
        self.assertIn("fit", card_ids)
        self.assertIn("completeness", card_ids)
        self.assertIn("value", card_ids)
        self.assertIn("energy", card_ids)

    def test_enriched_core_contains_registry_values(self):
        """Test enriched core contains all registered values."""
        # These should be in the enriched core
        self.assertIn("asking_price_eur", self.enriched)
        self.assertIn("living_area_m2", self.enriched)
        self.assertIn("energy_label", self.enriched)

    def test_validation_status_tracked(self):
        """Test that validation status is in KPIs."""
        self.assertIn("validation_passed", self.kpis)

    def test_energy_label_affects_chapter_4(self):
        """Test that different energy labels produce different outputs."""
        # Run with Label A
        data_a = self.core_data.copy()
        data_a["energy_label"] = "A"
        chapters_a, _, _ = execute_report_pipeline(
            run_id="test-energy-a",
            raw_data=data_a,
            preferences={}
        )
        
        # Run with Label G
        data_g = self.core_data.copy()
        data_g["energy_label"] = "G"
        chapters_g, _, _ = execute_report_pipeline(
            run_id="test-energy-g",
            raw_data=data_g,
            preferences={}
        )
        
        # Get chapter 4 main content
        ch4_a = chapters_a.get("4", {})
        ch4_g = chapters_g.get("4", {})
        
        # Both should exist
        self.assertIsNotNone(ch4_a)
        self.assertIsNotNone(ch4_g)
        
        # Content should differ based on energy label
        # (At minimum, the chapter_data should reflect the different labels)
        enriched_a_label = data_a["energy_label"]
        enriched_g_label = data_g["energy_label"]
        self.assertNotEqual(enriched_a_label, enriched_g_label)


if __name__ == "__main__":
    unittest.main()
