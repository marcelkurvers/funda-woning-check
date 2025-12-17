import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest
import re
from main import build_chapters

class TestChapterConsistency(unittest.TestCase):
    def setUp(self):
        # MANDATORY: Load from test-data directory
        from tests.data_loader import load_test_data
        self.core_data = load_test_data()
        self.chapters = build_chapters(self.core_data)

    def extract_metrics(self):
        """Helper to collect all metrics across chapters."""
        all_metrics = []
        for ch_id, ch_data in self.chapters.items():
            layout = ch_data.get("grid_layout", {})
            metrics = layout.get("metrics", [])
            for m in metrics:
                all_metrics.append({
                    "chapter": ch_id,
                    "label": m.get("label"),
                    "value": m.get("value"),
                    "id": m.get("id") # Some might have ID
                })
        return all_metrics

    def test_price_consistency(self):
        """Check if asking price is consistent across all chapters."""
        target_price = self.core_data["asking_price_eur"]
        # Normalize: remove non-digits
        target_val = int(re.sub(r'\D', '', target_price))

        metrics = self.extract_metrics()
        for m in metrics:
            # Check for Price-like labels
            if m["label"] and "vraagprijs" in m["label"].lower() and "m²" not in m["label"].lower():
                # This seems to be the total price
                val_str = m["value"]
                # Skip "TBD" or unknown if permissible, but here we expect data
                if "€" in val_str:
                    val = int(re.sub(r'\D', '', val_str))
                    self.assertEqual(val, target_val, 
                        f"Inconsistent price in Chapter {m['chapter']}: {val_str} vs {target_price}")

    def test_living_area_consistency(self):
        """Check if living area is consistent."""
        target_area = self.core_data["living_area_m2"]
        target_val = int(re.sub(r'\D', '', target_area))
        
        metrics = self.extract_metrics()
        for m in metrics:
            if m["label"] and "woonoppervlakte" in m["label"].lower():
                val_str = m["value"]
                # extract number
                matches = re.findall(r'\d+', val_str)
                if matches:
                    val = int(matches[0])
                    self.assertEqual(val, target_val,
                        f"Inconsistent area in Chapter {m['chapter']}: {val_str} vs {target_area}")

    def test_sqm_price_consistency(self):
        metrics = self.extract_metrics()
        sqm_prices = []

        for m in metrics:
            if m["label"] and "per m²" in m["label"].lower() and "vraagprijs" in m["label"].lower():
                val_str = m["value"]
                # Extract number
                digits = re.sub(r'\D', '', val_str)
                if digits:
                    sqm_prices.append((m["chapter"], int(digits)))

        if not sqm_prices:
            # It's okay if it doesn't appear, but if it does, it must be consistent.
            return

        # Check if all found values are roughly the same (allow small rounding diffs if any)
        first_val = sqm_prices[0][1]
        for ch, val in sqm_prices:
            # Allow deviation of 1 (rounding issues)
            self.assertTrue(abs(val - first_val) <= 1,
                f"Inconsistent calculated SqM price in Chapter {ch}: {val} vs {first_val}")

        # Verify calculation correctness
        price = int(re.sub(r'\D', '', self.core_data["asking_price_eur"]))
        area = int(re.sub(r'\D', '', self.core_data["living_area_m2"]))
        expected = int(price / area)
        
        self.assertTrue(abs(first_val - expected) <= 5,
            f"Calculated SqM price seems wrong: {first_val} (Expected {expected})")
    def test_bedroom_logic(self):
        """Check that bedroom count is logical.
        New behavior: Uses actual parsed 'bedrooms' field if available,
        otherwise estimates from living area (living_area / 25).
        """
        # Check if bedrooms field exists in core data
        if "bedrooms" in self.core_data:
            # Use actual parsed bedrooms
            expected_bedrooms = int(re.sub(r'\D', '', str(self.core_data["bedrooms"])))
        else:
            # Estimate from living area (new logic in chapter_1)
            living_area = int(re.sub(r'\D', '', self.core_data.get("living_area_m2", "0")))
            expected_bedrooms = max(3, int(living_area / 25))
        
        # Extract actual bedrooms from metrics
        metrics = self.extract_metrics()
        bedroom_metric = None
        for m in metrics:
            if m["id"] == "bedrooms" or (m["label"] and "slaapkamers" in m["label"].lower()):
                bedroom_metric = m
                break
        
        self.assertIsNotNone(bedroom_metric, "Bedroom metric not found in any chapter metrics.")
        actual_bedrooms = int(re.sub(r"\D", "", bedroom_metric["value"]))
        
        self.assertEqual(actual_bedrooms, expected_bedrooms,
                         f"Inconsistent bedroom count: expected {expected_bedrooms}, got {actual_bedrooms}")
        
        # Upper bound sanity check (using new MAX_BEDROOMS threshold)
        self.assertLessEqual(actual_bedrooms, 15, "Bedroom count unusually high, check data source.")


    def test_energy_label_consistency(self):
        """Check Energy Label consistency."""
        target_label = self.core_data["energy_label"]
        metrics = self.extract_metrics()
        
        found = False
        for m in metrics:
            if m["id"] == "energy_label" or (m["label"] and "energielabel" in m["label"].lower()):
                found = True
                self.assertIn(target_label, m["value"], 
                    f"Inconsistent Energy Label in Chapter {m['chapter']}: {m['value']}")
        
        if not found:
            print("Warning: Energy Label not found in any metrics.")

    def test_content_text_consistency(self):
        """
        Check if values mentioned in the text content (e.g. '€ 7500') 
        match the computed metrics.
        """
        metrics = self.extract_metrics()
        # Find price_m2 metric
        price_m2_val = None
        for m in metrics:
             if m["id"] == "price_m2":
                 # value is usually like "€ 7.500"
                 price_m2_val = int(re.sub(r'\D', '', m["value"]))
                 break
        
        if price_m2_val:
            # Check Chapter 0 content
            ch0 = self.chapters.get("0")
            if ch0:
                content = ch0["grid_layout"]["main"]["content"]
                # Look for the price in the text. 
                # Content has "vierkantemeterprijs van € {price_m2}"
                # We specifically look for the number.
                if str(price_m2_val) not in content and f"{price_m2_val:,}" not in content:
                     # try with dot separator
                     val_dot = f"{price_m2_val:,}".replace(",", ".")
                     self.assertIn(val_dot, content, 
                        f"Price per m2 ({val_dot}) not found in Chapter 0 text content.")



if __name__ == "__main__":
    unittest.main()
