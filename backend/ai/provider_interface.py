from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class AIProvider(ABC):
    """
    Abstract base class for all AI providers.
    Ensures a unified async interface for Gemini, OpenAI, and Anthropic.
    """

    @abstractmethod
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
        Generate text completion (optionally with images for multimodal models)

        Args:
            prompt: The user prompt/message
            model: Optional model override (fallback to provider default/env)
            system: System prompt/instructions
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            json_mode: Whether to force JSON output
            images: List of local file paths or URLs to images

        Returns:
            Generated text response as plain string
        """
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """
        Check if provider is available and healthy
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Provider identifier (e.g., 'ollama', 'openai', 'anthropic', 'gemini')
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available recommended models for this provider
        """
        pass

    @abstractmethod
    async def close(self):
        """
        Cleanup and close any persistent resources (e.g., HTTP clients)
        """
        pass
