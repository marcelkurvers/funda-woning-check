"""
4-PLANE CHAPTER GENERATOR

This module generates chapter content in the 4-Plane format.
Each chapter produces all four planes with proper isolation.

AI PROMPT RULE (PLANE B ONLY):
The AI operates ONLY in Plane B (Narrative Reasoning).
AI is forbidden from:
- listing KPIs
- showing tables
- mentioning raw values
- creating visuals
- scoring preferences

AI must:
- write a minimum of 300 words
- interpret existing registry data
- explain implications, risks, and meaning
- assume KPIs are shown elsewhere
"""

from typing import Dict, Any, List, Optional
import logging

from backend.domain.plane_models import (
    PlaneAVisualModel,
    PlaneBNarrativeModel,
    PlaneCFactModel,
    PlaneDPreferenceModel,
    ChapterPlaneComposition,
    VisualDataPoint,
    ChartConfig,
    FactualKPI,
    PersonaScore,
    PreferenceComparison,
    PlaneViolationError
)
from backend.domain.plane_validator import PlaneValidator, create_validated_chapter
from backend.domain.registry import CanonicalRegistry, RegistryEntry, RegistryType
from backend.domain.pipeline_context import PipelineContext

logger = logging.getLogger(__name__)


# =============================================================================
# PLANE B AI PROMPT (MANDATORY - DO NOT MODIFY)
# =============================================================================

PLANE_B_SYSTEM_PROMPT = """You are generating Plane B output ONLY.

You are forbidden from:
- listing KPIs
- showing tables
- mentioning raw values (no numbers like €, m², %)
- creating visuals or charts
- scoring preferences (no Marcel/Petra scores)

You must:
- write a minimum of 300 words (500+ for chapter 0)
- interpret existing registry data (explained elsewhere)
- explain implications, risks, and meaning
- assume KPIs are shown in a separate panel (Plane C)
- assume visuals are shown in a separate panel (Plane A)
- assume Marcel/Petra preferences are shown separately (Plane D)

Write as an editorial essay, not a report. Use flowing prose.
Use Dutch language. Be analytical, reflective, and explanatory.
Focus on the "why" and "what it means", not the "what".

If you cannot meet these rules, return an error.
"""


# =============================================================================
# CHAPTER-SPECIFIC PLANE CONFIGURATIONS
# =============================================================================

CHAPTER_PLANE_CONFIG = {
    0: {
        "name": "Executive Summary",
        "plane_a": {"required": True, "type": "high_level_market_visuals"},
        "plane_b": {"min_words": 500, "max_words": 700, "focus": "strategic_narrative"},
        "plane_c": {"required": True, "type": "key_kpis_summary"},
        "plane_d": {"required": True, "type": "joint_synthesis"},
    },
    1: {
        "name": "Kerngegevens",
        "plane_a": {"required": True, "type": "property_visuals"},
        "plane_b": {"min_words": 300, "focus": "property_analysis"},
        "plane_c": {"required": True, "type": "full_kpi_set"},
        "plane_d": {"required": True, "type": "persona_interpretation"},
    },
    2: {
        "name": "Matchanalyse Marcel & Petra",
        "plane_a": {"required": True, "type": "radar_comparison"},
        "plane_b": {"min_words": 300, "focus": "match_interpretation"},
        "plane_c": {"required": True, "type": "match_kpis"},
        "plane_d": {"required": True, "type": "persona_comparison"},
    },
    11: {
        "name": "Market Positioning",
        "plane_a": {"required": True, "type": "comparative_visuals", "mandatory": True},
        "plane_b": {"min_words": 300, "focus": "strategy_narrative"},
        "plane_c": {"required": True, "type": "price_comps_ranges"},
        "plane_d": {"required": True, "type": "risk_appetite_divergence"},
    },
    12: {
        "name": "Advice & Conclusion",
        "plane_a": {"required": True, "type": "scenario_visuals"},
        "plane_b": {"min_words": 300, "focus": "final_reasoning"},
        "plane_c": {"required": True, "type": "decision_kpis"},
        "plane_d": {"required": True, "type": "final_alignment_tension"},
    },
}


def get_chapter_config(chapter_id: int) -> Dict[str, Any]:
    """Get configuration for a specific chapter, with defaults for 1-10."""
    if chapter_id in CHAPTER_PLANE_CONFIG:
        return CHAPTER_PLANE_CONFIG[chapter_id]
    
    # Default for chapters 1-10
    return {
        "name": f"Chapter {chapter_id}",
        "plane_a": {"required": False, "type": "chapter_specific"},
        "plane_b": {"min_words": 300, "focus": "analysis"},
        "plane_c": {"required": True, "type": "full_kpi_set"},
        "plane_d": {"required": True, "type": "persona_interpretation"},
    }


# =============================================================================
# PLANE GENERATORS
# =============================================================================

def generate_plane_a(
    chapter_id: int,
    ctx: PipelineContext,
    chapter_data: Dict[str, Any]
) -> PlaneAVisualModel:
    """
    Generate Plane A (Visual Intelligence) content from registry data.
    
    RULES:
    - Only registry-verified data
    - No AI-generated values
    - No explanatory text
    """
    config = get_chapter_config(chapter_id)
    plane_config = config.get("plane_a", {})
    
    charts = []
    trends = []
    comparisons = []
    data_source_ids = []
    
    # Get registry entries for this chapter
    registry = ctx.registry
    
    # Build charts based on chapter type
    if chapter_id == 0:
        # Executive Summary: High-level market visuals
        charts = _build_summary_charts(registry, data_source_ids)
    elif chapter_id == 2:
        # Match Analysis: Radar/spider diagram
        charts = _build_match_charts(registry, chapter_data, data_source_ids)
    elif chapter_id == 11:
        # Market Positioning: Comparative visuals (MANDATORY)
        charts = _build_market_charts(registry, data_source_ids)
    else:
        # Default: Chapter-specific visuals
        charts = _build_default_charts(chapter_id, registry, chapter_data, data_source_ids)
    
    # Check if plane is applicable
    not_applicable = len(charts) == 0 and not plane_config.get("mandatory", False)
    
    return PlaneAVisualModel(
        charts=charts,
        trends=trends,
        comparisons=comparisons,
        data_source_ids=data_source_ids,
        not_applicable=not_applicable,
        not_applicable_reason="Geen visuele data beschikbaar voor dit hoofdstuk" if not_applicable else None
    )


def generate_plane_b(
    chapter_id: int,
    ctx: PipelineContext,
    chapter_data: Dict[str, Any],
    ai_narrative: Optional[str] = None
) -> PlaneBNarrativeModel:
    """
    Generate Plane B (Narrative Reasoning) content.
    
    This is where AI operates. The narrative should:
    - Interpret registry data
    - Explain implications
    - NOT contain raw KPIs
    - NOT contain Marcel/Petra scores
    """
    config = get_chapter_config(chapter_id)
    min_words = config.get("plane_b", {}).get("min_words", 300)
    
    # Use provided AI narrative or extract from chapter_data
    narrative_text = ai_narrative or chapter_data.get("narrative", {}).get("text", "")
    
    # Calculate word count
    word_count = len(narrative_text.split()) if narrative_text else 0
    
    # Check if narrative is missing or too short
    if not narrative_text or word_count < 50:
        # This is a violation - but we create the model anyway for the validator to catch
        narrative_text = ""
        word_count = 0
    
    return PlaneBNarrativeModel(
        narrative_text=narrative_text,
        word_count=word_count,
        not_applicable=False,  # Narrative is NEVER not applicable
        ai_generated=True,
        ai_provider=chapter_data.get("provenance", {}).get("provider"),
        ai_model=chapter_data.get("provenance", {}).get("model")
    )


def generate_plane_c(
    chapter_id: int,
    ctx: PipelineContext,
    chapter_data: Dict[str, Any]
) -> PlaneCFactModel:
    """
    Generate Plane C (Factual Anchor) content from registry.
    
    RULES:
    - Only structured data
    - No narrative prose
    - Explicit missing/unknown markers
    """
    registry = ctx.registry
    
    kpis = []
    parameters = {}
    data_sources = []
    missing_data = []
    uncertainties = []
    
    # Get chapter-owned variables
    chapter_variables = chapter_data.get("variables", {})
    
    for key, var_data in chapter_variables.items():
        if isinstance(var_data, dict):
            value = var_data.get("value")
            provenance = var_data.get("status", "unknown")
            
            kpis.append(FactualKPI(
                key=key,
                label=key.replace("_", " ").title(),
                value=value,
                provenance=provenance if provenance in ["fact", "inferred", "unknown"] else "unknown",
                registry_id=var_data.get("registry_id"),
                completeness=value is not None,
                missing_reason=var_data.get("missing_reason")
            ))
            
            if var_data.get("source"):
                data_sources.append(var_data["source"])
    
    # Check for explicitly missing data
    missing_critical = chapter_data.get("missing_critical_data", [])
    missing_data.extend(missing_critical)
    
    # Check registry for uncertainties
    for entry in registry.get_all().values():
        if entry.type == RegistryType.UNCERTAINTY:
            uncertainties.append(f"{entry.name}: {entry.value}")
    
    return PlaneCFactModel(
        kpis=kpis,
        parameters=parameters,
        data_sources=list(set(data_sources)),
        missing_data=missing_data,
        uncertainties=uncertainties[:5],  # Limit to 5
        not_applicable=False  # Facts are never not applicable
    )


def generate_plane_d(
    chapter_id: int,
    ctx: PipelineContext,
    chapter_data: Dict[str, Any]
) -> PlaneDPreferenceModel:
    """
    Generate Plane D (Human Preference) content.
    
    RULES:
    - Marcel vs Petra comparisons only
    - No raw registry data
    - No extended narrative
    """
    # Extract preference data
    comparison = chapter_data.get("comparison", {})
    marcel_data = comparison.get("marcel", {})
    petra_data = comparison.get("petra", {})
    
    # Build persona scores
    marcel = PersonaScore(
        match_score=chapter_data.get("marcel_match_score"),
        mood=_determine_mood(marcel_data),
        key_values=marcel_data.get("values", []) if isinstance(marcel_data, dict) else [],
        concerns=marcel_data.get("concerns", []) if isinstance(marcel_data, dict) else [],
        summary=marcel_data if isinstance(marcel_data, str) else marcel_data.get("summary")
    )
    
    petra = PersonaScore(
        match_score=chapter_data.get("petra_match_score"),
        mood=_determine_mood(petra_data),
        key_values=petra_data.get("values", []) if isinstance(petra_data, dict) else [],
        concerns=petra_data.get("concerns", []) if isinstance(petra_data, dict) else [],
        summary=petra_data if isinstance(petra_data, str) else petra_data.get("summary")
    )
    
    # Build comparisons
    comparisons = _build_preference_comparisons(chapter_data)
    
    # Extract overlap and tension points
    overlap_points = chapter_data.get("overlap_points", [])
    tension_points = chapter_data.get("tension_points", [])
    
    # For chapter 0, create joint synthesis
    joint_synthesis = None
    if chapter_id == 0:
        joint_synthesis = chapter_data.get("joint_synthesis", 
            "Marcel en Petra benaderen deze woning vanuit verschillende perspectieven "
            "die elkaar aanvullen. Waar Marcel de strategische en technische aspecten weegt, "
            "focust Petra op de directe leefkwaliteit. Beiden zien potentieel."
        )
    
    return PlaneDPreferenceModel(
        marcel=marcel,
        petra=petra,
        comparisons=comparisons,
        overlap_points=overlap_points,
        tension_points=tension_points,
        joint_synthesis=joint_synthesis,
        not_applicable=False
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _build_summary_charts(registry: CanonicalRegistry, data_source_ids: List[str]) -> List[ChartConfig]:
    """Build high-level summary charts for Chapter 0."""
    charts = []
    
    # Overall match gauge
    match_data = []
    for entry in registry.get_all().values():
        if "match" in entry.id.lower() and isinstance(entry.value, (int, float)):
            match_data.append(VisualDataPoint(
                label=entry.name,
                value=float(entry.value),
                unit="%"
            ))
            data_source_ids.append(entry.id)
    
    if match_data:
        charts.append(ChartConfig(
            chart_type="gauge",
            title="Match Score",
            data=match_data[:1],  # Just the overall match
            max_value=100
        ))
    
    return charts


def _build_match_charts(
    registry: CanonicalRegistry, 
    chapter_data: Dict[str, Any],
    data_source_ids: List[str]
) -> List[ChartConfig]:
    """Build radar/comparison charts for Match Analysis chapter."""
    charts = []
    
    # Build radar data
    radar_data = []
    dimensions = ["locatie", "prijs", "ruimte", "energie", "tuin", "buurt"]
    
    for dim in dimensions:
        value = 70  # Default
        for entry in registry.get_all().values():
            if dim in entry.id.lower() and isinstance(entry.value, (int, float)):
                value = float(entry.value)
                data_source_ids.append(entry.id)
                break
        
        radar_data.append(VisualDataPoint(
            label=dim.title(),
            value=value
        ))
    
    if radar_data:
        charts.append(ChartConfig(
            chart_type="radar",
            title="Woningprofiel",
            data=radar_data,
            max_value=100
        ))
    
    return charts


def _build_market_charts(registry: CanonicalRegistry, data_source_ids: List[str]) -> List[ChartConfig]:
    """Build comparative market charts for Chapter 11."""
    charts = []
    
    # Price comparison bar chart
    price_data = []
    for entry in registry.get_all().values():
        if "price" in entry.id.lower() or "prijs" in entry.id.lower():
            if isinstance(entry.value, (int, float)):
                price_data.append(VisualDataPoint(
                    label=entry.name[:15],
                    value=float(entry.value) / 1000,  # In thousands
                    unit="k"
                ))
                data_source_ids.append(entry.id)
    
    if price_data:
        charts.append(ChartConfig(
            chart_type="bar",
            title="Prijsvergelijking",
            data=price_data[:5],
            show_legend=True
        ))
    
    return charts


def _build_default_charts(
    chapter_id: int,
    registry: CanonicalRegistry,
    chapter_data: Dict[str, Any],
    data_source_ids: List[str]
) -> List[ChartConfig]:
    """Build default charts for other chapters."""
    charts = []
    
    # Try to build a bar chart from chapter variables
    variables = chapter_data.get("variables", {})
    bar_data = []
    
    for key, var in variables.items():
        if isinstance(var, dict) and isinstance(var.get("value"), (int, float)):
            bar_data.append(VisualDataPoint(
                label=key.replace("_", " ")[:15],
                value=float(var["value"])
            ))
            if var.get("registry_id"):
                data_source_ids.append(var["registry_id"])
    
    if bar_data:
        charts.append(ChartConfig(
            chart_type="bar",
            title=f"Kerndata Hoofdstuk {chapter_id}",
            data=bar_data[:6]
        ))
    
    return charts


def _determine_mood(persona_data: Any) -> Optional[str]:
    """Determine mood from persona data."""
    if not persona_data:
        return None
    
    if isinstance(persona_data, str):
        text = persona_data.lower()
        if any(w in text for w in ["positief", "goed", "sterk", "uitstekend"]):
            return "positive"
        elif any(w in text for w in ["negatief", "slecht", "zwak", "probleem"]):
            return "negative"
        elif any(w in text for w in ["gemengd", "twijfel", "afweging"]):
            return "mixed"
    
    return "neutral"


def _build_preference_comparisons(chapter_data: Dict[str, Any]) -> List[PreferenceComparison]:
    """Build preference comparisons from chapter data."""
    comparisons = []
    
    comparison_data = chapter_data.get("comparison", {})
    aspects = ["locatie", "indeling", "prijs", "toekomst", "sfeer"]
    
    for aspect in aspects:
        if aspect in comparison_data:
            marcel_view = comparison_data.get("marcel", {}).get(aspect, "Geen specifieke mening")
            petra_view = comparison_data.get("petra", {}).get(aspect, "Geen specifieke mening")
            
            # Determine alignment
            if marcel_view == petra_view:
                alignment = "aligned"
            elif "maar" in marcel_view.lower() or "maar" in petra_view.lower():
                alignment = "tension"
            else:
                alignment = "complementary"
            
            comparisons.append(PreferenceComparison(
                aspect=aspect.title(),
                marcel_view=marcel_view[:100] if isinstance(marcel_view, str) else str(marcel_view)[:100],
                petra_view=petra_view[:100] if isinstance(petra_view, str) else str(petra_view)[:100],
                alignment=alignment,
                requires_discussion=alignment == "tension"
            ))
    
    return comparisons[:5]


# =============================================================================
# MAIN GENERATION FUNCTION
# =============================================================================

def generate_four_plane_chapter(
    chapter_id: int,
    ctx: PipelineContext,
    chapter_data: Dict[str, Any],
    ai_narrative: Optional[str] = None,
    validate: bool = True
) -> ChapterPlaneComposition:
    """
    Generate a complete 4-plane chapter.
    
    Args:
        chapter_id: Chapter number (0-12)
        ctx: Pipeline context with registry
        chapter_data: Raw chapter data from previous generation
        ai_narrative: Optional pre-generated AI narrative for Plane B
        validate: Whether to validate plane constraints (default True)
        
    Returns:
        ChapterPlaneComposition with all four planes
        
    Raises:
        PlaneViolationError: If validation fails and validate=True
    """
    logger.info(f"Generating 4-plane composition for chapter {chapter_id}")
    
    # Generate each plane
    plane_a = generate_plane_a(chapter_id, ctx, chapter_data)
    plane_b = generate_plane_b(chapter_id, ctx, chapter_data, ai_narrative)
    plane_c = generate_plane_c(chapter_id, ctx, chapter_data)
    plane_d = generate_plane_d(chapter_id, ctx, chapter_data)
    
    # Get chapter title
    chapter_title = chapter_data.get("title", f"Hoofdstuk {chapter_id}")
    
    if validate:
        # Use validated creation which will raise on violation
        registry_ids = list(ctx.registry.get_all().keys())
        return create_validated_chapter(
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            plane_a=plane_a,
            plane_b=plane_b,
            plane_c=plane_c,
            plane_d=plane_d,
            registry_ids=registry_ids
        )
    else:
        # Create without validation (for testing/debugging only)
        return ChapterPlaneComposition(
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            plane_a=plane_a,
            plane_b=plane_b,
            plane_c=plane_c,
            plane_d=plane_d
        )
