"""
Pipeline Bridge - Integration with Database-Driven Workflow

This module bridges the new PipelineSpine with the existing database-driven
workflow in main.py. It provides a drop-in replacement for the old 
build_chapters and build_kpis functions.

The bridge ensures:
1. All execution flows through the spine
2. Validation is enforced on every chapter
3. The database receives structured, validated output
"""

import logging
from typing import Dict, Any, Tuple, Optional

from backend.pipeline.spine import PipelineSpine
from backend.domain.pipeline_context import ValidationFailure

logger = logging.getLogger(__name__)


def execute_report_pipeline(
    run_id: str,
    raw_data: Dict[str, Any],
    preferences: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], Dict[str, Any], Any]:
    """
    Execute the full report pipeline through the spine.
    
    This is the bridge function that main.py should call instead of
    the old build_chapters + build_kpis approach.
    
    Args:
        run_id: Unique run identifier
        raw_data: Parsed property data from scraper/parser
        preferences: Marcel & Petra preferences
    
    Returns:
        Tuple of (chapters_dict, kpis_dict, spine_instance)
        
        chapters_dict: Dict mapping chapter ID strings to chapter output
        kpis_dict: Dict containing dashboard KPI cards
        spine: The PipelineSpine instance (for debugging/inspection)
    """
    logger.info(f"Pipeline Bridge: Starting execution for run {run_id}")
    
    try:
        spine, output = PipelineSpine.execute_full_pipeline(
            run_id=run_id,
            raw_data=raw_data,
            preferences=preferences,
            strict_validation=False  # Allow partial output in production
        )
    except Exception as e:
        logger.error(f"Pipeline Bridge: Execution failed - {e}")
        raise
    
    # Convert chapters output to expected format
    chapters = output.get("chapters", {})
    
    # Build KPIs from registry data
    kpis = _build_kpis_from_spine(spine)
    
    # Also update raw_data with enriched values for database storage
    enriched_core = spine.ctx.get_registry_dict()
    
    logger.info(f"Pipeline Bridge: Complete. {len(chapters)} chapters, validation_passed={output.get('validation_passed')}")
    
    return chapters, kpis, enriched_core


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
