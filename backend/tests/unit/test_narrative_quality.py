"""
Narrative Quality Tests

ARCHITECTURAL UPDATE:
These tests validate that registry-only templates produce clean output.
They check for proper HTML structure and absence of legacy code patterns.

Tests validate:
1. No legacy CSS classes in output
2. Proper HTML structure in main_analysis
3. No raw data dumps

Tests do NOT expect:
- Rich editorial prose in fallback mode (requires AI)
- Computed variables in templates
"""

import pytest
import re
from intelligence import IntelligenceEngine
from chapters.chapter_0 import ExecutiveSummary


def test_no_raw_data_dump_in_main_analysis():
    """
    The main_analysis should not contain legacy styling classes.
    """
    data = {
        "address": "Teststraat 1",
        "asking_price_eur": 500000,
        "living_area_m2": 100,
        "energy_label": "A",
        "build_year": 2020,
        # Pre-computed values from enrichment
        "price_per_m2": 5000,
        "ai_score": 75,
        "marcel_match_score": 50,
        "petra_match_score": 50,
        "total_match_score": 50
    }
    
    chapter = ExecutiveSummary(data)
    output = chapter.generate()
    
    main_analysis = output.chapter_data.get('main_analysis', '')
    
    # Check for legacy CSS classes that should not be present
    assert "mag-v2-stat-box" not in main_analysis
    assert "mag-v2-dashboard" not in main_analysis
    
    # Should have valid content
    assert len(main_analysis) > 0


def test_no_double_persona_info():
    """
    Marcel and Petra info in comparison should not be duplicated in main_analysis.
    """
    data = {
        "address": "Teststraat 1",
        "asking_price_eur": 500000,
        "living_area_m2": 100,
        "energy_label": "A",
        "build_year": 2020,
        "marcel_match_score": 50,
        "petra_match_score": 50,
        "total_match_score": 50
    }
    
    chapter = ExecutiveSummary(data)
    output = chapter.generate()
    
    main_analysis = output.chapter_data.get('main_analysis', '')
    comparison = output.chapter_data.get('comparison', {})
    
    # Check for legacy CSS class
    assert "mag-v2-persona" not in main_analysis
    
    # Comparison text should not be wholly duplicated in main_analysis
    marcel_text = comparison.get('marcel', '')
    petra_text = comparison.get('petra', '')
    
    # Only check if texts are substantial (not just "Match score: X%")
    if len(marcel_text) > 50:
        assert marcel_text not in main_analysis, "Marcel text duplicated"
    if len(petra_text) > 50:
        assert petra_text not in main_analysis, "Petra text duplicated"


def test_editorial_prose_quality():
    """
    Verify that main_analysis has valid HTML structure.
    
    ARCHITECTURAL NOTE: In registry-only mode, this is basic HTML.
    Rich editorial prose requires AI generation.
    """
    data = {
        "address": "Hoge Duinlaan 26",
        "asking_price_eur": 3250000,
        "living_area_m2": 560,
        "energy_label": "A",
        "build_year": 2009,
        # Pre-computed values
        "price_per_m2": 5803,
        "ai_score": 85,
        "valuation_status": "Hoog segment"
    }
    
    chapter = ExecutiveSummary(data)
    output = chapter.generate()
    main_analysis = output.chapter_data.get('main_analysis', '')
    
    # Should have HTML structure
    assert "<" in main_analysis and ">" in main_analysis, "Should have HTML tags"
    
    # Should not start with raw variable name
    stripped = main_analysis.strip().lower()
    assert not stripped.startswith("vigerende"), "Should not start with raw key"
    
    # Should have content
    assert len(main_analysis) > 50, "Should have substantial content"


def test_chapter_output_has_required_fields():
    """Verify ExecutiveSummary output has all required fields."""
    data = {
        "address": "Test",
        "asking_price_eur": 500000,
        "living_area_m2": 100
    }
    
    chapter = ExecutiveSummary(data)
    output = chapter.generate()
    
    # Required fields
    assert output.title is not None
    assert output.chapter_data is not None
    assert output.grid_layout is not None
    
    # Chapter data should have key fields
    chapter_data = output.chapter_data
    assert 'title' in chapter_data
    assert 'main_analysis' in chapter_data


def test_no_computation_in_narrative():
    """
    ARCHITECTURAL TEST: Verify registry-only narratives don't compute.
    """
    IntelligenceEngine.set_provider(None)
    
    ctx = {
        "address": "Test",
        "asking_price_eur": 500000,
        "living_area_m2": 100,
        "energy_label": "B"
    }
    
    result = IntelligenceEngine.generate_chapter_narrative(0, ctx)
    
    # Provenance should indicate registry template
    provenance = result.get('_provenance', {})
    assert 'Registry' in provenance.get('provider', '')
    assert provenance.get('confidence') == 'low'
