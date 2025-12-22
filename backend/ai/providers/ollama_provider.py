import httpx
import os
import logging
import base64
from typing import List, Dict, Any, Optional

from ..provider_interface import AIProvider

logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    """
    Ollama AI provider implementation.
    Handles model listing and text generation using a local Ollama instance.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize the Ollama provider.

        Args:
            base_url: Optional base URL for Ollama API. If not provided, will auto-detect.
            timeout: Request timeout in seconds (default: 30)
        """
        if base_url is None:
            # Priority order:
            # 1. Explicit environment variable
            # 2. Detect Docker environment
            # 3. Fallback to localhost

            if os.environ.get("OLLAMA_BASE_URL"):
                base_url = os.environ.get("OLLAMA_BASE_URL")
                logger.info(f"Using OLLAMA_BASE_URL from environment: {base_url}")
            elif os.path.exists("/.dockerenv"):
                # Running inside Docker container
                base_url = "http://ollama:11434"  # Docker Compose service name
                logger.info("Detected Docker environment, using service name: ollama")
            else:
                # Local development
                base_url = "http://localhost:11434"
                logger.info("Local development mode, using localhost")
        else:
            logger.info(f"Using provided base_url: {base_url}")

        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.tags_endpoint = f"{self.base_url}/api/tags"

    @property
    def name(self) -> str:
        """
        Provider identifier.

        Returns:
            Provider name string
        """
        return "ollama"

    async def check_health(self) -> bool:
        """
        Check if the Ollama server is reachable.

        Returns:
            True if provider is accessible, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.base_url)
                return response.status_code == 200
        except httpx.RequestError as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """
        List available models on the local Ollama instance.

        Returns:
            List of model names/identifiers
        """
        try:
            # Use synchronous httpx.Client for list_models since interface is not async
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(self.tags_endpoint)
                response.raise_for_status()
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to list Ollama models - HTTP error: {e}")
            return []
        except httpx.RequestError as e:
            logger.error(f"Failed to list Ollama models - Request error: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
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
        Generate text using the specified model (supports multimodal).

        Args:
            prompt: The user prompt/message
            system: System prompt/instructions
            model: Model name (defaults to "llama3" if not provided)
            json_mode: Whether to force JSON output (requires model support)
            options: Additional Ollama options (temperature, etc.)

        Returns:
            Generated text response
        """
        # Default model if not specified
        if model is None:
            model = "llama3"

        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
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
                        else:
                            logger.warning(f"Ollama image path not found: {img_path}")
                    except Exception as e:
                        logger.error(f"Failed to encode image {img_path} for Ollama: {e}")
            if b64_images:
                payload["images"] = b64_images

        if options:
            payload["options"] = options

        try:
            logger.info(f"Sending request to Ollama ({model})...")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.generate_endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.TimeoutException:
            logger.error(f"Ollama request timed out after {self.timeout} seconds.")
            return f"Error: AI generation timed out after {self.timeout} seconds."
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama request failed with HTTP error: {e}")
            return f"Error: AI generation failed (HTTP {e.response.status_code})."
        except httpx.RequestError as e:
            logger.error(f"Ollama request failed: {e}")
            return f"Error: AI generation failed ({str(e)})."
        except Exception as e:
            logger.error(f"Unexpected error during Ollama generation: {e}", exc_info=True)
            return f"Error: AI generation failed ({str(e)})."
