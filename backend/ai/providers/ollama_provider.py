import httpx
import os
import logging
import base64
from typing import List, Dict, Any, Optional

from ..provider_interface import AIProvider

logger = logging.getLogger(__name__)

class OllamaProvider(AIProvider):
    """
    Hardened Ollama AI provider implementation.
    Reuses httpx.AsyncClient and handles lifecycle safely.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 180, model: Optional[str] = None):
        # Base URL should be provided by AIAuthority.
        if not base_url:
            raise ValueError("Ollama base_url is required.")

        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.default_model = model or "llama3"  # Default model without os.environ lookup
        
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self._async_client: Optional[httpx.AsyncClient] = None
        
        logger.info(f"OllamaProvider initialized (model={self.default_model}, timeout={self.timeout}s)")

    async def _get_client(self) -> httpx.AsyncClient:
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(
                timeout=httpx.Timeout(float(self.timeout)),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
                follow_redirects=True
            )
        return self._async_client

    async def close(self):
        if self._async_client and not self._async_client.is_closed:
            await self._async_client.aclose()
            self._async_client = None

    @property
    def name(self) -> str:
        return "ollama"

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
        selected_model = model or self.default_model
        
        payload = {
            "model": selected_model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "keep_alive": 0,  # CRITICAL: Unload model after request to prevent zombie processes
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        if json_mode:
            payload["format"] = "json"

        if images:
            b64_images = []
            client_ref = await self._get_client()
            for img_path in images:
                try:
                    if img_path.startswith(('http://', 'https://')):
                        resp = await client_ref.get(img_path)
                        resp.raise_for_status()
                        b64_images.append(base64.b64encode(resp.content).decode('utf-8'))
                    elif os.path.exists(img_path):
                        with open(img_path, "rb") as f:
                            b64_images.append(base64.b64encode(f.read()).decode('utf-8'))
                except Exception as e:
                    logger.warning(f"Ollama image process failed ({img_path}): {e}")
            if b64_images:
                payload["images"] = b64_images

        try:
            client = await self._get_client()
            response = await client.post(self.generate_endpoint, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise RuntimeError(f"Ollama failed: {str(e)}")

    def list_models(self) -> List[str]:
        """
        In a real scenario, this would call /api/tags. 
        For the factory list and UI consistency, we return common recommended models.
        """
        try:
            # We use a sync request here for consistency with the interface which is sync
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    return [m["name"] for m in models]
        except Exception:
            pass
        return ["llama3", "mistral", "phi3", "nomic-embed-text", "llama3.1"]

    async def check_health(self) -> bool:
        try:
            client = await self._get_client()
            response = await client.get(self.base_url, timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False
