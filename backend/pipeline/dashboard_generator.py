"""
Dashboard Generator - Generates Decision-Grade Dashboard

This module generates the first-class dashboard output.
It aggregates findings from all chapters and produces an executive decision memo.

CORE INVARIANTS:
1. Dashboard narrative MUST be 500-800 words
2. Narrative must be derived from chapters 1-12
3. Pipeline MUST fail if dashboard narrative is missing
"""

import logging
from typing import Dict, Any, List

from backend.domain.pipeline_context import PipelineContext, PipelineViolation
from backend.domain.models import DashboardOutput, DashboardContent, NarrativeContract, PersonaAlignment
from backend.domain.narrative_generator import NarrativeGenerator, NarrativeOutput
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)

DASHBOARD_MIN_WORDS = 500

def generate_dashboard_with_validation(ctx: PipelineContext) -> DashboardOutput:
    """
    Generate the dashboard with mandatory validation.
    
    Args:
        ctx: Pipeline context containing registry and generated chapters
    
    Returns:
        Validated DashboardOutput
    
    Raises:
        PipelineViolation: If validation fails
    """
    logger.info("DashboardGenerator: Starting generation")
    
    if not ctx.all_chapters_valid():
        raise PipelineViolation("Cannot generate dashboard: One or more chapters failed validation")
    
    # 1. Aggregate Context
    dashboard_context = _build_dashboard_context(ctx)
    
    # 2. Compute Structured Data (Heuristic/Registry-based)
    # In a full V3 implementation, this might also be AI-enhanced, 
    # but for now we derive it strictly from the registry to ensure speed & stability.
    structure = _derive_dashboard_structure(ctx)
    
    # 3. Generate Narrative (MANDATORY)
    from backend.intelligence import IntelligenceEngine
    ai_provider = IntelligenceEngine._provider
    
    try:
        narrative_out = NarrativeGenerator.generate_dashboard(
            context=dashboard_context,
            ai_provider=ai_provider
        )
        
        # 4. Final Validation (Double check)
        if narrative_out.word_count < DASHBOARD_MIN_WORDS:
             raise PipelineViolation(f"Dashboard narrative too short: {narrative_out.word_count} words")
             
    except Exception as e:
        logger.error(f"Dashboard narrative generation failed: {e}")
        raise PipelineViolation(f"Dashboard generation failed: {e}")
    
    # 5. Assemble Output
    content = DashboardContent(
        coverage=structure.get("coverage", {}),
        top_decision_drivers=structure.get("drivers", []),
        risks_and_unknowns=structure.get("risks", []),
        persona_alignment=PersonaAlignment(
            marcel=structure.get("marcel_alignment", {}),
            petra=structure.get("petra_alignment", {})
        ),
        narrative=NarrativeContract(
            text=narrative_out.text,
            word_count=narrative_out.word_count
        )
    )
    
    return DashboardOutput(dashboard=content)


def _build_dashboard_context(ctx: PipelineContext) -> Dict[str, Any]:
    """Build context for the AI."""
    reg = ctx.get_registry_dict()
    
    # Summary of key registry items
    summary = {
        k: v for k, v in reg.items() 
        if k in ['asking_price_eur', 'living_area_m2', 'energy_label', 
                 'total_match_score', 'marcel_match_score', 'petra_match_score']
    }
    
    # Get risks/issues from chapter data if available
    # We can scan the validated chapters for "metrics" or "advice"
    risks = []
    # This is a simplification; in V3 we'd extract specific risk flags
    
    return {
        "registry_summary": summary,
        "risks": risks,
        "scores": {
            "total": reg.get('total_match_score'),
            "marcel": reg.get('marcel_match_score'),
            "petra": reg.get('petra_match_score')
        },
        "_preferences": ctx.preferences
    }


def _derive_dashboard_structure(ctx: PipelineContext) -> Dict[str, Any]:
    """Derive the structured parts of the dashboard."""
    reg = ctx.get_registry_dict()
    
    # Coverage
    fields = ["asking_price_eur", "living_area_m2", "plot_area_m2", "build_year", "energy_label"]
    present = sum(1 for f in fields if reg.get(f))
    coverage = {
        "score": round(present / len(fields), 2),
        "missing": [f for f in fields if not reg.get(f)]
    }
    
    # Drivers - Top 3 strongest points
    # Derived from match reasons
    drivers = []
    marcel_reasons = reg.get('marcel_reasons', [])
    petra_reasons = reg.get('petra_reasons', [])
    
    if marcel_reasons: drivers.extend(marcel_reasons[:2])
    if petra_reasons: drivers.extend(petra_reasons[:2])
    
    # Risks - Low scores or unknowns
    risks = []
    if not reg.get('energy_label'): risks.append("Energielabel onbekend")
    if (reg.get('total_match_score') or 0) < 60: risks.append("Lage match score")
    
    return {
        "coverage": coverage,
        "drivers": drivers[:5],
        "risks": risks,
        "marcel_alignment": {"score": reg.get('marcel_match_score', 0)},
        "petra_alignment": {"score": reg.get('petra_match_score', 0)}
    }
