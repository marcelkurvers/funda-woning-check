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
    Refined Ollama AI provider implementation.
    Handles model selection via environment variables and ensures async correctness.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 120):
        """
        Initialize the Ollama provider.
        Priority:
        1. Environment variable OLLAMA_BASE_URL
        2. Detected Docker environment
        3. Localhost
        """
        if not base_url:
            base_url = os.environ.get("OLLAMA_BASE_URL")
            
        if not base_url:
            if os.path.exists("/.dockerenv"):
                base_url = "http://ollama:11434"
            else:
                base_url = "http://localhost:11434"

        self.base_url = base_url.rstrip('/')
        
        # Read timeout from env or use provided default (120s)
        env_timeout = os.environ.get("OLLAMA_TIMEOUT")
        self.timeout = int(env_timeout) if env_timeout else timeout
        
        # Default model: mistral (as per requirements)
        self.model = os.environ.get("OLLAMA_MODEL", "mistral")
        
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.tags_endpoint = f"{self.base_url}/api/tags"
        
        logger.info(f"OllamaProvider: base={self.base_url}, model={self.model}, timeout={self.timeout}s")

    @property
    def name(self) -> str:
        return "ollama"

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.base_url)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """Synchronous listing of models (interface requirement)"""
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
        Streaming is ALWAYS disabled.
        Only the OLLAMA_MODEL environment variable or explicit override is used.
        """
        # Selection priority: 1. Method argument, 2. Env variable (self.model)
        selected_model = model if model else self.model
        
        payload = {
            "model": selected_model,
            "prompt": prompt,
            "system": system,
            "stream": False,  # Mandatory: disabled streaming
        }

        if json_mode:
            payload["format"] = "json"

        if images:
            b64_images = []
            async with httpx.AsyncClient(timeout=10.0) as client:
                for img_path in images:
                    try:
                        if img_path.startswith(('http://', 'https://')):
                            resp = await client.get(img_path)
                            resp.raise_for_status()
                            b64_images.append(base64.b64encode(resp.content).decode('utf-8'))
                        elif os.path.exists(img_path):
                            with open(img_path, "rb") as f:
                                b64_images.append(base64.b64encode(f.read()).decode('utf-8'))
                    except Exception as e:
                        logger.warning(f"Failed to process image {img_path}: {e}")
            if b64_images:
                payload["images"] = b64_images

        if options:
            payload["options"] = options

        logger.info(f"Ollama Request: model={selected_model} (Timeout: {self.timeout}s)")
        
        try:
            # Use httpx.AsyncClient to ensure non-blocking I/O in async context
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(self.generate_endpoint, json=payload)
                
                if response.status_code != 200:
                    error_msg = f"Ollama Error {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                data = response.json()
                answer = data.get("response")
                
                if answer is None:
                    raise RuntimeError("Ollama returned invalid JSON (missing 'response' field)")
                
                return str(answer)
                
        except httpx.TimeoutException:
            logger.error(f"Ollama request timed out after {self.timeout}s")
            raise TimeoutError(f"Ollama request timed out after {self.timeout}s")
        except Exception as e:
            logger.error(f"Ollama Pipeline Failure: {e}")
            raise # Fail fast, do not return partial data
