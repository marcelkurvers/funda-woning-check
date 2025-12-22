import os
import logging
import base64
import mimetypes
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

from ..provider_interface import AIProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(AIProvider):
    """
    Hardened OpenAI provider implementation.
    Supports GPT-4o, GPT-4o-mini, and explicit parameter control.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 180, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set for OpenAI provider")
        
        # Use shared persistent client
        self.client = AsyncOpenAI(api_key=self.api_key, timeout=timeout)
        self._name = "openai"
        self.timeout = timeout
        self.default_model = model or os.getenv("AI_MODEL", "gpt-4o")
        logger.info(f"OpenAIProvider initialized with model: {self.default_model}")

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
        Refactored OpenAI generation using the latest AsyncOpenAI SDK.
        """
        selected_model = model or self.default_model
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})

        user_content = [{"type": "text", "text": prompt}]
        
        if images:
            for img_path in images:
                try:
                    if img_path.startswith(('http://', 'https://')):
                        user_content.append({
                            "type": "image_url",
                            "image_url": {"url": img_path}
                        })
                    elif os.path.exists(img_path):
                        mime_type, _ = mimetypes.guess_type(img_path)
                        mime_type = mime_type or "image/jpeg"
                        with open(img_path, "rb") as f:
                            b64_img = base64.b64encode(f.read()).decode("utf-8")
                            user_content.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime_type};base64,{b64_img}"}
                            })
                except Exception as e:
                    logger.warning(f"OpenAI image processing failed: {e}")

        messages.append({"role": "user", "content": user_content})

        params = {
            "model": selected_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if json_mode:
            params["response_format"] = {"type": "json_object"}
            # OpenAI requires 'json' in the prompt/system message for json_mode
            if "json" not in prompt.lower() and "json" not in (system or "").lower():
                if messages[0]["role"] == "system":
                    messages[0]["content"] += " Output must be in valid JSON format."
                else:
                    messages.insert(0, {"role": "system", "content": "Output must be in valid JSON format."})

        try:
            logger.info(f"OpenAI Request: model={selected_model}")
            completion = await self.client.chat.completions.create(**params)
            return completion.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI Generation Error: {e}")
            raise RuntimeError(f"OpenAI failed: {str(e)}")

    def list_models(self) -> List[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]

    async def check_health(self) -> bool:
        try:
            # Minimal call to verify connectivity
            await self.client.models.list()
            return True
        except Exception:
            return False

    async def close(self):
        await self.client.close()
