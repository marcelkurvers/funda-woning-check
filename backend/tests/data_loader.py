import os
import sys

# Ensure we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from parser import Parser

TEST_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../test-data"))
TEST_HTML_FILE = os.path.join(TEST_DATA_DIR, "test-html")

def load_test_data():
    """
    Mandatory data loader for tests.
    Reads from test-data/test-html and parses it using the standard Parser.
    Returns the core data dictionary.
    """
    if not os.path.exists(TEST_HTML_FILE):
        raise FileNotFoundError(f"Mandatory test data file not found: {TEST_HTML_FILE}")
    
    with open(TEST_HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    parser = Parser()
    core_data = parser.parse_html(content)
    
    # Enrichment for testing (fields that might not be in the raw paste but are needed for logic tests)
    # Ensure energy_label is present (default to G if missing)
    if not core_data.get("energy_label"):
         core_data["energy_label"] = "G"
    
    return core_data
