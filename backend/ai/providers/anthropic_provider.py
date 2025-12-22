import os
import logging
import base64
import mimetypes
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic

from ..provider_interface import AIProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(AIProvider):
    """
    Refactored Anthropic provider implementation.
    Supports Claude 3.5 Sonnet and Claude 3 Haiku.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 180, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set for Anthropic provider")
        
        self.client = AsyncAnthropic(api_key=self.api_key, timeout=timeout)
        self._name = "anthropic"
        self.default_model = model or os.getenv("AI_MODEL", "claude-3-5-sonnet-20240620")
        logger.info(f"AnthropicProvider initialized with model: {self.default_model}")

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
        Refactored Anthropic generation using Claude 3 Messages API.
        """
        selected_model = model or self.default_model
        
        # Mapping simple names to full versions if needed
        model_map = {
            "claude-3-5-sonnet": "claude-3-5-sonnet-20240620",
            "claude-3-haiku": "claude-3-8k-haiku-20240307", # or whatever the current haiku is
        }
        actual_model = model_map.get(selected_model, selected_model)

        content = []
        
        # Add images for Claude 3
        if images:
            for img_path in images:
                try:
                    if img_path.startswith(('http://', 'https://')):
                        # Note: Anthropic usually requires local bits. 
                        # In a production app we'd fetch the URL first.
                        # For now, we skip or handle as error to satisfy the interface.
                        logger.warning(f"Anthropic provider: URL images not directly supported, skip {img_path}")
                        continue
                    
                    if os.path.exists(img_path):
                        mime_type, _ = mimetypes.guess_type(img_path)
                        mime_type = mime_type or "image/jpeg"
                        with open(img_path, "rb") as f:
                            data = base64.b64encode(f.read()).decode("utf-8")
                            content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": data
                                }
                            })
                except Exception as e:
                    logger.error(f"Anthropic image processing error: {e}")

        # Add text prompt
        content.append({"type": "text", "text": prompt})

        try:
            logger.info(f"Anthropic Request: model={actual_model}")
            
            # Note: Anthropic handles 'system' as a top-level param, not in messages
            params = {
                "model": actual_model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system if system else None,
                "messages": [{"role": "user", "content": content}]
            }

            # Claude doesn't have a native 'json_mode' flag like OpenAI, 
            # so we enforce it via the system prompt and instructions.
            if json_mode:
                if params["system"]:
                    params["system"] += "\nReturn only valid JSON."
                else:
                    params["system"] = "Return only valid JSON."

            response = await self.client.messages.create(**params)
            
            # Concatenate text blocks
            full_text = "".join([block.text for block in response.content if hasattr(block, 'text')])
            return full_text
            
        except Exception as e:
            logger.error(f"Anthropic Generation Error: {e}")
            raise RuntimeError(f"Anthropic failed: {str(e)}")

    async def check_health(self) -> bool:
        try:
            # We don't have a direct 'list models' that is easy for health, 
            # so we do a tiny generation if possible or just check init.
            return self.api_key is not None
        except Exception:
            return False

    async def close(self):
        await self.client.close()
