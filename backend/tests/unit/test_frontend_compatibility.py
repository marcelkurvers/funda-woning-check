"""
Frontend Compatibility Tests - Using Correct Pipeline API

Tests that verify generated chapters have correct structure for frontend.
All tests use execute_report_pipeline() - the ONLY valid path.
"""
import unittest
import os
import sys

# Set test mode BEFORE imports
os.environ["PIPELINE_TEST_MODE"] = "true"

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.pipeline.bridge import execute_report_pipeline


class TestRegression(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.core_data = {
            "address": "Test Street 1",
            "asking_price_eur": 500000,
            "living_area_m2": 100,
            "description": "Test property"
        }
        cls.chapters, cls.kpis, cls.enriched = execute_report_pipeline(
            run_id="test-frontend-compat",
            raw_data=cls.core_data,
            preferences={}
        )
    
    def test_chapter_id_present(self):
        """Verify that every generated chapter has an 'id' field for frontend sorting."""
        for i in range(14):
            key = str(i)
            self.assertIn(key, self.chapters, f"Chapter {key} should be in chapters dict")
            self.assertIn("id", self.chapters[key], f"Chapter {key} MISSING 'id' field")
            self.assertEqual(self.chapters[key]["id"], key, f"Chapter {key} id mismatch")

    def test_chapter_has_title(self):
        """Verify that every generated chapter has a 'title' field."""
        for i in range(14):
            key = str(i)
            self.assertIn("title", self.chapters[key], f"Chapter {key} MISSING 'title' field")
            self.assertIsNotNone(self.chapters[key]["title"], f"Chapter {key} has None title")

    def test_chapter_has_grid_layout(self):
        """Verify that every generated chapter has a 'grid_layout' field."""
        for i in range(14):
            key = str(i)
            self.assertIn("grid_layout", self.chapters[key], f"Chapter {key} MISSING 'grid_layout' field")


if __name__ == "__main__":
    unittest.main()
