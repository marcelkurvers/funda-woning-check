import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest
from parser import Parser

# A mock of a more complex/messy HTML structure often found in manual copy-pastes or newer layouts
COMPLEX_HTML = """
<html>
<body>
    <div class="app-header"></div>
    <main>
        <div class="object-header">
            <h1 class="object-header__title">Grote Markt 1, 9999 XX Stad</h1>
            <div class="object-header__price-history">
                <span class="object-header__price">€ 450.000 k.k.</span>
            </div>
        </div>
        
        <div class="object-kenmerken-body">
            <h3 class="object-kenmerken-list-header">Overdracht</h3>
            <dl class="object-kenmerken-list">
                <dt>Vraagprijs</dt>
                <dd>€ 450.000 k.k.</dd>
                <dt>Status</dt>
                <dd>Beschikbaar</dd>
            </dl>
            
            <h3 class="object-kenmerken-list-header">Bouw</h3>
            <dl class="object-kenmerken-list">
                <dt>Soort woonhuis</dt>
                <dd>Eengezinswoning, vrijstaande woning</dd>
                <dt>Bouwjaar</dt>
                <dd><span>1995</span></dd>
            </dl>
            
            <h3 class="object-kenmerken-list-header">Oppervlakten en inhoud</h3>
            <dl class="object-kenmerken-list">
                <dt>Woonoppervlakte</dt>
                <dd>145 m²</dd>
                <dt>Perceel</dt>
                <dd>350 m²</dd>
                <dt>Inhoud</dt>
                <dd>500 m³</dd>
            </dl>

            <h3 class="object-kenmerken-list-header">Energie</h3>
            <dl class="object-kenmerken-list">
                <dt>Energielabel</dt>
                <dd> <span class="energy-label-class">A</span> </dd>
            </dl>
        </div>
        
        <!-- Alternate Layout Section (Simulating what might happen if classes are stripped) -->
        <div class="legacy-list">
           <span>Aantal kamers</span>
           <span>5 kamers (3 slaapkamers)</span>
        </div>
    </main>
</body>
</html>
"""

class TestComplexParsing(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_no_classes_layout(self):
        # Simulation of a "Print View" or "Reader Mode" or "Simple Copy" where classes are stripped
        # This is where current parser likely fails
        NO_CLASS_HTML = """
        <html>
        <body>
            <h1>Kerkstraat 10, Dorp</h1>
            <p>Vraagprijs: € 325.000 k.k.</p>
            
            <h2>Kenmerken</h2>
            <div>Woonoppervlakte: 120 m²</div>
            <div>Perceel: 200 m²</div>
            <div>Bouwjaar: 1980</div>
            <div>Energielabel: C</div>
            <div>Aantal kamers: 4</div>
        </body>
        </html>
        """
        data = self.parser.parse_html(NO_CLASS_HTML)
        print("Parsed No-Class Data:", data)
        
        # We expect these to fail initially, confirming the need for improvements
        self.assertEqual(data["asking_price_eur"], "€ 325.000")
        self.assertIn("120", data["living_area_m2"] or "")
        self.assertIn("1980", data["build_year"] or "")
        self.assertEqual(data["energy_label"], "C")

if __name__ == "__main__":
    unittest.main()
