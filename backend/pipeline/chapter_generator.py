"""
Chapter Generator - Generates Chapters Using Registry Context

This module generates chapters using the canonical registry from PipelineContext.
Every chapter generation receives the locked registry as its source of truth.

CORE INVARIANTS (NON-NEGOTIABLE):
1. If a factual value appears in AI output, this module MUST reject it
2. AI output is validated against the interpretation schema before processing
3. EVERY chapter (0-12) MUST have a narrative of at least 300 words
4. If narrative is missing or too short, the pipeline MUST FAIL

NARRATIVE ENFORCEMENT:
- NarrativeGenerator.generate() is called for each chapter 0-12
- Narrative word count is validated (minimum 300 words)
- There is NO code path where a chapter is returned without narrative

KEY PRINCIPLES:
1. Chapters receive registry data, not raw data
2. AI output is validated for numeric content (facts are FORBIDDEN)
3. AI and fallback paths both produce the same output structure
4. Validation is NOT the concern of this module - that's done at the spine level
"""

import logging
from typing import Dict, Any, Optional

from backend.domain.pipeline_context import PipelineContext, PipelineViolation
from backend.domain.ownership import OwnershipMap
from backend.domain.guardrails import PolicyLevel
from backend.domain.chapter_variables import get_chapter_variables, should_show_core_data
from backend.domain.narrative_generator import (
    NarrativeGenerator, 
    NarrativeOutput,
    NarrativeGenerationError,
    NarrativeWordCountError
)

logger = logging.getLogger(__name__)


# Chapters that MUST have narrative (0-12, excluding media chapter 13)
NARRATIVE_REQUIRED_CHAPTERS = set(range(13))  # 0-12

# Minimum word count for narrative
NARRATIVE_MINIMUM_WORDS = 300


def generate_chapter_with_validation(ctx: PipelineContext, chapter_id: int) -> Dict[str, Any]:
    """
    Generate a single chapter using the 4-PLANE BACKBONE (for 0-12) or legacy (for 13).
    
    FAIL-CLOSED ARCHITECTURE (Chapters 0-12):
    Every chapter is generated with ALL 4 planes:
    - Plane A: Visual Intelligence (charts, graphs)
    - Plane B: Narrative Reasoning (300+ words prose)
    - Plane C: Factual Anchor (KPIs, data)
    - Plane D: Human Preference (Marcel vs Petra)
    
    No fallback. No partial output. No graceful degradation.
    
    Chapter 13 (Appendix): Uses legacy generation without 4-plane structure.
    
    Args:
        ctx: The locked PipelineContext with canonical registry
        chapter_id: Chapter number (0-13)
    
    Returns:
        Chapter output dict with 4-plane structure (0-12) or legacy format (13)
    
    Raises:
        PipelineViolation: If registry not locked
        BackboneEnforcementError: If plane validation fails (chapters 0-12)
    """
    if not ctx.is_registry_locked():
        raise PipelineViolation("Cannot generate chapter - registry is not locked")
    
    # Build scoped context from registry (respecting ownership)
    scoped_data = _build_scoped_context(ctx, chapter_id)
    
    # Add preferences for AI reasoning
    scoped_data['_preferences'] = ctx.preferences
    
    # ==========================================================================
    # CHAPTER 13 (Appendix): Use legacy generation, NO 4-plane backbone
    # ==========================================================================
    if chapter_id == 13:
        return _generate_legacy_chapter(ctx, chapter_id, scoped_data)
    
    # ==========================================================================
    # STEP 1: Generate narrative using NarrativeGenerator (Chapters 0-12)
    # ==========================================================================
    ai_narrative = None
    if chapter_id in NARRATIVE_REQUIRED_CHAPTERS:
        try:
            narrative_output = _generate_and_validate_narrative(ctx, chapter_id, scoped_data)
            ai_narrative = narrative_output.text
            logger.info(f"Chapter {chapter_id}: Generated narrative ({narrative_output.word_count} words)")
        except Exception as e:
            logger.error(f"Chapter {chapter_id} narrative generation failed: {e}")
            raise PipelineViolation(f"Narrative generation failed for chapter {chapter_id}: {e}")
    
    # ==========================================================================
    # STEP 2: Generate legacy chapter data for additional context
    # ==========================================================================
    from backend.intelligence import IntelligenceEngine
    
    try:
        legacy_narrative = IntelligenceEngine.generate_chapter_narrative(chapter_id, scoped_data)
    except Exception as e:
        logger.warning(f"Chapter {chapter_id} legacy generation failed: {e}")
        legacy_narrative = {}
    
    # ==========================================================================
    # STEP 3: Generate 4-PLANE structure using backbone (FAIL-CLOSED)
    # ==========================================================================
    from backend.pipeline.four_plane_backbone import (
        generate_four_plane_chapter,
        convert_plane_composition_to_dict,
        BackboneEnforcementError
    )
    
    # Merge legacy data with scoped data for plane generation
    chapter_data = {
        **scoped_data,
        **legacy_narrative,
        "variables": legacy_narrative.get("variables", {}),
        "comparison": legacy_narrative.get("comparison", {}),
        "missing_critical_data": legacy_narrative.get("metadata", {}).get("missing_vars", []),
        "provenance": legacy_narrative.get("_provenance", {}),
    }
    
    try:
        # Generate 4-plane composition (validates all planes)
        composition = generate_four_plane_chapter(
            ctx=ctx,
            chapter_id=chapter_id,
            ai_narrative=ai_narrative,
            chapter_data=chapter_data
        )
        
        # Convert to dict format for API/frontend
        output = convert_plane_composition_to_dict(composition)
        
        # Add segment and provenance
        output["segment"] = _get_segment_name(chapter_id)
        output["provenance"] = legacy_narrative.get("_provenance")
        output["missing_critical_data"] = chapter_data.get("missing_critical_data", [])
        
        # Add main_analysis for legacy compatibility (ValidationGate expects this)
        if output.get("plane_b") and output["plane_b"].get("narrative_text"):
            output["main_analysis"] = output["plane_b"]["narrative_text"]
        
        # === FAIL-LOUD DIAGNOSTICS (MANDATORY) ===
        _emit_four_plane_diagnostics(ctx, chapter_id, output, legacy_narrative.get("_provenance", {}))
        
        logger.info(f"Chapter {chapter_id}: 4-plane generation successful")
        
        return output
        
    except BackboneEnforcementError as e:
        # Backbone validation failed - this is FATAL
        # Emit diagnostic block for debugging
        _emit_four_plane_diagnostics_error(ctx, chapter_id, e)
        logger.error(f"Chapter {chapter_id}: BACKBONE ENFORCEMENT FAILED - {e}")
        
        if ctx.truth_policy.enforce_four_plane_structure == PolicyLevel.STRICT:
             raise PipelineViolation(f"{e} (Policy: enforce_four_plane_structure)")
        
        raise PipelineViolation(str(e))


def _generate_legacy_chapter(
    ctx: PipelineContext, 
    chapter_id: int, 
    scoped_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a chapter using legacy (non-4-plane) generation.
    
    Used for Chapter 13 (Appendix) which doesn't require the 4-plane structure.
    """
    from backend.intelligence import IntelligenceEngine
    
    output = IntelligenceEngine.generate_chapter_narrative(chapter_id, scoped_data)
    output = _structure_chapter_output(chapter_id, output, ctx)
    output["segment"] = _get_segment_name(chapter_id)
    
    return output


def _generate_and_validate_narrative(
    ctx: PipelineContext, 
    chapter_id: int, 
    scoped_data: Dict[str, Any]
) -> NarrativeOutput:
    """
    Generate and validate narrative for a chapter.
    
    This is the SINGLE point where narrative is generated.
    There is NO fallback. There is NO skip.
    
    Args:
        ctx: Pipeline context
        chapter_id: Chapter number
        scoped_data: Scoped data context for this chapter
    
    Returns:
        NarrativeOutput with validated text and word count
    
    Raises:
        PipelineViolation: If narrative generation fails or word count < 300
    """
    # Get AI provider if available
    from backend.intelligence import IntelligenceEngine
    ai_provider = IntelligenceEngine._provider
    
    try:
        narrative_output = NarrativeGenerator.generate(
            chapter_id=chapter_id,
            context=scoped_data,
            ai_provider=ai_provider
        )
        
        # Validate word count
        if narrative_output.word_count < NARRATIVE_MINIMUM_WORDS:
            raise PipelineViolation(
                f"Chapter {chapter_id} narrative too short: {narrative_output.word_count} words "
                f"(minimum {NARRATIVE_MINIMUM_WORDS})"
            )
        
        logger.info(
            f"Chapter {chapter_id} narrative generated: {narrative_output.word_count} words"
        )
        
        return narrative_output
        
    except NarrativeWordCountError as e:
        if ctx.truth_policy.fail_closed_narrative_generation == PolicyLevel.STRICT:
             # This is already raising Violation, so we just add policy note
             raise PipelineViolation(f"{e} (Policy: fail_closed_narrative_generation)")
        raise PipelineViolation(str(e))

    except NarrativeGenerationError as e:
        if ctx.truth_policy.fail_closed_narrative_generation == PolicyLevel.STRICT:
            raise PipelineViolation(f"Chapter {chapter_id} narrative generation failed: {e} (Policy: fail_closed_narrative_generation)")
        raise PipelineViolation(f"Chapter {chapter_id} narrative generation failed: {e}")

    except Exception as e:
        # Any other error is still a pipeline violation
        logger.error(f"Narrative generation failed for Chapter {chapter_id}: {e}")
        if ctx.truth_policy.fail_closed_narrative_generation == PolicyLevel.STRICT:
             raise PipelineViolation(f"Chapter {chapter_id} narrative generation error: {e} (Policy: fail_closed_narrative_generation)")
        raise PipelineViolation(f"Chapter {chapter_id} narrative generation error: {e}")


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


# =============================================================================
# FAIL-LOUD DIAGNOSTICS (MANDATORY)
# =============================================================================

def _emit_four_plane_diagnostics(
    ctx: PipelineContext, 
    chapter_id: int, 
    output: Dict[str, Any],
    provenance: Dict[str, Any]
) -> None:
    """
    Emit a copy/paste diagnostic block to logs.
    
    This is MANDATORY for fail-loud behavior - allows user to copy/paste
    diagnostics when debugging 4-plane rendering issues.
    """
    diagnostics = output.get("diagnostics", {})
    plane_status = diagnostics.get("plane_status", {})
    
    # Determine if any planes are problematic
    missing_planes = [p for p, s in plane_status.items() if s in ("missing", "empty", "insufficient")]
    
    log_block = f"""
=== 4PLANE DIAGNOSTICS (COPY/PASTE) ===
run_id={ctx.run_id}
chapter_id={chapter_id}
mode={ctx.preferences.get('mode', 'unknown')}
provider={provenance.get('provider', 'unknown')}
model={provenance.get('model', 'unknown')}
plane_status=A:{plane_status.get('A', '?')},B:{plane_status.get('B', '?')},C:{plane_status.get('C', '?')},D:{plane_status.get('D', '?')}
missing_planes={','.join(missing_planes) if missing_planes else 'none'}
missing_fields={','.join(diagnostics.get('missing_required_fields', [])) or 'none'}
validation_passed={diagnostics.get('validation_passed', 'unknown')}
exception=none
=======================================
"""
    
    # Log based on result
    if missing_planes:
        logger.warning(log_block)
    else:
        logger.info(f"Chapter {chapter_id}: 4-plane diagnostics OK - plane_status={plane_status}")


def _emit_four_plane_diagnostics_error(
    ctx: PipelineContext, 
    chapter_id: int, 
    error: Exception
) -> None:
    """
    Emit a copy/paste diagnostic block to logs when 4-plane generation fails.
    
    This is MANDATORY for fail-loud behavior.
    """
    log_block = f"""
=== 4PLANE DIAGNOSTICS (COPY/PASTE) ===
run_id={ctx.run_id}
chapter_id={chapter_id}
mode={ctx.preferences.get('mode', 'unknown')}
provider=error
model=error
plane_status=FAILED
missing_planes=ALL
missing_fields=ALL
validation_passed=False
exception={type(error).__name__}
stack_hint={str(error)[:200]}
=======================================
"""
    logger.error(log_block)

