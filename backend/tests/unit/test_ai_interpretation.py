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
        
        # Check Interpretation
        self.assertIn('voldoet aan', narrative['interpretation'], "Should interpret as compliant")
        self.assertIn('raadzaam', narrative['interpretation'], "Should suggest plan is advisable, not necessary")
        
        # Check Strengths
        strengths = str(narrative['strengths'])
        self.assertIn('Energielabel A', strengths, "Should highlight Label A as strength")
        
        # Check Advice
        advice = narrative['advice']
        self.assertNotIn('na-isolatie', advice, "Should NOT suggest isolation for Label A")

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
        self.assertIn('fundering', narrative_ch3['main_analysis'], "Should mention foundation risks for 1930s")
        self.assertIn('asbest', narrative_ch3['advice'], "Should warn about asbestos")
        
        # Chapter 4: Energy
        narrative_ch4 = IntelligenceEngine.generate_chapter_narrative(4, ctx)
        self.assertIn('noodzakelijk', narrative_ch4['interpretation'], "Energy plan should be necessary")
        self.assertIn('na-isolatie', narrative_ch4['advice'], "Should suggest isolation")

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
        
        # Check Interpretation
        self.assertIn('luxe gezinswoning', narrative['interpretation'])
        self.assertIn('zeer ruim bemeten', narrative['interpretation'])
        
        # Check Strengths
        strengths = str(narrative['strengths'])
        self.assertIn('Royaal woonoppervlak', strengths)
        self.assertIn('Groot perceel', strengths)

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
