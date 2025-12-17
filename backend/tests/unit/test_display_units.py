import unittest
import re
from main import build_chapters


class TestDisplayUnits(unittest.TestCase):
    """Test that units (m², €, etc.) are not duplicated in display"""
    
    def setUp(self):
        self.core_data = {
            "address": "Teststraat 123",
            "asking_price_eur": "€ 500.000",
            "living_area_m2": "165 m²",
            "plot_area_m2": "634 m²",
            "build_year": "1988",
            "energy_label": "B",
            "rooms": "5",
        }
        self.chapters = build_chapters(self.core_data)
    
    def test_no_duplicate_m2_in_metrics(self):
        """Check that m² is not duplicated in metric displays"""
        for ch_id, ch_data in self.chapters.items():
            if not ch_data.get("grid_layout"):
                continue
            
            metrics = ch_data["grid_layout"].get("metrics", [])
            for metric in metrics:
                value = metric.get("value", "")
                label = metric.get("label", "")
                
                # Check for duplicate m²
                if "m²" in value or "m2" in value:
                    # Count occurrences
                    m2_count = value.count("m²") + value.count("m2")
                    self.assertLessEqual(m2_count, 1, 
                        f"Chapter {ch_id}, metric '{label}': Duplicate m² in value '{value}'")
    
    def test_no_duplicate_m2_in_hero(self):
        """Check that m² is not duplicated in hero labels"""
        for ch_id, ch_data in self.chapters.items():
            if not ch_data.get("grid_layout"):
                continue
            
            hero = ch_data["grid_layout"].get("hero", {})
            labels = hero.get("labels", [])
            
            for label in labels:
                if "m²" in label or "m2" in label:
                    m2_count = label.count("m²") + label.count("m2")
                    self.assertLessEqual(m2_count, 1,
                        f"Chapter {ch_id}, hero label: Duplicate m² in '{label}'")
    
    def test_price_m2_calculation_accuracy(self):
        """Verify that price per m² calculations are correct"""
        # Expected: 500000 / 165 = 3030.30... ≈ 3030
        expected_price_m2 = 500000 // 165  # Integer division
        
        for ch_id, ch_data in self.chapters.items():
            if not ch_data.get("grid_layout"):
                continue
            
            metrics = ch_data["grid_layout"].get("metrics", [])
            for metric in metrics:
                label = metric.get("label", "")
                if "per m²" in label.lower() or "prijs/m²" in label.lower():
                    value = metric.get("value", "")
                    # Extract numeric value
                    digits = re.sub(r'[^\d]', '', value)
                    if digits:
                        actual = int(digits)
                        # Allow 1% margin for rounding
                        margin = max(1, int(expected_price_m2 * 0.01))
                        self.assertAlmostEqual(actual, expected_price_m2, delta=margin,
                            msg=f"Chapter {ch_id}: Price/m² calculation error. Expected ~{expected_price_m2}, got {actual}")
    
    def test_derived_metrics_consistency(self):
        """Check that derived metrics are consistent across chapters"""
        price_m2_values = []
        
        for ch_id, ch_data in self.chapters.items():
            if not ch_data.get("grid_layout"):
                continue
            
            metrics = ch_data["grid_layout"].get("metrics", [])
            for metric in metrics:
                label = metric.get("label", "")
                if "per m²" in label.lower() or "prijs/m²" in label.lower():
                    value = metric.get("value", "")
                    digits = re.sub(r'[^\d]', '', value)
                    if digits:
                        price_m2_values.append((ch_id, int(digits)))
        
        if len(price_m2_values) > 1:
            # All should be the same (or very close)
            first_val = price_m2_values[0][1]
            for ch_id, val in price_m2_values:
                # Allow 1 euro difference for rounding
                self.assertAlmostEqual(val, first_val, delta=1,
                    msg=f"Inconsistent price/m² in chapter {ch_id}: {val} vs {first_val}")


if __name__ == "__main__":
    unittest.main()
