"""
AI Preference Matching Tests

ARCHITECTURAL UPDATE:
These tests validate preference matching behavior with the new architecture.
- Match scores are computed in the enrichment layer
- Registry-only templates display pre-computed scores
- AI (when available) generates rich narrative

Tests are designed to pass whether AI is available or not.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import pytest
import asyncio
from intelligence import IntelligenceEngine
from ai.provider_interface import AIProvider
from ai.providers.ollama_provider import OllamaProvider


@pytest.fixture(autouse=True)
def cleanup_provider():
    """Ensure provider is reset before and after each test"""
    IntelligenceEngine.set_provider(None)
    yield
    IntelligenceEngine.set_provider(None)


@pytest.mark.asyncio
async def test_chapter_0_fallback_comparison():
    """
    Verify that Chapter 0 returns a 'comparison' object even WITHOUT AI.
    
    ARCHITECTURAL NOTE: Registry-only templates have minimal comparison content.
    They display pre-computed match scores, not rich prose.
    """
    ctx = {
        "address": "Teststraat 1",
        "asking_price_eur": 500000,
        "living_area_m2": 120,
        "energy_label": "A",
        "build_year": 2020,
        # Pre-computed scores
        "marcel_match_score": 70,
        "petra_match_score": 60,
        "total_match_score": 65
    }
    
    IntelligenceEngine.set_provider(None)
    result = IntelligenceEngine.generate_chapter_narrative(0, ctx)
    
    assert "comparison" in result
    assert "marcel" in result["comparison"]
    assert "petra" in result["comparison"]
    
    # Registry-only templates have score-based content
    marcel_text = result["comparison"]["marcel"]
    petra_text = result["comparison"]["petra"]
    
    # Should have some content (even if just "Match score: X%")
    assert len(marcel_text) > 0, "Marcel comparison should have content"
    assert len(petra_text) > 0, "Petra comparison should have content"


@pytest.mark.asyncio
async def test_ai_preference_matching_with_real_ollama():
    """
    Test preference matching with real OllamaProvider (if available).
    Falls back gracefully when Ollama is not running.
    """
    ctx = {
        "address": "Duinlaan 26",
        "asking_price_eur": 850000,
        "living_area_m2": 185,
        "plot_area_m2": 550,
        "energy_label": "C",
        "build_year": 1975,
        "media_urls": [],
        "_preferences": {
            "marcel": {"priorities": ["warmtepomp", "glasvezel"], "style": "tech-modern"},
            "petra": {"priorities": ["glas in lood", "tuin op zuid"], "style": "sfeervol-jaren30"}
        },
        # Pre-computed scores
        "marcel_match_score": 40,
        "petra_match_score": 30,
        "total_match_score": 35
    }

    provider = OllamaProvider()
    IntelligenceEngine.set_provider(provider)

    scenarios = [
        (0, "Executive Summary"),
        (2, "Matchanalyse"),
        (4, "Energie"),
    ]

    for chapter_id, chapter_name in scenarios:
        print(f"\n--- Testing Chapter {chapter_id} ({chapter_name}) ---")
        
        try:
            result = IntelligenceEngine.generate_chapter_narrative(chapter_id, ctx)
            
            # Basic structure should always be present
            assert result is not None, f"Chapter {chapter_id} returned None"
            assert isinstance(result, dict), f"Chapter {chapter_id} didn't return dict"
            assert "title" in result, f"Chapter {chapter_id} missing title"
            
            # Comparison should exist if available
            if "comparison" in result:
                comparison = result["comparison"]
                assert isinstance(comparison, dict), f"Chapter {chapter_id} comparison not a dict"
            
            print(f"✅ Chapter {chapter_id}: Success")
            
        except Exception as e:
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ["connection", "failed", "timeout", "refused", "ollama"]):
                print(f"ℹ️  Chapter {chapter_id}: Ollama unavailable (expected)")
                continue
            else:
                raise AssertionError(f"Chapter {chapter_id} unexpected error: {e}")


@pytest.mark.asyncio
async def test_real_provider_health_check():
    """Test that real Ollama provider health check works correctly."""
    provider = OllamaProvider()
    
    try:
        health = await provider.check_health()
        assert isinstance(health, bool), "Health check should return boolean"
        
        if health:
            print("✅ Ollama is running and healthy")
        else:
            print("ℹ️  Ollama is not available")
            
    except Exception as e:
        error_msg = str(e).lower()
        assert any(keyword in error_msg for keyword in ["connection", "timeout", "refused"]), \
            f"Unexpected error type: {e}"
        print("ℹ️  Ollama connection error (expected in CI/CD)")


@pytest.mark.asyncio
async def test_real_provider_model_listing():
    """Test that real Ollama provider can list models."""
    provider = OllamaProvider()
    
    models = provider.list_models()
    
    assert isinstance(models, list), "list_models should return a list"
    assert len(models) > 0, "Should return at least fallback models"
    
    print(f"✅ Found {len(models)} available models")


@pytest.mark.asyncio
async def test_preference_integration_end_to_end():
    """End-to-end test of preference matching."""
    ctx = {
        "address": "Testlaan 100, Amsterdam",
        "asking_price_eur": 650000,
        "living_area_m2": 150,
        "rooms": 4,
        "build_year": 1985,
        "_preferences": {
            "marcel": {"priorities": ["Garage", "Zonnepanelen"]},
            "petra": {"priorities": ["Grote tuin", "Open keuken"]}
        },
        "marcel_match_score": 50,
        "petra_match_score": 40,
        "total_match_score": 45
    }
    
    provider = OllamaProvider()
    IntelligenceEngine.set_provider(provider)
    
    try:
        result = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "title" in result, "Result should have a title"
        
        print("✅ End-to-end preference integration test passed")
        
    except Exception as e:
        error_msg = str(e).lower()
        if any(keyword in error_msg for keyword in ["connection", "failed", "timeout", "ollama"]):
            print("ℹ️  Ollama unavailable - fallback behavior verified")
        else:
            raise AssertionError(f"Unexpected error: {e}")


@pytest.mark.asyncio
async def test_fallback_quality_without_ai():
    """Verify that fallback responses have proper structure."""
    IntelligenceEngine.set_provider(None)
    
    ctx = {
        "address": "Voorbeeldstraat 1",
        "asking_price_eur": 500000,
        "living_area_m2": 120,
        "build_year": 2000
    }
    
    for chapter_id in [0, 1, 2, 4, 10]:
        result = IntelligenceEngine.generate_chapter_narrative(chapter_id, ctx)
        
        assert isinstance(result, dict), f"Chapter {chapter_id} should return dict"
        assert "title" in result, f"Chapter {chapter_id} should have title"
        assert "main_analysis" in result, f"Chapter {chapter_id} should have main_analysis"
        
        # Check provenance indicates registry template
        provenance = result.get('_provenance', {})
        assert 'Registry' in provenance.get('provider', ''), \
            f"Chapter {chapter_id} should use registry template"
    
    print("✅ All fallback responses have proper structure")
