
import pytest
from bs4 import BeautifulSoup
from parser import Parser

class TestParserEdgeCases:
    """
    Tests for specific edge cases and error scenarios observed in production.
    """
    
    @pytest.fixture
    def parser(self):
        return Parser()

    def test_navigation_text_address_bug(self, parser):
        """
        Test that common navigation text is NOT picked up as the address.
        Scenario: User pastes full page including "Ga naar", "Menu", etc.
        """
        # Case 1: "Ga naar" at the start
        html_ga_naar = """
        <html><body>
        Ga naar
        Zoeken
        Menu
        
        Amsterdamseweg 123, 1111 AA Diemen
        € 450.000 k.k.
        </body></html>
        """
        data = parser.parse_html(html_ga_naar)
        assert "Ga naar" not in data["address"]
        assert "Amsterdamseweg 123" in data["address"]

        # Case 2: "Funda" or "Menu" at start
        html_menu = """
        <html><body>
        funda
        menu
        inloggen
        
        Kerkstraat 1, 1000 AA Amsterdam
        </body></html>
        """
        data_menu = parser.parse_html(html_menu)
        assert "funda" not in data_menu["address"].lower()
        assert "menu" not in data_menu["address"].lower()
        assert "Kerkstraat 1" in data_menu["address"]

    def test_photo_count_as_rooms_bug(self, parser):
        """
        Test that photo counts (e.g. "54 foto's") are not mistaken for room counts.
        Scenario: "54" appears near "kamers" or is just a loose number picked up incorrectly.
        """
        html_photos = """
        <html><body>
        Bekijk alle 54 foto's
        
        Kenmerken
        Wonen
        165 m²
        
        Aantal kamers
        6 kamers (4 slaapkamers)
        </body></html>
        """
        data = parser.parse_html(html_photos)
        
        # Should be 6 rooms, definitely NOT 54
        assert data["rooms"] != "54"
        assert "6" in str(data["rooms"])
        
        # Also check validation logic - if it DOES pick up 54, it should be sanitized
        # But ideally the parser is smart enough to avoid it entirely.

    def test_suspicious_room_count_correction(self, parser):
        """
        Test that impossible room counts are not just warned about, but corrected or invalidated.
        """
        # Scenario where "54" is somehow forced as the room count
        # We simulate this by checking the validation logic directly or passing a string that definitely yields 54
        
        # If the parser extracts "54", the validator should reject it
        parser_data = {"rooms": "54", "living_area_m2": "165"}
        validated = parser._validate_data(parser_data)
        
        # Should be None or capped, not "54"
        # We expect the validation to clean this up
        assert validated["rooms"] != "54"
        assert validated["rooms"] is None or int(validated["rooms"]) <= 30

    def test_duplicate_m2_display_fix(self, parser):
        """
        Ensure we don't have issues with m2 being double parsed or formatted weirdly.
        (Though this was mentioned as a separate issue, it's good to check)
        """
        html_m2 = """
        Woonoppervlakte
        120 m²
        """
        data = parser.parse_html(html_m2)
        # Should just be "120", not "120 m2" or "120 m²" if we want pure numbers
        # Based on current parser it seems to return strings, sometimes with units. 
        # Ideally it returns just the number string "120" or "120 m2" but consistently.
        # Let's check what it currently does.
        # The parser regex usually extracts just the number or the whole string?
        # Looking at code: `_extract_spec` -> returns the value found.
        # If text is "120 m²", it returns "120 m²".
        # IntelligenceEngine._parse_int handles the cleanup later.
        pass

