"""
AI AUTHORITY - SINGLE SOURCE OF TRUTH FOR ALL AI ORCHESTRATION

This module is the ONLY place in the codebase that:
1. Reads AI API keys from environment
2. Selects active providers
3. Determines operational status
4. Applies fallback cascade

PROVIDER HIERARCHY (STRICT):
    OpenAI (default) -> Gemini -> Claude -> Ollama (last resort)

NO OTHER MODULE may:
- Call os.getenv() for AI keys
- Select providers
- Determine model availability

All consumers MUST use AIAuthority methods.
"""

from __future__ import annotations

import os
import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================

class ProviderStatus(str, Enum):
    """Provider operational status."""
    AVAILABLE = "available"
    QUOTA_EXCEEDED = "quota_exceeded"
    OFFLINE = "offline"
    NOT_CONFIGURED = "not_configured"
    ERROR = "error"
    UNKNOWN = "unknown"


class StatusCategory(str, Enum):
    """Distinguishes implementation errors from operational limits."""
    IMPLEMENTATION_VALID = "implementation_valid"
    IMPLEMENTATION_INVALID = "implementation_invalid"
    OPERATIONALLY_LIMITED = "operationally_limited"


@dataclass
class ProviderState:
    """Complete state of a single provider."""
    name: str
    label: str
    configured: bool
    operational: bool
    status: ProviderStatus
    category: StatusCategory
    reason: Optional[str] = None
    models: List[str] = field(default_factory=list)
    last_check_ts: float = 0.0


@dataclass
class RuntimeDecision:
    """The decision record from AIAuthority.resolve_runtime()."""
    active_provider: str
    active_model: str
    status: ProviderStatus
    category: StatusCategory
    reasons: List[str]
    fallbacks_tried: List[str]
    all_providers: Dict[str, ProviderState]
    user_message: str
    resume_hint: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


# =============================================================================
# PROVIDER HIERARCHY (STRICT ORDER)
# =============================================================================

PROVIDER_HIERARCHY = ["openai", "gemini", "anthropic", "ollama"]

PROVIDER_MODELS = {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-preview", "o1-mini"],
    "gemini": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
    "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
    "ollama": ["llama3", "llama3.1", "mistral", "phi3", "qwen2"],
}

PROVIDER_LABELS = {
    "openai": "OpenAI",
    "gemini": "Google Gemini", 
    "anthropic": "Anthropic Claude",
    "ollama": "Ollama (Local)",
}

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini-2.0-flash-exp",
    "anthropic": "claude-3-5-sonnet-20241022",
    "ollama": "llama3",
}


# =============================================================================
# AI AUTHORITY SINGLETON
# =============================================================================

class AIAuthority:
    """
    THE SINGLE SOURCE OF TRUTH for AI provider selection and configuration.
    
    This class:
    - Reads all API keys (ONLY place allowed to call os.getenv for AI keys)
    - Determines which providers are configured
    - Checks operational status
    - Applies strict fallback cascade
    - Provides unified view for UI + extension
    """
    
    _instance: Optional["AIAuthority"] = None
    _last_decision: Optional[RuntimeDecision] = None
    _provider_states: Dict[str, ProviderState] = {}
    _keys_loaded: bool = False
    
    # API Keys (loaded once)
    _openai_key: Optional[str] = None
    _anthropic_key: Optional[str] = None
    _gemini_key: Optional[str] = None
    _ollama_base_url: Optional[str] = None
    
    def __new__(cls) -> "AIAuthority":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Load all keys and initialize provider states."""
        self._load_keys()
        self._init_provider_states()
    
    def _load_keys(self):
        """
        Load all API keys from environment.
        THIS IS THE ONLY PLACE IN THE CODEBASE THAT READS AI KEYS.
        """
        if self._keys_loaded:
            return
            
        # OpenAI
        self._openai_key = os.environ.get("OPENAI_API_KEY")
        
        # Anthropic
        self._anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        
        # Gemini (check both variants)
        self._gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        
        # Ollama base URL
        self._ollama_base_url = os.environ.get("OLLAMA_BASE_URL")
        if not self._ollama_base_url:
            # Auto-detect Docker vs local
            self._ollama_base_url = "http://ollama:11434" if os.path.exists("/.dockerenv") else "http://localhost:11434"
        
        self._keys_loaded = True
        
        logger.info(
            f"[AIAuthority] Keys loaded: OpenAI={bool(self._openai_key)}, "
            f"Gemini={bool(self._gemini_key)}, Anthropic={bool(self._anthropic_key)}"
        )
    
    def _init_provider_states(self):
        """Initialize provider states based on key presence."""
        for provider in PROVIDER_HIERARCHY:
            configured = self._is_provider_configured(provider)
            self._provider_states[provider] = ProviderState(
                name=provider,
                label=PROVIDER_LABELS[provider],
                configured=configured,
                operational=configured,  # Assume operational if configured (will be tested)
                status=ProviderStatus.AVAILABLE if configured else ProviderStatus.NOT_CONFIGURED,
                category=StatusCategory.IMPLEMENTATION_VALID if configured else StatusCategory.IMPLEMENTATION_INVALID,
                reason=None if configured else "API key not configured",
                models=PROVIDER_MODELS.get(provider, []),
                last_check_ts=time.time(),
            )
    
    def _is_provider_configured(self, provider: str) -> bool:
        """Check if provider has required credentials."""
        if provider == "openai":
            return bool(self._openai_key)
        elif provider == "gemini":
            return bool(self._gemini_key)
        elif provider == "anthropic":
            return bool(self._anthropic_key)
        elif provider == "ollama":
            return True  # Always "configured" (local service)
        return False
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a provider.
        ONLY AIAuthority is allowed to provide keys to factories.
        """
        self._load_keys()
        if provider == "openai":
            return self._openai_key
        elif provider == "gemini":
            return self._gemini_key
        elif provider == "anthropic":
            return self._anthropic_key
        return None
    
    def get_ollama_base_url(self) -> str:
        """Get Ollama base URL."""
        self._load_keys()
        return self._ollama_base_url or "http://localhost:11434"
    
    async def _check_provider_operational(self, provider: str) -> Tuple[bool, ProviderStatus, str]:
        """
        Check if a provider is operational (can accept requests).
        Returns (is_operational, status, reason).
        """
        import httpx
        
        if provider == "openai":
            if not self._openai_key:
                return False, ProviderStatus.NOT_CONFIGURED, "API key not configured"
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {self._openai_key}"}
                    )
                    if resp.status_code == 200:
                        return True, ProviderStatus.AVAILABLE, "Operational"
                    elif resp.status_code == 401:
                        return False, ProviderStatus.ERROR, "Invalid API key"
                    elif resp.status_code == 429:
                        return False, ProviderStatus.QUOTA_EXCEEDED, "Rate limit exceeded"
                    else:
                        return False, ProviderStatus.ERROR, f"HTTP {resp.status_code}"
            except httpx.TimeoutException:
                return False, ProviderStatus.OFFLINE, "Connection timeout"
            except Exception as e:
                return False, ProviderStatus.OFFLINE, str(e)
                
        elif provider == "gemini":
            if not self._gemini_key:
                return False, ProviderStatus.NOT_CONFIGURED, "API key not configured"
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(
                        f"https://generativelanguage.googleapis.com/v1beta/models?key={self._gemini_key}"
                    )
                    if resp.status_code == 200:
                        return True, ProviderStatus.AVAILABLE, "Operational"
                    elif resp.status_code == 400 and "quota" in resp.text.lower():
                        return False, ProviderStatus.QUOTA_EXCEEDED, "Quota exceeded"
                    elif resp.status_code == 403:
                        return False, ProviderStatus.ERROR, "Invalid API key or access denied"
                    else:
                        return False, ProviderStatus.ERROR, f"HTTP {resp.status_code}"
            except httpx.TimeoutException:
                return False, ProviderStatus.OFFLINE, "Connection timeout"
            except Exception as e:
                return False, ProviderStatus.OFFLINE, str(e)
                
        elif provider == "anthropic":
            if not self._anthropic_key:
                return False, ProviderStatus.NOT_CONFIGURED, "API key not configured"
            # Anthropic doesn't have a simple health endpoint
            # Assume operational if key is present
            return True, ProviderStatus.AVAILABLE, "Key present (verified on first use)"
            
        elif provider == "ollama":
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"{self._ollama_base_url}/api/tags")
                    if resp.status_code == 200:
                        return True, ProviderStatus.AVAILABLE, "Operational"
                    else:
                        return False, ProviderStatus.ERROR, f"HTTP {resp.status_code}"
            except httpx.TimeoutException:
                return False, ProviderStatus.OFFLINE, "Ollama not reachable (timeout)"
            except Exception as e:
                return False, ProviderStatus.OFFLINE, f"Ollama not reachable: {e}"
        
        return False, ProviderStatus.UNKNOWN, "Unknown provider"
    
    async def resolve_runtime(self, force_refresh: bool = False) -> RuntimeDecision:
        """
        Determine which provider to use, applying strict fallback cascade.
        
        HIERARCHY: OpenAI -> Gemini -> Claude -> Ollama
        
        Returns a RuntimeDecision with complete diagnostic information.
        """
        if self._last_decision and not force_refresh:
            # Return cached decision if recent (within 30 seconds)
            if time.time() - self._last_decision.timestamp < 30:
                return self._last_decision
        
        self._load_keys()
        
        reasons: List[str] = []
        fallbacks_tried: List[str] = []
        selected_provider: Optional[str] = None
        selected_model: Optional[str] = None
        final_status = ProviderStatus.UNKNOWN
        final_category = StatusCategory.IMPLEMENTATION_INVALID
        
        # Try each provider in hierarchy order
        for provider in PROVIDER_HIERARCHY:
            is_operational, status, reason = await self._check_provider_operational(provider)
            
            # Update provider state
            self._provider_states[provider] = ProviderState(
                name=provider,
                label=PROVIDER_LABELS[provider],
                configured=self._is_provider_configured(provider),
                operational=is_operational,
                status=status,
                category=self._status_to_category(status),
                reason=reason,
                models=PROVIDER_MODELS.get(provider, []),
                last_check_ts=time.time(),
            )
            
            if is_operational and selected_provider is None:
                selected_provider = provider
                selected_model = DEFAULT_MODELS.get(provider, PROVIDER_MODELS[provider][0])
                final_status = status
                final_category = self._status_to_category(status)
                reasons.append(f"Selected {provider}: {reason}")
            elif not is_operational:
                fallbacks_tried.append(provider)
                reasons.append(f"Skipped {provider}: {reason}")
        
        # Handle no provider available
        if selected_provider is None:
            selected_provider = "ollama"  # Last resort even if offline
            selected_model = DEFAULT_MODELS["ollama"]
            final_status = ProviderStatus.OFFLINE
            final_category = StatusCategory.OPERATIONALLY_LIMITED
            reasons.append("All providers unavailable, defaulting to Ollama (may be offline)")
        
        # Build user message
        user_message = self._build_user_message(selected_provider, final_status, final_category)
        resume_hint = self._build_resume_hint(final_status)
        
        decision = RuntimeDecision(
            active_provider=selected_provider,
            active_model=selected_model,
            status=final_status,
            category=final_category,
            reasons=reasons,
            fallbacks_tried=fallbacks_tried,
            all_providers=self._provider_states.copy(),
            user_message=user_message,
            resume_hint=resume_hint,
            timestamp=time.time(),
        )
        
        self._last_decision = decision
        
        logger.info(
            f"[AIAuthority] Runtime resolved: {selected_provider}/{selected_model} "
            f"(status={final_status.value}, fallbacks={fallbacks_tried})"
        )
        
        return decision
    
    def _status_to_category(self, status: ProviderStatus) -> StatusCategory:
        """Convert provider status to status category."""
        if status == ProviderStatus.AVAILABLE:
            return StatusCategory.IMPLEMENTATION_VALID
        elif status == ProviderStatus.NOT_CONFIGURED:
            return StatusCategory.IMPLEMENTATION_INVALID
        elif status in (ProviderStatus.QUOTA_EXCEEDED, ProviderStatus.OFFLINE):
            return StatusCategory.OPERATIONALLY_LIMITED
        else:
            return StatusCategory.OPERATIONALLY_LIMITED
    
    def _build_user_message(self, provider: str, status: ProviderStatus, category: StatusCategory) -> str:
        """Build user-facing message."""
        if category == StatusCategory.IMPLEMENTATION_VALID:
            return f"✓ AI actief via {PROVIDER_LABELS.get(provider, provider)}"
        elif category == StatusCategory.OPERATIONALLY_LIMITED:
            if status == ProviderStatus.QUOTA_EXCEEDED:
                return f"⚠️ {PROVIDER_LABELS.get(provider, provider)} quota bereikt - systeem correct geconfigureerd"
            elif status == ProviderStatus.OFFLINE:
                return f"⚠️ {PROVIDER_LABELS.get(provider, provider)} tijdelijk offline"
            else:
                return f"⚠️ AI beperkt beschikbaar via {PROVIDER_LABELS.get(provider, provider)}"
        else:
            return "⚙️ AI configuratie vereist - controleer API keys"
    
    def _build_resume_hint(self, status: ProviderStatus) -> Optional[str]:
        """Build resume hint for operational limits."""
        if status == ProviderStatus.QUOTA_EXCEEDED:
            return "Quota wordt automatisch hersteld. Probeer later opnieuw."
        elif status == ProviderStatus.OFFLINE:
            return "Controleer netwerkverbinding of Ollama service."
        return None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get unified capabilities view for UI + extension.
        This is consumed by /api/ai/runtime-status endpoint.
        """
        from backend.ai.bridge import safe_execute_async
        decision = safe_execute_async(self.resolve_runtime())
        
        return {
            "active_provider": decision.active_provider,
            "active_model": decision.active_model,
            "status": decision.status.value,
            "category": decision.category.value,
            "user_message": decision.user_message,
            "resume_hint": decision.resume_hint,
            "providers": {
                name: {
                    "name": state.name,
                    "label": state.label,
                    "configured": state.configured,
                    "operational": state.operational,
                    "status": state.status.value,
                    "category": state.category.value,
                    "reason": state.reason,
                    "models": state.models,
                }
                for name, state in decision.all_providers.items()
            },
            "fallbacks_tried": decision.fallbacks_tried,
            "reasons": decision.reasons,
            "provider_hierarchy": PROVIDER_HIERARCHY,
            "timestamp": decision.timestamp,
        }
    
    def create_text_provider(self, model_override: Optional[str] = None):
        """
        Create a text generation provider using current runtime decision.
        This is the ONLY way to get a text provider.
        """
        from backend.ai.bridge import safe_execute_async
        decision = safe_execute_async(self.resolve_runtime())
        
        provider_name = decision.active_provider
        model = model_override or decision.active_model
        
        # Import here to avoid circular imports
        from backend.ai.providers.openai_provider import OpenAIProvider
        from backend.ai.providers.anthropic_provider import AnthropicProvider
        from backend.ai.providers.gemini_provider import GeminiProvider
        from backend.ai.providers.ollama_provider import OllamaProvider
        
        if provider_name == "openai":
            return OpenAIProvider(
                api_key=self._openai_key,
                model=model,
                timeout=180
            )
        elif provider_name == "gemini":
            return GeminiProvider(
                api_key=self._gemini_key,
                model=model,
                timeout=180
            )
        elif provider_name == "anthropic":
            return AnthropicProvider(
                api_key=self._anthropic_key,
                model=model,
                timeout=180
            )
        elif provider_name == "ollama":
            return OllamaProvider(
                base_url=self._ollama_base_url,
                model=model,
                timeout=180
            )
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    def create_image_provider(self):
        """
        Create an image generation provider.
        Currently only Gemini supports image generation.
        """
        from backend.ai.image_provider_interface import NoImageProvider
        from backend.ai.providers.gemini_image_provider import GeminiImageProvider
        
        if self._gemini_key:
            return GeminiImageProvider(api_key=self._gemini_key)
        else:
            logger.warning("[AIAuthority] No image provider available (Gemini key missing)")
            return NoImageProvider()
    
    def invalidate_cache(self):
        """Force re-evaluation on next resolve_runtime call."""
        self._last_decision = None
    
    @classmethod
    def reset_singleton(cls):
        """Reset singleton for testing."""
        cls._instance = None


# =============================================================================
# MODULE-LEVEL ACCESSOR (for convenience)
# =============================================================================

def get_ai_authority() -> AIAuthority:
    """Get the global AIAuthority instance."""
    return AIAuthority()
