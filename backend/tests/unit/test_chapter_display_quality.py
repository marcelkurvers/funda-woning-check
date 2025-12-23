
import unittest
import os
import sys
import json

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from main import build_chapters
from domain.models import ChapterOutput

class TestChapterDisplayQuality(unittest.TestCase):
    def setUp(self):
        self.core_data = {
            "address": "Prinsengracht 123",
            "asking_price_eur": "€ 850.000",
            "living_area_m2": "120",
            "build_year": "1930",
            "energy_label": "A",
            "marcel_match_score": 88.0,
            "petra_match_score": 94.0
        }

    def test_chapter_0_contains_all_required_frontend_data(self):
        """CRITICAL: Chapter 0 must contain variables, comparison, and segment."""
        chapters = build_chapters(self.core_data)
        ch0 = chapters["0"]
        
        # 1. Structural requirements
        self.assertIn("chapter_data", ch0)
        cd = ch0["chapter_data"]
        
        # 2. Data Matrix requirements (The 'Executive Summary NO info' fix)
        self.assertIn("variables", cd, "Chapter 0 MUST contain 'variables' for the Data Matrix")
        self.assertTrue(len(cd["variables"]) > 0, "Chapter 0 variables should not be empty")
        self.assertIn("asking_price_eur", cd["variables"], "Variables should contain asking price")
        
        # 3. Persona Match requirements
        self.assertIn("comparison", cd, "Chapter 0 MUST contain 'comparison' for persona cards")
        self.assertIn("marcel", cd["comparison"], "Comparison must have Marcel")
        self.assertIn("petra", cd["comparison"], "Comparison must have Petra")
        
        # 4. Display scores (Special bridge for v6.0.0)
        self.assertIn("marcel_match_score", cd, "Chapter 0 MUST expose 'marcel_match_score' to frontend")
        self.assertEqual(cd["marcel_match_score"], 88.0)
        
        # 5. Segment Tag requirements
        self.assertIn("segment", ch0, "Every chapter MUST HAVE a 'segment' name defined")
        self.assertEqual(ch0["segment"], "EXECUTIVE / STRATEGIE")

    def test_all_chapters_have_segments(self):
        """Ensures the segment header exists and is correctly mapped for all chapters."""
        chapters = build_chapters(self.core_data)
        
        expected_segments = {
            "0": "EXECUTIVE / STRATEGIE",
            "1": "OBJECT / ARCHITECTUUR",
            "2": "SYNERGIE / MATCH",
            "12": "VERDICT / STRATEGIE"
        }
        
        for ch_id, expected in expected_segments.items():
            self.assertIn(ch_id, chapters)
            self.assertEqual(chapters[ch_id]["segment"], expected)

if __name__ == "__main__":
    unittest.main()
