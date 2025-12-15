import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import sys
import os
import unittest
import json

# Add backend root to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import build_chapters

class TestExploreInsights(unittest.TestCase):
    def test_capture_chapter_insights(self):
        """
        Generates chapters with rich mock data and captures the resulting
        structure to identify new insights/data points available for display.
        """
        # 1. Rich Mock Data simulating a comprehensive property
        core_data = {
            "address": "Inzichtslaan 42, Toekomststad",
            "asking_price_eur": "€ 750.000",
            "living_area_m2": "145 m²",
            "plot_area_m2": "400 m²",
            "build_year": "2015",
            "energy_label": "A++",
            "description": "Een prachtige woning met veel lichtinval en uitbouwmogelijkheden. Zonnepanelen, warmtepomp, en een ruime tuin op het zuiden. Gelegen in een kindvriendelijke buurt.",
            # Add more specific fields that might trigger specialized logic if the chapters use them
            "insulation": ["Dakisolatie", "Muurisolatie", "Vloerisolatie", "Dubbel glas"],
            "heating": "Warmtepomp",
            "type": "Vrijstaande woning",
            "rooms": "5",
            "bedrooms": "4",
            "bathrooms": "2",
            "garden_orientation": "Zuid",
            "backyard_surface": "200 m²",
            "garage": "Aangebouwd steen"
        }

        print(f"\n[INFO] Generating chapters for mock property: {core_data['address']}...")
        chapters = build_chapters(core_data)
        
        insights_report = {}

        # 2. Iterate and Inspect
        for cid, content in chapters.items():
            chapter_title = content.get("title", f"Chapter {cid}")
            print(f"\n--- Analysing Chapter {cid}: {chapter_title} ---")
            
            layout = content.get("grid_layout", {})
            metrics = layout.get("metrics", [])
            sidebar = layout.get("sidebar", [])
            main = layout.get("main", {}).get("content", [])
            
            # Capture Metrics
            captured_metrics = []
            for m in metrics:
                # Capture everything in the metric to see potential new fields
                captured_metrics.append(m)
                print(f"  [Metric] {m.get('label', 'No Label')}: {m.get('value')} (ID: {m.get('id')})")
                
            # Capture Sidebar Items
            captured_sidebar = []
            for s in sidebar:
                captured_sidebar.append(s)
                print(f"  [Sidebar] Type: {s.get('type')} - {s.get('title', 'No Title')}")

            # Capture Main Content specifics (if structured)
            captured_main = []
            for m_item in main:
                # Assuming main content might be blocks or text
                 captured_main.append(m_item)
            
            insights_report[cid] = {
                "title": chapter_title,
                "metrics_count": len(metrics),
                "metrics_data": captured_metrics,
                "sidebar_count": len(sidebar),
                "sidebar_data": captured_sidebar,
                "main_data_summary": f"{len(main)} content blocks" 
            }

        # 3. Save to artifact (Use absolute path to ensure we can find it)
        output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/test_chapter_insights.json"))
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(insights_report, f, indent=2, ensure_ascii=False)
            
        print(f"\n[SUCCESS] Insights captured in {output_file}")
        
        # 4. Basic Assertions to ensure the test itself 'passes'
        self.assertTrue(len(chapters) > 0, "Should generate at least one chapter")
        self.assertIn("0", chapters, "Executive Summary (Ch 0) must be present")

if __name__ == "__main__":
    unittest.main()
