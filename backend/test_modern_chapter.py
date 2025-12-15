import unittest
from main import build_chapters

class TestModernChapter(unittest.TestCase):
    def test_chapter_structure_modern(self):
        # 1. Mock Data
        core_data = {
            "address": "Teststraat 1",
            "asking_price_eur": "€ 500.000",
            "living_area_m2": "120 m²",
            "plot_area_m2": "300 m²",
            "build_year": "1990",
            "energy_label": "B"
        }

        # 2. Run
        chapters = build_chapters(core_data)

        # 3. Assert - Check Chapter 1
        ch1 = chapters["1"]
        self.assertIn("grid_layout", ch1, "Chapter 1 should have grid_layout")
        
        layout = ch1["grid_layout"]
        self.assertIn("metrics", layout)
        self.assertIn("main", layout)
        self.assertIn("sidebar", layout)


        # 4. Check Left Column (KPIs)
        # Chapter 1 now focuses on Surface areas
        # 4. Check Metrics (was Left Column)
        labels = [item["label"] for item in layout["metrics"]]
        self.assertIn("Woonoppervlakte", labels)

        # 4b. Verify Chapter 0 exists and has Price
        ch0 = chapters["0"]
        layout0 = ch0["grid_layout"]
        # Modern Dashboard check
        labels0 = [item["label"] for item in layout0["metrics"]]
        self.assertIn("Vraagprijs per m²", labels0)

        # 5. Check Sidebar (Advice)
        # Check if we have advisor type items
        types = [item.get("type") for item in layout["sidebar"]]
        self.assertTrue(any("advisor" in t for t in types if t))
        
        # 6. Check Main
        self.assertTrue(len(layout["main"]["content"]) > 0)
        self.assertIn("chapter-intro", layout["main"]["content"])

        # 7. Check PDF Fallback
        self.assertIn("blocks", ch1)
        # Blocks are now empty as we fully use grid_layout
        # self.assertEqual(ch1["blocks"][0]["type"], "paragraph")

    def test_energy_chapter_layout(self):
        # Check Chapter 4 (Energy)
        core_data = {"energy_label": "A++"}
        chapters = build_chapters(core_data)
        
        ch4 = chapters["4"]
        layout = ch4["grid_layout"]
        
        # Should have metrics in modern dashboard
        self.assertIn("metrics", layout)
        labels = [item["id"] for item in layout["metrics"]]

        self.assertIn("label", labels)


if __name__ == "__main__":
    unittest.main()
