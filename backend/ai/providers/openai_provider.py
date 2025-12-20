import os
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import openai

from ..provider_interface import AIProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """
    OpenAI AI provider implementation.
    Handles model listing and text generation using OpenAI's GPT models.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key (falls back to OPENAI_API_KEY env var)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OpenAI API key not provided")
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")

        self.timeout = timeout
        self.client = AsyncOpenAI(api_key=self.api_key, timeout=timeout)
        self._name = "openai"
        logger.info("OpenAI provider initialized")

    async def generate(
        self,
        prompt: str,
        system: str = "",
        model: str = None,
        json_mode: bool = False,
        options: Dict[str, Any] = None
    ) -> str:
        """
        Generate text completion using OpenAI's GPT models

        Args:
            prompt: The user prompt/message
            system: System prompt/instructions
            model: Model name (defaults to gpt-4o)
            json_mode: Whether to force JSON output
            options: Additional options (temperature, max_tokens, etc.)

        Returns:
            Generated text response
        """
        if options is None:
            options = {}

        # Default model
        if model is None:
            model = "gpt-4o"

        # Build messages array
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Prepare request parameters
        request_params = {
            "model": model,
            "messages": messages
        }

        # Add optional parameters
        if "temperature" in options:
            request_params["temperature"] = options["temperature"]

        if "max_tokens" in options:
            request_params["max_tokens"] = options["max_tokens"]

        if "top_p" in options:
            request_params["top_p"] = options["top_p"]

        if "frequency_penalty" in options:
            request_params["frequency_penalty"] = options["frequency_penalty"]

        if "presence_penalty" in options:
            request_params["presence_penalty"] = options["presence_penalty"]

        if "stop" in options:
            request_params["stop"] = options["stop"]

        # Handle JSON mode
        if json_mode:
            request_params["response_format"] = {"type": "json_object"}
            # Add JSON instruction to system prompt
            json_instruction = "You must respond with valid JSON only."
            if system:
                messages[0]["content"] += f"\n\n{json_instruction}"
            else:
                messages.insert(0, {"role": "system", "content": json_instruction})

        # Make API call
        try:
            logger.info(f"Sending request to OpenAI ({model})...")
            response = await self.client.chat.completions.create(**request_params)

            # Extract text from response
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content or ""

            logger.warning("OpenAI response had no content")
            return ""
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}", exc_info=True)
            return f"Error: AI generation failed ({str(e)})."

    def list_models(self) -> List[str]:
        """
        List available OpenAI models

        Returns:
            List of GPT model identifiers
        """
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]

    async def check_health(self) -> bool:
        """
        Check if OpenAI API is accessible

        Returns:
            True if provider is accessible, False otherwise
        """
        try:
            # Make a minimal API call to test connectivity
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use fastest/cheapest model
                max_tokens=5,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return response is not None
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False

    @property
    def name(self) -> str:
        """
        Provider identifier

        Returns:
            "openai"
        """
        return self._name
