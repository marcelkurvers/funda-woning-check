"""
AI RUNTIME STATUS API - Unified endpoint for UI + Extension

This module provides the single /api/ai/runtime-status endpoint that:
1. Returns active provider + model
2. Returns per-provider configuration and operational status
3. Returns available models per provider
4. Is consumed by BOTH landing page and browser extension

NO OTHER ENDPOINT should provide this information.
"""

import logging
from fastapi import APIRouter
from typing import Dict, Any

from backend.ai.ai_authority import get_ai_authority
from backend.ai.ollama_guard import get_ollama_guard

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai-runtime"])


@router.get("/runtime-status")
async def get_runtime_status() -> Dict[str, Any]:
    """
    Unified runtime status endpoint.
    
    This endpoint is the SINGLE SOURCE OF TRUTH for:
    - Active provider and model
    - Per-provider configuration status
    - Per-provider operational status
    - Available models per provider
    - Fallback information
    
    CONSUMERS:
    - Landing page UI (Settings panel)
    - Browser extension (Provider/Model dropdowns)
    """
    authority = get_ai_authority()
    
    # Force fresh evaluation
    decision = await authority.resolve_runtime(force_refresh=True)
    
    # Build response
    providers = {}
    for name, state in decision.all_providers.items():
        providers[name] = {
            "name": state.name,
            "label": state.label,
            "configured": state.configured,
            "operational": state.operational,
            "status": state.status.value,
            "category": state.category.value,
            "reason": state.reason,
            "models": state.models,
            "is_active": name == decision.active_provider,
        }
    
    # Get Ollama status if applicable
    ollama_guard_status = None
    if decision.active_provider == "ollama" or providers.get("ollama", {}).get("configured"):
        try:
            guard = get_ollama_guard()
            ollama_guard_status = guard.get_status()
        except Exception as e:
            logger.warning(f"Failed to get Ollama guard status: {e}")
    
    return {
        # Active selection
        "active_provider": decision.active_provider,
        "active_model": decision.active_model,
        
        # Overall status
        "status": decision.status.value,
        "category": decision.category.value,
        "user_message": decision.user_message,
        "resume_hint": decision.resume_hint,
        
        # Per-provider details
        "providers": providers,
        
        # Hierarchy and fallback info
        "provider_hierarchy": ["openai", "gemini", "anthropic", "ollama"],
        "fallbacks_tried": decision.fallbacks_tried,
        "reasons": decision.reasons,
        
        # Ollama-specific
        "ollama_guard": ollama_guard_status,
        
        # Timestamp
        "timestamp": decision.timestamp,
    }


@router.post("/ollama/cleanup")
async def cleanup_ollama() -> Dict[str, Any]:
    """
    Trigger Ollama cleanup operation.
    
    This endpoint:
    1. Unloads all loaded models
    2. Detects lingering processes
    3. Optionally kills zombie processes
    
    Returns detailed result of cleanup operation.
    """
    guard = get_ollama_guard()
    
    try:
        result = await guard.cleanup(kill_lingering=True)
        
        return {
            "success": result.success,
            "processes_found": [
                {
                    "pid": p.pid,
                    "command": p.command,
                    "model": p.model_name,
                }
                for p in result.processes_found
            ],
            "processes_killed": result.processes_killed,
            "errors": result.errors,
            "timestamp": result.timestamp,
        }
    except Exception as e:
        logger.error(f"Ollama cleanup failed: {e}")
        return {
            "success": False,
            "processes_found": [],
            "processes_killed": [],
            "errors": [str(e)],
            "timestamp": None,
        }


@router.get("/ollama/status")
async def get_ollama_status() -> Dict[str, Any]:
    """
    Get current Ollama status and process information.
    """
    guard = get_ollama_guard()
    return guard.get_status()


@router.post("/invalidate-cache")
async def invalidate_runtime_cache() -> Dict[str, Any]:
    """
    Force re-evaluation of runtime decision.
    Useful after configuration changes.
    """
    authority = get_ai_authority()
    authority.invalidate_cache()
    
    # Get fresh decision
    decision = await authority.resolve_runtime(force_refresh=True)
    
    return {
        "success": True,
        "active_provider": decision.active_provider,
        "active_model": decision.active_model,
        "message": "Cache invalidated, runtime re-evaluated",
    }
