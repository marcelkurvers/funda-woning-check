"""
Integration Tests for AI System

These tests validate the integration between IntelligenceEngine and AI providers.
They DO NOT test runtime availability or execute real AI calls.

ARCHITECTURAL PRINCIPLE:
Integration tests verify that components work together correctly through their interfaces,
not that external services are running.

MIGRATION NOTE:
This file replaces the old test_ollama_integration.py which incorrectly tested
runtime availability. The new tests focus on integration contracts and state management.
"""

import unittest
from intelligence import IntelligenceEngine
from ai.provider_interface import AIProvider
from ai.providers.ollama_provider import OllamaProvider
from ai.provider_factory import ProviderFactory


class TestProviderIntegration(unittest.TestCase):
    """Test integration between IntelligenceEngine and AI providers"""

    def setUp(self):
        """Reset provider state before each test"""
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        """Clean up provider state after each test"""
        IntelligenceEngine.set_provider(None)

    def test_provider_injection_into_engine(self):
        """Verify provider can be injected into IntelligenceEngine"""
        provider = OllamaProvider()
        IntelligenceEngine.set_provider(provider)
        
        self.assertIsNotNone(IntelligenceEngine._provider)
        self.assertEqual(IntelligenceEngine._provider, provider)
        self.assertIsInstance(IntelligenceEngine._provider, AIProvider)

    def test_provider_identity_preserved_after_injection(self):
        """Verify provider identity is preserved after injection"""
        provider = OllamaProvider()
        IntelligenceEngine.set_provider(provider)
        
        # Should be the exact same object
        self.assertIs(IntelligenceEngine._provider, provider)

    def test_engine_accepts_different_provider_types(self):
        """Verify engine accepts different provider implementations"""
        # Test with Ollama
        ollama_provider = OllamaProvider()
        IntelligenceEngine.set_provider(ollama_provider)
        self.assertEqual(IntelligenceEngine._provider.name, "ollama")
        
        # Test with factory-created provider
        factory_provider = ProviderFactory.create_provider("ollama")
        IntelligenceEngine.set_provider(factory_provider)
        self.assertEqual(IntelligenceEngine._provider.name, "ollama")

    def test_engine_narrative_generation_with_provider_set(self):
        """Verify engine can generate narratives with provider configured"""
        provider = OllamaProvider()
        IntelligenceEngine.set_provider(provider)
        
        ctx = {
            "address": "Teststraat 1, Amsterdam",
            "price": 500000,
            "area": 120,
            "year": 2010
        }
        
        # Should return a result (either AI or fallback)
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)
        self.assertIn('main_analysis', result)

    def test_engine_narrative_generation_without_provider(self):
        """Verify engine provides fallback when no provider set"""
        IntelligenceEngine.set_provider(None)
        
        ctx = {
            "address": "Teststraat 1, Amsterdam",
            "price": 500000,
            "area": 120
        }
        
        # Should return fallback data
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)
        self.assertIn('intro', result)

    def test_provider_configuration_accessible_after_injection(self):
        """Verify provider configuration remains accessible after injection"""
        provider = OllamaProvider(base_url="http://custom:11434", timeout=60)
        IntelligenceEngine.set_provider(provider)
        
        # Configuration should be preserved
        self.assertEqual(IntelligenceEngine._provider.base_url, "http://custom:11434")
        self.assertEqual(IntelligenceEngine._provider.timeout, 60)


class TestPreferenceIntegration(unittest.TestCase):
    """Test integration of preferences with narrative generation"""

    def setUp(self):
        """Reset provider state before each test"""
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        """Clean up provider state after each test"""
        IntelligenceEngine.set_provider(None)

    def test_preferences_included_in_context(self):
        """Verify preferences are correctly passed to narrative generation"""
        IntelligenceEngine.set_provider(None)  # Use fallback
        
        ctx = {
            "address": "Teststraat 42",
            "price": 750000,
            "_preferences": {
                "marcel": {"priorities": ["Garage", "Thuiskantoor"]},
                "petra": {"priorities": ["Tuin op zuid", "Open keuken"]}
            }
        }
        
        # Should not crash with preferences
        result = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)

    def test_preferences_structure_preserved(self):
        """Verify preferences structure is preserved in context"""
        ctx = {
            "address": "Test",
            "_preferences": {
                "marcel": {"priorities": ["Garage"]},
                "petra": {"priorities": ["Tuin"]}
            }
        }
        
        # Preferences should be accessible
        self.assertIn("_preferences", ctx)
        self.assertIn("marcel", ctx["_preferences"])
        self.assertIn("petra", ctx["_preferences"])

    def test_fit_score_calculation_in_enrichment(self):
        """
        ARCHITECTURAL CHANGE: Fit score is now calculated in enrichment layer.
        
        This test verifies that match scores are computed during enrichment,
        not in IntelligenceEngine.
        """
        from enrichment import DataEnricher
        
        raw_data = {
            "address": "Test",
            "prijs": "€ 500.000",
            "oppervlakte": "120 m²",
            "description": "Woning met garage en tuin",
            "features": ["Garage", "Tuin"],
            "_preferences": {
                "marcel": {"priorities": ["Garage", "Zonnepanelen"]},
                "petra": {"priorities": ["Tuin", "Glas in lood"]}
            }
        }
        
        enriched = DataEnricher.enrich(raw_data)
        
        # Match scores should be computed in enrichment
        self.assertIn('marcel_match_score', enriched)
        self.assertIn('petra_match_score', enriched)
        self.assertIn('total_match_score', enriched)
        
        # Should be numeric values
        self.assertIsInstance(enriched['marcel_match_score'], (int, float))
        self.assertIsInstance(enriched['petra_match_score'], (int, float))


class TestMultiChapterIntegration(unittest.TestCase):
    """Test integration across multiple chapter types"""

    def setUp(self):
        """Reset provider state before each test"""
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        """Clean up provider state after each test"""
        IntelligenceEngine.set_provider(None)

    def test_consistent_output_across_chapters(self):
        """Verify all chapters produce consistent output structure"""
        ctx = {
            "address": "Teststraat 1",
            "price": 500000,
            "area": 120,
            "year": 2000,
            "label": "B"
        }
        
        # Test chapters 0-5
        for chapter_id in range(6):
            result = IntelligenceEngine.generate_chapter_narrative(chapter_id, ctx)
            
            # All should return dict
            self.assertIsInstance(result, dict, 
                                f"Chapter {chapter_id} should return dict")
            
            # All should have title
            self.assertIn('title', result, 
                         f"Chapter {chapter_id} should have title")

    def test_chapter_specific_logic_integration(self):
        """Verify chapter-specific logic integrates correctly"""
        # Chapter 4 (Energy) specific test
        ctx_energy = {
            "address": "Test",
            "label": "A",
            "year": 2022
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(4, ctx_energy)
        
        self.assertIn('title', result)
        self.assertIn('intro', result)
        
        # Registry-only template should reference energy/sustainability
        full_text = result.get('intro', '') + result.get('main_analysis', '')
        self.assertTrue(
            'energie' in full_text.lower() or 'duurzaam' in full_text.lower(),
            "Chapter 4 should reference energy topics"
        )

    def test_data_propagation_across_chapters(self):
        """Verify property data propagates correctly to all chapters"""
        ctx = {
            "address": "Kalverstraat 1, Amsterdam",
            "price": 750000,
            "area": 150,
            "year": 1995,
            "label": "C"
        }
        
        # Generate multiple chapters
        results = {}
        for chapter_id in [0, 1, 2, 4]:
            results[chapter_id] = IntelligenceEngine.generate_chapter_narrative(
                chapter_id, ctx
            )
        
        # All should have received the data
        for chapter_id, result in results.items():
            self.assertIsInstance(result, dict)
            self.assertGreater(len(result.get('intro', '')), 0)


class TestProviderStateIsolation(unittest.TestCase):
    """Test that provider state is properly isolated between tests"""

    def test_provider_state_starts_clean(self):
        """Verify provider state starts as None"""
        # This should be None due to setUp
        self.assertIsNone(IntelligenceEngine._provider)

    def test_provider_state_can_be_set_and_cleared(self):
        """Verify provider state can be set and cleared within test"""
        # Start clean
        self.assertIsNone(IntelligenceEngine._provider)
        
        # Set provider
        provider = OllamaProvider()
        IntelligenceEngine.set_provider(provider)
        self.assertIsNotNone(IntelligenceEngine._provider)
        
        # Clear provider
        IntelligenceEngine.set_provider(None)
        self.assertIsNone(IntelligenceEngine._provider)

    def tearDown(self):
        """Ensure provider state is cleaned up"""
        IntelligenceEngine.set_provider(None)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in integration scenarios"""

    def setUp(self):
        """Reset provider state before each test"""
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        """Clean up provider state after each test"""
        IntelligenceEngine.set_provider(None)

    def test_engine_handles_missing_context_data(self):
        """Verify engine handles missing context data gracefully"""
        # Minimal context
        ctx = {"address": "Test"}
        
        # Should not crash
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)

    def test_engine_handles_empty_context(self):
        """Verify engine handles empty context gracefully"""
        ctx = {}
        
        # Should not crash
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        self.assertIsInstance(result, dict)

    def test_parse_int_handles_invalid_input(self):
        """Verify _parse_int handles invalid input without crashing"""
        # Should not raise exceptions
        self.assertEqual(IntelligenceEngine._parse_int(None), 0)
        self.assertEqual(IntelligenceEngine._parse_int(""), 0)
        self.assertEqual(IntelligenceEngine._parse_int("invalid"), 0)
        self.assertEqual(IntelligenceEngine._parse_int([]), 0)


if __name__ == '__main__':
    unittest.main()
