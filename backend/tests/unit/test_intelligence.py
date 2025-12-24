"""
IntelligenceEngine Logic Tests

ARCHITECTURAL UPDATE:
These tests now validate registry-only template behavior. 
The old heuristic-based narrative functions have been removed.
All computed values come from the enrichment layer.

Tests validate:
1. Data parsing helpers (_parse_int)
2. Output structure compliance
3. Registry-only template content

Tests do NOT expect:
- Computed ratios or estimations in fallback mode
- Heuristic-based narrative content
- Values not present in the input context
"""

import unittest
from intelligence import IntelligenceEngine


class TestIntelligenceEngine(unittest.TestCase):
    """Test IntelligenceEngine business logic and data processing"""

    def setUp(self):
        """Ensure tests run in fallback mode for determinism"""
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        """Clean up provider state after tests"""
        IntelligenceEngine.set_provider(None)

    def test_parse_int_helper(self):
        """Test the robust integer parsing logic used across chapters."""
        self.assertEqual(IntelligenceEngine._parse_int("200 m²"), 200)
        self.assertEqual(IntelligenceEngine._parse_int("€ 1.500.000"), 1500000)
        self.assertEqual(IntelligenceEngine._parse_int("1995"), 1995)
        self.assertEqual(IntelligenceEngine._parse_int("invalid"), 0)
        self.assertEqual(IntelligenceEngine._parse_int(None), 0)

    def test_generate_chapter_narrative_structure(self):
        """Ensure generated structure strictly follows the schema required by the Bento Grid."""
        context = {
            'address': 'Kalverstraat 1',
            'asking_price_eur': 500000,
            'living_area_m2': 120,
            'plot_area_m2': 0,
            'build_year': 1990,
            'energy_label': 'B'
        }
        # Test Chapter 1 (General)
        narrative = IntelligenceEngine.generate_chapter_narrative(1, context)
        
        # Required Keys for Frontend Mapping
        self.assertIn('intro', narrative)
        self.assertIn('main_analysis', narrative)
        self.assertIn('interpretation', narrative)
        self.assertIn('conclusion', narrative)
        self.assertIn('strengths', narrative)
        self.assertIn('advice', narrative)
        
        # Check types
        self.assertIsInstance(narrative['intro'], str)
        self.assertIsInstance(narrative['strengths'], list)
        
        # Registry-only templates should have content
        self.assertGreater(len(narrative['intro']), 0)
        self.assertGreater(len(narrative['main_analysis']), 0)

    def test_chapter_4_energy_logic(self):
        """
        Test Chapter 4 (Energy) output structure.
        
        ARCHITECTURAL NOTE: Registry-only templates don't compute energy advice.
        They display the energy label and indicate AI analysis is needed.
        """
        # Case 1: Green Label
        ctx_green = {
            'energy_label': 'A', 
            'build_year': 2022, 
            'address': 'Test'
        }
        nar_green = IntelligenceEngine.generate_chapter_narrative(4, ctx_green)
        
        # Should have proper structure
        self.assertIn('title', nar_green)
        self.assertIn('intro', nar_green)
        self.assertIn('main_analysis', nar_green)
        
        # Registry-only template should reference energy/sustainability topics
        full_text = nar_green.get('intro', '') + nar_green.get('main_analysis', '')
        self.assertTrue(
            'energie' in full_text.lower() or 'duurzaam' in full_text.lower(),
            "Chapter 4 should reference energy topics"
        )

        # Case 2: Bad Label - should still have proper structure
        ctx_red = {'energy_label': 'G', 'build_year': 1930, 'address': 'Test'}
        nar_red = IntelligenceEngine.generate_chapter_narrative(4, ctx_red)
        
        self.assertIn('title', nar_red)
        self.assertIn('main_analysis', nar_red)
        self.assertGreater(len(nar_red['main_analysis']), 0)

    def test_chapter_0_executive_summary(self):
        """
        Test Chapter 0 (Executive Summary) output structure.
        
        ARCHITECTURAL NOTE: Registry-only templates display passed values,
        they don't compute derived metrics like price ratios.
        """
        # Full Data
        ctx_full = {
            'address': 'Test', 
            'asking_price_eur': 500000, 
            'living_area_m2': 100, 
            'energy_label': 'C'
        }
        nar = IntelligenceEngine.generate_chapter_narrative(0, ctx_full)
        
        # Required structure
        self.assertIn('title', nar)
        self.assertIn('intro', nar)
        self.assertIn('main_analysis', nar)
        
        # Title should be "Executive Summary" (from registry template)
        self.assertEqual(nar['title'], "Executive Summary")
        
        # Intro should have content
        self.assertGreater(len(nar['intro']), 0)
        
        # Missing Data - should still work
        ctx_missing = {'address': 'Test'}  # Price/Area missing
        nar_missing = IntelligenceEngine.generate_chapter_narrative(0, ctx_missing)
        
        # Should have valid structure even with missing data
        self.assertIn('title', nar_missing)
        self.assertIn('main_analysis', nar_missing)
        self.assertGreater(len(nar_missing['main_analysis']), 0)

    def test_fallback_uses_registry_templates(self):
        """
        ARCHITECTURAL TEST: Verify fallback uses registry-only templates.
        
        Without AI provider, IntelligenceEngine should use templates that
        only display registry values, never compute new values.
        """
        IntelligenceEngine.set_provider(None)
        
        ctx = {
            'address': 'Teststraat 1',
            'asking_price_eur': 450000,
            'living_area_m2': 120,
            'energy_label': 'B'
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(0, ctx)
        
        # Check provenance indicates registry template
        provenance = result.get('_provenance', {})
        self.assertIn('Registry', provenance.get('provider', ''))
        self.assertEqual(provenance.get('confidence'), 'low')

    def test_all_chapters_have_consistent_structure(self):
        """Verify all 14 chapters return consistent structure."""
        ctx = {
            'address': 'Test',
            'asking_price_eur': 500000,
            'living_area_m2': 120,
            'build_year': 2000,
            'energy_label': 'B'
        }
        
        for chapter_id in range(14):
            result = IntelligenceEngine.generate_chapter_narrative(chapter_id, ctx)
            
            # All should return dict
            self.assertIsInstance(result, dict, f"Chapter {chapter_id} should return dict")
            
            # All should have title and main_analysis
            self.assertIn('title', result, f"Chapter {chapter_id} missing title")
            self.assertIn('main_analysis', result, f"Chapter {chapter_id} missing main_analysis")


if __name__ == '__main__':
    unittest.main()
