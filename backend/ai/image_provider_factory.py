"""
IMAGE PROVIDER FACTORY

Factory for creating image generation provider instances.
Manages provider selection and configuration validation.

FAIL-LOUD: Returns NoImageProvider if no valid provider configured,
never returns None or raises silently.
"""

import os
import logging
from typing import Optional

from backend.ai.image_provider_interface import (
    ImageGenerationProvider,
    NoImageProvider,
)
from backend.ai.providers.gemini_image_provider import GeminiImageProvider

logger = logging.getLogger(__name__)


# Singleton instance cache
_image_provider_instance: Optional[ImageGenerationProvider] = None


def get_image_provider(force_new: bool = False) -> ImageGenerationProvider:
    """
    Get or create the image generation provider.
    
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
    
    # Check for Gemini API key
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if gemini_key:
        logger.info("Image provider: Gemini configured")
        _image_provider_instance = GeminiImageProvider(api_key=gemini_key)
    else:
        logger.warning("Image provider: No API key found, using NoImageProvider")
        _image_provider_instance = NoImageProvider()
    
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
    
    return {
        "provider_name": provider.provider_name,
        "model_name": provider.model_name,
        "is_configured": provider.is_configured(),
        "api_key_present": bool(
            os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        ),
    }


def reset_image_provider():
    """Reset the singleton instance (for testing)."""
    global _image_provider_instance
    _image_provider_instance = None
