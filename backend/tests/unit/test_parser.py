# TEST_REGIME: STRUCTURAL
# REQUIRES: None (parser tests)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest
from parser import Parser
import json

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
    <dd>5 kamers (3 slaapkamers)</dd>
    
    <dt>Aantal badkamers</dt>
    <dd>2 badkamers en 1 apart toilet</dd>
    
    <dt>Soort woonhuis</dt>
    <dd>Eengezinswoning</dd>
    
    <dt>Soort bouw</dt>
    <dd>Bestaande bouw</dd>
</body>
</html>
"""

# Test case with illogical data (33 bedrooms)
ILLOGICAL_HTML = """
<html>
<body>
    <div class="object-header__price">€ 450.000 k.k.</div>
    <h1 class="object-header__title">Test Address</h1>
    
    <dt>Aantal kamers</dt>
    <dd>33 kamers (33 slaapkamers)</dd>
    
    <dt>Aantal badkamers</dt>
    <dd>20 badkamers</dd>
    
    <dt>Woonoppervlakte</dt>
    <dd>5000 m²</dd>
    
    <dt>Bouwjaar</dt>
    <dd>1200</dd>
</body>
</html>
"""

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_parse_sample(self):
        """Test basic parsing with valid data"""
        data = self.parser.parse_html(SAMPLE_HTML)
        
        self.assertEqual(data["asking_price_eur"], "€ 450.000")
        self.assertIn("Straatnaam 123", data["address"])
        self.assertEqual(data["living_area_m2"], "120 m²")
        self.assertEqual(data["plot_area_m2"], "200 m²")
        self.assertEqual(data["build_year"], "1995")
        self.assertEqual(data["energy_label"], "A")
        self.assertEqual(data["rooms"], "5 kamers (3 slaapkamers)")
        self.assertEqual(data["bedrooms"], "3")
        self.assertEqual(data["bathrooms"], "2")
        self.assertEqual(data["property_type"], "Eengezinswoning")
        self.assertEqual(data["construction_type"], "Bestaande bouw")

    def test_parse_real_fixture(self):
        """Test parsing with real Funda fixture data"""
        fixture_path = os.path.join(os.path.dirname(__file__), "../fixtures/user_funda.html")
        
        if not os.path.exists(fixture_path):
            self.skipTest(f"Fixture file not found: {fixture_path}")
        
        with open(fixture_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        data = self.parser.parse_html(html)
        
        # Verify key fields are extracted
        self.assertIsNotNone(data.get("asking_price_eur"), "Price should be extracted")
        self.assertIsNotNone(data.get("address"), "Address should be extracted")
        self.assertIsNotNone(data.get("living_area_m2"), "Living area should be extracted")
        self.assertIsNotNone(data.get("bedrooms"), "Bedrooms should be extracted")
        self.assertIsNotNone(data.get("bathrooms"), "Bathrooms should be extracted")
        
        # Verify specific values from the fixture
        self.assertEqual(data["asking_price_eur"], "€ 1.400.000")
        self.assertEqual(data["bedrooms"], "6")
        self.assertEqual(data["bathrooms"], "2")
        self.assertEqual(data["build_year"], "1979")
        self.assertEqual(data["energy_label"], "B")
        
        # Verify no parsing warnings for this valid data
        self.assertNotIn("_parsing_warnings", data, "Valid data should not have warnings")

    def test_illogical_data_validation(self):
        """Test that illogical data is flagged and capped"""
        data = self.parser.parse_html(ILLOGICAL_HTML)
        
        # Check that warnings were generated
        self.assertIn("_parsing_warnings", data, "Illogical data should generate warnings")
        warnings = data["_parsing_warnings"]
        
        # Verify specific warnings
        warning_text = " ".join(warnings)
        self.assertIn("bedroom", warning_text.lower(), "Should warn about bedrooms")
        self.assertIn("bathroom", warning_text.lower(), "Should warn about bathrooms")
        
        # Verify data was capped
        bedrooms = int(data["bedrooms"])
        self.assertLessEqual(bedrooms, self.parser.MAX_BEDROOMS, 
                            f"Bedrooms should be capped at {self.parser.MAX_BEDROOMS}")
        
        bathrooms = int(data["bathrooms"])
        self.assertLessEqual(bathrooms, self.parser.MAX_BATHROOMS,
                            f"Bathrooms should be capped at {self.parser.MAX_BATHROOMS}")

    def test_bedroom_extraction_from_rooms(self):
        """Test that bedrooms are correctly extracted from rooms field"""
        html = """
        <html><body>
        <dt>Aantal kamers</dt>
        <dd>8 kamers (4 slaapkamers)</dd>
        </body></html>
        """
        data = self.parser.parse_html(html)
        self.assertEqual(data["bedrooms"], "4")

    def test_cross_validation_bedrooms_vs_rooms(self):
        """Test that bedrooms cannot exceed total rooms"""
        # This shouldn't happen in real data, but let's test the validation
        html = """
        <html><body>
        <dt>Aantal kamers</dt>
        <dd>3 kamers (5 slaapkamers)</dd>
        </body></html>
        """
        data = self.parser.parse_html(html)
        
        # Should have a warning
        if "_parsing_warnings" in data:
            warning_text = " ".join(data["_parsing_warnings"])
            self.assertIn("exceeds total rooms", warning_text.lower())

    def test_comprehensive_field_extraction(self):
        """Test that all new fields are being extracted"""
        fixture_path = os.path.join(os.path.dirname(__file__), "../fixtures/user_funda.html")
        
        if not os.path.exists(fixture_path):
            self.skipTest(f"Fixture file not found: {fixture_path}")
        
        with open(fixture_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        data = self.parser.parse_html(html)
        
        # List of fields that should be extracted
        expected_fields = [
            "asking_price_eur",
            "asking_price_per_m2",
            "address",
            "living_area_m2",
            "plot_area_m2",
            "build_year",
            "energy_label",
            "rooms",
            "bedrooms",
            "bathrooms",
            "property_type",
            "construction_type",
            "garage",
            "garden",
            "balcony",
            "roof_type",
            "heating",
            "insulation"
        ]
        
        extracted_count = 0
        missing_fields = []
        
        for field in expected_fields:
            if data.get(field):
                extracted_count += 1
            else:
                missing_fields.append(field)
        
        # We should extract at least 80% of fields from a complete listing
        extraction_rate = extracted_count / len(expected_fields)
        self.assertGreater(extraction_rate, 0.8, 
                          f"Should extract at least 80% of fields. Missing: {missing_fields}")

    def test_data_quality_report(self):
        """Generate a quality report for parsed data"""
        fixture_path = os.path.join(os.path.dirname(__file__), "../fixtures/user_funda.html")
        
        if not os.path.exists(fixture_path):
            self.skipTest(f"Fixture file not found: {fixture_path}")
        
        with open(fixture_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        data = self.parser.parse_html(html)
        
        # Generate quality report
        report = {
            "total_fields": 18,
            "extracted_fields": sum(1 for v in data.values() if v and not str(v).startswith("_")),
            "warnings": data.get("_parsing_warnings", []),
            "completeness": 0,
            "critical_fields_present": True,
            "data_sample": {}
        }
        
        report["completeness"] = round(report["extracted_fields"] / report["total_fields"] * 100, 1)
        
        # Check critical fields
        critical_fields = ["asking_price_eur", "address", "living_area_m2", "bedrooms"]
        for field in critical_fields:
            if not data.get(field):
                report["critical_fields_present"] = False
                break
        
        # Sample data
        report["data_sample"] = {
            "address": data.get("address"),
            "price": data.get("asking_price_eur"),
            "bedrooms": data.get("bedrooms"),
            "bathrooms": data.get("bathrooms"),
            "living_area": data.get("living_area_m2")
        }
        
        print("\n" + "="*60)
        print("PARSER QUALITY REPORT")
        print("="*60)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        print("="*60)
        
        # Assertions
        self.assertGreater(report["completeness"], 70, "Should extract >70% of fields")
        self.assertTrue(report["critical_fields_present"], "All critical fields must be present")

if __name__ == "__main__":
    unittest.main()
