"""
Provider Factory - Creates and manages AI provider instances
"""
from typing import Dict, Optional
from .provider_interface import AIProvider


class ProviderRegistry:
    """Registry for AI providers"""

    _providers: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, provider_class: type):
        """Register a provider class"""
        cls._providers[name] = provider_class

    @classmethod
    def get_provider_class(cls, name: str) -> Optional[type]:
        """Get a provider class by name"""
        return cls._providers.get(name)

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered provider names"""
        return list(cls._providers.keys())


class ProviderFactory:
    """Factory for creating AI provider instances"""

    @staticmethod
    def create_provider(
        provider_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ) -> AIProvider:
        """
        Create an AI provider instance

        Args:
            provider_name: Name of the provider (ollama, openai, anthropic, gemini)
            api_key: API key for cloud providers (not needed for Ollama)
            base_url: Base URL for the provider (mainly for Ollama)
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific arguments

        Returns:
            AIProvider instance

        Raises:
            ValueError: If provider is not registered or configuration is invalid
        """
        provider_class = ProviderRegistry.get_provider_class(provider_name)

        if not provider_class:
            available = ", ".join(ProviderRegistry.list_providers())
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available providers: {available}"
            )

        # Construct provider-specific arguments
        provider_kwargs = {"timeout": timeout, **kwargs}

        if provider_name == "ollama":
            if base_url:
                provider_kwargs["base_url"] = base_url
        else:
            # Cloud providers need API keys
            if not api_key:
                raise ValueError(f"API key required for {provider_name} provider")
            provider_kwargs["api_key"] = api_key

        return provider_class(**provider_kwargs)


def register_providers():
    """Register all available providers"""
    try:
        from .providers.ollama_provider import OllamaProvider
        ProviderRegistry.register("ollama", OllamaProvider)
    except ImportError:
        pass

    try:
        from .providers.openai_provider import OpenAIProvider
        ProviderRegistry.register("openai", OpenAIProvider)
    except ImportError:
        pass

    try:
        from .providers.anthropic_provider import AnthropicProvider
        ProviderRegistry.register("anthropic", AnthropicProvider)
    except ImportError:
        pass

    try:
        from .providers.gemini_provider import GeminiProvider
        ProviderRegistry.register("gemini", GeminiProvider)
    except ImportError:
        pass


# Auto-register providers on module import
register_providers()
