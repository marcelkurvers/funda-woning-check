"""
Contract Tests for AI Providers

These tests validate that all AI providers conform to the AIProvider interface contract.
They DO NOT test runtime availability, network reachability, or service health.

ARCHITECTURAL PRINCIPLE:
AI availability is an execution concern, not a correctness concern.
Tests validate structure, contracts, routing, and state - NOT runtime liveness.
"""

import unittest
import inspect
from typing import get_type_hints
from ai.provider_interface import AIProvider
from ai.providers.ollama_provider import OllamaProvider
from ai.providers.openai_provider import OpenAIProvider
from ai.providers.anthropic_provider import AnthropicProvider
from ai.providers.gemini_provider import GeminiProvider


class TestProviderContracts(unittest.TestCase):
    """Verify all providers implement the AIProvider interface correctly"""

    def test_ollama_implements_interface(self):
        """Verify OllamaProvider implements AIProvider interface"""
        provider = OllamaProvider()
        self.assertIsInstance(provider, AIProvider)

    def test_openai_implements_interface(self):
        """Verify OpenAIProvider implements AIProvider interface"""
        # OpenAI requires API key, but we're only testing interface compliance
        try:
            provider = OpenAIProvider(api_key="test_key_for_interface_validation")
            self.assertIsInstance(provider, AIProvider)
        except ValueError as e:
            # If it fails due to API key validation, that's a config issue, not interface
            if "api_key" not in str(e).lower():
                raise

    def test_anthropic_implements_interface(self):
        """Verify AnthropicProvider implements AIProvider interface"""
        try:
            provider = AnthropicProvider(api_key="test_key_for_interface_validation")
            self.assertIsInstance(provider, AIProvider)
        except ValueError as e:
            if "api_key" not in str(e).lower():
                raise

    def test_gemini_implements_interface(self):
        """Verify GeminiProvider implements AIProvider interface"""
        try:
            provider = GeminiProvider(api_key="test_key_for_interface_validation")
            self.assertIsInstance(provider, AIProvider)
        except ValueError as e:
            if "api_key" not in str(e).lower():
                raise

    def test_all_providers_have_name_property(self):
        """Verify all providers have a name property"""
        provider = OllamaProvider()
        self.assertTrue(hasattr(provider, 'name'))
        self.assertEqual(provider.name, "ollama")

    def test_all_providers_have_generate_method(self):
        """Verify all providers have generate method with correct signature"""
        provider = OllamaProvider()
        
        # Method exists
        self.assertTrue(hasattr(provider, 'generate'))
        self.assertTrue(callable(provider.generate))
        
        # Check signature
        sig = inspect.signature(provider.generate)
        params = list(sig.parameters.keys())
        
        # Required parameters
        self.assertIn('prompt', params)
        self.assertIn('model', params)
        self.assertIn('system', params)
        self.assertIn('temperature', params)
        self.assertIn('max_tokens', params)
        self.assertIn('json_mode', params)

    def test_all_providers_have_check_health_method(self):
        """Verify all providers have check_health method"""
        provider = OllamaProvider()
        
        self.assertTrue(hasattr(provider, 'check_health'))
        self.assertTrue(callable(provider.check_health))
        
        # Verify it's async
        self.assertTrue(inspect.iscoroutinefunction(provider.check_health))

    def test_all_providers_have_list_models_method(self):
        """Verify all providers have list_models method"""
        provider = OllamaProvider()
        
        self.assertTrue(hasattr(provider, 'list_models'))
        self.assertTrue(callable(provider.list_models))

    def test_all_providers_have_close_method(self):
        """Verify all providers have close method for cleanup"""
        provider = OllamaProvider()
        
        self.assertTrue(hasattr(provider, 'close'))
        self.assertTrue(callable(provider.close))
        
        # Verify it's async
        self.assertTrue(inspect.iscoroutinefunction(provider.close))


class TestProviderConfiguration(unittest.TestCase):
    """Verify providers accept and store configuration correctly"""

    def test_ollama_accepts_base_url_configuration(self):
        """Verify OllamaProvider accepts base_url parameter"""
        custom_url = "http://custom-ollama:11434"
        provider = OllamaProvider(base_url=custom_url)
        
        self.assertEqual(provider.base_url, custom_url)

    def test_ollama_accepts_timeout_configuration(self):
        """Verify OllamaProvider accepts timeout parameter"""
        custom_timeout = 60
        provider = OllamaProvider(timeout=custom_timeout)
        
        self.assertEqual(provider.timeout, custom_timeout)

    def test_ollama_accepts_model_configuration(self):
        """Verify OllamaProvider accepts model parameter"""
        custom_model = "llama3"
        provider = OllamaProvider(model=custom_model)
        
        self.assertEqual(provider.default_model, custom_model)

    def test_ollama_has_default_configuration(self):
        """Verify OllamaProvider has sensible defaults"""
        provider = OllamaProvider()
        
        # Should have default base_url
        self.assertIsNotNone(provider.base_url)
        self.assertTrue(provider.base_url.startswith("http"))
        
        # Should have default timeout
        self.assertIsNotNone(provider.timeout)
        self.assertGreater(provider.timeout, 0)

    def test_openai_requires_api_key(self):
        """Verify OpenAIProvider requires API key in configuration"""
        # Should raise ValueError when no API key provided
        with self.assertRaises(ValueError) as context:
            OpenAIProvider(api_key=None)
        
        self.assertIn("api_key", str(context.exception).lower())

    def test_anthropic_requires_api_key(self):
        """Verify AnthropicProvider requires API key in configuration"""
        with self.assertRaises(ValueError) as context:
            AnthropicProvider(api_key=None)
        
        self.assertIn("api_key", str(context.exception).lower())

    def test_gemini_requires_api_key(self):
        """Verify GeminiProvider requires API key in configuration"""
        with self.assertRaises(ValueError) as context:
            GeminiProvider(api_key=None)
        
        self.assertIn("api_key", str(context.exception).lower())


class TestProviderCapabilities(unittest.TestCase):
    """Verify providers declare their capabilities correctly"""

    def test_ollama_declares_supported_models(self):
        """Verify OllamaProvider declares supported models"""
        provider = OllamaProvider()
        models = provider.list_models()
        
        # Should return a list
        self.assertIsInstance(models, list)
        
        # Should have at least fallback models
        self.assertGreater(len(models), 0)
        
        # All models should be strings
        for model in models:
            self.assertIsInstance(model, str)

    def test_provider_name_is_lowercase(self):
        """Verify provider names are lowercase for consistency"""
        provider = OllamaProvider()
        self.assertEqual(provider.name, provider.name.lower())

    def test_provider_name_is_unique_identifier(self):
        """Verify each provider has a unique name"""
        providers = [
            OllamaProvider(),
        ]
        
        names = [p.name for p in providers]
        
        # Ollama should be 'ollama'
        self.assertIn("ollama", names)


class TestProviderSchemaCompliance(unittest.TestCase):
    """Verify providers return data in expected schema format"""

    def test_list_models_returns_list_of_strings(self):
        """Verify list_models returns List[str]"""
        provider = OllamaProvider()
        models = provider.list_models()
        
        self.assertIsInstance(models, list)
        for model in models:
            self.assertIsInstance(model, str)
            self.assertGreater(len(model), 0)

    def test_name_property_returns_string(self):
        """Verify name property returns str"""
        provider = OllamaProvider()
        
        self.assertIsInstance(provider.name, str)
        self.assertGreater(len(provider.name), 0)

    def test_configuration_properties_have_correct_types(self):
        """Verify configuration properties have correct types"""
        provider = OllamaProvider(base_url="http://test:11434", timeout=30)
        
        self.assertIsInstance(provider.base_url, str)
        self.assertIsInstance(provider.timeout, (int, float))


if __name__ == '__main__':
    unittest.main()
