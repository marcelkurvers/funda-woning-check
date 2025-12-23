"""
Chapter Generator - Generates Chapters Using Registry Context

This module generates chapters using the canonical registry from PipelineContext.
Every chapter generation receives the locked registry as its source of truth.

KEY PRINCIPLES:
1. Chapters receive registry data, not raw data
2. AI and fallback paths both produce the same output structure
3. Validation is NOT the concern of this module - that's done at the spine level
"""

import logging
from typing import Dict, Any, Optional

from backend.domain.pipeline_context import PipelineContext
from backend.domain.ownership import OwnershipMap
from backend.domain.chapter_variables import get_chapter_variables, should_show_core_data

logger = logging.getLogger(__name__)


def generate_chapter_with_validation(ctx: PipelineContext, chapter_id: int) -> Dict[str, Any]:
    """
    Generate a single chapter using the registry context.
    
    This function:
    1. Gets owned variables for this chapter
    2. Builds scoped context from registry
    3. Calls the intelligence engine (AI or fallback)
    4. Returns structured output
    
    NOTE: Validation is performed by the caller (PipelineSpine), not here.
    This ensures validation can never be bypassed.
    
    Args:
        ctx: The locked PipelineContext with canonical registry
        chapter_id: Chapter number (0-13)
    
    Returns:
        Chapter output dict ready for validation
    """
    if not ctx.is_registry_locked():
        from backend.domain.pipeline_context import PipelineViolation
        raise PipelineViolation("Cannot generate chapter - registry is not locked")
    
    # Build scoped context from registry (respecting ownership)
    scoped_data = _build_scoped_context(ctx, chapter_id)
    
    # Add preferences for AI reasoning
    scoped_data['_preferences'] = ctx.preferences
    
    # Generate narrative using existing intelligence engine
    from backend.intelligence import IntelligenceEngine
    
    try:
        narrative = IntelligenceEngine.generate_chapter_narrative(chapter_id, scoped_data)
    except Exception as e:
        logger.error(f"Chapter {chapter_id} generation failed: {e}")
        # Create error output structure - this will fail validation
        narrative = _create_error_output(chapter_id, str(e))
    
    # Structure the output consistently
    output = _structure_chapter_output(chapter_id, narrative, ctx)
    
    return output


def _build_scoped_context(ctx: PipelineContext, chapter_id: int) -> Dict[str, Any]:
    """
    Build a scoped data context for a chapter from the registry.
    
    This respects ownership rules - chapters only see what they own
    plus reference data needed for AI reasoning.
    """
    registry_dict = ctx.get_registry_dict()
    owned_vars = get_chapter_variables(chapter_id)
    show_core = should_show_core_data(chapter_id)
    
    scoped = {}
    
    for key, value in registry_dict.items():
        # Include if owned by this chapter
        if key in owned_vars:
            scoped[key] = value
            continue
        
        # Include core data if this is Chapter 0
        if show_core and key in [
            'asking_price_eur', 'living_area_m2', 'plot_area_m2', 
            'build_year', 'energy_label', 'address', 'postal_code', 'city',
        ]:
            scoped[key] = value
            continue
        
        # Always include narrative source text (AI needs this)
        if key in ['description', 'features', 'media_captions', 'media_urls']:
            scoped[key] = value
            continue
        
        # Always include identity info
        if key in ['address', 'funda_url']:
            scoped[key] = value
            continue
        
        # Include match scores and reasons for all chapters
        if key in ['marcel_match_score', 'petra_match_score', 'total_match_score',
                   'marcel_reasons', 'petra_reasons', 'ai_score']:
            scoped[key] = value
            continue
    
    return scoped


def _structure_chapter_output(
    chapter_id: int, 
    narrative: Dict[str, Any],
    ctx: PipelineContext
) -> Dict[str, Any]:
    """
    Structure raw narrative output into consistent chapter format.
    """
    from backend.config.settings import get_settings
    settings = get_settings()
    
    title = narrative.get('title', settings.chapters.titles.get(str(chapter_id), f"Hoofdstuk {chapter_id}"))
    
    # Extract provenance if present
    prov_dict = narrative.get('_provenance')
    
    # Build consistent output structure
    output = {
        "id": str(chapter_id),
        "title": title,
        "grid_layout": {
            "main": {"title": title, "content": narrative.get("main_analysis", "")},
            "metrics": narrative.get("metrics", [{"id": "status", "label": "Status", "value": "Generated"}])
        },
        "blocks": [],
        "chapter_data": {
            "title": title,
            "intro": narrative.get("intro", ""),
            "main_analysis": narrative.get("main_analysis", ""),
            "conclusion": narrative.get("conclusion", ""),
            "strengths": narrative.get("strengths", []),
            "advice": narrative.get("advice", []),
            "interpretation": narrative.get("interpretation", ""),
            "variables": narrative.get("variables", {}),
            "comparison": narrative.get("comparison", {}),
            "sidebar_items": narrative.get("sidebar_items", []),
            "metrics": narrative.get("metrics", [])
        },
        "segment": _get_segment_name(chapter_id),
        "provenance": prov_dict,
        "missing_critical_data": narrative.get('metadata', {}).get('missing_vars', [])
    }
    
    # Special handling for Chapter 0 - include property core
    if chapter_id == 0:
        output["property_core"] = ctx.get_registry_dict()
        output["chapter_data"]["property_core"] = ctx.get_registry_dict()
    
    return output


def _get_segment_name(chapter_id: int) -> str:
    """Get the stylized segment name for a chapter."""
    segments = {
        0: "EXECUTIVE / STRATEGIE",
        1: "OBJECT / ARCHITECTUUR",
        2: "SYNERGIE / MATCH",
        3: "TECHNIEK / CONDITIE",
        4: "ENERGETICA / AUDIT",
        5: "LAYOUT / POTENTIE",
        6: "AFWERKING / ONDERHOUD",
        7: "EXTERIEUR / TUIN",
        8: "MOBILITEIT / PARKEREN",
        9: "JURIDISCH / KADASTER",
        10: "FINANCIEEL / RENDEMENT",
        11: "MARKT / POSITIE",
        12: "VERDICT / STRATEGIE",
        13: "MEDIA / BIBLIOTHEEK"
    }
    return segments.get(chapter_id, f"DOSSIER / SEGMENT {chapter_id}")


def _create_error_output(chapter_id: int, error_message: str) -> Dict[str, Any]:
    """Create an error output structure when generation fails."""
    return {
        "title": f"Generation Error - Chapter {chapter_id}",
        "intro": "An error occurred during chapter generation.",
        "main_analysis": f"<div class='error'>Error: {error_message}</div>",
        "conclusion": "Chapter generation failed.",
        "variables": {},
        "comparison": {},
        "strengths": [],
        "advice": [],
        "_generation_error": True,
        "_error_message": error_message
    }
