"""
Preferenties Vergelijking Tests

ARCHITECTURAL UPDATE:
These tests validate registry-only template behavior for matching.
Match scores and reasons are now pre-computed in the enrichment layer.

Tests validate:
1. Chapter 2 has proper structure with comparison fields
2. Marcel and Petra are mentioned in output
3. Percentage indicators are present

Tests do NOT expect:
- Real-time matching logic in fallback mode
- Specific priority items in template narratives (requires AI)
"""

import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from intelligence import IntelligenceEngine


class TestPreferentiesVergelijking(unittest.TestCase):
    """
    Test scenario specifiek voor de vergelijking van Marcel & Petra preferenties.
    
    ARCHITECTURAL NOTE: In registry-only mode, the template displays
    pre-computed scores. The actual matching logic is in the enrichment layer.
    """

    def setUp(self):
        IntelligenceEngine.set_provider(None)

    def test_vergelijking_logica(self):
        """
        Test Chapter 2 (Matchanalyse) structure and content.
        
        ARCHITECTURAL NOTE: Pre-computed scores are provided in context.
        Template displays these, it doesn't compute matches.
        """
        ctx = {
            'description': 'Ruime woning met een moderne keuken en een grote tuin.',
            'features': ['Zonnepanelen', 'Lichte woonkamer', 'Garage'],
            '_preferences': {
                'marcel': {
                    'priorities': ['Garage', 'Zonnepanelen'],
                    'hidden_priorities': ['Moderne Groepenkast']
                },
                'petra': {
                    'priorities': ['Grote tuin', 'Sfeer'],
                    'hidden_priorities': ['Veilige Buurt']
                }
            },
            # Pre-computed in enrichment layer
            'marcel_match_score': 66,
            'petra_match_score': 25,
            'total_match_score': 45,
            'marcel_reasons': ['Garage', 'Zonnepanelen'],
            'petra_reasons': ['Sfeer']
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        # Check structure
        self.assertIn('title', result)
        self.assertIn('intro', result)
        self.assertIn('main_analysis', result)
        self.assertIn('comparison', result)
        
        # Check that comparison has marcel and petra keys
        comparison = result.get('comparison', {})
        self.assertIn('marcel', comparison)
        self.assertIn('petra', comparison)
        
        # Check that names appear in combined text
        combined_text = (
            result.get('intro', '') + 
            result.get('main_analysis', '') + 
            str(comparison)
        )
        
        self.assertIn("Marcel", combined_text, "Marcel moet worden genoemd")
        self.assertIn("Petra", combined_text, "Petra moet worden genoemd")
        
        # Check for percentage in intro or main analysis
        full_text = result.get('intro', '') + result.get('main_analysis', '')
        self.assertIn("%", full_text, "Er moet een percentage aanwezig zijn")

    def test_chapter_2_returns_valid_structure(self):
        """Verify Chapter 2 always returns valid structure."""
        ctx = {'address': 'Minimal test'}
        
        result = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        # Required fields
        self.assertIn('title', result)
        self.assertIn('intro', result)
        self.assertIn('main_analysis', result)
        self.assertIn('comparison', result)
        
        # Types
        self.assertIsInstance(result['title'], str)
        self.assertIsInstance(result['comparison'], dict)


if __name__ == '__main__':
    unittest.main()
