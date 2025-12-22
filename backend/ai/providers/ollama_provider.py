import httpx
import os
import logging
import base64
import asyncio
from typing import List, Dict, Any, Optional

from ..provider_interface import AIProvider

logger = logging.getLogger(__name__)

class OllamaProvider(AIProvider):
    """
    Hardened Ollama AI provider implementation.
    Reuses httpx.AsyncClient and handles lifecycle safely.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 120):
        """
        Initialize the Ollama provider.
        """
        if not base_url:
            base_url = os.environ.get("OLLAMA_BASE_URL")
            
        if not base_url:
            if os.path.exists("/.dockerenv"):
                base_url = "http://ollama:11434"
            else:
                base_url = "http://localhost:11434"

        self.base_url = base_url.rstrip('/')
        
        env_timeout = os.environ.get("OLLAMA_TIMEOUT")
        self.timeout = int(env_timeout) if env_timeout else timeout
        self.model = os.environ.get("OLLAMA_MODEL", "mistral")
        
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.tags_endpoint = f"{self.base_url}/api/tags"
        
        # Shared client instance for connection pooling (Risk 2 Mitigation)
        self._async_client: Optional[httpx.AsyncClient] = None
        
        logger.info(f"OllamaProvider initialized (model={self.model}, timeout={self.timeout}s)")

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialize and return a shared AsyncClient"""
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(
                timeout=httpx.Timeout(float(self.timeout)),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
                follow_redirects=True
            )
        return self._async_client

    async def close(self):
        """Shutdown hook for resources cleanup"""
        if self._async_client and not self._async_client.is_closed:
            await self._async_client.aclose()
            self._async_client = None
            logger.info("OllamaProvider: Shared AsyncClient closed.")

    @property
    def name(self) -> str:
        return "ollama"

    async def check_health(self) -> bool:
        try:
            client = await self._get_client()
            response = await client.get(self.base_url, timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """Synchronous listing remains using sync client to avoid loop mixing in simple calls"""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.tags_endpoint)
                response.raise_for_status()
                data = response.json()
                return [m['name'] for m in data.get('models', [])]
        except Exception as e:
            logger.error(f"Ollama list_models failed: {e}")
            return []

    async def generate(
        self,
        prompt: str,
        system: str = "",
        model: str = None,
        images: List[str] = None,
        json_mode: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate text response from Ollama.
        Reuses a shared AsyncClient for performance and resource management.
        """
        selected_model = model if model else self.model
        
        payload = {
            "model": selected_model,
            "prompt": prompt,
            "system": system,
            "stream": False,
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

        if options:
            payload["options"] = options

        logger.info(f"Ollama Request: model={selected_model} (Awaiting response...)")
        
        try:
            client = await self._get_client()
            response = await client.post(self.generate_endpoint, json=payload)
            
            if response.status_code != 200:
                error_body = response.text
                logger.error(f"Ollama Error Response: {error_body}")
                raise RuntimeError(f"Ollama server returned {response.status_code}")
            
            data = response.json()
            answer = data.get("response")
            
            if answer is None:
                raise RuntimeError("Ollama returned invalid response structure")
            
            return str(answer)
                
        except httpx.TimeoutException:
            logger.error(f"Ollama timeout after {self.timeout}s")
            raise TimeoutError(f"Ollama request timed out after {self.timeout}s")
        except Exception as e:
            logger.error(f"Ollama provider failure: {e}", exc_info=True)
            raise
