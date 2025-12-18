import sys
import os
import unittest

# Adjust path to include backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from intelligence import IntelligenceEngine

class TestPreferentiesVergelijking(unittest.TestCase):
    """
    Test scenario specifiek voor de vergelijking van Marcel & Petra preferenties.
    """

    def test_vergelijking_logica(self):
        ctx = {
            'description': 'Ruime woning met een moderne keuken en een grote tuin.',
            'features': ['Zonnepanelen', 'Lichte woonkamer', 'Garage'],
            '_preferences': {
                'marcel': {
                    'priorities': ['Garage', 'Zonnepanelen'], # 2 matches
                    'hidden_priorities': ['Moderne Groepenkast'] # 0 matches
                },
                'petra': {
                    'priorities': ['Grote tuin', 'Sfeer'], # 1 match, 1 miss
                    'hidden_priorities': ['Veilige Buurt'] # 0 matches
                }
            }
        }
        
        # Chapter 2 is de matchanalyse
        result = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        # Check of beide namen voorkomen in de analyse of interpretatie
        combined_text = result['intro'] + result['main_analysis'] + result['interpretation']
        
        self.assertIn("Marcel", combined_text, "Marcel moet worden genoemd in de vergelijking")
        self.assertIn("Petra", combined_text, "Petra moet worden genoemd in de vergelijking")
        
        # Check of scores worden berekend (bijv. een percentage teken)
        self.assertIn("%", result['intro'], "Er moet een match-percentage aanwezig zijn")
        
        # Check of specifieke items worden gevonden
        self.assertIn("Zonnepanelen", result['main_analysis'])
        self.assertIn("Garage", result['main_analysis'])
        
        print(f"Test geslaagd: Marcel & Petra vergelijking gedetecteerd in {result['title']}")

if __name__ == '__main__':
    unittest.main()
