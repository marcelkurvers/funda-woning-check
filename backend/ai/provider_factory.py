"""
PROVIDER FACTORY - Thin wrapper around AIAuthority

This module provides backward-compatible factory interface for creating AI providers.
All key management and provider selection is delegated to AIAuthority.

IMPORTANT: New code should use AIAuthority.create_text_provider() directly.
This factory exists for backward compatibility only.
"""

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
    
    DEPRECATED: Prefer using AIAuthority.create_text_provider() for new code.
    This factory is maintained for backward compatibility.
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
        
        IMPORTANT: If api_key is not provided, this method will get it from AIAuthority.
        This ensures AIAuthority remains the single source of truth for keys.
        
        Args:
            name: Provider name (openai, anthropic, gemini, ollama). 
            **kwargs: Config parameters like api_key, base_url, timeout.
        """
        # Default to openai if not specified (per hierarchy requirement)
        provider_name = (name or "openai").lower()
        
        provider_class = cls._registry.get(provider_name)
        if not provider_class:
            raise ValueError(
                f"Unsupported AI_PROVIDER: '{provider_name}'. "
                f"Supported: {list(cls._registry.keys())}"
            )

        # Ensure timeout is present
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 180

        # Get API key from AIAuthority if not explicitly provided
        if provider_name != 'ollama' and 'api_key' not in kwargs:
            from backend.ai.ai_authority import get_ai_authority
            kwargs['api_key'] = get_ai_authority().get_api_key(provider_name)
        
        # Get Ollama base URL from AIAuthority if not provided
        if provider_name == 'ollama' and 'base_url' not in kwargs:
            from backend.ai.ai_authority import get_ai_authority
            kwargs['base_url'] = get_ai_authority().get_ollama_base_url()

        logger.info(f"Factory: Creating {provider_name} provider (Config: {list(kwargs.keys())})")
        
        try:
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
        """
        Returns metadata about registered providers for the UI.
        
        DEPRECATED: Use /api/ai/runtime-status endpoint instead.
        """
        # Delegate to AIAuthority for consistency
        from backend.ai.ai_authority import PROVIDER_HIERARCHY, PROVIDER_MODELS, PROVIDER_LABELS
        
        return {
            name: {
                "name": name,
                "label": PROVIDER_LABELS.get(name, name),
                "models": PROVIDER_MODELS.get(name, [])
            }
            for name in PROVIDER_HIERARCHY
        }


def register_providers():
    """Legacy compatibility helper"""
    pass

