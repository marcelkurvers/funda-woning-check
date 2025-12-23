import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
import sys
import os

# Adjust path to include backend (parent of 'tests')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from intelligence import IntelligenceEngine

class TestAiInterpretation(unittest.TestCase):
    """
    Verifies that the AI narrative generation is DYNAMIC and not hardcoded.
    It checks if different input contexts produce different advice, strengths, and interpretations.
    """
    
    def setUp(self):
        """Ensure clean state before each test - no AI provider set"""
        IntelligenceEngine.set_provider(None)
    
    def tearDown(self):
        """Clean up after each test"""
        IntelligenceEngine.set_provider(None)

    def test_scenario_modern_eco_house(self):
        """Test a modern, energy-efficient house."""
        ctx = {
            'prijs': '500000',
            'oppervlakte': '120',
            'perceel': '200',
            'bouwjaar': '2020',
            'label': 'A',
            'adres': 'Nieuwbouwlaan 12'
        }
        
        narrative = IntelligenceEngine.generate_chapter_narrative(4, ctx) # Sustainability Chapter
        
        # Check Interpretation (Positive) - more flexible
        interpretation_lower = narrative['interpretation'].lower()
        self.assertTrue(
            'waarde' in interpretation_lower or 'premium' in interpretation_lower or 'comfort' in interpretation_lower,
            "Should interpret modern A-label house positively"
        )
        # Check Interpretation (Negative - Verification of Logic)
        intro_lower = narrative['intro'].lower()
        self.assertFalse(
            'investering' in intro_lower and 'nodig' in intro_lower,
            "Should NOT describe A-label house as needing investment"
        )
        
        # Check Strengths - more flexible
        strengths_str = str(narrative['strengths']).lower()
        self.assertTrue(
            'label' in strengths_str and 'a' in strengths_str,
            "Should highlight good energy label as strength"
        )
        
        # Check Advice - should not suggest major isolation work
        advice_str = str(narrative['advice']).lower()
        self.assertFalse(
            'spouwmuur' in advice_str and 'isolatie' in advice_str,
            "Should NOT suggest major insulation for Label A"
        )

    def test_scenario_old_fixer_upper(self):
        """Test an old house with poor energy label."""
        ctx = {
            'prijs': '350000',
            'oppervlakte': '100',
            'perceel': '150',
            'bouwjaar': '1910',
            'label': 'G',
            'adres': 'Oude Dorpsstraat 1'
        }
        
        # Chapter 3: Construction
        narrative_ch3 = IntelligenceEngine.generate_chapter_narrative(3, ctx)
        # More flexible check - look for foundation-related keywords
        main_analysis_lower = narrative_ch3['main_analysis'].lower()
        self.assertTrue(
            'fundering' in main_analysis_lower or 'foundation' in main_analysis_lower or 'hout' in main_analysis_lower,
            "Should mention foundation or construction risks for old houses"
        )
        
        # Check advice contains asbestos warning (more flexible)
        advice_str = str(narrative_ch3['advice']).lower()
        self.assertTrue(
            'asbest' in advice_str or 'asbestos' in advice_str or '1980' in advice_str,
            "Should warn about asbestos or old building materials"
        )
        
        # Chapter 4: Energy
        narrative_ch4 = IntelligenceEngine.generate_chapter_narrative(4, ctx)
        
        # More flexible interpretation check
        interpretation_lower = narrative_ch4['interpretation'].lower()
        self.assertTrue(
            'kans' in interpretation_lower or 'potentie' in interpretation_lower or 'investering' in interpretation_lower,
            "Energy plan should mention opportunity or investment potential"
        )
        
        # Check for isolation advice (more flexible)
        advice_str_ch4 = str(narrative_ch4['advice']).lower()
        self.assertTrue(
            'isolatie' in advice_str_ch4 or 'spouw' in advice_str_ch4 or 'glas' in advice_str_ch4,
            "Should suggest some form of insulation improvement"
        )
        
        # Negative Checks (Cross-Verification)
        self.assertNotIn('waarde-vermeerderaar', narrative_ch4['interpretation'], "Old G-label should NOT be a value adder yet")
        self.assertNotIn('Gasloos', str(narrative_ch4['strengths']), "Old house should not be gasless")

    def test_all_chapters_generation(self):
        """
        Parametric test to ensure ALL chapters (1-12) generate a valid narrative structure
        without crashing, given a standard dataset.
        """
        # Complete mock data
        ctx = {
            "adres": "Teststraat 1",
            "prijs": "€ 500.000",
            "oppervlakte": "120",
            "perceel": "200",
            "bouwjaar": "1990",
            "label": "B"
        }
        
        required_keys = ["title", "intro", "main_analysis", "conclusion"]
        
        for i in range(1, 13):
            with self.subTest(chapter=i):
                print(f"Testing capture logic for Chapter {i}")
                output = IntelligenceEngine.generate_chapter_narrative(i, ctx)
                
                # Check basic keys
                for key in required_keys:
                    self.assertIn(key, output, f"Chapter {i} missing key: {key}")
                    self.assertTrue(output[key], f"Chapter {i} has empty {key}")
                
                # Check specifics
                if i == 1:
                    self.assertIn("120 m²", output["intro"])
                if i == 4:
                    self.assertIn("B", output["intro"]) # Energy label check

    def test_scenario_luxury_villa(self):
        """Test a large luxury villa."""
        ctx = {
            'prijs': '1500000',
            'oppervlakte': '300',
            'perceel': '2000',
            'bouwjaar': '1995',
            'label': 'B',
            'adres': 'Villapark 1'
        }
        
        # Chapter 1: General Features
        narrative = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # Check Interpretation - more flexible
        interpretation_lower = narrative['interpretation'].lower()
        self.assertTrue(
            'levensstijl' in interpretation_lower or 'luxe' in interpretation_lower or 'lifestyle' in interpretation_lower,
            "Should mention lifestyle for luxury villa"
        )
        self.assertTrue(
            '300' in narrative['interpretation'] or 'royaal' in interpretation_lower or 'ruim' in interpretation_lower,
            "Should mention large size"
        )
        
        # Check Strengths - more flexible
        strengths_str = str(narrative['strengths']).lower()
        self.assertTrue(
            ('royaal' in strengths_str or 'ruim' in strengths_str) and ('wonen' in strengths_str or 'oppervlak' in strengths_str),
            "Should highlight spacious living"
        )
        self.assertTrue(
            'vrijheid' in strengths_str or 'privacy' in strengths_str or 'tuin' in strengths_str,
            "Should highlight privacy/outdoor space"
        )

    def test_html_structure_consistency(self):
        """Verify that the required HTML keys are present in all chapters."""
        ctx = {'adres': 'Test', 'bouwjaar': '2000'}
        
        # Check a sample of chapters
        for ch_id in [1, 2, 3, 12]:
            narrative = IntelligenceEngine.generate_chapter_narrative(ch_id, ctx)
            self.assertIn('interpretation', narrative, f"Chapter {ch_id} missing interpretation")
            self.assertIn('advice', narrative, f"Chapter {ch_id} missing advice")
            self.assertIn('strengths', narrative, f"Chapter {ch_id} missing strengths")
            self.assertIn('conclusion', narrative)

if __name__ == '__main__':
    unittest.main()
