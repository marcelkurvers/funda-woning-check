"""
IMAGE PROVIDER FACTORY - Thin wrapper around AIAuthority

Factory for creating image generation provider instances.
DELEGATES to AIAuthority for all key management and provider creation.

FAIL-LOUD: Returns NoImageProvider if no valid provider configured,
never returns None or raises silently.
"""

import logging
from typing import Optional

from backend.ai.image_provider_interface import (
    ImageGenerationProvider,
    NoImageProvider,
)

logger = logging.getLogger(__name__)


# Singleton instance cache
_image_provider_instance: Optional[ImageGenerationProvider] = None


def get_image_provider(force_new: bool = False) -> ImageGenerationProvider:
    """
    Get or create the image generation provider.
    
    DELEGATES TO AIAuthority - does not read API keys directly.
    
    FAIL-LOUD:
    - If GEMINI_API_KEY is set → returns GeminiImageProvider
    - If no key is set → returns NoImageProvider (explicit failure)
    - Never returns None
    
    Args:
        force_new: Force creation of new instance (for testing)
        
    Returns:
        ImageGenerationProvider instance
    """
    global _image_provider_instance
    
    if _image_provider_instance is not None and not force_new:
        return _image_provider_instance
    
    # Use AIAuthority as single source of truth
    from backend.ai.ai_authority import get_ai_authority
    authority = get_ai_authority()
    
    _image_provider_instance = authority.create_image_provider()
    
    if _image_provider_instance.is_configured():
        logger.info(f"Image provider: {_image_provider_instance.provider_name} configured")
    else:
        logger.warning("Image provider: No API key found, using NoImageProvider")
    
    return _image_provider_instance


def is_image_generation_available() -> bool:
    """
    Check if image generation is available.
    
    Returns:
        True if a real image provider is configured
    """
    provider = get_image_provider()
    return provider.is_configured()


def get_image_provider_status() -> dict:
    """
    Get status information about the image provider.
    
    Returns:
        Dict with provider status for UI display
    """
    provider = get_image_provider()
    
    # Get key status from AIAuthority
    from backend.ai.ai_authority import get_ai_authority
    authority = get_ai_authority()
    gemini_key = authority.get_api_key("gemini")
    
    return {
        "provider_name": provider.provider_name,
        "model_name": provider.model_name,
        "is_configured": provider.is_configured(),
        "api_key_present": bool(gemini_key),
    }


def reset_image_provider():
    """Reset the singleton instance (for testing)."""
    global _image_provider_instance
    _image_provider_instance = None
