"""
Chapter Consistency Tests - Using Correct Pipeline API

Tests that verify data consistency across chapters.
All tests use execute_report_pipeline() - the ONLY valid path.
"""
import sys
import os

# Set test mode BEFORE imports
os.environ["PIPELINE_TEST_MODE"] = "true"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest
import re

from backend.pipeline.bridge import execute_report_pipeline
from tests.data_loader import load_test_data


class TestChapterConsistency(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.core_data = load_test_data()
        cls.chapters, cls.kpis, cls.enriched = execute_report_pipeline(
            run_id="test-consistency",
            raw_data=cls.core_data,
            preferences={}
        )

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
                    "id": m.get("id")
                })
        return all_metrics

    def test_all_chapters_generated(self):
        """Check all 14 chapters are generated."""
        self.assertEqual(len(self.chapters), 14)
        for i in range(14):
            self.assertIn(str(i), self.chapters)

    def test_enriched_core_has_prices(self):
        """Check enriched core has price data."""
        self.assertIn("asking_price_eur", self.enriched)

    def test_enriched_core_has_areas(self):
        """Check enriched core has area data."""
        self.assertIn("living_area_m2", self.enriched)

    def test_kpis_have_completeness(self):
        """Check KPIs include completeness metric."""
        self.assertIn("completeness", self.kpis)

    def test_energy_label_in_enriched(self):
        """Check energy label is in enriched core."""
        self.assertIn("energy_label", self.enriched)


if __name__ == "__main__":
    unittest.main()
