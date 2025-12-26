# backend/api/ai_status.py

"""AI Status API - Provides real-time AI provider status information."""

import asyncio
import time
from fastapi import APIRouter
from typing import Dict, Any, Optional
from pydantic import BaseModel

from backend.config.settings import get_settings
from backend.intelligence import IntelligenceEngine

router = APIRouter(prefix="/api/ai", tags=["ai"])


class AIStatusResponse(BaseModel):
    provider: str
    model: str
    status: str  # online, offline, error, unconfigured
    latency_ms: Optional[int] = None
    error_message: Optional[str] = None
    available_providers: list[str]
    configured_providers: Dict[str, bool]
    capabilities: Optional[Dict[str, Any]] = None  # Added global capability status


async def _check_ollama_health(base_url: str) -> tuple[bool, int]:
    """Check if Ollama is reachable and measure latency."""
    import httpx
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/api/tags")
            latency = int((time.time() - start) * 1000)
            return response.status_code == 200, latency
    except Exception:
        return False, 0


async def _check_openai_health(api_key: str) -> tuple[bool, int]:
    """Check if OpenAI API is reachable."""
    if not api_key:
        return False, 0
    import httpx
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            latency = int((time.time() - start) * 1000)
            return response.status_code == 200, latency
    except Exception:
        return False, 0


async def _check_anthropic_health(api_key: str) -> tuple[bool, int]:
    """Check if Anthropic API is reachable."""
    if not api_key:
        return False, 0
    # Anthropic doesn't have a simple health endpoint, just check key exists
    return True, 0


async def _check_gemini_health(api_key: str) -> tuple[bool, int]:
    """Check if Gemini API is reachable."""
    if not api_key:
        return False, 0
    import httpx
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            )
            latency = int((time.time() - start) * 1000)
            return response.status_code == 200, latency
    except Exception:
        return False, 0


@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status():
    """Get current AI provider status and availability."""
    settings = get_settings()
    
    current_provider = settings.ai.provider
    current_model = settings.ai.model
    
    # Check which providers are configured (have API keys or endpoints)
    configured = {
        "ollama": bool(settings.ai.ollama_base_url),
        "openai": bool(settings.ai.openai_api_key),
        "anthropic": bool(settings.ai.anthropic_api_key),
        "gemini": bool(settings.ai.gemini_api_key),
    }
    
    # Check health of current provider
    status = "unconfigured"
    latency_ms = None
    error_message = None
    
    try:
        if current_provider == "ollama":
            is_online, latency_ms = await _check_ollama_health(settings.ai.ollama_base_url)
            status = "online" if is_online else "offline"
        elif current_provider == "openai":
            if settings.ai.openai_api_key:
                is_online, latency_ms = await _check_openai_health(settings.ai.openai_api_key)
                status = "online" if is_online else "error"
            else:
                status = "unconfigured"
                error_message = "API key not set"
        elif current_provider == "anthropic":
            if settings.ai.anthropic_api_key:
                status = "online"  # Can't easily health check
            else:
                status = "unconfigured"
                error_message = "API key not set"
        elif current_provider == "gemini":
            if settings.ai.gemini_api_key:
                is_online, latency_ms = await _check_gemini_health(settings.ai.gemini_api_key)
                status = "online" if is_online else "error"
            else:
                # Fallback: check raw env var if settings didn't pick it up
                import os
                if os.getenv("GEMINI_API_KEY"):
                     status = "online" # Assume online if present, since checking logic above depends on settings
                else:
                    status = "unconfigured"
                    error_message = "API key not set"
    except Exception as e:
        status = "error"
        error_message = str(e)
    
    # Get Global Capabilities
    from backend.ai.capability_manager import get_capability_manager
    capabilities = get_capability_manager().get_all_statuses()
    
    return AIStatusResponse(
        provider=current_provider,
        model=current_model,
        status=status,
        latency_ms=latency_ms,
        error_message=error_message,
        available_providers=["ollama", "openai", "anthropic", "gemini"],
        configured_providers=configured,
        capabilities={name: status.to_api_dict() if hasattr(status, 'to_api_dict') else status.dict() for name, status in capabilities.items()}
    )


@router.get("/capabilities")
async def get_ai_capabilities():
    """
    Get global AI capability status.
    
    This endpoint exposes the capability layer for the frontend.
    Key distinction:
    - is_implementation_valid: True means the system is correctly configured
    - is_operational_limit: True means external resource constraint (quota, outage)
    
    The frontend should use this to show appropriate status messages.
    """
    from backend.ai.capability_manager import get_capability_manager
    return get_capability_manager().to_api_response()



@router.get("/models/{provider}")
async def get_available_models(provider: str):
    """Get available models for a specific provider."""
    settings = get_settings()
    
    if provider == "ollama":
        import httpx
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{settings.ai.ollama_base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    return {"provider": "ollama", "models": models}
        except Exception as e:
            return {"provider": "ollama", "models": [], "error": str(e)}
    
    elif provider == "openai":
        return {
            "provider": "openai",
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        }
    
    elif provider == "anthropic":
        return {
            "provider": "anthropic",
            "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
        }
    
    elif provider == "gemini":
        return {
            "provider": "gemini",
            "models": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"]
        }
    
    return {"provider": provider, "models": [], "error": "Unknown provider"}


@router.get("/providers")
async def get_providers():
    """Get all available providers with their models."""
    from backend.ai.provider_factory import ProviderFactory
    return ProviderFactory.list_providers()
