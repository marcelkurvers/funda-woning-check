
import unittest
import os
import sys

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from main import build_chapters
from domain.models import ChapterOutput

class TestRegression(unittest.TestCase):
    def test_chapter_id_present(self):
        """Verify that every generated chapter has an 'id' field for frontend sorting."""
        core_data = {"address": "Test Street 1", "asking_price_eur": "500000", "living_area_m2": "100"}
        chapters = build_chapters(core_data)
        
        for i in range(13):
            key = str(i)
            self.assertIn(key, chapters, f"Chapter {key} should be in chapters dict")
            self.assertIn("id", chapters[key], f"Chapter {key} MISSING 'id' field")
            self.assertEqual(chapters[key]["id"], key, f"Chapter {key} id mismatch")

    def test_chapter_data_bridging(self):
        """Verify that layout items are bridged to chapter_data for frontend compatibility."""
        core_data = {"address": "Test Street 1", "asking_price_eur": "500000", "living_area_m2": "100"}
        chapters = build_chapters(core_data)
        
        for i in range(13):
            ch = chapters[str(i)]
            self.assertIn("chapter_data", ch, f"Chapter {i} MISSING 'chapter_data'")
            cd = ch["chapter_data"]
            self.assertIn("sidebar_items", cd, f"Chapter {i} chapter_data MISSING 'sidebar_items'")
            self.assertIn("metrics", cd, f"Chapter {i} chapter_data MISSING 'metrics'")

if __name__ == "__main__":
    unittest.main()
