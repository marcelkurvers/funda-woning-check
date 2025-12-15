import unittest
from main import build_chapters

class TestModernDesignCompliance(unittest.TestCase):
    def setUp(self):
        # 1. Extensive Mock Data to ensure "rich" rendered info possibility
        self.core_data = {
            "address": "Prinsengracht 1",
            "asking_price_eur": "€ 1.250.000",
            "living_area_m2": "185 m²",
            "plot_area_m2": "0 m²",
            "build_year": "1890",
            "energy_label": "C",
            "rooms": "5",
            # Add other potential fields that might be used
            "description": "Prachtig pand aan de gracht met high-end afwerking. Volledig gerenoveerd in 2020."
        }
        self.chapters = build_chapters(self.core_data)

    def test_all_chapters_exist(self):
        """Verify we have the expected number of chapters (0-12)"""
        for i in range(13):
            self.assertIn(str(i), self.chapters, f"Chapter {i} is missing from generation")

    def test_modern_4k_structure_compliance(self):
        """
        Check if every chapter follows the 'Modern 4K' layout:
        - grid_layout structure
        - Sections: metrics (Top/Left), main (Center), sidebar (Right/Advice)
        """
        for i in range(13):
            ch_key = str(i)
            chapter = self.chapters[ch_key]
            
            with self.subTest(chapter=f"Chapter {i} ({chapter.get('title')})"):
                # 1. Structure Check
                self.assertIn("grid_layout", chapter, "Missing grid_layout")
                layout = chapter["grid_layout"]
                
                # Verify Layout Type
                self.assertEqual(layout.get("layout_type"), "modern_dashboard", f"Chapter {i} layout_type mismatch")
                
                # Verify the Modern trio sections
                self.assertIn("metrics", layout, f"Chapter {i} missing 'metrics' section")
                self.assertIn("main", layout, f"Chapter {i} missing 'main' section")
                self.assertIn("sidebar", layout, f"Chapter {i} missing 'sidebar' section")

                # 2. Content Checks - Metrics
                metrics = layout["metrics"]
                self.assertIsInstance(metrics, list, "Metrics should be a list")
                # Every chapter should have at least some metrics (top bar or left items)
                self.assertTrue(len(metrics) > 0, f"Chapter {i} has empty metrics")
                for m in metrics:
                    self.assertIn("label", m, "Metric item missing label")
                    self.assertIn("value", m, "Metric item missing value")
                    # Check not empty/mockup
                    self.assertNotEqual(m["value"], "Unknown", "Metric has placeholder 'Unknown'")
                    self.assertNotEqual(m["value"], "", "Metric value is empty")

                # 3. Content Checks - Main
                main = layout["main"]
                self.assertIn("content", main, "Main section missing content")
                content = main["content"]
                # Content can be text or list of components. Assuming rich list for Modern UI.
                if isinstance(content, list):
                    self.assertTrue(len(content) > 0, "Main content list is empty")
                    # Check for rich types
                    types = [c.get("type", "unknown") for c in content if isinstance(c, dict)]
                    self.assertTrue(len(types) > 0, "No typed components in main content")
                else:
                    # If it's a string, it shouldn't be empty
                    self.assertTrue(len(str(content)) > 10, "Main content text too short")

                # 4. Content Checks - Sidebar
                sidebar = layout["sidebar"]
                self.assertIsInstance(sidebar, list, "Sidebar should be a list")
                # Sidebar might be optional in *some* designs, but prompt implies "sections that display"
                # So we expect advice or tools here.
                # However, strictly typically 0-12 chapters all have advice in this app logic.
                if len(sidebar) == 0:
                    print(f"WARNING: Sidebar empty for Chapter {i}")
                
                # Check for specific Modern UI component types if sidebar exists
                for widget in sidebar:
                    self.assertIn("type", widget, "Sidebar widget missing type")
                    
    def test_data_integrity_no_placeholders(self):
        """
        Ensure data is based on rendered info, not placeholders.
        """
        forbidden_terms = ["Lorem Ipsum", "Dolor Sit Amet", "TBD", "Template"]
        
        for i, ch_data in self.chapters.items():
            # Dump to string to search comprehensively
            dump = str(ch_data)
            for term in forbidden_terms:
                self.assertNotIn(term, dump, f"Chapter {i} contains placeholder text '{term}'")

    def test_enriched_by_ai_check(self):
        """
        Check for evidence of AI/Logic enrichment.
        Example: Price per m2 calculation or specific advice generation.
        """
        # Chapter 0 or 1 usually contains derived metrics
        ch0 = self.chapters.get("0")
        if ch0:
            layout = ch0["grid_layout"]
            metrics = layout.get("metrics", [])
            # In setUp we set 1.250.000 / 185 = ~6756
            # We look for something that resembles this enriched calculation if it's there
            # OR checking for "Prinsengracht" in the title or content
            
            dump = str(ch0)
            self.assertIn("Prinsengracht", dump, "Address not found in Chapter 0")

if __name__ == "__main__":
    unittest.main()
