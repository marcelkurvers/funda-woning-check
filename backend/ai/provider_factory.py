import os
import logging
from typing import Optional, Dict, Type, Any
from .provider_interface import AIProvider
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.gemini_provider import GeminiProvider
from .providers.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)

class ProviderFactory:
    """
    Factory for creating AI provider instances.
    Supports both environment-driven and explicit configuration.
    """

    _registry: Dict[str, Type[AIProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
        "ollama": OllamaProvider
    }

    @classmethod
    def create_provider(cls, name: Optional[str] = None, **kwargs) -> AIProvider:
        """
        Creates an AI provider instance.
        
        Args:
            name: Provider name (openai, anthropic, gemini, ollama). 
                  If None, uses AI_PROVIDER env var.
            **kwargs: Config parameters like api_key, base_url, timeout.
        """
        provider_name = (name or os.getenv("AI_PROVIDER", "openai")).lower()
        
        provider_class = cls._registry.get(provider_name)
        if not provider_class:
            raise ValueError(
                f"Unsupported AI_PROVIDER: '{provider_name}'. "
                f"Supported: {list(cls._registry.keys())}"
            )

        # Ensure timeout is present
        if 'timeout' not in kwargs:
            kwargs['timeout'] = int(os.getenv("AI_TIMEOUT", "180"))

        logger.info(f"Factory: Creating {provider_name} provider (Config: {list(kwargs.keys())})")
        
        try:
            # We filter kwargs based on the provider's needs if necessary, 
            # but our providers are flexible with their __init__ or we can just pass them.
            # Most of our providers take (api_key/base_url, timeout).
            
            if provider_name == 'ollama':
                # Ollama uses base_url instead of api_key
                return provider_class(
                    base_url=kwargs.pop('base_url', None),
                    timeout=kwargs.pop('timeout', 180),
                    model=kwargs.pop('model', None),
                    **kwargs
                )
            else:
                # API-based providers
                return provider_class(
                    api_key=kwargs.pop('api_key', None),
                    timeout=kwargs.pop('timeout', 180),
                    model=kwargs.pop('model', None),
                    **kwargs
                )
        except Exception as e:
            logger.error(f"Failed to instantiate {provider_name} provider: {e}")
            raise
            
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[AIProvider]):
        """Allows extension of the factory with new providers"""
        cls._registry[name] = provider_class

    @classmethod
    def list_providers(cls) -> Dict[str, Any]:
        """Returns metadata about registered providers for the UI"""
        return {
            "openai": {
                "name": "openai",
                "label": "OpenAI",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-preview", "o1-mini"]
            },
            "anthropic": {
                "name": "anthropic",
                "label": "Anthropic",
                "models": ["claude-3-5-sonnet-20240620", "claude-3-haiku-20240307", "claude-3-opus-20240229"]
            },
            "gemini": {
                "name": "gemini",
                "label": "Google Gemini",
                "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-3-fast", "gemini-3-pro", "gemini-3-thinking"]
            },
            "ollama": {
                "name": "ollama",
                "label": "Ollama (Local)",
                "models": ["llama3", "mistral", "phi3", "nomic-embed-text", "llama3.1"]
            }
        }

def register_providers():
    """Legacy compatibility helper"""
    pass
