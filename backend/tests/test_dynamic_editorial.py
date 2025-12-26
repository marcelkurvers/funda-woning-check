# TEST_REGIME: STRUCTURAL
# REQUIRES: None (template logic tests)
import pytest
from chapters.formatter import EditorialEngine

class TestDynamicEditorial:
    
    @pytest.fixture
    def narrative(self):
        return {
            "main_analysis": "<p>Content.</p>",
            "variables": {}
        }

    def test_smart_get_resolves_aliases(self):
        """Test the underlying _smart_get logic directly."""
        data_a = {"asking_price_eur": 500000}
        data_b = {"price": 500000}
        data_c = {"prijs": 500000}
        
        keys = ['price', 'asking_price_eur', 'prijs']
        
        assert EditorialEngine._smart_get(data_a, keys) == 500000
        assert EditorialEngine._smart_get(data_b, keys) == 500000
        assert EditorialEngine._smart_get(data_c, keys) == 500000
        assert EditorialEngine._smart_get({}, keys, default=0) == 0

    def test_chapter_0_market_pulse_dynamic_keys(self, narrative):
        """
        Verify Chapter 0 (Market Pulse) correctly picks up price/area 
        regardless of input key format (raw parser input vs cleaned input).
        """
        # Case 1: Raw Parser Keys (Dutch strings)
        raw_data = {
            "asking_price_eur": "€ 450.000 k.k.",
            "living_area_m2": "120 m²"
        }
        html_raw = EditorialEngine.format_narrative(0, narrative, raw_data)
        
        # Calculation: 450000 / 120 = 3750
        assert "€ 3,750" in html_raw or "3.750" in html_raw # Check generic number formatting parts
        assert "Market Position Index" in html_raw

        # Case 2: Cleaned Keys (Integers)
        clean_data = {
            "price": 450000,
            "area": 120
        }
        html_clean = EditorialEngine.format_narrative(0, narrative, clean_data)
        assert "€ 3,750" in html_clean or "3.750" in html_clean

    def test_chapter_1_property_dna_dynamic_keys(self, narrative):
        """Verify Chapter 1 (Property DNA) finds year/volume/rooms with various aliases."""
        # Case 1: Standard Parser
        data_1 = {
            "build_year": "1995",
            "volume_m3": "400",
            "rooms": "5"
        }
        html_1 = EditorialEngine.format_narrative(1, narrative, data_1)
        assert "1995" in html_1
        assert "400 m³" in html_1
        assert "5" in html_1
        
        # Case 2: Dutch Aliases or Alternative sources
        data_2 = {
            "bouwjaar": 2020,
            "inhoud": 600,
            "aantal_kamers": 8
        }
        html_2 = EditorialEngine.format_narrative(1, narrative, data_2)
        assert "2020" in html_2
        assert "600 m³" in html_2
        assert "8" in html_2

    def test_chapter_2_synergy_scores(self, narrative):
        """Verify Chapter 2 (Synergy) handles different score keys."""
        # Case 1: Full specific keys
        data_1 = {
            "marcel_match_score": 88,
            "petra_match_score": 77
        }
        html_1 = EditorialEngine.format_narrative(2, narrative, data_1)
        assert "88%" in html_1
        assert "77%" in html_1
        
        # Case 2: Short keys
        data_2 = {
            "match_marcel": 60,
            "match_petra": 90
        }
        html_2 = EditorialEngine.format_narrative(2, narrative, data_2)
        assert "60%" in html_2
        assert "90%" in html_2

    def test_robustness_messy_input(self, narrative):
        """Ensure the engine formats safely even with messy input data."""
        messy_data = {
            "asking_price_eur": "€ 1.250.000,- ",  # Typical formatted string
            "living_area_m2": "  180m2  ",
            "build_year": "? (geschat)"
        }
        
        # Should not crash
        html = EditorialEngine.format_narrative(0, narrative, messy_data)
        
        # Price: 1250000 / 180 = 6944
        assert "Market Position Index" in html
        assert "6,944" in html or "6.944" in html
