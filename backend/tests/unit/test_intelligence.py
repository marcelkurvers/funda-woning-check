import unittest
from intelligence import IntelligenceEngine

class TestIntelligenceEngine(unittest.TestCase):
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
            'adres': 'Kalverstraat 1',
            'prijs': '€ 500.000',
            'oppervlakte': '120 m²',
            'perceel': '0 m²',
            'bouwjaar': '1990',
            'label': 'B'
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
        
        # Check basic logic application
        self.assertIn("Kalverstraat", narrative['intro']) 
        self.assertIsInstance(narrative['strengths'], list)

    def test_chapter_4_energy_logic(self):
        """Test specific business logic for Energy Chapter."""
        # Case 1: Green Label
        ctx_green = {'label': 'A', 'bouwjaar': '2022', 'adres': 'Test'}
        nar_green = IntelligenceEngine.generate_chapter_narrative(4, ctx_green)
        self.assertIn("A", nar_green['intro'])
        self.assertTrue(any("Gasloos" in s for s in nar_green.get('strengths', [])))

        # Case 2: Bad Label
        ctx_red = {'label': 'G', 'bouwjaar': '1930', 'adres': 'Test'}
        nar_red = IntelligenceEngine.generate_chapter_narrative(4, ctx_red)
        self.assertIn("investering", nar_red['intro'].lower())

    def test_chapter_0_executive_summary(self):
        """Test the executive summary generation including missing data checks."""
        # Full Data
        ctx_full = {'adres': 'Test', 'prijs': 500000, 'oppervlakte': 100, 'label': 'C'}
        nar = IntelligenceEngine.generate_chapter_narrative(0, ctx_full)
        print(f"DEBUG INTRO: {nar['intro']}")
        
        # In current version, Chapter 0 title is set in the dictate
        self.assertEqual(nar['title'], "Executive Summary & Strategie")
        self.assertIn("Analyse van Test", nar['intro'])
        self.assertIn("100 m²", nar['intro'])
        
        # Missing Data
        ctx_missing = {'adres': 'Test'} # Price/Area missing
        nar_missing = IntelligenceEngine.generate_chapter_narrative(0, ctx_missing)
        # Should warn about missing KPIs or provide generic text
        self.assertTrue(len(nar_missing['main_analysis']) > 0)

if __name__ == '__main__':
    unittest.main()
