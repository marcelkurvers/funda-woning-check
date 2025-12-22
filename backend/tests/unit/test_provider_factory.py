"""
Tests for AI provider factory and registry (ProviderFactory, ProviderRegistry)
"""
import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# Create proper exception classes for mocked modules (must match test_providers.py)
class MockAPITimeoutError(Exception):
    pass

class MockAPIError(Exception):
    pass

class MockAPIConnectionError(Exception):
    pass

class MockRateLimitError(Exception):
    pass

class MockAPIStatusError(Exception):
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code = status_code

# Mock optional dependencies before importing providers
mock_anthropic = MagicMock()
mock_anthropic.APITimeoutError = MockAPITimeoutError
mock_anthropic.APIError = MockAPIError
mock_anthropic.APIConnectionError = MockAPIConnectionError
mock_anthropic.RateLimitError = MockRateLimitError
mock_anthropic.APIStatusError = MockAPIStatusError
sys.modules['anthropic'] = mock_anthropic

sys.modules['openai'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.genai'] = MagicMock()
sys.modules['google.genai.types'] = MagicMock()

from ai.provider_factory import ProviderFactory
from ai.provider_interface import AIProvider
from ai.providers.ollama_provider import OllamaProvider
from ai.providers.openai_provider import OpenAIProvider
from ai.providers.anthropic_provider import AnthropicProvider
from ai.providers.gemini_provider import GeminiProvider


# ============================================================================
# ProviderRegistry Tests
# ============================================================================

class TestProviderRegistry:
    """Tests for ProviderFactory Registry logic"""

    def test_list_providers_returns_all_registered(self):
        """Test list_providers returns all registered provider metadata"""
        providers = ProviderFactory.list_providers()

        assert "ollama" in providers
        assert "openai" in providers
        assert "anthropic" in providers
        assert "gemini" in providers
        assert len(providers) >= 4

    def test_registry_contains_correct_classes(self):
        """Test that the internal registry has the correct classes"""
        assert ProviderFactory._registry["ollama"] is OllamaProvider
        assert ProviderFactory._registry["openai"] is OpenAIProvider
        assert ProviderFactory._registry["anthropic"] is AnthropicProvider
        assert ProviderFactory._registry["gemini"] is GeminiProvider

    def test_register_new_provider(self):
        """Test registering a new provider class"""
        # Create a mock provider class
        class TestProvider(AIProvider):
            @property
            def name(self):
                return "test"

            async def generate(self, prompt, system="", model=None, json_mode=False, **kwargs):
                return "test"

            def list_models(self):
                return ["test-model"]

            async def check_health(self):
                return True

        # Register it
        ProviderFactory.register_provider("test_provider", TestProvider)

        # Verify it's registered
        assert "test_provider" in ProviderFactory._registry
        assert ProviderFactory._registry["test_provider"] is TestProvider

        # Clean up
        del ProviderFactory._registry["test_provider"]


# ============================================================================
# ProviderFactory Tests
# ============================================================================

class TestProviderFactory:
    """Tests for ProviderFactory"""

    def test_create_ollama_provider_default(self):
        """Test creating Ollama provider with defaults"""
        provider = ProviderFactory.create_provider("ollama")

        assert isinstance(provider, OllamaProvider)
        assert provider.name == "ollama"
        assert provider.timeout == 180

    def test_create_ollama_provider_custom_url(self):
        """Test creating Ollama provider with custom base URL"""
        provider = ProviderFactory.create_provider(
            "ollama",
            base_url="http://custom-ollama:9999"
        )

        assert isinstance(provider, OllamaProvider)
        assert provider.base_url == "http://custom-ollama:9999"

    def test_create_ollama_provider_custom_timeout(self):
        """Test creating Ollama provider with custom timeout"""
        provider = ProviderFactory.create_provider(
            "ollama",
            timeout=60
        )

        assert isinstance(provider, OllamaProvider)
        assert provider.timeout == 60

    def test_create_openai_provider_with_api_key(self):
        """Test creating OpenAI provider with API key"""
        provider = ProviderFactory.create_provider(
            "openai",
            api_key="test-openai-key"
        )

        assert isinstance(provider, OpenAIProvider)
        assert provider.name == "openai"
        assert provider.api_key == "test-openai-key"

    def test_create_openai_provider_without_api_key_raises_error(self):
        """Test creating OpenAI provider without API key raises ValueError"""
        with pytest.raises(ValueError, match="OPENAI_API_KEY must be set"):
            ProviderFactory.create_provider("openai")

    def test_create_anthropic_provider_with_api_key(self):
        """Test creating Anthropic provider with API key"""
        provider = ProviderFactory.create_provider(
            "anthropic",
            api_key="test-anthropic-key"
        )

        assert isinstance(provider, AnthropicProvider)
        assert provider.name == "anthropic"
        assert provider.api_key == "test-anthropic-key"

    def test_create_anthropic_provider_without_api_key_raises_error(self):
        """Test creating Anthropic provider without API key raises ValueError"""
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY must be set"):
            ProviderFactory.create_provider("anthropic")

    def test_create_gemini_provider_with_api_key(self):
        """Test creating Gemini provider with API key"""
        with patch("google.generativeai.configure"):
            provider = ProviderFactory.create_provider(
                "gemini",
                api_key="test-gemini-key"
            )

            assert isinstance(provider, GeminiProvider)
            assert provider.name == "gemini"
            assert provider.api_key == "test-gemini-key"

    def test_create_gemini_provider_without_api_key_raises_error(self):
        """Test creating Gemini provider without API key raises ValueError"""
        with pytest.raises(ValueError, match="GEMINI_API_KEY or GOOGLE_API_KEY must be set"):
            ProviderFactory.create_provider("gemini")

    def test_create_unknown_provider_raises_error(self):
        """Test creating unknown provider raises ValueError with helpful message"""
        with pytest.raises(ValueError) as exc_info:
            ProviderFactory.create_provider("nonexistent")

        error_message = str(exc_info.value)
        assert "Unsupported AI_PROVIDER: 'nonexistent'" in error_message
        assert "Supported:" in error_message
        assert "ollama" in error_message
        assert "openai" in error_message
        assert "anthropic" in error_message
        assert "gemini" in error_message

    def test_create_provider_with_extra_kwargs(self):
        """Test creating provider with additional keyword arguments"""
        provider = ProviderFactory.create_provider(
            "ollama",
            timeout=45,
            base_url="http://custom:8080"
        )

        assert isinstance(provider, OllamaProvider)
        assert provider.timeout == 45
        assert provider.base_url == "http://custom:8080"

    def test_create_all_providers_with_valid_config(self):
        """Test that all providers can be created with valid configuration"""
        with patch("google.generativeai.configure"):
            # Ollama (no API key needed)
            ollama = ProviderFactory.create_provider("ollama")
            assert isinstance(ollama, OllamaProvider)

            # OpenAI (needs API key)
            openai = ProviderFactory.create_provider("openai", api_key="test-key")
            assert isinstance(openai, OpenAIProvider)

            # Anthropic (needs API key)
            anthropic = ProviderFactory.create_provider("anthropic", api_key="test-key")
            assert isinstance(anthropic, AnthropicProvider)

            # Gemini (needs API key)
            gemini = ProviderFactory.create_provider("gemini", api_key="test-key")
            assert isinstance(gemini, GeminiProvider)

    def test_provider_factory_respects_timeout_parameter(self):
        """Test that timeout parameter is properly passed to all providers"""
        with patch("google.generativeai.configure"):
            custom_timeout = 120

            ollama = ProviderFactory.create_provider("ollama", timeout=custom_timeout)
            assert ollama.timeout == custom_timeout

            openai = ProviderFactory.create_provider("openai", api_key="key", timeout=custom_timeout)
            assert openai.timeout == custom_timeout

            anthropic = ProviderFactory.create_provider("anthropic", api_key="key", timeout=custom_timeout)
            assert anthropic.timeout == custom_timeout

            gemini = ProviderFactory.create_provider("gemini", api_key="key", timeout=custom_timeout)
            assert gemini.timeout == custom_timeout


# ============================================================================
# Integration Tests
# ============================================================================

class TestFactoryRegistryIntegration:
    """Tests for factory and registry working together"""

    def test_factory_uses_registry_for_provider_lookup(self):
        """Test that factory properly uses registry for provider class lookup"""
        # Create provider through factory
        provider = ProviderFactory.create_provider("ollama")

        # Verify it's the same class as from registry
        provider_class = ProviderFactory._registry.get("ollama")
        assert isinstance(provider, provider_class)

    def test_custom_provider_can_be_registered_and_created(self):
        """Test that custom providers can be registered and created via factory"""
        # Define a custom provider that accepts api_key (since factory requires it for non-ollama providers)
        class CustomProvider(AIProvider):
            def __init__(self, api_key=None, timeout=30, **kwargs):
                self.api_key = api_key
                self.timeout = timeout
                self.custom_arg = kwargs.get("custom_arg", "default")

            @property
            def name(self):
                return "custom"

            async def generate(self, prompt, system="", model=None, json_mode=False, options=None):
                return "custom response"

            def list_models(self):
                return ["custom-model-1", "custom-model-2"]

            async def check_health(self):
                return True
                
            async def close(self):
                pass

        # Register the custom provider
        ProviderFactory.register_provider("custom", CustomProvider)

        try:
            # Create it using the factory (need to provide api_key since it's not "ollama")
            provider = ProviderFactory.create_provider(
                "custom",
                api_key="test-api-key",
                timeout=60,
                custom_arg="test_value"
            )

            # Verify it was created correctly
            assert isinstance(provider, CustomProvider)
            assert provider.name == "custom"
            assert provider.api_key == "test-api-key"
            assert provider.timeout == 60
            assert provider.custom_arg == "test_value"
            assert "custom-model-1" in provider.list_models()

        finally:
            # Clean up
            if "custom" in ProviderFactory._registry:
                del ProviderFactory._registry["custom"]

    def test_all_registered_providers_can_be_created(self):
        """Test that every registered provider can be created via factory"""
        with patch("google.generativeai.configure"):
            providers = list(ProviderFactory._registry.keys())

            for provider_name in providers:
                # Prepare arguments based on provider type
                kwargs = {}
                if provider_name != "ollama":
                    kwargs["api_key"] = "test-key"

                # Create the provider
                provider = ProviderFactory.create_provider(provider_name, **kwargs)

                # Verify it implements the interface
                assert isinstance(provider, AIProvider)
                assert provider.name == provider_name
                assert callable(provider.generate)
                assert callable(provider.list_models)
                assert callable(provider.check_health)


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestProviderFactoryErrorHandling:
    """Tests for error handling in provider factory"""

    def test_none_provider_name_raises_error(self):
        """Test that None as provider name raises helpful error"""
        with pytest.raises(Exception):  # Will be caught by registry lookup
            ProviderFactory.create_provider(None)

    def test_empty_provider_name_raises_error(self):
        """Test that empty string as provider name raises helpful error"""
        with pytest.raises(ValueError, match="OPENAI_API_KEY must be set"):
            ProviderFactory.create_provider("")

    def test_case_sensitive_provider_names(self):
        """Test that provider names are case-handled (forced lowercase)"""
        # Should NOT raise because factory calls .lower()
        ollama = ProviderFactory.create_provider("Ollama")
        assert ollama.name == "ollama"

        # Should also NOT raise because factory calls .lower()
        openai = ProviderFactory.create_provider("OPENAI", api_key="key")
        assert openai.name == "openai"

    def test_helpful_error_message_lists_available_providers(self):
        """Test that error message for unknown provider lists available options"""
        try:
            ProviderFactory.create_provider("invalid_provider")
        except ValueError as e:
            error_msg = str(e)
            assert "Unsupported AI_PROVIDER: 'invalid_provider'" in error_msg
            assert "Supported:" in error_msg

            # Should list all available providers
            providers = list(ProviderFactory._registry.keys())
            for provider in providers:
                assert provider in error_msg
