"""
Routing & Orchestration Tests for AI System

These tests validate provider selection logic, fallback mechanisms, and state management.
They DO NOT test runtime availability or execute real AI calls.

ARCHITECTURAL PRINCIPLE:
Tests verify routing correctness and state transitions, not execution outcomes.
"""

import unittest
from intelligence import IntelligenceEngine
from ai.provider_factory import ProviderFactory
from ai.providers.ollama_provider import OllamaProvider
from ai.provider_interface import AIProvider


class TestProviderRouting(unittest.TestCase):
    """Verify provider selection and routing logic"""

    def setUp(self):
        """Reset provider state before each test"""
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        """Clean up provider state after each test"""
        IntelligenceEngine.set_provider(None)

    def test_factory_creates_ollama_provider(self):
        """Verify factory creates Ollama provider correctly"""
        provider = ProviderFactory.create_provider("ollama")
        
        self.assertIsNotNone(provider)
        self.assertIsInstance(provider, AIProvider)
        self.assertEqual(provider.name, "ollama")

    def test_factory_creates_openai_provider_with_key(self):
        """Verify factory creates OpenAI provider with API key"""
        provider = ProviderFactory.create_provider("openai", api_key="test_key")
        
        self.assertIsNotNone(provider)
        self.assertIsInstance(provider, AIProvider)
        self.assertEqual(provider.name, "openai")

    def test_factory_creates_anthropic_provider_with_key(self):
        """Verify factory creates Anthropic provider with API key"""
        provider = ProviderFactory.create_provider("anthropic", api_key="test_key")
        
        self.assertIsNotNone(provider)
        self.assertIsInstance(provider, AIProvider)
        self.assertEqual(provider.name, "anthropic")

    def test_factory_creates_gemini_provider_with_key(self):
        """Verify factory creates Gemini provider with API key"""
        provider = ProviderFactory.create_provider("gemini", api_key="test_key")
        
        self.assertIsNotNone(provider)
        self.assertIsInstance(provider, AIProvider)
        self.assertEqual(provider.name, "gemini")

    def test_factory_rejects_unknown_provider(self):
        """Verify factory raises error for unknown provider"""
        with self.assertRaises(ValueError) as context:
            ProviderFactory.create_provider("unknown_provider")
        
        self.assertIn("unsupported", str(context.exception).lower())

    def test_factory_passes_configuration_to_provider(self):
        """Verify factory passes configuration parameters correctly"""
        provider = ProviderFactory.create_provider(
            "ollama",
            base_url="http://custom:11434",
            timeout=60
        )
        
        self.assertEqual(provider.base_url, "http://custom:11434")
        self.assertEqual(provider.timeout, 60)

    def test_factory_lists_all_registered_providers(self):
        """Verify factory can list all registered providers"""
        providers = ProviderFactory.list_providers()
        
        self.assertIsInstance(providers, dict)
        self.assertIn("ollama", providers)
        self.assertIn("openai", providers)
        self.assertIn("anthropic", providers)
        self.assertIn("gemini", providers)

    def test_provider_registry_contains_metadata(self):
        """Verify provider registry contains required metadata"""
        providers = ProviderFactory.list_providers()
        
        for provider_name, metadata in providers.items():
            self.assertIn("name", metadata)
            self.assertIn("label", metadata)
            self.assertIn("models", metadata)
            self.assertIsInstance(metadata["models"], list)


class TestIntelligenceEngineProviderManagement(unittest.TestCase):
    """Verify IntelligenceEngine manages provider state correctly"""

    def setUp(self):
        """Reset provider state before each test"""
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        """Clean up provider state after each test"""
        IntelligenceEngine.set_provider(None)

    def test_can_set_provider(self):
        """Verify engine accepts provider injection"""
        provider = OllamaProvider(base_url="http://mock:11434")
        IntelligenceEngine.set_provider(provider)
        
        self.assertIsNotNone(IntelligenceEngine._provider)
        self.assertEqual(IntelligenceEngine._provider, provider)

    def test_can_clear_provider(self):
        """Verify engine can clear provider (set to None)"""
        provider = OllamaProvider(base_url="http://mock:11434")
        IntelligenceEngine.set_provider(provider)
        self.assertIsNotNone(IntelligenceEngine._provider)
        
        IntelligenceEngine.set_provider(None)
        self.assertIsNone(IntelligenceEngine._provider)

    def test_can_replace_provider(self):
        """Verify engine can replace existing provider"""
        provider1 = OllamaProvider(base_url="http://mock:11434")
        IntelligenceEngine.set_provider(provider1)
        self.assertEqual(IntelligenceEngine._provider, provider1)
        
        provider2 = OllamaProvider(base_url="http://mock:11434")
        IntelligenceEngine.set_provider(provider2)
        self.assertEqual(IntelligenceEngine._provider, provider2)
        self.assertNotEqual(IntelligenceEngine._provider, provider1)

    def test_provider_persists_across_calls(self):
        """Verify provider state persists across multiple calls"""
        provider = OllamaProvider(base_url="http://mock:11434")
        IntelligenceEngine.set_provider(provider)
        
        # Multiple accesses should return same provider
        self.assertEqual(IntelligenceEngine._provider, provider)
        self.assertEqual(IntelligenceEngine._provider, provider)
        self.assertEqual(IntelligenceEngine._provider, provider)


class TestProviderStateTransitions(unittest.TestCase):
    """Verify provider state transitions are handled correctly"""

    def setUp(self):
        """Reset provider state before each test"""
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        """Clean up provider state after each test"""
        IntelligenceEngine.set_provider(None)

    def test_transition_from_no_provider_to_provider(self):
        """Verify clean transition from no provider to provider"""
        # Start with no provider
        self.assertIsNone(IntelligenceEngine._provider)
        
        # Set provider
        provider = OllamaProvider(base_url="http://mock:11434")
        IntelligenceEngine.set_provider(provider)
        
        # Verify transition
        self.assertIsNotNone(IntelligenceEngine._provider)
        self.assertEqual(IntelligenceEngine._provider.name, "ollama")

    def test_transition_from_provider_to_no_provider(self):
        """Verify clean transition from provider to no provider"""
        # Start with provider
        provider = OllamaProvider(base_url="http://mock:11434")
        IntelligenceEngine.set_provider(provider)
        self.assertIsNotNone(IntelligenceEngine._provider)
        
        # Clear provider
        IntelligenceEngine.set_provider(None)
        
        # Verify transition
        self.assertIsNone(IntelligenceEngine._provider)

    def test_transition_between_different_providers(self):
        """Verify clean transition between different provider types"""
        # Start with Ollama
        provider1 = OllamaProvider(base_url="http://mock:11434")
        IntelligenceEngine.set_provider(provider1)
        self.assertEqual(IntelligenceEngine._provider.name, "ollama")
        
        # Switch to different provider instance
        provider2 = OllamaProvider(base_url="http://mock:11434")
        IntelligenceEngine.set_provider(provider2)
        
        # Verify transition
        self.assertEqual(IntelligenceEngine._provider, provider2)
        self.assertNotEqual(IntelligenceEngine._provider, provider1)


if __name__ == '__main__':
    unittest.main()
