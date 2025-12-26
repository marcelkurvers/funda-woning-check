"""
Configuration Status API - Explicit UX Endpoints

This module provides endpoints for the explicit configuration UX.
All endpoints are designed with security in mind - no raw keys exposed.

Endpoints:
- GET /api/config/status - Full configuration status with safe key visibility
- POST /api/config/test-provider - Test provider authentication
- GET /api/config/health - Health check with latency
- POST /api/config/update - Update configuration (non-sensitive only)
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Literal
from datetime import datetime

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from backend.domain.app_config import (
    AppConfig, 
    OperatingMode, 
    KeyStatus, 
    build_app_config,
    validate_config_for_execution
)
from backend.config.settings import get_settings, reset_settings
from backend.ai.provider_factory import ProviderFactory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config-status", tags=["configuration-status"])


# === Response Models ===

class HealthStatus(BaseModel):
    """Health status of a service."""
    status: Literal["healthy", "degraded", "unhealthy", "unknown"]
    latency_ms: Optional[int] = None
    message: Optional[str] = None


class ProviderTestResult(BaseModel):
    """Result of testing provider authentication."""
    success: bool
    provider: str
    model: str
    message: str
    latency_ms: Optional[int] = None
    response_preview: Optional[str] = None


class ConfigStatusResponse(BaseModel):
    """Full configuration status - SAFE, no raw keys."""
    
    # Current selection
    provider: str
    model: str
    mode: str
    mode_display: str
    
    # Provider availability
    can_use_provider: bool
    provider_error: Optional[str] = None
    
    # Key status (SAFE - no raw keys)
    key_status: Dict[str, Dict[str, Any]]
    
    # Available providers with their status
    providers: Dict[str, Dict[str, Any]]
    
    # Performance settings
    timeout: int
    temperature: float
    max_tokens: int
    
    # Health
    backend_health: HealthStatus
    ollama_health: Optional[HealthStatus] = None
    
    # Timestamps
    computed_at: str


class ConfigUpdateRequest(BaseModel):
    """Request to update configuration - non-sensitive fields only."""
    provider: Optional[str] = None
    model: Optional[str] = None
    mode: Optional[str] = None
    timeout: Optional[int] = Field(None, ge=5, le=300)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=256, le=32768)


# === Helper Functions ===

async def check_ollama_health(base_url: str) -> HealthStatus:
    """Check Ollama server health."""
    import httpx
    
    if not base_url:
        return HealthStatus(status="not_configured", message="Base URL not configured")
    
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/api/tags")
            latency = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                return HealthStatus(status="healthy", latency_ms=latency)
            else:
                return HealthStatus(
                    status="degraded", 
                    latency_ms=latency,
                    message=f"Status code: {response.status_code}"
                )
    except httpx.TimeoutException:
        return HealthStatus(status="unhealthy", message="Connection timeout")
    except Exception as e:
        return HealthStatus(status="unhealthy", message=str(e))


async def check_provider_health(provider: str, api_key: Optional[str]) -> HealthStatus:
    """Check cloud provider health."""
    import httpx
    
    if not api_key:
        return HealthStatus(status="unknown", message="API key not configured")
    
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=10.0) as client:
            if provider == "openai":
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
            elif provider == "anthropic":
                # Anthropic doesn't have a simple health check endpoint
                return HealthStatus(status="healthy", message="Key present (cannot verify)")
            elif provider == "gemini":
                response = await client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                )
            else:
                return HealthStatus(status="unknown", message=f"Unknown provider: {provider}")
            
            latency = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                return HealthStatus(status="healthy", latency_ms=latency)
            elif response.status_code == 401:
                return HealthStatus(status="unhealthy", latency_ms=latency, message="Invalid API key")
            else:
                return HealthStatus(
                    status="degraded",
                    latency_ms=latency,
                    message=f"Status code: {response.status_code}"
                )
    except httpx.TimeoutException:
        return HealthStatus(status="unhealthy", message="Connection timeout")
    except Exception as e:
        return HealthStatus(status="unhealthy", message=str(e))


# === Endpoints ===

@router.get("/status", response_model=ConfigStatusResponse)
async def get_config_status(show_fingerprint: bool = False):
    """
    Get complete configuration status.
    
    This is the primary endpoint for the Settings UI.
    All sensitive data (API keys) is represented safely as KeyStatus objects.
    
    Args:
        show_fingerprint: If true, include last 4 chars of keys (requires user acknowledgment)
    """
    settings = get_settings()
    config = build_app_config(show_fingerprints=show_fingerprint)
    
    # Validate current configuration
    can_use, error = validate_config_for_execution(config)
    
    # Check backend health (self)
    backend_health = HealthStatus(status="healthy", latency_ms=0)
    
    # Check Ollama health if configured or if it's the selected provider
    ollama_health = None
    if config.provider == "ollama" or config.ollama_base_url:
        if config.ollama_base_url:
             ollama_health = await check_ollama_health(config.ollama_base_url)
        else:
             ollama_health = HealthStatus(status="not_configured", message="Ollama URL missing")
    
    # Convert providers to dict format
    providers_dict = {
        name: {
            "name": p.name,
            "label": p.label,
            "models": p.models,
            "available": p.available,
            "key_present": p.key_status.present if p.key_status else (name == "ollama"),
            "key_source": p.key_status.source if p.key_status else "none",
        }
        for name, p in config.providers.items()
    }
    
    # Convert key status to dict format
    key_status_dict = {
        name: {
            "present": ks.present,
            "source": ks.source,
            "last_updated": ks.last_updated,
            "fingerprint": ks.fingerprint if show_fingerprint else None,
        }
        for name, ks in config.key_status.items()
    }
    
    return ConfigStatusResponse(
        provider=config.provider,
        model=config.model,
        mode=config.mode.value,
        mode_display=config.mode_display,
        can_use_provider=can_use,
        provider_error=error if not can_use else None,
        key_status=key_status_dict,
        providers=providers_dict,
        timeout=config.timeout,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        backend_health=backend_health,
        ollama_health=ollama_health,
        computed_at=datetime.now().isoformat(),
    )


@router.post("/test-provider", response_model=ProviderTestResult)
async def test_provider_authentication(
    provider: str = Body(...),
    model: Optional[str] = Body(None)
):
    """
    Test provider authentication with a simple prompt.
    
    This verifies that:
    1. The API key is valid
    2. The model is accessible
    3. The provider responds correctly
    
    SECURITY: This endpoint does not expose any keys.
    """
    settings = get_settings()
    config = build_app_config()
    
    # Validate provider selection
    if provider not in config.providers:
        return ProviderTestResult(
            success=False,
            provider=provider,
            model=model or "unknown",
            message=f"Unknown provider: {provider}"
        )
    
    provider_config = config.providers[provider]
    test_model = model or (provider_config.models[0] if provider_config.models else "unknown")
    
    # Check if provider is available
    if not provider_config.available and provider != "ollama":
        return ProviderTestResult(
            success=False,
            provider=provider,
            model=test_model,
            message=f"API key not configured for {provider_config.label}. Set via environment variable."
        )
    
    # Test the provider
    try:
        start = time.time()
        
        # Get the actual key (internally, not exposed)
        if provider == "openai":
            api_key = settings.ai.openai_api_key
        elif provider == "anthropic":
            api_key = settings.ai.anthropic_api_key
        elif provider == "gemini":
            api_key = settings.ai.gemini_api_key
        else:
            api_key = None
        
        # Create provider instance
        if provider == "ollama":
            if not settings.ai.ollama_base_url:
                 return ProviderTestResult(
                    success=False,
                    provider=provider,
                    model=test_model,
                    message="Ollama base URL not configured."
                )
            instance = ProviderFactory.create_provider(
                provider,
                base_url=settings.ai.ollama_base_url,
                model=test_model,
                timeout=10
            )
        else:
            instance = ProviderFactory.create_provider(
                provider,
                api_key=api_key,
                model=test_model,
                timeout=10
            )
        
        # Send test prompt
        response = await instance.generate(
            "Reply with exactly: 'OK'",
            system="You are a test assistant. Reply only with 'OK'.",
            max_tokens=10,
            temperature=0
        )
        
        latency = int((time.time() - start) * 1000)
        
        if response and len(response) > 0:
            return ProviderTestResult(
                success=True,
                provider=provider,
                model=test_model,
                message=f"✓ {provider_config.label} responded successfully",
                latency_ms=latency,
                response_preview=response[:50] if len(response) > 50 else response
            )
        else:
            return ProviderTestResult(
                success=False,
                provider=provider,
                model=test_model,
                message="Provider returned empty response",
                latency_ms=latency
            )
            
    except Exception as e:
        return ProviderTestResult(
            success=False,
            provider=provider,
            model=test_model,
            message=f"Test failed: {str(e)}"
        )


@router.get("/health")
async def get_health_summary():
    """Quick health check with latency measurement."""
    start = time.time()
    config = build_app_config()
    
    ollama_health = None
    if config.provider == "ollama":
        if config.ollama_base_url:
            ollama_health = await check_ollama_health(config.ollama_base_url)
        else:
            ollama_health = HealthStatus(status="not_configured", message="Ollama URL missing")
    
    return {
        "status": "ok",
        "latency_ms": int((time.time() - start) * 1000),
        "provider": config.provider,
        "model": config.model,
        "mode": config.mode.value,
        "ollama_status": ollama_health.status if ollama_health else None,
    }


@router.post("/update")
async def update_config(update: ConfigUpdateRequest):
    """
    Update non-sensitive configuration.
    
    SECURITY: This endpoint cannot modify API keys.
    Keys must be set via environment variables or secrets.
    """
    settings = get_settings()
    updated_fields = []
    
    # Update AI settings
    if update.provider is not None:
        settings.ai.provider = update.provider
        updated_fields.append("provider")
    
    if update.model is not None:
        settings.ai.model = update.model
        updated_fields.append("model")
    
    if update.timeout is not None:
        settings.ai.timeout = update.timeout
        updated_fields.append("timeout")
    
    # Persist to database
    import sqlite3
    import json
    
    db_path = settings.database_url
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Update mode in settings if provided
        if update.mode is not None:
            settings.ai.mode = update.mode
            updated_fields.append("mode")
        
        # Persist AI config (without keys) - mode is now included here
        ai_config = {
            "provider": settings.ai.provider,
            "model": settings.ai.model,
            "mode": settings.ai.mode,  # Store mode as part of ai section
            "timeout": settings.ai.timeout,
            "fallback_enabled": settings.ai.fallback_enabled,
        }
        cur.execute(
            "INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)",
            ("config.ai", json.dumps(ai_config))
        )
        
        # Clean up any legacy config.mode key
        cur.execute("DELETE FROM kv_store WHERE key = 'config.mode'")
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to persist config: {e}")
    
    # Reset settings cache
    reset_settings()
    
    # Reinitialize AI provider
    try:
        from backend.main import init_ai_provider
        init_ai_provider()
    except Exception as e:
        logger.warning(f"Failed to reinitialize AI provider: {e}")
    
    return {
        "status": "updated",
        "updated_fields": updated_fields,
        "message": f"Updated: {', '.join(updated_fields)}" if updated_fields else "No changes"
    }


@router.get("/modes")
async def get_available_modes():
    """Get all available operating modes with descriptions."""
    return {
        "modes": [
            {
                "value": "fast",
                "label": "⚡ FAST",
                "description": "Snelle analyse met beperkte narratief. Geschikt voor snelle beoordelingen.",
                "ai_required": True,
            },
            {
                "value": "full",
                "label": "📊 FULL",
                "description": "Volledige 4-vlak analyse met uitgebreide narratieven. Aanbevolen voor definitieve rapporten.",
                "ai_required": True,
            },
            {
                "value": "debug",
                "label": "🔧 DEBUG",
                "description": "Geen AI calls. Gebruikt deterministische placeholders. Voor testen en development.",
                "ai_required": False,
            },
            {
                "value": "offline",
                "label": "📴 OFFLINE",
                "description": "Geen netwerkverbinding nodig. Lokale verwerking met fallback content.",
                "ai_required": False,
            },
        ]
    }


@router.get("/providers")
async def get_providers_with_status():
    """Get all providers with their current status."""
    config = build_app_config()
    
    result = []
    for name, provider in config.providers.items():
        result.append({
            "name": provider.name,
            "label": provider.label,
            "models": provider.models,
            "available": provider.available,
            "is_current": name == config.provider,
            "key_status": {
                "present": provider.key_status.present if provider.key_status else (name == "ollama"),
                "source": provider.key_status.source if provider.key_status else "none",
            } if name != "ollama" else {"present": True, "source": "local"},
            "requires_key": name != "ollama",
        })
    
    return {"providers": result}
