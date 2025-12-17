# Additional parser edge case tests
import pytest
from parser import Parser

@pytest.fixture
def parser():
    return Parser()

def test_address_blocklist_ignored(parser):
    # HTML that includes navigation text "Ga naar" before the address line
    html = """
    <html><body>
    Ga naar
    Menu
    Amsterdamseweg 123, 1111 AA Diemen
    </body></html>
    """
    data = parser.parse_html(html)
    # The address should be the line with the street, not "Ga naar"
    assert data["address"] == "Amsterdamseweg 123, 1111 AA Diemen"

def test_bedroom_capping(parser):
    # Simulate a scenario where the extracted bedroom count is unrealistically high
    # We'll monkey‑patch the _extract_bedrooms method to return a high number
    def fake_extract_bedrooms(_):
        return "54"
    parser._extract_bedrooms = fake_extract_bedrooms
    # Minimal HTML to allow parsing (price etc. not needed for this test)
    html = "<html><body><div class='object-header__title'>Test</div></body></html>"
    data = parser.parse_html(html)
    # The validated data should cap bedrooms at MAX_BEDROOMS (15) and include a warning
    assert data["bedrooms"] == str(parser.MAX_BEDROOMS)
    assert "_parsing_warnings" in data
    warnings = data["_parsing_warnings"]
    assert any("Suspicious bedroom count" in w for w in warnings)
