"""
Explore Insights Tests - Using Correct Pipeline API

Generates chapters and captures insights for analysis.
All tests use execute_report_pipeline() - the ONLY valid path.
"""
import sys
import os

# Set test mode BEFORE imports
os.environ["PIPELINE_TEST_MODE"] = "true"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
import json

from backend.pipeline.bridge import execute_report_pipeline


class TestExploreInsights(unittest.TestCase):
    def test_capture_chapter_insights(self):
        """
        Generates chapters with rich mock data and captures the resulting
        structure to identify new insights/data points available for display.
        """
        # Rich Mock Data
        core_data = {
            "address": "Inzichtslaan 42, Toekomststad",
            "asking_price_eur": 750000,
            "living_area_m2": 145,
            "plot_area_m2": 400,
            "build_year": 2015,
            "energy_label": "A++",
            "description": "Een prachtige woning met veel lichtinval en uitbouwmogelijkheden.",
            "rooms": 5,
            "bedrooms": 4,
        }

        print(f"\n[INFO] Generating chapters for mock property: {core_data['address']}...")
        
        chapters, kpis, enriched = execute_report_pipeline(
            run_id="test-explore-insights",
            raw_data=core_data,
            preferences={}
        )
        
        insights_report = {}

        # Iterate and Inspect
        for cid, content in chapters.items():
            chapter_title = content.get("title", f"Chapter {cid}")
            print(f"\n--- Analysing Chapter {cid}: {chapter_title} ---")
            
            layout = content.get("grid_layout", {})
            metrics = layout.get("metrics", [])
            
            # Capture Metrics
            for m in metrics:
                print(f"  [Metric] {m.get('label', 'No Label')}: {m.get('value')} (ID: {m.get('id')})")
            
            insights_report[cid] = {
                "title": chapter_title,
                "metrics_count": len(metrics),
            }

        print(f"\n[SUCCESS] Insights captured")
        
        # Basic Assertions
        self.assertEqual(len(chapters), 14, "Should generate 14 chapters")
        self.assertIn("0", chapters, "Executive Summary (Ch 0) must be present")


if __name__ == "__main__":
    unittest.main()
