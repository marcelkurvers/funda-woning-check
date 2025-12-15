import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest
from domain.models import PropertyCore, UIComponent, ChapterLayout, ChapterOutput

class TestDomainModels(unittest.TestCase):
    def test_property_core_defaults(self):
        """Test default values for PropertyCore"""
        core = PropertyCore(funda_url="http://test.url")
        self.assertEqual(core.address, "onbekend (handmatig te vullen)")
        self.assertEqual(core.energy_label, "onbekend")
        self.assertIsNone(core.asking_price_eur)
        self.assertEqual(core.extra_data, {})

    def test_ui_component_structure(self):
        """Test UIComponent creation"""
        comp = UIComponent(type="metric", label="Price", value="€100")
        self.assertEqual(comp.type, "metric")
        self.assertEqual(comp.label, "Price")
        self.assertEqual(comp.value, "€100")
        self.assertIsNone(comp.trend)

    def test_chapter_output_flexibility(self):
        """Test ChapterOutput accepts dict for grid_layout"""
        layout_dict = {
            "layout_type": "modern_dashboard",
            "metrics": [],
            "main": {},
            "sidebar": []
        }
        output = ChapterOutput(title="Test Chapter", grid_layout=layout_dict)
        self.assertEqual(output.title, "Test Chapter")
        self.assertEqual(output.grid_layout, layout_dict)

if __name__ == "__main__":
    unittest.main()
