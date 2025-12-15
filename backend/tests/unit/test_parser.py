import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest
from parser import Parser

SAMPLE_HTML = """
<html>
<body>
    <div class="object-header__price">€ 450.000 k.k.</div>
    <h1 class="object-header__title">Straatnaam 123, 1234 AB Stad</h1>
    
    <dt>Woonoppervlakte</dt>
    <dd>120 m²</dd>
    
    <dt>Perceel</dt>
    <dd>200 m²</dd>
    
    <dt>Bouwjaar</dt>
    <dd>1995</dd>
    
    <dt>Energielabel</dt>
    <dd>A</dd>
    
    <dt>Aantal kamers</dt>
    <dd>5 kamers</dd>
</body>
</html>
"""

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_parse_sample(self):
        data = self.parser.parse_html(SAMPLE_HTML)
        
        self.assertEqual(data["asking_price_eur"], "€ 450.000")
        self.assertIn("Straatnaam 123", data["address"])
        self.assertEqual(data["living_area_m2"], "120 m²")
        self.assertEqual(data["plot_area_m2"], "200 m²")
        self.assertEqual(data["build_year"], "1995")
        self.assertEqual(data["energy_label"], "A")
        self.assertEqual(data["rooms"], "5 kamers")

if __name__ == "__main__":
    unittest.main()
