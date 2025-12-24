# backend/api/config.py

"""Configuration management API routes.

Provides endpoints to get and update application configuration, persisting
changes to the kv_store table.
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any

from backend.config.settings import get_settings, reset_settings
import sqlite3
import json

# Helper to get a DB connection using the configured database URL
def _get_conn():
    settings = get_settings()
    db_path = settings.database_url
    return sqlite3.connect(db_path)

router = APIRouter(prefix="/api/config", tags=["configuration"])

class ConfigUpdateRequest(BaseModel):
    ai: Optional[Dict[str, Any]] = None
    market: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    pipeline: Optional[Dict[str, Any]] = None

@router.get("/")
async def get_config():
    """Return the full current configuration."""
    settings = get_settings()
    return {
        "ai": settings.ai.model_dump(),
        "market": settings.market.model_dump(),
        "preferences": settings.preferences.model_dump(),
        "validation": settings.validation.model_dump(),
        "pipeline": settings.pipeline.model_dump(),
        "database_url": settings.database_url,
    }

@router.get("/{section}")
async def get_config_section(section: str):
    """Return a specific configuration section."""
    config = await get_config()
    if section not in config:
        raise HTTPException(status_code=404, detail=f"Configuration section '{section}' not found")
    return config[section]

@router.get("/{section}/{key}")
async def get_config_value(section: str, key: str):
    """Return a specific configuration value within a section."""
    section_config = await get_config_section(section)
    if key not in section_config:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found in section '{section}'")
    return {key: section_config[key]}

def _persist_section(key: str, data: dict):
    con = _get_conn()
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)", (f"config.{key}", json.dumps(data)))
    con.commit()
    con.close()

@router.post("/")
async def update_config_bulk(config: ConfigUpdateRequest):
    """Bulk update configuration sections and persist them."""
    settings = get_settings()

    sections_updated = []
    if config.ai:
        for k, v in config.ai.items():
            if hasattr(settings.ai, k):
                setattr(settings.ai, k, v)
        _persist_section("ai", settings.ai.model_dump())
        sections_updated.append("ai")

    if config.market:
        for k, v in config.market.items():
            if hasattr(settings.market, k):
                setattr(settings.market, k, v)
        _persist_section("market", settings.market.model_dump())
        sections_updated.append("market")

    if config.preferences:
        for k, v in config.preferences.items():
            if hasattr(settings.preferences, k):
                setattr(settings.preferences, k, v)
        _persist_section("preferences", settings.preferences.model_dump())
        sections_updated.append("preferences")

    if config.validation:
        for k, v in config.validation.items():
            if hasattr(settings.validation, k):
                setattr(settings.validation, k, v)
        _persist_section("validation", settings.validation.model_dump())
        sections_updated.append("validation")

    if config.pipeline:
        for k, v in config.pipeline.items():
            if hasattr(settings.pipeline, k):
                setattr(settings.pipeline, k, v)
        _persist_section("pipeline", settings.pipeline.model_dump())
        sections_updated.append("pipeline")

    reset_settings()
    
    # Trigger AI re-init if AI section was updated
    if "ai" in sections_updated:
        try:
            from backend.main import init_ai_provider
            init_ai_provider()
        except: pass
        
    return {"status": "updated", "sections": sections_updated}


@router.put("/{section}/{key}")
async def update_config_value(section: str, key: str, value: Any = Body(...)):
    """Update a specific configuration value."""
    settings = get_settings()
    
    if not hasattr(settings, section):
        raise HTTPException(status_code=404, detail=f"Section '{section}' not found")
    
    target_section = getattr(settings, section)
    if not hasattr(target_section, key):
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found in section '{section}'")
    
    # Update the value
    try:
        setattr(target_section, key, value)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Persist the whole section
    _persist_section(section, target_section.model_dump())
    
    reset_settings()
    return {"status": "updated", "section": section, "key": key, "new_value": value}
