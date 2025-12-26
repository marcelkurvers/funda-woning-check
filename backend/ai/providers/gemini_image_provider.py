"""
GEMINI IMAGE GENERATION PROVIDER

Implements image generation using Google's Gemini/Imagen API.
This is SEPARATE from text generation (GeminiProvider).

SUPPORTED MODELS:
- gemini-2.0-flash-exp (with image generation capability)
- imagen-3.0-generate-001 (dedicated image model)

FAIL-LOUD: All errors return explicit status, never silent failure.
"""

import os
import logging
import base64
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

from google import genai
from google.genai import types

from backend.ai.image_provider_interface import (
    ImageGenerationProvider,
    ImageGenerationRequest,
    ImageGenerationResult,
    ImageGenerationStatus,
)

logger = logging.getLogger(__name__)


class GeminiImageProvider(ImageGenerationProvider):
    """
    Google Gemini/Imagen image generation provider.
    
    Uses the google-genai SDK to generate images from prompts.
    Supports both Gemini multimodal and dedicated Imagen models.
    """
    
    # Default model for image generation - "Gemini 3 Pro" / "Nano Banana"
    DEFAULT_MODEL = "gemini-2.0-flash-exp" 
    
    # Models known to support image generation (including aliases)
    IMAGE_CAPABLE_MODELS = {
        "gemini-2.0-flash-exp",
        "imagen-3.0-generate-001",
        "gemini-3.0-pro-exp",
        "gemini-3-pro-image-preview", # Alias
        "gemini-2.5-flash-image",     # Alias
        "nano-banana",                 # Alias
        "nano-banana-pro",             # Alias
    }
    
    # Internal mapping to actual Google GenAI Runtime IDs
    MODEL_ID_MAPPING = {
        "gemini-3-pro-image-preview": "gemini-2.0-flash-exp", # "Nano Banana Pro"
        "gemini-2.5-flash-image": "gemini-2.0-flash-exp",     # "Nano Banana"
        "nano-banana": "gemini-2.0-flash-exp",
        "nano-banana-pro": "gemini-2.0-flash-exp", 
        # Future proofing:
        "gemini-3.0-pro-exp": "gemini-2.0-flash-exp", 
    }
    
    # Static directory for generated images
    STATIC_DIR = Path(__file__).parent.parent.parent / "static" / "generated"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        save_to_disk: bool = True
    ):
        """
        Initialize Gemini image provider.
        
        Args:
            api_key: Gemini API key (MUST be provided by AIAuthority)
            model: Model to use for generation
            save_to_disk: Whether to save images to disk (vs base64 only)
        """
        # API key MUST be provided by AIAuthority - no fallback to os.getenv
        self.api_key = api_key
        
        # Determine model config
        config_model = model or self.DEFAULT_MODEL
        
        # Enforce image capability (Step 1)
        if config_model not in self.IMAGE_CAPABLE_MODELS:
            logger.warning(
                f"Configured model '{config_model}' is not in known image-capable list: {self.IMAGE_CAPABLE_MODELS}. "
                "Generation may fail or fall back."
            )
            
        self._model = config_model
        # Resolve actual runtime ID
        self._runtime_model = self.MODEL_ID_MAPPING.get(config_model, config_model)
        self.save_to_disk = save_to_disk
        self.client = None
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"GeminiImageProvider initialized with model: {self._model}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
    
    @property
    def provider_name(self) -> str:
        return "gemini_imagen"
    
    @property
    def model_name(self) -> str:
        return self._model
    
    def is_configured(self) -> bool:
        """Check if API key is present."""
        return bool(self.api_key)
    
    async def check_availability(self) -> bool:
        """Check if provider is available and working."""
        if not self.client:
            return False
        try:
            # Quick health check
            async for _ in self.client.aio.models.list(config={'page_size': 1}):
                return True
            return False
        except Exception as e:
            logger.error(f"Gemini availability check failed: {e}")
            return False
    
    async def generate_image(
        self,
        request: ImageGenerationRequest
    ) -> ImageGenerationResult:
        """
        Generate an image using Gemini.
        
        FAIL-LOUD: Returns explicit failure status with error details.
        """
        # Check configuration
        if not self.is_configured():
            logger.warning("GeminiImageProvider: No API key configured")
            return ImageGenerationResult(
                status=ImageGenerationStatus.NO_PROVIDER,
                provider_name=self.provider_name,
                model_name=self.model_name,
                prompt=request.prompt,
                error_message="GEMINI_API_KEY not configured. Image generation disabled.",
                generation_metadata={
                    "visual_type": request.visual_type,
                    "data_used": request.data_used,
                }
            )

        # Enforce image capability strict check at runtime
        if self._model not in self.IMAGE_CAPABLE_MODELS:
            logger.error(f"GeminiImageProvider: Model {self._model} does not support image generation")
            return ImageGenerationResult(
                status=ImageGenerationStatus.FAILED,
                provider_name=self.provider_name,
                model_name=self.model_name,
                prompt=request.prompt,
                error_message=f"Configured Gemini model '{self._model}' does not support image generation",
                generation_metadata={
                    "visual_type": request.visual_type,
                    "model_capability_check": "failed"
                }
            )
        
        if not self.client:
            logger.error("GeminiImageProvider: Client not initialized")
            return ImageGenerationResult(
                status=ImageGenerationStatus.FAILED,
                provider_name=self.provider_name,
                model_name=self.model_name,
                prompt=request.prompt,
                error_message="Gemini client initialization failed",
                generation_metadata={
                    "visual_type": request.visual_type,
                    "data_used": request.data_used,
                }
            )
        
        try:
            logger.info(f"Generating image: type={request.visual_type}, data_fields={len(request.data_used)}")
            
            # Build the generation prompt
            full_prompt = self._build_image_prompt(request)
            
            # Configure for image generation
            config = types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                temperature=0.7,
            )
            
            # Create a FRESH client for this request to avoid event loop/transport issues
            # across threads (since this runs in safe_execute_async)
            local_client = genai.Client(api_key=self.api_key)
            
            logger.info(f"GeminiImageProvider: Generating with runtime model {self._runtime_model} (mapped from {self._model})")
            
            # Generate content
            response = await local_client.aio.models.generate_content(
                model=self._runtime_model,
                contents=full_prompt,
                config=config,
            )
            
            # Extract image from response
            image_data = None
            mime_type = "image/png"
            
            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        mime_type = part.inline_data.mime_type or "image/png"
                        break
            
            if not image_data:
                logger.warning("GeminiImageProvider: No image in response")
                return ImageGenerationResult(
                    status=ImageGenerationStatus.FAILED,
                    provider_name=self.provider_name,
                    model_name=self.model_name,
                    prompt=request.prompt,
                    error_message="Model did not return an image. Response may have been text-only.",
                    generation_metadata={
                        "visual_type": request.visual_type,
                        "data_used": request.data_used,
                        "response_text": response.text if hasattr(response, 'text') else None,
                    }
                )
            
            # Save to disk if configured
            image_uri = None
            image_base64 = None
            
            if self.save_to_disk:
                image_uri = await self._save_image(image_data, request, mime_type)
            else:
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            logger.info(f"Image generated successfully: uri={image_uri}")
            
            # Capability Reporting - Success
            from backend.ai.capability_manager import get_capability_manager, CapabilityState
            get_capability_manager().report_status(
                "image_generation", 
                CapabilityState.AVAILABLE, 
                "System fully operational"
            )
            
            return ImageGenerationResult(
                status=ImageGenerationStatus.GENERATED,
                provider_name=self.provider_name,
                model_name=self.model_name,
                prompt=request.prompt,
                image_uri=image_uri,
                image_base64=image_base64,
                generation_metadata={
                    "visual_type": request.visual_type,
                    "data_used": request.data_used,
                    "title": request.title,
                    "insight_summary": request.insight_summary,
                    "mime_type": mime_type,
                }
            )
            
        except Exception as e:
            logger.error(f"GeminiImageProvider generation failed: {e}")
            
            # Capability Reporting - with enhanced user messages
            from backend.ai.capability_manager import get_capability_manager, CapabilityState, StatusCategory
            manager = get_capability_manager()
            
            # Detect Quota Limits
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                manager.report_status(
                    "image_generation", 
                    CapabilityState.QUOTA_EXCEEDED, 
                    message="Google Gemini API quota exceeded (Nano Banana). Please try again later.",
                    category=StatusCategory.OPERATIONALLY_LIMITED,  # Explicit: NOT an implementation error
                    resume_hint="Quota typically resets within 24 hours."
                )
            else:
                manager.report_status(
                    "image_generation", 
                    CapabilityState.OFFLINE, 
                    message=f"Provider error: {error_str}",
                    category=StatusCategory.OPERATIONALLY_LIMITED  # External provider issue
                )

            return ImageGenerationResult(
                status=ImageGenerationStatus.FAILED,
                provider_name=self.provider_name,
                model_name=self.model_name,
                prompt=request.prompt,
                error_message=str(e),
                generation_metadata={
                    "visual_type": request.visual_type,
                    "data_used": request.data_used,
                    "exception_type": type(e).__name__,
                }
            )
    
    def _build_image_prompt(self, request: ImageGenerationRequest) -> str:
        """Build a detailed prompt for image generation."""
        prompt_parts = [
            f"Create a professional {request.visual_type} visualization.",
            "",
            f"Title: {request.title}" if request.title else "",
            "",
            "Style requirements:",
            "- Clean, modern infographic design",
            "- Professional color palette (blues, greens, neutral tones)",
            "- Clear visual hierarchy",
            "- No text overlays (keep it visual)",
            "- Suitable for a real estate analysis report",
            "",
            f"Key insight to visualize: {request.insight_summary}" if request.insight_summary else "",
            "",
            "Original prompt:",
            request.prompt,
        ]
        
        return "\n".join(p for p in prompt_parts if p)
    
    async def _save_image(
        self,
        image_data: bytes,
        request: ImageGenerationRequest,
        mime_type: str
    ) -> str:
        """Save image to disk and return URI."""
        # Ensure directory exists
        self.STATIC_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        ext = "png" if "png" in mime_type else "jpg"
        filename = f"{request.visual_type}_{uuid.uuid4().hex[:8]}.{ext}"
        filepath = self.STATIC_DIR / filename
        
        # Write file
        filepath.write_bytes(image_data)
        
        # Return relative URI for frontend
        return f"/static/generated/{filename}"
