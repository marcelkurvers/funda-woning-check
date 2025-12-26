"""
IMAGE GENERATION PROVIDER INTERFACE

This module defines the abstract interface for image generation providers.
Image generation is SEPARATE from text generation - different infrastructure.

FAIL-LOUD PRINCIPLE:
- If image generation fails → return failure status, never silent fallback
- If no API key configured → return explicit not_applicable_reason
- All errors must be visible in diagnostics

SUPPORTED PROVIDERS:
- Gemini (via Imagen API or Gemini multimodal)
- Future: DALL-E, Stable Diffusion, etc.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ImageGenerationStatus(Enum):
    """Status of image generation attempt."""
    PENDING = "pending"
    GENERATED = "generated"
    FAILED = "failed"
    SKIPPED = "skipped"
    NO_PROVIDER = "no_provider"


@dataclass
class ImageGenerationResult:
    """
    Result of an image generation attempt.
    
    FAIL-LOUD: This dataclass always contains status information.
    Never returns None or empty without explanation.
    """
    status: ImageGenerationStatus
    provider_name: Optional[str] = None
    model_name: Optional[str] = None
    prompt: str = ""
    image_uri: Optional[str] = None
    image_base64: Optional[str] = None
    error_message: Optional[str] = None
    generation_metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "status": self.status.value,
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "prompt": self.prompt,
            "image_uri": self.image_uri,
            "image_base64": self.image_base64,
            "error_message": self.error_message,
            "generation_metadata": self.generation_metadata,
        }


@dataclass
class ImageGenerationRequest:
    """
    Request for image generation.
    
    All requests MUST include:
    - prompt: The generation prompt
    - data_used: Registry field IDs used to construct the prompt
    - visual_type: Type of visual (infographic, diagram, etc.)
    """
    prompt: str
    visual_type: str  # infographic, diagram, comparison_visual, timeline
    data_used: List[str]  # Registry field IDs
    title: str = ""
    insight_summary: str = ""
    uncertainties: List[str] = None
    
    def __post_init__(self):
        if self.uncertainties is None:
            self.uncertainties = []


class ImageGenerationProvider(ABC):
    """
    Abstract base class for image generation providers.
    
    SEPARATION: This is DISTINCT from AIProvider (text generation).
    Image generation requires different API endpoints and handling.
    
    FAIL-LOUD: All implementations must:
    - Return explicit failure status, never silent degradation
    - Log all generation attempts
    - Include provider metadata in results
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier (e.g., 'gemini_imagen', 'dalle')."""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model being used for generation."""
        pass
    
    @abstractmethod
    async def generate_image(
        self,
        request: ImageGenerationRequest
    ) -> ImageGenerationResult:
        """
        Generate an image from the request.
        
        Args:
            request: Image generation request with prompt and metadata
            
        Returns:
            ImageGenerationResult with status, image data or error
            
        FAIL-LOUD: Never raise silently. Always return a result with status.
        """
        pass
    
    @abstractmethod
    async def check_availability(self) -> bool:
        """
        Check if this provider is available and configured.
        
        Returns:
            True if API key is set and provider is reachable
        """
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """
        Check if API key / credentials are configured.
        
        Returns:
            True if credentials are present (doesn't verify they work)
        """
        pass


class NoImageProvider(ImageGenerationProvider):
    """
    Fallback provider when no real provider is configured.
    
    FAIL-LOUD: This provider always returns NOT_APPLICABLE status
    with clear reason. It never silently fails.
    """
    
    @property
    def provider_name(self) -> str:
        return "none"
    
    @property
    def model_name(self) -> str:
        return "none"
    
    async def generate_image(
        self,
        request: ImageGenerationRequest
    ) -> ImageGenerationResult:
        """Always returns NO_PROVIDER status with explanation."""
        logger.warning("NoImageProvider: Image generation requested but no provider configured")
        return ImageGenerationResult(
            status=ImageGenerationStatus.NO_PROVIDER,
            provider_name=self.provider_name,
            model_name=self.model_name,
            prompt=request.prompt,
            error_message="No image generation provider configured. Set GEMINI_API_KEY to enable image generation.",
            generation_metadata={
                "visual_type": request.visual_type,
                "data_used": request.data_used,
            }
        )
    
    async def check_availability(self) -> bool:
        return False
    
    def is_configured(self) -> bool:
        return False
