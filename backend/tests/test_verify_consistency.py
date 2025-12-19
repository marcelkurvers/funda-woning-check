import os
import pytest
from backend.consistency import ConsistencyChecker
from backend.parser import Parser

# Path to test data
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test-data")
TEST_HTML_FILE = os.path.join(TEST_DATA_DIR, "test-html")

def test_consistency_check_happy_path():
    """
    Test that the ConsistencyChecker correctly validates a known good file.
    """
    if not os.path.exists(TEST_HTML_FILE):
        pytest.skip("Test data file not found")

    with open(TEST_HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 1. Parse the HTML (Simulate the app flow)
    parser = Parser()
    parsed_data = parser.parse_html(html_content)
    
    # 2. Run Consistency Checker
    checker = ConsistencyChecker()
    report = checker.check(html_content, parsed_data)
    
    # 3. Assert no mismatches
    mismatches = [item for item in report if item["status"] == "mismatch"]
    assert len(mismatches) == 0, f"Expected 0 mismatches, found: {mismatches}"

def test_consistency_check_detects_price_mismatch():
    """
    Test that the ConsistencyChecker detects a price mismatch.
    """
    if not os.path.exists(TEST_HTML_FILE):
        pytest.skip("Test data file not found")

    with open(TEST_HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    parser = Parser()
    parsed_data = parser.parse_html(html_content)
    
    # MANIPULATE DATA: Simulate a parser bug that divides price by 10
    parsed_data["asking_price_eur"] = "€ 140.000" 
    
    checker = ConsistencyChecker()
    report = checker.check(html_content, parsed_data)
    
    # Assert mismatch found
    mismatches = [item for item in report if item["status"] == "mismatch"]
    assert len(mismatches) >= 1
    
    price_error = next((m for m in mismatches if m["field"] == "asking_price_eur"), None)
    assert price_error is not None
    price_error = next((m for m in mismatches if m["field"] == "asking_price_eur"), None)
    assert price_error is not None
    # New logic doesn't extract the "source truth", it just fails to find the parsed value.
    # So we check that the parsed value is mentioned in the error context.
    assert "140.000" in price_error["parsed"]
    assert "not found" in price_error["message"] or "niet gevonden" in price_error["message"]

def test_consistency_check_detects_label_mismatch():
    """
    Test that the ConsistencyChecker detects an energy label mismatch.
    """
    if not os.path.exists(TEST_HTML_FILE):
        pytest.skip("Test data file not found")

    with open(TEST_HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    parser = Parser()
    parsed_data = parser.parse_html(html_content)
    
    # MANIPULATE DATA: Simulate parser finding wrong label
    parsed_data["energy_label"] = "G"
    
    checker = ConsistencyChecker()
    report = checker.check(html_content, parsed_data)
    
    label_error = next((m for m in report if m["field"] == "energy_label" and m["status"] == "mismatch"), None)
    assert label_error is not None
    assert label_error["parsed"] == "G"
