import requests
import json
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Client for interacting with a local Ollama instance.
    Handles model listing and text generation.
    """
    def __init__(self, base_url: Optional[str] = None):
        if base_url is None:
            # Default to environment variable or standard local address
            # In Docker on Mac, host.docker.internal is needed to reach host's localhost
            base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
            
        self.base_url = base_url.rstrip('/')
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.tags_endpoint = f"{self.base_url}/api/tags"

    def check_health(self) -> bool:
        """Checks if the Ollama server is reachable."""
        try:
            response = requests.get(self.base_url)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_models(self) -> List[str]:
        """Lists available models on the local Ollama instance."""
        try:
            response = requests.get(self.tags_endpoint)
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

    def generate(self, 
                 prompt: str, 
                 system: str = "", 
                 model: str = "llama3", 
                 json_mode: bool = False,
                 options: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates text using the specified model.
        
        Args:
            prompt: The user prompt.
            system: The system prompt (context).
            model: The model name to use.
            json_mode: Whether to force JSON output (requires model support).
            options: Additional Ollama options (temperature, etc.).
            
        Returns:
            The generated text response.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
        }
        
        if json_mode:
            payload["format"] = "json"
            
        if options:
            payload["options"] = options

        try:
            logger.info(f"Sending request to Ollama ({model})...")
            response = requests.post(self.generate_endpoint, json=payload, timeout=120) # 2 min timeout for long gens
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out.")
            return "Error: AI generation timed out."
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            return f"Error: AI generation failed ({str(e)})."
