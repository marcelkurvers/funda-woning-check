"""
Schema Validation Tests for AI System

These tests validate that narrative outputs conform to expected schema structures.
They DO NOT test AI quality or runtime availability.

ARCHITECTURAL PRINCIPLE:
Tests verify output structure and data types, not content quality or AI availability.
"""

import unittest
from intelligence import IntelligenceEngine


class TestNarrativeOutputSchema(unittest.TestCase):
    """Verify narrative outputs conform to expected schema"""

    def setUp(self):
        """Reset provider state to use fallback"""
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        """Clean up provider state"""
        IntelligenceEngine.set_provider(None)

    def test_chapter_1_schema_compliance(self):
        """Verify Chapter 1 (General) output has required fields"""
        ctx = {
            "address": "Teststraat 1",
            "price": 500000,
            "area": 120,
            "year": 2000
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # Required fields
        required_fields = ['title', 'intro', 'main_analysis', 'interpretation', 
                          'conclusion', 'strengths', 'advice']
        
        for field in required_fields:
            self.assertIn(field, result, f"Missing required field: {field}")
        
        # Type validation
        self.assertIsInstance(result['title'], str)
        self.assertIsInstance(result['intro'], str)
        self.assertIsInstance(result['main_analysis'], str)
        self.assertIsInstance(result['interpretation'], str)
        self.assertIsInstance(result['conclusion'], str)
        self.assertIsInstance(result['strengths'], list)
        # Advice is a list of strings (contract: structured advice points)
        self.assertIsInstance(result['advice'], list)

    def test_chapter_0_schema_compliance(self):
        """Verify Chapter 0 (Executive Summary) output has required fields"""
        ctx = {
            "address": "Teststraat 1",
            "price": 500000,
            "area": 120,
            "year": 2000,
            "label": "B"
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(0, ctx)
        
        # Chapter 0 specific fields
        self.assertIn('title', result)
        self.assertIn('intro', result)
        self.assertIn('main_analysis', result)
        
        # Type validation
        self.assertIsInstance(result['title'], str)
        self.assertIsInstance(result['intro'], str)

    def test_chapter_2_schema_compliance(self):
        """Verify Chapter 2 (Preferences) output has required fields"""
        ctx = {
            "address": "Teststraat 1",
            "price": 500000,
            "_preferences": {
                "marcel": {"priorities": ["Garage", "Zonnepanelen"]},
                "petra": {"priorities": ["Tuin", "Glas in lood"]}
            }
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        # Required fields
        self.assertIn('title', result)
        self.assertIn('intro', result)
        self.assertIn('main_analysis', result)
        
        # Preferences-specific field
        if 'comparison' in result:
            self.assertIsInstance(result['comparison'], dict)

    def test_chapter_4_schema_compliance(self):
        """Verify Chapter 4 (Energy) output has required fields"""
        ctx = {
            "address": "Teststraat 1",
            "label": "A",
            "year": 2020
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(4, ctx)
        
        # Required fields
        required_fields = ['title', 'intro', 'main_analysis', 'interpretation', 
                          'conclusion', 'strengths', 'advice']
        
        for field in required_fields:
            self.assertIn(field, result, f"Chapter 4 missing field: {field}")

    def test_strengths_field_is_list_of_strings(self):
        """Verify strengths field is always a list of strings"""
        ctx = {"address": "Test", "price": 500000, "area": 120}
        
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        self.assertIsInstance(result['strengths'], list)
        
        for strength in result['strengths']:
            self.assertIsInstance(strength, str)
            self.assertGreater(len(strength), 0, "Strength should not be empty string")

    def test_all_text_fields_are_non_empty(self):
        """Verify all text fields contain actual content"""
        ctx = {"address": "Test", "price": 500000, "area": 120}
        
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        text_fields = ['title', 'intro', 'main_analysis', 'interpretation', 
                      'conclusion']
        
        for field in text_fields:
            if field in result:
                self.assertIsInstance(result[field], str)
                self.assertGreater(len(result[field]), 0, 
                                 f"{field} should not be empty")
        
        # Advice is a list, check it separately
        if 'advice' in result:
            self.assertIsInstance(result['advice'], list)
            self.assertGreater(len(result['advice']), 0, "advice list should not be empty")

    def test_output_is_json_serializable(self):
        """Verify narrative output can be serialized to JSON"""
        import json
        
        ctx = {"address": "Test", "price": 500000, "area": 120}
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # Should not raise exception
        json_str = json.dumps(result)
        self.assertIsInstance(json_str, str)
        
        # Should be deserializable
        deserialized = json.loads(json_str)
        self.assertEqual(deserialized['title'], result['title'])


class TestNarrativeDataIntegration(unittest.TestCase):
    """Verify narratives correctly integrate property data"""

    def setUp(self):
        """Reset provider state to use fallback"""
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        """Clean up provider state"""
        IntelligenceEngine.set_provider(None)

    def test_narrative_references_property_address(self):
        """Verify narrative incorporates property address"""
        ctx = {
            "address": "Kalverstraat 42, Amsterdam",
            "price": 500000,
            "area": 120
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # At least one field should reference the address or location
        full_text = ' '.join([
            result.get('intro', ''),
            result.get('main_analysis', ''),
            result.get('conclusion', '')
        ]).lower()
        
        # Should mention address or Amsterdam
        self.assertTrue(
            any(term in full_text for term in ['kalverstraat', 'amsterdam', 'object', 'woning']),
            "Narrative should reference property or location"
        )

    def test_narrative_uses_actual_property_data(self):
        """Verify narrative uses actual property data, not placeholders"""
        ctx = {
            "address": "Teststraat 1",
            "price": 750000,
            "area": 150,
            "year": 1995
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        full_text = str(result).lower()
        
        # Should not contain generic placeholders
        self.assertNotIn("[address]", full_text)
        self.assertNotIn("[price]", full_text)
        self.assertNotIn("placeholder", full_text)
        self.assertNotIn("lorem ipsum", full_text)

    def test_chapter_4_energy_logic_green_label(self):
        """Verify Chapter 4 correctly processes green energy label"""
        ctx = {
            "address": "Test",
            "label": "A",
            "year": 2022
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(4, ctx)
        
        # Should mention the A label
        intro = result['intro']
        self.assertIn("A", intro, "Should mention energy label A")
        
        # Should have positive strengths for green label
        strengths = result.get('strengths', [])
        self.assertGreater(len(strengths), 0, "Green label should have strengths")

    def test_chapter_4_energy_logic_poor_label(self):
        """Verify Chapter 4 correctly processes poor energy label"""
        ctx = {
            "address": "Test",
            "label": "G",
            "year": 1930
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(4, ctx)
        
        intro = result['intro'].lower()
        
        # Should mention improvement opportunity or investment
        self.assertTrue(
            any(term in intro for term in ['investering', 'renovatie', 'verbetering', 
                                           'kans', 'verbeteren', 'moderniseren']),
            "Poor energy label should mention improvement opportunity"
        )

    def test_chapter_0_handles_missing_data(self):
        """Verify Chapter 0 gracefully handles missing data"""
        ctx = {
            "address": "Test"
            # Missing price, area, etc.
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(0, ctx)
        
        # Should still return valid structure
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)
        self.assertIn('main_analysis', result)
        
        # Should not crash or return empty content
        self.assertGreater(len(result['main_analysis']), 0)


class TestHelperFunctions(unittest.TestCase):
    """Verify helper functions work correctly"""

    def test_parse_int_helper_with_area(self):
        """Verify _parse_int correctly parses area strings"""
        self.assertEqual(IntelligenceEngine._parse_int("200 m²"), 200)
        self.assertEqual(IntelligenceEngine._parse_int("120m²"), 120)
        self.assertEqual(IntelligenceEngine._parse_int("150 m2"), 150)

    def test_parse_int_helper_with_price(self):
        """Verify _parse_int correctly parses price strings"""
        self.assertEqual(IntelligenceEngine._parse_int("€ 500.000"), 500000)
        self.assertEqual(IntelligenceEngine._parse_int("€ 1.500.000"), 1500000)
        self.assertEqual(IntelligenceEngine._parse_int("750000"), 750000)

    def test_parse_int_helper_with_year(self):
        """Verify _parse_int correctly parses year strings"""
        self.assertEqual(IntelligenceEngine._parse_int("1995"), 1995)
        self.assertEqual(IntelligenceEngine._parse_int("2022"), 2022)

    def test_parse_int_helper_with_invalid_input(self):
        """Verify _parse_int handles invalid input gracefully"""
        self.assertEqual(IntelligenceEngine._parse_int("invalid"), 0)
        self.assertEqual(IntelligenceEngine._parse_int(""), 0)
        self.assertEqual(IntelligenceEngine._parse_int(None), 0)

    def test_parse_int_helper_with_numeric_input(self):
        """Verify _parse_int handles numeric input"""
        self.assertEqual(IntelligenceEngine._parse_int(500000), 500000)
        self.assertEqual(IntelligenceEngine._parse_int(120), 120)

    def test_calculate_fit_score_returns_float(self):
        """Verify calculate_fit_score returns float between 0 and 1"""
        ctx = {
            "address": "Test",
            "price": 500000,
            "area": 120,
            "_preferences": {
                "marcel": {"priorities": ["Garage"]},
                "petra": {"priorities": ["Tuin"]}
            }
        }
        
        score = IntelligenceEngine.calculate_fit_score(ctx)
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestSchemaConsistency(unittest.TestCase):
    """Verify schema consistency across different chapters"""

    def setUp(self):
        """Reset provider state to use fallback"""
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        """Clean up provider state"""
        IntelligenceEngine.set_provider(None)

    def test_all_chapters_return_dict(self):
        """Verify all chapters return dictionary output"""
        ctx = {
            "address": "Test",
            "price": 500000,
            "area": 120,
            "year": 2000,
            "label": "B"
        }
        
        # Test chapters 0-5
        for chapter_id in range(6):
            result = IntelligenceEngine.generate_chapter_narrative(chapter_id, ctx)
            self.assertIsInstance(result, dict, 
                                f"Chapter {chapter_id} should return dict")

    def test_all_chapters_have_title(self):
        """Verify all chapters include a title field"""
        ctx = {
            "address": "Test",
            "price": 500000,
            "area": 120,
            "year": 2000,
            "label": "B"
        }
        
        # Test chapters 0-5
        for chapter_id in range(6):
            result = IntelligenceEngine.generate_chapter_narrative(chapter_id, ctx)
            self.assertIn('title', result, 
                         f"Chapter {chapter_id} should have title")
            self.assertIsInstance(result['title'], str)

    def test_all_chapters_have_intro(self):
        """Verify all chapters include an intro field"""
        ctx = {
            "address": "Test",
            "price": 500000,
            "area": 120,
            "year": 2000,
            "label": "B"
        }
        
        # Test chapters 0-5
        for chapter_id in range(6):
            result = IntelligenceEngine.generate_chapter_narrative(chapter_id, ctx)
            self.assertIn('intro', result, 
                         f"Chapter {chapter_id} should have intro")
            self.assertIsInstance(result['intro'], str)


if __name__ == '__main__':
    unittest.main()
