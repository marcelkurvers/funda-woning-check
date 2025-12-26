"""
Pipeline Bridge - Integration with Database-Driven Workflow (FAIL-CLOSED)

This module bridges the PipelineSpine with the existing database-driven
workflow in main.py. It provides the ONLY valid entry point for report generation.

FAIL-CLOSED ENFORCEMENT:
1. All execution flows through the spine
2. Validation is BLOCKING on every chapter
3. The database receives ONLY validated, structured output
4. No bypass paths exist

If validation fails in production, the pipeline ABORTS.
"""

import os
import logging
from typing import Dict, Any, Tuple, Optional

from backend.pipeline.spine import PipelineSpine, is_production_mode
from backend.domain.pipeline_context import PipelineViolation, ValidationFailure
from backend.domain.registry import RegistryConflict, RegistryLocked

logger = logging.getLogger(__name__)


def execute_report_pipeline(
    run_id: str,
    raw_data: Dict[str, Any],
    preferences: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Execute the full report pipeline through the spine.
    
    This is the ONLY function that main.py should call.
    All other generation paths are deprecated and blocked.
    
    FAIL-CLOSED BEHAVIOR:
    - In production: validation failure raises PipelineViolation
    - Registry conflicts raise RegistryConflict
    - No partial output, no warnings-only - failures are fatal
    
    Args:
        run_id: Unique run identifier
        raw_data: Parsed property data from scraper/parser
        preferences: Marcel & Petra preferences
    
    Returns:
        Tuple of (chapters_dict, kpis_dict, enriched_core_dict, core_summary_dict)
        
        chapters_dict: Dict mapping chapter ID strings to validated chapter output
        kpis_dict: Dict containing dashboard KPI cards + validation_passed flag
        enriched_core: Enriched registry dict for database storage
        core_summary: MANDATORY backbone contract (CoreSummary as dict)
        
    Raises:
        PipelineViolation: If validation fails (production mode)
        RegistryConflict: If registry conflicts occur
        RegistryLocked: If attempting to modify locked registry
    """
    logger.info(f"Pipeline Bridge: Starting execution for run {run_id}")
    
    # Determine strict mode
    strict = is_production_mode()
    
    try:
        spine, output = PipelineSpine.execute_full_pipeline(
            run_id=run_id,
            raw_data=raw_data,
            preferences=preferences,
            strict_validation=strict
        )
    except PipelineViolation as e:
        logger.error(f"Pipeline Bridge: FATAL - Validation failure - {e}")
        raise  # Re-raise - no graceful degradation
    except RegistryConflict as e:
        logger.error(f"Pipeline Bridge: FATAL - Registry conflict - {e}")
        raise  # Re-raise - no graceful degradation
    except Exception as e:
        logger.error(f"Pipeline Bridge: FATAL - Unexpected error - {e}")
        raise  # Re-raise - no swallowing of errors
    
    # Convert chapters output to expected format
    chapters = output.get("chapters", {})
    
    # INJECT DASHBOARD AS CHAPTER 0 (LAW 2)
    # The dashboard is a first-class output that replaces the old KPI summary.
    # We map it to Chapter 0 so the frontend renders it as the primary view.
    dashboard_data = spine.ctx.get_dashboard()
    if dashboard_data:
        chapter_0 = _convert_dashboard_to_chapter(dashboard_data, spine.ctx)
        chapters["0"] = chapter_0
        # Also validate it technically to be safe? It's already validated by generator.
    
    # Build KPIs from registry data (Legacy support + Dashboard alignment)
    kpis = _build_kpis_from_spine(spine)
    
    # Get enriched core for database storage
    enriched_core = spine.ctx.get_registry_dict()
    
    # === MANDATORY: Get CoreSummary from output ===
    # CoreSummary is the backbone contract - MUST be present
    core_summary = output.get("core_summary", {})
    if not core_summary:
        logger.error(f"Pipeline Bridge: FATAL - CoreSummary missing from output")
        raise PipelineViolation("CoreSummary is MANDATORY but was not found in pipeline output")
    
    logger.info(
        f"Pipeline Bridge: Complete. {len(chapters)} chapters, "
        f"validation_passed={output.get('validation_passed')}, "
        f"core_summary_completeness={core_summary.get('completeness_score', 'N/A')}"
    )
    
    return chapters, kpis, enriched_core, core_summary


def _convert_dashboard_to_chapter(dashboard: Dict[str, Any], ctx: Any) -> Dict[str, Any]:
    """Convert strict DashboardOutput to Chapter 0 format for frontend."""
    content = dashboard.get("dashboard", {})
    narrative = content.get("narrative", {})
    
    # Format Top Drivers as list items
    drivers = content.get("top_decision_drivers", [])
    risks = content.get("risks_and_unknowns", [])
    
    # Construct the chapter mapping
    return {
        "id": "0",
        "title": "EXECUTIVE DASHBOARD",
        "narrative": narrative, # Pass strictly
        "segment": "BESLUITVORMING",
        "chapter_data": {
            "title": "Executive Besluitvorming",
            "intro": "Directie Samenvatting",
            "main_analysis": narrative.get("text", ""), # This ensures narrative renders in main block
            "sections": [
                {"title": "Strategische Drivers", "items": drivers},
                {"title": "Risico's & Onzekerheden", "items": risks}
            ],
            "metrics": _build_dashboard_metrics(content, ctx),
            "narrative": narrative # Redundant but safe for frontend
        },
        "grid_layout": {
             # Basic layout for compatibility
             "main": {"content": narrative.get("text", "")},
             "metrics": _build_dashboard_metrics(content, ctx)
        }
    }


def _build_dashboard_metrics(content: Dict[str, Any], ctx: Any) -> list:
    """Build metrics list from dashboard content."""
    coverage = content.get("coverage", {}).get("score", 0)
    marcel_score = content.get("persona_alignment", {}).get("marcel", {}).get("score", 0)
    petra_score = content.get("persona_alignment", {}).get("petra", {}).get("score", 0)
    
    return [
        {"id": "marcel", "label": "Marcel Match", "value": f"{marcel_score}%"},
        {"id": "petra", "label": "Petra Match", "value": f"{petra_score}%"},
        {"id": "quality", "label": "Data Kwaliteit", "value": f"{int(coverage*100)}%"}
    ]


def _build_kpis_from_spine(spine: PipelineSpine) -> Dict[str, Any]:
    """Build KPI dashboard data from the pipeline spine."""
    ctx = spine.ctx
    
    # Get key values from registry
    price = ctx.get_registry_value("asking_price_eur") or 0
    total_match = ctx.get_registry_value("total_match_score") or 50
    energy_label = ctx.get_registry_value("energy_label") or "?"
    
    # Calculate completeness
    fields = ["asking_price_eur", "living_area_m2", "plot_area_m2", "build_year", "energy_label"]
    present = sum(1 for f in fields if ctx.get_registry_value(f))
    completeness = round(present / len(fields), 2)
    
    # Fit score from registry
    fit_score = total_match / 100.0
    
    # Format price
    if isinstance(price, (int, float)) and price > 0:
        value_text = f"€ {int(price):,}".replace(',', '.')
    else:
        value_text = "€ N/B"
    
    cards = [
        {
            "id": "fit",
            "title": "Match Score",
            "value": f"{int(fit_score * 100)}%",
            "trend": "up" if fit_score > 0.6 else "neutral",
            "desc": "Match Marcel & Petra"
        },
        {
            "id": "completeness",
            "title": "Data Kwaliteit",
            "value": f"{int(completeness * 100)}%",
            "trend": "up" if completeness > 0.8 else "neutral",
            "desc": "Extrahering"
        },
        {
            "id": "value",
            "title": "Vraagprijs",
            "value": value_text,
            "trend": "neutral",
            "desc": "Per direct"
        },
        {
            "id": "energy",
            "title": "Energielabel",
            "value": energy_label,
            "trend": "neutral",
            "desc": "Duurzaamheid"
        }
    ]
    
    return {
        "dashboard_cards": cards,
        "completeness": completeness,
        "fit_score": fit_score,
        "validation_passed": spine.ctx.all_chapters_valid(),
        "registry_entry_count": len(spine.ctx.registry.get_all())
    }


def build_unknowns_from_context(ctx) -> list:
    """Build list of missing/unknown fields from context."""
    fields = ["asking_price_eur", "living_area_m2", "plot_area_m2", "build_year", "energy_label", "rooms", "bedrooms"]
    return [f for f in fields if not ctx.get_registry_value(f)]


# =============================================================================
# DEPRECATED BYPASS BLOCKER
# =============================================================================

def _raise_bypass_blocked(func_name: str):
    """Raise an error when a deprecated bypass function is called."""
    raise PipelineViolation(
        f"FATAL: Bypass attempt blocked. The function '{func_name}' is deprecated "
        f"and CANNOT be used. All report generation MUST go through execute_report_pipeline(). "
        f"This is a structural enforcement - no exceptions."
    )
