# AI Woning Rapport - AI Provider Integration Guide

**Version**: 2.0
**Last Updated**: 2025-12-20

---

## 1. Overview

AI Woning Rapport supports multiple AI providers through a unified interface. This allows switching between local (Ollama) and cloud providers (OpenAI, Anthropic, Gemini) without code changes.

### Supported Providers

| Provider | Type | API Key Required | Best For |
|----------|------|------------------|----------|
| **Ollama** | Local | No | Privacy, offline use, no API costs |
| **OpenAI** | Cloud | Yes | GPT-4 quality, fast responses |
| **Anthropic** | Cloud | Yes | Claude models, long context |
| **Gemini** | Cloud | Yes | Google integration, multimodal |

---

## 2. Provider Interface

All providers implement the `AIProvider` abstract base class:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: str = "",
        model: str = None,
        json_mode: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate text completion.

        Args:
            prompt: User prompt
            system: System prompt (context/instructions)
            model: Model ID (uses default if None)
            json_mode: Force JSON output format
            options: Provider-specific options (temperature, etc.)

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models for this provider"""
        pass

    @abstractmethod
    def check_health(self) -> bool:
        """Check if provider is available and responding"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (ollama, openai, etc.)"""
        pass
```

---

## 3. Provider Implementations

### 3.1 Ollama Provider

**Location:** `backend/ai/providers/ollama_provider.py`

**Configuration:**
```python
OLLAMA_BASE_URL=http://localhost:11434  # or http://ollama:11434 in Docker
```

**URL Detection Priority:**
1. `OLLAMA_BASE_URL` environment variable
2. Docker environment detection (`/.dockerenv` file) → `http://ollama:11434`
3. Fallback → `http://localhost:11434`

**Recommended Models:**
- `llama3` - General purpose, good quality
- `qwen2.5-coder:7b` - Code and technical content
- `mistral` - Fast, efficient

**Example:**
```python
from ai.providers.ollama_provider import OllamaProvider

provider = OllamaProvider()
response = await provider.generate(
    prompt="Analyze this property data...",
    system="You are a real estate consultant...",
    model="llama3"
)
```

### 3.2 OpenAI Provider

**Location:** `backend/ai/providers/openai_provider.py`

**Configuration:**
```python
OPENAI_API_KEY=sk-...
```

**Recommended Models:**
- `gpt-4o` - Best quality, multimodal
- `gpt-4-turbo` - Fast, high quality
- `gpt-3.5-turbo` - Budget option

**Example:**
```python
from ai.providers.openai_provider import OpenAIProvider

provider = OpenAIProvider(api_key="sk-...")
response = await provider.generate(
    prompt="Analyze this property...",
    system="You are a real estate consultant...",
    model="gpt-4o",
    json_mode=True
)
```

### 3.3 Anthropic Provider

**Location:** `backend/ai/providers/anthropic_provider.py`

**Configuration:**
```python
ANTHROPIC_API_KEY=sk-ant-...
```

**Recommended Models:**
- `claude-3-5-sonnet-20241022` - Best balance
- `claude-3-opus-20240229` - Highest quality
- `claude-3-haiku-20240307` - Fastest

**Example:**
```python
from ai.providers.anthropic_provider import AnthropicProvider

provider = AnthropicProvider(api_key="sk-ant-...")
response = await provider.generate(
    prompt="Analyze this property...",
    system="You are a real estate consultant...",
    model="claude-3-5-sonnet-20241022"
)
```

### 3.4 Gemini Provider

**Location:** `backend/ai/providers/gemini_provider.py`

**Configuration:**
```python
GEMINI_API_KEY=...
```

**Recommended Models:**
- `gemini-1.5-pro` - Best quality
- `gemini-1.5-flash` - Fast, efficient
- `gemini-pro` - Standard

**Example:**
```python
from ai.providers.gemini_provider import GeminiProvider

provider = GeminiProvider(api_key="...")
response = await provider.generate(
    prompt="Analyze this property...",
    system="You are a real estate consultant...",
    model="gemini-1.5-pro",
    json_mode=True
)
```

---

## 4. Provider Factory

The `ProviderFactory` handles provider instantiation and selection:

```python
from ai.provider_factory import ProviderFactory
from config.settings import get_settings

settings = get_settings()
provider = ProviderFactory.get_provider(settings)

# Or get a specific provider
ollama = ProviderFactory.get_provider_by_name("ollama")
```

### Fallback Chain

When `ai_fallback_enabled` is `True`, the system attempts providers in order:

1. **Configured provider** (from settings)
2. **Ollama** (if available locally)
3. **Hardcoded fallback** (no AI, uses static content)

---

## 5. Adding a New Provider

To add a new AI provider:

### Step 1: Create Provider Class

```python
# backend/ai/providers/new_provider.py

from ai.provider_interface import AIProvider
from typing import List, Dict, Any, Optional

class NewProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = SomeSDK(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        system: str = "",
        model: str = None,
        json_mode: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        # Implementation
        pass

    def list_models(self) -> List[str]:
        return ["model-1", "model-2"]

    def check_health(self) -> bool:
        try:
            # Ping the service
            return True
        except:
            return False

    @property
    def name(self) -> str:
        return "new_provider"
```

### Step 2: Register in Factory

```python
# backend/ai/provider_factory.py

from ai.providers.new_provider import NewProvider

PROVIDERS = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
    "new_provider": NewProvider,  # Add here
}
```

### Step 3: Add Configuration

```python
# backend/config/settings.py

class AppSettings(BaseSettings):
    # ...
    new_provider_api_key: Optional[str] = None
```

### Step 4: Add to Frontend Settings

Update `frontend/src/components/settings/AIProviderSettings.tsx` to include the new provider option.

---

## 6. Error Handling

All providers should handle errors gracefully:

```python
try:
    response = await provider.generate(prompt, system)
except ProviderTimeoutError:
    # AI generation timed out
    logger.error("Provider timeout")
    return fallback_content
except ProviderConnectionError:
    # Cannot reach provider
    logger.error("Provider unavailable")
    return fallback_content
except ProviderAuthError:
    # Invalid API key
    raise ConfigurationError("Invalid API key for provider")
```

---

## 7. Testing Providers

### Unit Tests

Comprehensive tests for all providers are located in:
`backend/tests/unit/test_providers.py`

Run with:
```bash
pytest backend/tests/unit/test_providers.py
```

### Mock Provider for Testing

```python
# backend/tests/mocks/mock_provider.py

class MockAIProvider(AIProvider):
    def __init__(self, responses: Dict[str, str] = None):
        self.responses = responses or {}

    async def generate(self, prompt, system="", **kwargs) -> str:
        return self.responses.get(prompt, "Mock response")

    def list_models(self) -> List[str]:
        return ["mock-model"]

    def check_health(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return "mock"
```

---

## 8. Performance Considerations

| Provider | Avg Latency | Cost | Context Length |
|----------|-------------|------|----------------|
| Ollama (llama3) | 2-5s | Free | 8K tokens |
| OpenAI (gpt-4o) | 1-3s | $0.01/1K tokens | 128K tokens |
| Anthropic (claude-3.5) | 1-3s | $0.003/1K tokens | 200K tokens |
| Gemini (1.5-pro) | 1-2s | $0.00125/1K tokens | 1M tokens |

**Recommendation:** Start with Ollama for development, switch to cloud providers for production quality.
