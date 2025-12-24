"""
Modern Design Compliance Tests - Using Correct Pipeline API

Tests that verify chapters follow modern design patterns.
All tests use execute_report_pipeline() - the ONLY valid path.
"""
import sys
import os

# Set test mode BEFORE imports
os.environ["PIPELINE_TEST_MODE"] = "true"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest

from backend.pipeline.bridge import execute_report_pipeline


class TestModernDesignCompliance(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.core_data = {
            "address": "Prinsengracht 1",
            "asking_price_eur": 1250000,
            "living_area_m2": 185,
            "plot_area_m2": 0,
            "build_year": 1890,
            "energy_label": "C",
            "rooms": 5,
            "description": "Prachtig pand aan de gracht met high-end afwerking. Volledig gerenoveerd in 2020."
        }
        cls.chapters, cls.kpis, cls.enriched = execute_report_pipeline(
            run_id="test-modern-design",
            raw_data=cls.core_data,
            preferences={}
        )

    def test_all_chapters_exist(self):
        """Verify we have the expected number of chapters (0-13)"""
        for i in range(14):
            self.assertIn(str(i), self.chapters, f"Chapter {i} is missing from generation")

    def test_chapters_have_required_structure(self):
        """Check every chapter has required structure fields."""
        for i in range(14):
            ch_key = str(i)
            chapter = self.chapters[ch_key]
            
            with self.subTest(chapter=f"Chapter {i}"):
                self.assertIn("id", chapter, "Missing id")
                self.assertIn("title", chapter, "Missing title")
                self.assertIn("grid_layout", chapter, "Missing grid_layout")
                self.assertIn("segment", chapter, "Missing segment")

    def test_chapters_have_grid_layout_main(self):
        """Check every chapter's grid_layout has a main section."""
        for i in range(14):
            ch_key = str(i)
            chapter = self.chapters[ch_key]
            
            layout = chapter.get("grid_layout", {})
            self.assertIn("main", layout, f"Chapter {i} missing 'main' in grid_layout")
                
    def test_data_integrity_no_placeholders(self):
        """Ensure data is based on rendered info, not placeholders."""
        forbidden_terms = ["Lorem Ipsum", "Dolor Sit Amet", "TBD", "[Template]"]
        
        for i, ch_data in self.chapters.items():
            dump = str(ch_data)
            for term in forbidden_terms:
                self.assertNotIn(term, dump, f"Chapter {i} contains placeholder text '{term}'")

    def test_address_present_in_chapter_0(self):
        """Check address is present in Chapter 0."""
        ch0 = self.chapters.get("0")
        if ch0:
            dump = str(ch0)
            self.assertIn("Prinsengracht", dump, "Address not found in Chapter 0")


if __name__ == "__main__":
    unittest.main()
