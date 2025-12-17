import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import unittest
from chapters.utils import (
    parse_int, parse_float, validate_bedrooms,
    validate_living_area, safe_get, ensure_grid_layout
)


class TestParsingUtilities(unittest.TestCase):
    """Test parsing helper functions"""
    
    def test_parse_int_valid_numbers(self):
        """Test parsing valid integer inputs"""
        self.assertEqual(parse_int("123"), 123)
        self.assertEqual(parse_int("1500000"), 1500000)
        self.assertEqual(parse_int(200), 200)
    
    def test_parse_int_formatted_numbers(self):
        """Test parsing formatted numbers (European style)"""
        self.assertEqual(parse_int("1.500.000"), 1500000)
        self.assertEqual(parse_int("€ 1.500.000"), 1500000)
        self.assertEqual(parse_int("200 m²"), 200)
        self.assertEqual(parse_int("1,500"), 1500)
    
    def test_parse_int_invalid_inputs(self):
        """Test parsing invalid inputs returns default"""
        self.assertEqual(parse_int("invalid"), 0)
        self.assertEqual(parse_int(None), 0)
        self.assertEqual(parse_int(""), 0)
        self.assertEqual(parse_int("abc123"), 123)  # Extracts digits
    
    def test_parse_int_custom_default(self):
        """Test custom default value"""
        self.assertEqual(parse_int("invalid", default=999), 999)
        self.assertEqual(parse_int(None, default=-1), -1)
    
    def test_parse_float_valid(self):
        """Test parsing valid float inputs"""
        self.assertEqual(parse_float("123.45"), 123.45)
        self.assertEqual(parse_float("123,45"), 123.45)  # European format
        self.assertEqual(parse_float(200.5), 200.5)
    
    def test_parse_float_invalid(self):
        """Test parsing invalid float inputs"""
        self.assertEqual(parse_float("invalid"), 0.0)
        self.assertEqual(parse_float(None), 0.0)
        self.assertEqual(parse_float("", default=1.5), 1.5)


class TestValidationUtilities(unittest.TestCase):
    """Test validation helper functions"""
    
    def test_validate_bedrooms_normal_range(self):
        """Test bedroom validation in normal range"""
        self.assertEqual(validate_bedrooms(6), 5)  # 6 rooms -> 5 bedrooms
        self.assertEqual(validate_bedrooms(4), 3)  # 4 rooms -> 3 bedrooms
        self.assertEqual(validate_bedrooms(2), 1)  # 2 rooms -> 1 bedroom (minimum)
    
    def test_validate_bedrooms_upper_bound(self):
        """Test bedroom validation caps at 10"""
        self.assertEqual(validate_bedrooms(50), 10)  # Should cap at 10
        self.assertEqual(validate_bedrooms(33), 10)  # The infamous 33 bedrooms case
        self.assertEqual(validate_bedrooms(11), 10)
    
    def test_validate_bedrooms_explicit_count(self):
        """Test using explicit bedroom count"""
        self.assertEqual(validate_bedrooms(10, bedrooms=5), 5)
        self.assertEqual(validate_bedrooms(10, bedrooms=15), 10)  # Still caps at 10
    
    def test_validate_bedrooms_minimum(self):
        """Test minimum bedroom count is 1"""
        self.assertEqual(validate_bedrooms(0), 1)
        self.assertEqual(validate_bedrooms(1), 1)
    
    def test_validate_living_area_normal(self):
        """Test living area validation in normal range"""
        self.assertEqual(validate_living_area(150), 150)
        self.assertEqual(validate_living_area(200), 200)
        self.assertEqual(validate_living_area(50), 50)
    
    def test_validate_living_area_bounds(self):
        """Test living area validation with bounds"""
        self.assertEqual(validate_living_area(0), 1)  # Minimum 1
        self.assertEqual(validate_living_area(-10), 1)  # Negative becomes 1
        self.assertEqual(validate_living_area(3000), 2000)  # Cap at 2000
        self.assertEqual(validate_living_area(5000), 2000)  # Cap at 2000


class TestSafetyUtilities(unittest.TestCase):
    """Test safety helper functions"""
    
    def test_safe_get_existing_key(self):
        """Test safe_get with existing keys"""
        context = {"name": "Test", "value": 123}
        self.assertEqual(safe_get(context, "name"), "Test")
        self.assertEqual(safe_get(context, "value"), "123")  # Converts to string
    
    def test_safe_get_missing_key(self):
        """Test safe_get with missing keys returns default"""
        context = {"name": "Test"}
        self.assertEqual(safe_get(context, "missing"), "")
        self.assertEqual(safe_get(context, "missing", "default"), "default")
    
    def test_safe_get_none_value(self):
        """Test safe_get with None value returns default"""
        context = {"name": None}
        self.assertEqual(safe_get(context, "name"), "")
        self.assertEqual(safe_get(context, "name", "fallback"), "fallback")
    
    def test_ensure_grid_layout_missing(self):
        """Test ensure_grid_layout adds fallback when missing"""
        chapter_dict = {"title": "Test Chapter"}
        result = ensure_grid_layout(chapter_dict)
        
        self.assertIn('grid_layout', result)
        self.assertEqual(result['grid_layout']['layout_type'], 'fallback')
        self.assertIn('hero', result['grid_layout'])
        self.assertIn('metrics', result['grid_layout'])
        self.assertIn('main', result['grid_layout'])
        self.assertIn('sidebar', result['grid_layout'])
    
    def test_ensure_grid_layout_existing(self):
        """Test ensure_grid_layout preserves existing layout"""
        chapter_dict = {
            "title": "Test",
            "grid_layout": {
                "layout_type": "modern_dashboard",
                "hero": {"address": "Test"}
            }
        }
        result = ensure_grid_layout(chapter_dict)
        
        self.assertEqual(result['grid_layout']['layout_type'], 'modern_dashboard')
        self.assertEqual(result['grid_layout']['hero']['address'], 'Test')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_parse_int_extreme_values(self):
        """Test parsing very large numbers"""
        self.assertEqual(parse_int("999999999"), 999999999)
        self.assertEqual(parse_int("1.000.000.000"), 1000000000)
    
    def test_validate_bedrooms_edge_cases(self):
        """Test bedroom validation edge cases"""
        # The QA report case: 33 bedrooms should be capped
        self.assertEqual(validate_bedrooms(34), 10)
        
        # Explicit bedroom count overrides calculation
        self.assertEqual(validate_bedrooms(100, bedrooms=3), 3)
    
    def test_validate_living_area_warnings(self):
        """Test that extremely large areas are capped with warning"""
        # This should cap at 2000 and ideally log a warning
        result = validate_living_area(10000)
        self.assertEqual(result, 2000)


if __name__ == "__main__":
    unittest.main()
