from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class AIProvider(ABC):
    """Abstract base class for all AI providers"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: str = "",
        model: str = None,
        images: List[str] = None,
        json_mode: bool = False,
        options: Dict[str, Any] = None
    ) -> str:
        """
        Generate text completion (optionally with images for multimodal models)

        Args:
            prompt: The user prompt/message
            system: System prompt/instructions
            model: Model name (provider-specific)
            images: List of local file paths or URLs to images
            json_mode: Whether to force JSON output
            options: Provider-specific options (temperature, max_tokens, etc.)

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models for this provider

        Returns:
            List of model names/identifiers
        """
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """
        Check if provider is available and healthy

        Returns:
            True if provider is accessible, False otherwise
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Provider identifier (e.g., 'ollama', 'openai', 'anthropic', 'gemini')

        Returns:
            Provider name string
        """
        pass
