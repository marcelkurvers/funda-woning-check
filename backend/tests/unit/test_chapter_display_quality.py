"""
Chapter Display Quality Tests - Using Correct Pipeline API

Tests that verify chapter display quality and frontend data requirements.
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


class TestChapterDisplayQuality(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.core_data = {
            "address": "Prinsengracht 123",
            "asking_price_eur": 850000,
            "living_area_m2": 120,
            "build_year": 1930,
            "energy_label": "A",
            "description": "Beautiful Amsterdam property"
        }
        cls.chapters, cls.kpis, cls.enriched = execute_report_pipeline(
            run_id="test-display-quality",
            raw_data=cls.core_data,
            preferences={
                "marcel": {"priorities": ["tech"]},
                "petra": {"priorities": ["light"]}
            }
        )

    def test_chapter_0_exists(self):
        """CRITICAL: Chapter 0 must exist."""
        self.assertIn("0", self.chapters)
        ch0 = self.chapters["0"]
        self.assertIn("id", ch0)
        self.assertIn("title", ch0)

    def test_all_chapters_have_segments(self):
        """Ensures every chapter has a segment field."""
        for ch_id in range(14):
            key = str(ch_id)
            self.assertIn(key, self.chapters, f"Chapter {key} missing")
            ch = self.chapters[key]
            self.assertIn("segment", ch, f"Chapter {key} MUST have 'segment' field")
            self.assertIsNotNone(ch["segment"], f"Chapter {key} segment should not be None")

    def test_chapters_have_grid_layout(self):
        """Every chapter must have grid_layout structure."""
        for ch_id in range(14):
            key = str(ch_id)
            ch = self.chapters[key]
            self.assertIn("grid_layout", ch, f"Chapter {key} MUST have 'grid_layout'")


if __name__ == "__main__":
    unittest.main()
