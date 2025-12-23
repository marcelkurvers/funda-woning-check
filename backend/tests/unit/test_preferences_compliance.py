import sys
import os
import unittest

# Adjust path to include backend (parent of 'tests')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from intelligence import IntelligenceEngine

class TestPreferencesCompliance(unittest.TestCase):
    """
    Verifies that the AI correctly interprets and scores user preferences 
    (Marcel and Petra) against property data.
    """

    def setUp(self):
        # Ensure no residual client is attached
        IntelligenceEngine.set_provider(None)

    def test_marcel_petra_preferences_match(self):
        """
        Test that specific preferences for Marcel (Tech) and Petra (Atmosphere) are check
        and a percentage match is calculated.
        """
        # 1. Setup Context with Property Data
        # Property has: Solar panels (Marcel match), 1930s style (Petra match)
        ctx = {
            'description': 'Prachtige woning uit de jaren 30 (bouwjaar 1935) met authentieke details.',
            'features': ['Zonnepanelen', 'Glasvezel', 'CV-ketel 2020'],
            '_preferences': {
                'marcel': {
                    'priorities': ['Zonnepanelen', 'Glasvezel', 'Warmtepomp'], # 2 matches, 1 miss
                    'hidden_priorities': ['Garage'] # 1 miss
                },
                'petra': {
                    'priorities': ['Jaren 30', 'Bad'], # 1 match, 1 miss
                    'hidden_priorities': ['Tuin op zuid'] # 1 miss
                }
            }
        }
        
        # Total priorities: 3 + 1 + 2 + 1 = 7
        # Total matches: 2 (Solar, Fiber) + 1 (Years 30) = 3
        # Expected score: 3/7 * 100 = ~42%
        
        # 2. Generate Chapter 2 Narrative
        narrative = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        # 3. Assertions
        
        # Check title
        self.assertEqual(narrative['title'], "Matchanalyse M&P")
        
        # Check Percentage in Intro
        # "scoort deze woning een match van 42%."
        self.assertRegex(narrative['intro'], r"match van \d+%", "Percentage should be reported in intro")
        
        # Check specific analysis for Marcel
        self.assertIn("Zonnepanelen", narrative['main_analysis'])
        self.assertIn("Glasvezel", narrative['main_analysis'])
        
        # Check specific analysis for Petra
        self.assertIn("Jaren 30", narrative['main_analysis'])
        
        print(f"\nGenerated Intro: {narrative['intro']}")
        print(f"Computed Score Content: {narrative['conclusion']}")

    def test_missing_preferences_handling(self):
        """Test behavior when no preferences are provided."""
        ctx = {
            'description': 'Gewoon huis.',
            'features': [],
            # No _preferences key or empty
        }
        
        narrative = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        # Should default to 50% or handle gracefully
        self.assertIn("50%", narrative['intro']) 
        self.assertIn("Geen specifieke", narrative['main_analysis'])

if __name__ == '__main__':
    unittest.main()
