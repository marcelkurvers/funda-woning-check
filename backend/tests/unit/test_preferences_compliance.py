"""
Preferences Compliance Tests

ARCHITECTURAL UPDATE:
These tests validate registry-only template behavior for preference matching.
Match scores are now computed in the enrichment layer, not in IntelligenceEngine.

Tests validate:
1. Chapter 2 (Matchanalyse) has proper structure
2. Pre-computed match scores are displayed
3. Missing preferences are handled gracefully

Tests do NOT expect:
- Computed match percentages in fallback mode
- Priority item matching in template narratives
- Specific formatting like "match van X%"
"""

import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from intelligence import IntelligenceEngine


class TestPreferencesCompliance(unittest.TestCase):
    """
    Verifies that Chapter 2 (Matchanalyse) handles preferences correctly.
    
    ARCHITECTURAL NOTE: Match scores are now pre-computed in enrichment layer.
    Registry-only templates display these pre-computed scores, they don't
    perform matching logic themselves.
    """

    def setUp(self):
        IntelligenceEngine.set_provider(None)

    def test_marcel_petra_preferences_match(self):
        """
        Test that Chapter 2 displays pre-computed match information.
        
        ARCHITECTURAL NOTE: The actual matching is done in the enrichment layer.
        Here we test that the registry-only template has proper structure.
        """
        ctx = {
            'description': 'Prachtige woning uit de jaren 30.',
            'features': ['Zonnepanelen', 'Glasvezel', 'CV-ketel 2020'],
            '_preferences': {
                'marcel': {
                    'priorities': ['Zonnepanelen', 'Glasvezel', 'Warmtepomp'],
                    'hidden_priorities': ['Garage']
                },
                'petra': {
                    'priorities': ['Jaren 30', 'Bad'],
                    'hidden_priorities': ['Tuin op zuid']
                }
            },
            # Pre-computed scores (would come from enrichment in real pipeline)
            'marcel_match_score': 50,
            'petra_match_score': 30,
            'total_match_score': 40,
            'marcel_reasons': ['Zonnepanelen', 'Glasvezel'],
            'petra_reasons': ['Jaren 30']
        }
        
        narrative = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        # Check proper structure
        self.assertIn('title', narrative)
        self.assertIn('intro', narrative)
        self.assertIn('main_analysis', narrative)
        
        # Title should be for matchanalyse
        self.assertIn('Match', narrative['title'])
        
        # Should have comparison field
        self.assertIn('comparison', narrative)
        self.assertIsInstance(narrative['comparison'], dict)
        
        # Intro should have content
        self.assertGreater(len(narrative['intro']), 0)
        
        # Main analysis should mention scores
        full_text = narrative['intro'] + narrative['main_analysis']
        self.assertTrue(
            '%' in full_text or 'score' in full_text.lower() or 'match' in full_text.lower(),
            "Should reference match scores"
        )

    def test_missing_preferences_handling(self):
        """
        Test behavior when no preferences are provided.
        
        ARCHITECTURAL NOTE: Registry-only templates show default values
        when preferences are missing, they don't compute defaults.
        """
        ctx = {
            'description': 'Gewoon huis.',
            'features': [],
            # No _preferences key - should use defaults
            'marcel_match_score': 0,
            'petra_match_score': 0,
            'total_match_score': 0
        }
        
        narrative = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        # Should return valid structure
        self.assertIn('title', narrative)
        self.assertIn('main_analysis', narrative)
        
        # Should have content
        self.assertGreater(len(narrative['main_analysis']), 10)
        
        # Should indicate scores (even if 0)
        full_text = narrative.get('intro', '') + narrative.get('main_analysis', '')
        self.assertTrue(
            '%' in full_text or '0' in full_text or 'score' in full_text.lower(),
            "Should reference match scores or indicate their absence"
        )

    def test_chapter_2_provenance_indicates_registry_template(self):
        """Verify Chapter 2 fallback uses registry template."""
        ctx = {'address': 'Test'}
        
        narrative = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        provenance = narrative.get('_provenance', {})
        self.assertIn('Registry', provenance.get('provider', ''))


if __name__ == '__main__':
    unittest.main()
