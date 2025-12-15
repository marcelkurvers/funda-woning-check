import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import sys
import os
import unittest
# Add backend root to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chapters.registry import get_chapter_class
from chapters.base import BaseChapter
from domain.models import ChapterOutput

class TestChapters(unittest.TestCase):
    def setUp(self):
        self.mock_data = {
            "address": "Teststraat 1",
            "funda_url": "http://test.nl",
            "asking_price_eur": "€ 500.000",
            "living_area_m2": "120 m²",
            "plot_area_m2": "200 m²",
            "build_year": "1990",
            "energy_label": "A"
        }

    def test_chapter_registry(self):
        """Test that all chapters 0-12 are registered"""
        for i in range(13):
            cls = get_chapter_class(i)
            self.assertIsNotNone(cls, f"Chapter {i} is missing from registry")
            self.assertTrue(issubclass(cls, BaseChapter))

    def test_chapter_generation(self):
        """Test that each chapter generates valid output"""
        for i in range(13):
             cls = get_chapter_class(i)
             instance = cls(self.mock_data)
             output = instance.generate()
             
             self.assertIsInstance(output, ChapterOutput)
             self.assertTrue(output.title, f"Chapter {i} has no title")
             self.assertIsNotNone(output.grid_layout, f"Chapter {i} has no grid layout")
             
             # Test content existence
             # Modern dashboard uses 'main' dict with 'content'
             if isinstance(output.grid_layout, dict) and "main" in output.grid_layout:
                 main = output.grid_layout["main"]
                 self.assertTrue(len(main.get("content", "")) > 0, f"Chapter {i} main content empty")
             else:
                 # Legacy fallback check
                 self.assertTrue(len(output.grid_layout.getattr("center", [])) > 0, f"Chapter {i} center col empty")

             
             # Specific checks
             if i == 0:
                 self.assertEqual(output.title, "0. Executive Summary")
             elif i == 1:
                 # Check logic: Should have Woonoppervlakte in metrics
                 if isinstance(output.grid_layout, dict) and "metrics" in output.grid_layout:
                     ids = [x["id"] for x in output.grid_layout["metrics"]]
                     self.assertIn("living", ids)
                 else:
                     # Legacy
                     labels = [x.label for x in output.grid_layout.left if x.label]
                     self.assertTrue(any("Woonoppervlakte" in l for l in labels))

if __name__ == '__main__':
    unittest.main()
