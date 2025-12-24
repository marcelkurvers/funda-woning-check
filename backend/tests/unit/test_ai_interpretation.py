"""
AI Interpretation Tests

ARCHITECTURAL UPDATE:
These tests validate output structure, not heuristic-based content.
The old narrative functions with computed interpretations have been removed.
Registry-only templates display values without computing interpretations.

Tests validate:
1. All chapters return valid structure
2. Required fields are present
3. Content is not empty

Tests do NOT expect:
- Heuristic-based interpretations (e.g., "lifestyle" for luxury, "foundation risks" for old)
- Computed strengths/advice based on property characteristics
- These require AI generation
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
from intelligence import IntelligenceEngine


class TestAiInterpretation(unittest.TestCase):
    """
    Verifies that narratives have valid structure.
    
    ARCHITECTURAL NOTE: Registry-only templates don't compute interpretations.
    Rich, contextual interpretations require AI generation.
    """
    
    def setUp(self):
        """Ensure clean state - no AI provider"""
        IntelligenceEngine.set_provider(None)
    
    def tearDown(self):
        """Clean up"""
        IntelligenceEngine.set_provider(None)

    def test_scenario_modern_eco_house(self):
        """
        Test modern eco-house produces valid output structure.
        """
        ctx = {
            'asking_price_eur': 500000,
            'living_area_m2': 120,
            'plot_area_m2': 200,
            'build_year': 2020,
            'energy_label': 'A',
            'address': 'Nieuwbouwlaan 12'
        }
        
        narrative = IntelligenceEngine.generate_chapter_narrative(4, ctx)
        
        # Should have valid structure
        self.assertIn('title', narrative)
        self.assertIn('intro', narrative)
        self.assertIn('main_analysis', narrative)
        self.assertIn('interpretation', narrative)
        
        # Content should not be empty
        self.assertGreater(len(narrative['intro']), 0)
        self.assertGreater(len(narrative['main_analysis']), 0)

    def test_scenario_old_fixer_upper(self):
        """
        Test old house produces valid output structure.
        """
        ctx = {
            'asking_price_eur': 350000,
            'living_area_m2': 100,
            'plot_area_m2': 150,
            'build_year': 1910,
            'energy_label': 'G',
            'address': 'Oude Dorpsstraat 1'
        }
        
        # Chapter 3: Construction
        narrative_ch3 = IntelligenceEngine.generate_chapter_narrative(3, ctx)
        
        self.assertIn('title', narrative_ch3)
        self.assertIn('main_analysis', narrative_ch3)
        self.assertGreater(len(narrative_ch3['main_analysis']), 0)
        
        # Chapter 4: Energy
        narrative_ch4 = IntelligenceEngine.generate_chapter_narrative(4, ctx)
        
        self.assertIn('title', narrative_ch4)
        self.assertIn('intro', narrative_ch4)
        self.assertGreater(len(narrative_ch4['intro']), 0)

    def test_all_chapters_generation(self):
        """
        Verify ALL chapters (0-13) generate valid structure.
        """
        ctx = {
            "address": "Teststraat 1",
            "asking_price_eur": 500000,
            "living_area_m2": 120,
            "plot_area_m2": 200,
            "build_year": 1990,
            "energy_label": "B"
        }
        
        required_keys = ["title", "intro", "main_analysis", "conclusion"]
        
        for i in range(14):
            with self.subTest(chapter=i):
                output = IntelligenceEngine.generate_chapter_narrative(i, ctx)
                
                # Check basic keys exist
                for key in required_keys:
                    self.assertIn(key, output, f"Chapter {i} missing key: {key}")
                
                # Content should not be empty
                self.assertGreater(len(output['title']), 0, f"Chapter {i} empty title")
                self.assertGreater(len(output['main_analysis']), 0, f"Chapter {i} empty main_analysis")

    def test_scenario_luxury_villa(self):
        """
        Test luxury villa produces valid output structure.
        """
        ctx = {
            'asking_price_eur': 1500000,
            'living_area_m2': 300,
            'plot_area_m2': 2000,
            'build_year': 1995,
            'energy_label': 'B',
            'address': 'Villapark 1'
        }
        
        narrative = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # Should have valid structure
        self.assertIn('title', narrative)
        self.assertIn('intro', narrative)
        self.assertIn('main_analysis', narrative)
        self.assertIn('interpretation', narrative)
        
        # Lists should be present (may be empty in registry-only mode)
        self.assertIn('strengths', narrative)
        self.assertIn('advice', narrative)
        self.assertIsInstance(narrative['strengths'], list)
        self.assertIsInstance(narrative['advice'], list)

    def test_html_structure_consistency(self):
        """Verify that required fields are present in all chapters."""
        ctx = {'address': 'Test', 'build_year': 2000}
        
        for ch_id in [1, 2, 3, 12]:
            narrative = IntelligenceEngine.generate_chapter_narrative(ch_id, ctx)
            
            self.assertIn('interpretation', narrative, f"Chapter {ch_id} missing interpretation")
            self.assertIn('advice', narrative, f"Chapter {ch_id} missing advice")
            self.assertIn('strengths', narrative, f"Chapter {ch_id} missing strengths")
            self.assertIn('conclusion', narrative, f"Chapter {ch_id} missing conclusion")

    def test_registry_template_provenance(self):
        """Verify registry-only templates have correct provenance."""
        ctx = {'address': 'Test'}
        
        for ch_id in [0, 1, 2, 4]:
            narrative = IntelligenceEngine.generate_chapter_narrative(ch_id, ctx)
            
            provenance = narrative.get('_provenance', {})
            self.assertIn('Registry', provenance.get('provider', ''),
                         f"Chapter {ch_id} should use registry template")
            self.assertEqual(provenance.get('confidence'), 'low',
                           f"Chapter {ch_id} registry template should have low confidence")


if __name__ == '__main__':
    unittest.main()
