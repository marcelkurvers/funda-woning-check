import anthropic
import logging
from typing import List, Dict, Any, Optional

from ..provider_interface import AIProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    """
    Anthropic (Claude) AI provider implementation.
    Handles model listing and text generation using Anthropic's Claude models.
    """

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize Anthropic provider

        Args:
            api_key: Anthropic API key
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key
        self.timeout = timeout
        self.client = anthropic.AsyncAnthropic(
            api_key=api_key,
            timeout=timeout
        )
        logger.info("Anthropic provider initialized")

    async def generate(
        self,
        prompt: str,
        system: str = "",
        model: str = None,
        json_mode: bool = False,
        options: Dict[str, Any] = None
    ) -> str:
        """
        Generate text completion using Anthropic's Claude models

        Args:
            prompt: The user prompt/message
            system: System prompt/instructions
            model: Model name (defaults to claude-3-5-sonnet-20241022)
            json_mode: Whether to force JSON output
            options: Additional options (temperature, max_tokens, etc.)

        Returns:
            Generated text response
        """
        if options is None:
            options = {}

        # Default model
        if model is None:
            model = "claude-3-5-sonnet-20241022"

        # Anthropic requires max_tokens
        max_tokens = options.get("max_tokens", 4096)

        # Build messages array
        messages = [{"role": "user", "content": prompt}]

        # Prepare request parameters
        request_params = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages
        }

        # Add system prompt if provided
        if system:
            request_params["system"] = system

        # Add temperature if provided
        if "temperature" in options:
            request_params["temperature"] = options["temperature"]

        # Handle JSON mode
        if json_mode:
            # Append JSON instruction to system prompt
            json_instruction = "\n\nYou must respond with valid JSON only. Do not include any explanation or text outside the JSON structure."
            if "system" in request_params:
                request_params["system"] += json_instruction
            else:
                request_params["system"] = json_instruction.strip()

        # Make API call
        try:
            logger.info(f"Sending request to Anthropic ({model})...")
            response = await self.client.messages.create(**request_params)

            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text

            logger.warning("Anthropic response had no content")
            return ""
        except anthropic.APITimeoutError:
            logger.error(f"Anthropic request timed out after {self.timeout} seconds.")
            return f"Error: AI generation timed out after {self.timeout} seconds."
        except anthropic.APIConnectionError as e:
            logger.error(f"Anthropic connection error: {e}")
            return f"Error: AI generation failed (connection error)."
        except anthropic.RateLimitError as e:
            logger.error(f"Anthropic rate limit exceeded: {e}")
            return f"Error: AI generation failed (rate limit exceeded)."
        except anthropic.APIStatusError as e:
            logger.error(f"Anthropic request failed with status {e.status_code}: {e}")
            return f"Error: AI generation failed (HTTP {e.status_code})."
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            return f"Error: AI generation failed ({str(e)})."
        except Exception as e:
            logger.error(f"Unexpected error during Anthropic generation: {e}", exc_info=True)
            return f"Error: AI generation failed ({str(e)})."

    def list_models(self) -> List[str]:
        """
        List available Anthropic models

        Returns:
            List of Claude model identifiers
        """
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]

    async def check_health(self) -> bool:
        """
        Check if Anthropic API is accessible

        Returns:
            True if provider is accessible, False otherwise
        """
        try:
            # Make a minimal API call to test connectivity
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use fastest/cheapest model
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except anthropic.APIError as e:
            logger.error(f"Anthropic health check failed (API error): {e}")
            return False
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False

    @property
    def name(self) -> str:
        """
        Provider identifier

        Returns:
            "anthropic"
        """
        return "anthropic"
