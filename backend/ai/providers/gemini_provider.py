import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai

from ..provider_interface import AIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """
    Google Gemini AI provider implementation.
    Handles model listing and text generation using Google's Gemini models.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize Gemini provider

        Args:
            api_key: Google API key (falls back to GOOGLE_API_KEY or GEMINI_API_KEY env var)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("Gemini API key not provided")
            raise ValueError("Gemini API key must be provided or set in GOOGLE_API_KEY or GEMINI_API_KEY environment variable")

        genai.configure(api_key=self.api_key)
        self.timeout = timeout
        self._name = "gemini"
        logger.info("Gemini provider initialized")

    async def generate(
        self,
        prompt: str,
        system: str = "",
        model: str = None,
        json_mode: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate text completion using Google's Gemini models

        Args:
            prompt: The user prompt/message
            system: System prompt/instructions (will be prepended to prompt)
            model: Model name (defaults to gemini-pro)
            json_mode: Whether to force JSON output
            options: Additional options (temperature, max_tokens, etc.)

        Returns:
            Generated text response
        """
        if options is None:
            options = {}

        # Default model
        if model is None:
            model = "gemini-pro"

        try:
            # Combine system and prompt (Gemini doesn't separate system messages)
            full_prompt = prompt
            if system:
                full_prompt = f"{system}\n\n{prompt}"

            # Add JSON instruction if needed
            if json_mode:
                json_instruction = "\n\nYou must respond with valid JSON only. Do not include any explanation or text outside the JSON structure."
                full_prompt += json_instruction

            # Build generation config from options
            generation_config = {}

            if "temperature" in options:
                generation_config["temperature"] = options["temperature"]

            if "max_tokens" in options:
                generation_config["max_output_tokens"] = options["max_tokens"]
            elif "max_output_tokens" in options:
                generation_config["max_output_tokens"] = options["max_output_tokens"]

            if "top_p" in options:
                generation_config["top_p"] = options["top_p"]

            if "top_k" in options:
                generation_config["top_k"] = options["top_k"]

            # Initialize the model
            gemini_model = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config if generation_config else None
            )

            logger.info(f"Sending request to Gemini ({model})...")

            # Generate content asynchronously
            response = await gemini_model.generate_content_async(full_prompt)

            # Extract text from response
            if response and response.text:
                return response.text

            logger.warning("Gemini response had no content")
            return ""

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}", exc_info=True)
            return f"Error: AI generation failed ({str(e)})."

    def list_models(self) -> List[str]:
        """
        List available Gemini models

        Returns:
            List of Gemini model identifiers
        """
        return [
            "gemini-pro",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]

    async def check_health(self) -> bool:
        """
        Check if Gemini API is accessible

        Returns:
            True if provider is accessible, False otherwise
        """
        try:
            # Simple check: verify API key is set and try to instantiate a model
            if not self.api_key:
                return False

            # Try to instantiate a model as a basic health check
            model = genai.GenerativeModel('gemini-pro')
            # If we get here without exception, API key is valid
            return True
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False

    @property
    def name(self) -> str:
        """
        Provider identifier

        Returns:
            "gemini"
        """
        return self._name
