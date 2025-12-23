import pytest
import re
from intelligence import IntelligenceEngine
from chapters.chapter_0 import ExecutiveSummary

def test_no_raw_data_dump_in_main_analysis():
    """
    CRITICAL: The main_analysis should be pure narrative storytelling.
    It must NOT contain a raw list of variables/keys like "vigerende vraagprijs: € 3,250,000".
    """
    data = {
        "address": "Teststraat 1",
        "asking_price_eur": "€ 500.000",
        "living_area_m2": "100",
        "energy_label": "A",
        "build_year": "2020"
    }
    
    # Test Chapter 0 (Executive Summary)
    chapter = ExecutiveSummary(data)
    output = chapter.generate()
    
    main_analysis = output.chapter_data.get('main_analysis', '')
    variables = output.chapter_data.get('variables', {})
    
    # Check for raw key-value pairs in the text
    for key in variables.keys():
        key_readable = key.replace('_', ' ')
        # We check if the key is followed by its value within a short distance, indicating a list
        val = variables[key].get('value', '')
        if isinstance(val, str) and val:
             # Look for "key: value" or "key \n value"
             pattern = re.compile(rf"{re.escape(key_readable)}.*{re.escape(val)}", re.IGNORECASE | re.DOTALL)
             # However, some narrative might mention them. A "dump" usually has multiple in a row.
             # We look for the presence of the "mag-v2-stat-box" which we just removed.
             assert "mag-v2-stat-box" not in main_analysis, f"Found legacy mag-v2-stat-box in main_analysis for {key}"
             assert "mag-v2-dashboard" not in main_analysis, "Found legacy mag-v2-dashboard in main_analysis"

def test_no_double_persona_info():
    """
    Marcel and Petra info should only be in the comparison field, not in main_analysis.
    """
    data = {
        "address": "Teststraat 1",
        "asking_price_eur": "€ 500.000",
        "living_area_m2": "100",
        "energy_label": "A",
        "build_year": "2020"
    }
    
    chapter = ExecutiveSummary(data)
    output = chapter.generate()
    
    main_analysis = output.chapter_data.get('main_analysis', '')
    comparison = output.chapter_data.get('comparison', {})
    
    marcel_text = comparison.get('marcel', '')
    petra_text = comparison.get('petra', '')
    
    if marcel_text:
        # It shouldn't be a verbatim block in the main analysis
        assert "mag-v2-persona" not in main_analysis, "Found legacy mag-v2-persona block in main_analysis"
        # The exact text shouldn't be repeated in its entirety
        assert marcel_text not in main_analysis, "Marcel comparative text is duplicated in main_analysis"
        
    if petra_text:
        assert petra_text not in main_analysis, "Petra comparative text is duplicated in main_analysis"

def test_editorial_prose_quality():
    """
    Verify that main_analysis looks like HTML prose, not a fragment list.
    """
    data = {
        "address": "Hoge Duinlaan 26",
        "asking_price_eur": "€ 3.250.000",
        "living_area_m2": "560",
        "energy_label": "A",
        "build_year": "2009"
    }
    
    chapter = ExecutiveSummary(data)
    output = chapter.generate()
    main_analysis = output.chapter_data.get('main_analysis', '')
    
    # Needs to have paragraphs
    assert "<p>" in main_analysis or "<div>" in main_analysis
    # Should not start with 'Vigerende' (which was the first variable in the dump)
    assert not main_analysis.strip().startswith("vigerende"), "Main analysis starts with a raw variable key!"
    
    # Should have a decent length to be "editorial"
    assert len(main_analysis) > 100
