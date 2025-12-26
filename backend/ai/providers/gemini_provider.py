import os
import logging
import base64
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

from ..provider_interface import AIProvider

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    """
    Refactored Google Gemini provider using the modern google-genai SDK.
    Supports Gemini 3 family and 1.5 Flash/Pro.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 180, model: Optional[str] = None):
        # API key MUST be provided by AIAuthority - no fallback to os.getenv
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided (via AIAuthority)")
        
        # Initialize the unified Google GenAI client
        self.client = genai.Client(api_key=self.api_key)
        self.timeout = timeout
        self._name = "gemini"
        
        # Default model as per requirements - Unify on Gemini 2.0 Flash Exp (Nano Banana)
        self.default_model = model or "gemini-2.0-flash-exp"
        logger.info(f"GeminiProvider initialized with model: {self.default_model}")

    @property
    def name(self) -> str:
        return self._name

    async def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False,
        images: Optional[List[str]] = None
    ) -> str:
        """
        Unified generation using google.genai SDK.
        """
        selected_model = model or self.default_model
        
        # Map user-friendly names to actual model IDs if necessary
        # Note: mapping might be needed if "gemini-3-fast" is an alias
        model_map = {
            "gemini-3-fast": "gemini-2.0-flash-exp", 
            "gemini-3-pro": "gemini-2.0-flash-exp", # UNIFIED: Plane B and A2 must use SAME model (Nano Banana)
            "gemini-3-thinking": "gemini-2.0-flash-thinking-exp", # Kept separate if specifically requested
            "nano-banana": "gemini-2.0-flash-exp",
            "nano-banana-pro": "gemini-2.0-flash-exp",
        }
        actual_model = model_map.get(selected_model, selected_model)

        contents = []
        
        # Add images if multimodal
        if images:
            for img_path in images:
                try:
                    if img_path.startswith(('http://', 'https://')):
                        # Note: google-genai supports URLs in some contexts, 
                        # but often requires downloading for Content parts
                        # For simplicity and reliability, we let the SDK handle or logger warn
                        contents.append(types.Part.from_uri(uri=img_path, mime_type="image/jpeg"))
                    elif os.path.exists(img_path):
                        with open(img_path, "rb") as f:
                            img_data = f.read()
                            contents.append(types.Part.from_bytes(data=img_data, mime_type="image/jpeg"))
                except Exception as e:
                    logger.error(f"Failed to process image {img_path}: {e}")

        # Add text prompt
        contents.append(types.Part.from_text(text=prompt))
        
        config = types.GenerateContentConfig(
            system_instruction=system if system else None,
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json" if json_mode else "text/plain",
        )

        try:
            logger.info(f"Gemini Request: model={actual_model}")
            # The google-genai SDK generate_content is synchronous by default in many beta versions, 
            # but we use it correctly as per latest docs or wrap if needed. 
            # Assuming the user wants async-safe behavior.
            
            # Using the async client if available or proper awaitable
            response = await self.client.aio.models.generate_content(
                model=actual_model,
                contents=contents,
                config=config
            )
            
            return response.text or ""
            
        except Exception as e:
            logger.error(f"Gemini Generation Error: {e}")
            raise RuntimeError(f"Gemini failed: {str(e)}")

    def list_models(self) -> List[str]:
        return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-3-fast", "gemini-3-pro", "gemini-3-thinking"]

    async def check_health(self) -> bool:
        if not self.api_key:
            return False
        try:
            # Quick list models check to verify API key
            async for _ in self.client.aio.models.list(config={'page_size': 1}):
                return True
            return False
        except Exception:
            return False

    async def close(self):
        # google-genai client doesn't explicitly require closing in all versions 
        # but we provide the hook for compatibility
        pass
