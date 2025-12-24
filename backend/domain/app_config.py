"""
Canonical Application Configuration (AppConfig)

This is the SINGLE SOURCE OF TRUTH for all configuration in the system.
It is used by:
- Backend pipeline execution
- AI provider factory
- UI rendering (via API)
- Browser extension API calls

SECURITY RULES:
- Raw API keys are NEVER included in this object
- Only boolean presence + source is exposed
- Keys are loaded from environment/secrets but never returned

EXPLICIT CONFIGURATION PRINCIPLE:
- No implicit defaults that could surprise users
- If provider requires a key and it's missing, fail-closed
- Mode selection is explicit and enforced
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, computed_field


class OperatingMode(str, Enum):
    """Operating modes with explicit semantics."""
    
    FAST = "fast"       # Shortened narratives, speed-optimized
    FULL = "full"       # Full 4-plane generation, all narratives
    DEBUG = "debug"     # No AI calls, uses deterministic placeholders
    OFFLINE = "offline" # Same as DEBUG - no network calls


class KeyStatus(BaseModel):
    """Safe key status - never contains the actual key."""
    
    present: bool = False
    source: Literal["env", "config", "secret", "none"] = "none"
    last_updated: Optional[str] = None
    fingerprint: Optional[str] = None  # Last 4 chars, only if explicitly enabled
    
    @classmethod
    def from_key(
        cls, 
        key_value: Optional[str], 
        source: Literal["env", "config", "secret", "none"] = "none",
        show_fingerprint: bool = False
    ) -> "KeyStatus":
        """Create KeyStatus from an actual key value (safely)."""
        if not key_value:
            return cls(present=False, source="none")
        
        fingerprint = None
        if show_fingerprint and len(key_value) >= 4:
            fingerprint = f"...{key_value[-4:]}"
        
        return cls(
            present=True,
            source=source,
            last_updated=datetime.now().isoformat(),
            fingerprint=fingerprint
        )


class ProviderConfig(BaseModel):
    """Configuration for AI providers - no raw keys exposed."""
    
    name: str
    label: str
    models: list[str]
    selected_model: Optional[str] = None
    key_status: KeyStatus = Field(default_factory=KeyStatus)
    base_url: Optional[str] = None  # For Ollama
    available: bool = False  # Whether provider can be used (has key or is local)


class AppConfig(BaseModel):
    """
    Canonical Application Configuration.
    
    This object is the single source of truth for all configuration.
    It is computed at request time and never persisted with sensitive data.
    """
    
    # === PROVIDER SELECTION (Explicit, no defaults) ===
    provider: str = Field(
        default="ollama",
        description="Selected AI provider. Must be explicitly chosen."
    )
    model: str = Field(
        default="llama3",
        description="Selected model for the provider."
    )
    mode: OperatingMode = Field(
        default=OperatingMode.FULL,
        description="Operating mode. Explicit selection required."
    )
    
    # === TIMEOUTS & PERFORMANCE ===
    timeout: int = Field(default=60, ge=5, le=300, description="Provider timeout in seconds")
    retry_policy: Literal["off", 1, 2] = Field(default=1, description="Retry attempts on failure")
    concurrency_cap: int = Field(default=4, ge=1, le=10, description="Max concurrent AI calls")
    prefer_speed: bool = Field(default=False, description="Prefer speed over quality")
    
    # === TEMPERATURE & GENERATION PARAMS ===
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=256, le=32768)
    
    # === BASE URL & CONNECTIVITY ===
    base_url: str = Field(default="http://localhost:8000", description="Backend API URL")
    ollama_base_url: Optional[str] = Field(default=None, description="Ollama server URL")
    
    # === KEY STATUS (Safe, no raw keys) ===
    key_status: Dict[str, KeyStatus] = Field(
        default_factory=lambda: {
            "openai": KeyStatus(),
            "anthropic": KeyStatus(),
            "gemini": KeyStatus(),
        }
    )
    
    # === PROVIDER METADATA ===
    providers: Dict[str, ProviderConfig] = Field(default_factory=dict)
    
    # === COMPUTED STATUS ===
    @computed_field
    @property
    def can_use_selected_provider(self) -> bool:
        """Check if the selected provider can be used."""
        if self.mode in (OperatingMode.DEBUG, OperatingMode.OFFLINE):
            return True  # No AI needed
        if self.provider == "ollama":
            return True  # No key required
        key_state = self.key_status.get(self.provider)
        return key_state.present if key_state else False
    
    @computed_field
    @property
    def effective_mode(self) -> str:
        """The actual mode after considering provider availability."""
        if not self.can_use_selected_provider and self.mode not in (OperatingMode.DEBUG, OperatingMode.OFFLINE):
            return "unavailable_key_missing"
        return self.mode.value
    
    @computed_field
    @property
    def mode_display(self) -> str:
        """Human-readable mode description."""
        displays = {
            OperatingMode.FAST: "⚡ FAST - Snelle analyse, beperkte narratief",
            OperatingMode.FULL: "📊 FULL - Volledige 4-vlak analyse",
            OperatingMode.DEBUG: "🔧 DEBUG - Geen AI, deterministische output",
            OperatingMode.OFFLINE: "📴 OFFLINE - Geen netwerk, lokale verwerking",
        }
        return displays.get(self.mode, str(self.mode))


class RunConfig(BaseModel):
    """
    Per-request configuration that can override AppConfig.
    Used when extension sends specific preferences.
    """
    
    provider: Optional[str] = None
    model: Optional[str] = None
    mode: Optional[OperatingMode] = None
    timeout: Optional[int] = None
    
    @classmethod
    def merge_with_app_config(cls, app_config: AppConfig, run_config: Optional["RunConfig"]) -> AppConfig:
        """Merge run-specific config into app config."""
        if not run_config:
            return app_config
        
        merged = app_config.model_copy()
        
        if run_config.provider:
            merged.provider = run_config.provider
        if run_config.model:
            merged.model = run_config.model
        if run_config.mode:
            merged.mode = run_config.mode
        if run_config.timeout:
            merged.timeout = run_config.timeout
        
        return merged


# === GLOBAL CONFIG ACCESS ===

def build_app_config(show_fingerprints: bool = False) -> AppConfig:
    """
    Build the canonical AppConfig from all sources.
    
    Loading order:
    1. Code defaults
    2. Environment variables
    3. Persisted settings (from DB)
    4. Per-request overrides are handled separately via RunConfig
    
    SECURITY: Raw keys are never included in the returned config.
    """
    from backend.config.settings import get_settings
    
    settings = get_settings()
    
    # Read API keys directly from environment variables
    # Note: docker-compose passes OPENAI_API_KEY (not AI_OPENAI_API_KEY)
    openai_key = os.environ.get("OPENAI_API_KEY") or settings.ai.openai_api_key
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY") or settings.ai.anthropic_api_key
    gemini_key = os.environ.get("GEMINI_API_KEY") or settings.ai.gemini_api_key
    
    # Build safe key status
    key_status = {
        "openai": KeyStatus.from_key(
            openai_key,
            source="env" if os.environ.get("OPENAI_API_KEY") else ("config" if settings.ai.openai_api_key else "none"),
            show_fingerprint=show_fingerprints
        ),
        "anthropic": KeyStatus.from_key(
            anthropic_key,
            source="env" if os.environ.get("ANTHROPIC_API_KEY") else ("config" if settings.ai.anthropic_api_key else "none"),
            show_fingerprint=show_fingerprints
        ),
        "gemini": KeyStatus.from_key(
            gemini_key,
            source="env" if os.environ.get("GEMINI_API_KEY") else ("config" if settings.ai.gemini_api_key else "none"),
            show_fingerprint=show_fingerprints
        ),
    }
    
    # Build provider configs
    providers = {
        "ollama": ProviderConfig(
            name="ollama",
            label="Ollama (Lokaal)",
            models=["llama3", "llama3.1", "mistral", "phi3", "qwen2"],
            selected_model=settings.ai.model if settings.ai.provider == "ollama" else None,
            base_url=settings.ai.ollama_base_url,
            available=True,  # Always available (local)
        ),
        "openai": ProviderConfig(
            name="openai",
            label="OpenAI",
            models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-preview"],
            selected_model=settings.ai.model if settings.ai.provider == "openai" else None,
            key_status=key_status["openai"],
            available=key_status["openai"].present,
        ),
        "anthropic": ProviderConfig(
            name="anthropic",
            label="Anthropic",
            models=["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            selected_model=settings.ai.model if settings.ai.provider == "anthropic" else None,
            key_status=key_status["anthropic"],
            available=key_status["anthropic"].present,
        ),
        "gemini": ProviderConfig(
            name="gemini",
            label="Google Gemini",
            models=["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
            selected_model=settings.ai.model if settings.ai.provider == "gemini" else None,
            key_status=key_status["gemini"],
            available=key_status["gemini"].present,
        ),
    }
    
    # Determine mode from settings/environment
    # Default to FULL, but respect explicit settings
    mode_str = os.environ.get("AI_MODE", "full").lower()
    try:
        mode = OperatingMode(mode_str)
    except ValueError:
        mode = OperatingMode.FULL
    
    return AppConfig(
        provider=settings.ai.provider,
        model=settings.ai.model,
        mode=mode,
        timeout=settings.ai.timeout,
        ollama_base_url=settings.ai.ollama_base_url,
        key_status=key_status,
        providers=providers,
    )


def validate_config_for_execution(config: AppConfig) -> tuple[bool, str]:
    """
    Validate configuration before pipeline execution.
    
    Returns (is_valid, error_message).
    
    FAIL-CLOSED BEHAVIOR:
    - If mode is FULL/FAST and provider requires key but key is missing: FAIL
    - If provider is not available: FAIL
    - Never silently fallback to Ollama
    """
    if config.mode in (OperatingMode.DEBUG, OperatingMode.OFFLINE):
        return True, ""
    
    # Check if provider is available
    provider_config = config.providers.get(config.provider)
    if not provider_config:
        return False, f"Unknown provider: {config.provider}"
    
    if not provider_config.available:
        if config.provider == "ollama":
            return False, "Ollama niet beschikbaar. Controleer of Ollama draait."
        else:
            return False, f"API key ontbreekt voor {provider_config.label}. Stel deze in via omgevingsvariabelen."
    
    return True, ""
