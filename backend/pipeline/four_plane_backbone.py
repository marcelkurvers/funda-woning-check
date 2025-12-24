"""
4-PLANE BACKBONE - FAIL-CLOSED ENFORCEMENT

This module is the SINGLE source of truth for 4-plane chapter generation.
No output can be produced without passing through this backbone.

PLANES (ALL MANDATORY):
🟦 PLANE A — VISUAL INTELLIGENCE (LEFT)
    - Charts, graphs, visuals
    - NO text, NO explanations
    - Source: registry data only

🟩 PLANE B — NARRATIVE REASONING (CENTER–UPPER) 
    - Minimum 300 words per chapter
    - Continuous, flowing prose
    - NO KPIs, NO tables, NO raw values
    
🟨 PLANE C — FACTUAL ANCHOR (CENTER–LOWER)
    - KPIs, parameters, facts
    - Compact, structured, factual
    - NO narrative, NO interpretation
    
🟥 PLANE D — HUMAN PREFERENCE (RIGHT)
    - Marcel vs Petra comparisons
    - Overlap and tension points
    - NO general analysis

FAIL-CLOSED PRINCIPLES:
1. Chapter = 4 planes. Missing any plane = chapter invalid
2. Plane content must not cross boundaries
3. Violations cause hard failures, not warnings
4. No fallback paths, no silent degradation
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from backend.domain.plane_models import (
    PlaneAVisualModel,
    PlaneBNarrativeModel,
    PlaneCFactModel,
    PlaneDPreferenceModel,
    ChapterPlaneComposition,
    PlaneViolationError,
    VisualDataPoint,
    ChartConfig,
    FactualKPI,
    PersonaScore,
    PreferenceComparison
)
from backend.domain.plane_validator import PlaneValidator, create_validated_chapter
from backend.domain.registry import CanonicalRegistry
from backend.domain.pipeline_context import PipelineContext, PipelineViolation

logger = logging.getLogger(__name__)


# =============================================================================
# BACKBONE ERROR TYPES
# =============================================================================

class BackboneViolationType(Enum):
    """Types of backbone violations that cause pipeline failure."""
    PLANE_A_MISSING = "plane_a_missing"
    PLANE_B_MISSING = "plane_b_missing"
    PLANE_B_INSUFFICIENT_WORDS = "plane_b_insufficient_words"
    PLANE_B_CONTAINS_KPIS = "plane_b_contains_kpis"
    PLANE_C_MISSING = "plane_c_missing"
    PLANE_C_CONTAINS_NARRATIVE = "plane_c_contains_narrative"
    PLANE_D_MISSING = "plane_d_missing"
    PLANE_D_CONTAINS_ANALYSIS = "plane_d_contains_analysis"
    CROSS_PLANE_CONTENT = "cross_plane_content"


@dataclass
class BackboneViolation:
    """A violation detected by the backbone validator."""
    chapter_id: int
    plane: str
    violation_type: BackboneViolationType
    message: str
    
    def to_error_string(self) -> str:
        return f"[Chapter {self.chapter_id}][Plane {self.plane}] {self.violation_type.value}: {self.message}"


class BackboneEnforcementError(Exception):
    """
    FATAL ERROR: Backbone validation failed.
    
    This error CANNOT be caught and ignored.
    It means the pipeline output is INVALID.
    """
    def __init__(self, violations: List[BackboneViolation]):
        self.violations = violations
        message = (
            f"BACKBONE ENFORCEMENT FAILED\n"
            f"4-Plane structure violated. Output rejected.\n"
            f"{len(violations)} violation(s):\n" +
            "\n".join(f"  - {v.to_error_string()}" for v in violations)
        )
        super().__init__(message)


# =============================================================================
# BACKBONE GENERATOR
# =============================================================================

class FourPlaneBackbone:
    """
    The 4-Plane Backbone Generator.
    
    This class is responsible for:
    1. Generating all 4 planes for each chapter
    2. Validating plane isolation (no cross-plane content)
    3. Enforcing minimum requirements (300 words for Plane B)
    4. Rejecting invalid output
    
    There is NO fallback. There is NO skip.
    """
    
    # Word count requirements
    MIN_WORDS_CHAPTER_0 = 500  # Executive Summary
    MIN_WORDS_CHAPTERS_1_12 = 300  # Regular chapters
    
    def __init__(self, ctx: PipelineContext):
        """
        Initialize the backbone.
        
        Args:
            ctx: Pipeline context with locked registry
        """
        if not ctx.is_registry_locked():
            raise PipelineViolation("FourPlaneBackbone requires locked registry")
        
        self.ctx = ctx
        self.validator = PlaneValidator()
    
    def generate_chapter(
        self, 
        chapter_id: int,
        ai_narrative: Optional[str] = None,
        chapter_data: Optional[Dict[str, Any]] = None
    ) -> ChapterPlaneComposition:
        """
        Generate a complete 4-plane chapter.
        
        Args:
            chapter_id: Chapter number (0-12)
            ai_narrative: AI-generated narrative for Plane B
            chapter_data: Additional chapter data from existing generation
        
        Returns:
            Complete ChapterPlaneComposition with all 4 planes
        
        Raises:
            BackboneEnforcementError: If plane validation fails
        """
        if chapter_data is None:
            chapter_data = {}
        
        logger.info(f"FourPlaneBackbone: Generating chapter {chapter_id}")
        
        # Generate each plane
        plane_a = self._generate_plane_a(chapter_id, chapter_data)
        plane_b = self._generate_plane_b(chapter_id, ai_narrative, chapter_data)
        plane_c = self._generate_plane_c(chapter_id, chapter_data)
        plane_d = self._generate_plane_d(chapter_id, chapter_data)
        
        # Get chapter title
        chapter_title = self._get_chapter_title(chapter_id, chapter_data)
        
        # Pre-validate planes before composition
        violations = self._pre_validate_planes(chapter_id, plane_a, plane_b, plane_c, plane_d)
        if violations:
            raise BackboneEnforcementError(violations)
        
        # Create validated composition
        try:
            registry_ids = list(self.ctx.registry.get_all().keys())
            composition = create_validated_chapter(
                chapter_id=chapter_id,
                chapter_title=chapter_title,
                plane_a=plane_a,
                plane_b=plane_b,
                plane_c=plane_c,
                plane_d=plane_d,
                registry_ids=registry_ids
            )
            
            logger.info(
                f"FourPlaneBackbone: Chapter {chapter_id} validated. "
                f"Plane B: {plane_b.word_count} words"
            )
            
            return composition
            
        except PlaneViolationError as e:
            # Convert to backbone error for consistent handling
            raise BackboneEnforcementError([
                BackboneViolation(
                    chapter_id=chapter_id,
                    plane=e.source_plane,
                    violation_type=BackboneViolationType.CROSS_PLANE_CONTENT,
                    message=e.details
                )
            ])
    
    def _pre_validate_planes(
        self,
        chapter_id: int,
        plane_a: PlaneAVisualModel,
        plane_b: PlaneBNarrativeModel,
        plane_c: PlaneCFactModel,
        plane_d: PlaneDPreferenceModel
    ) -> List[BackboneViolation]:
        """Pre-validate planes before composition for clearer error messages."""
        violations = []
        
        # Check Plane B word count
        min_words = self.MIN_WORDS_CHAPTER_0 if chapter_id == 0 else self.MIN_WORDS_CHAPTERS_1_12
        
        if not plane_b.not_applicable and plane_b.word_count < min_words:
            violations.append(BackboneViolation(
                chapter_id=chapter_id,
                plane="B",
                violation_type=BackboneViolationType.PLANE_B_INSUFFICIENT_WORDS,
                message=f"Narrative has {plane_b.word_count} words, minimum is {min_words}"
            ))
        
        # Check for empty Plane B narrative
        if not plane_b.not_applicable and not plane_b.narrative_text.strip():
            violations.append(BackboneViolation(
                chapter_id=chapter_id,
                plane="B",
                violation_type=BackboneViolationType.PLANE_B_MISSING,
                message="Narrative text is empty"
            ))
        
        return violations
    
    def _generate_plane_a(self, chapter_id: int, chapter_data: Dict[str, Any]) -> PlaneAVisualModel:
        """Generate Plane A (Visual Intelligence)."""
        charts = []
        data_source_ids = []
        
        # Build charts from registry data
        registry = self.ctx.registry
        
        if chapter_id == 0:
            # Executive Summary: Overall match gauge
            charts = self._build_summary_charts(registry, data_source_ids)
        elif chapter_id == 2:
            # Match Analysis: Radar diagram
            charts = self._build_match_charts(registry, chapter_data, data_source_ids)
        elif chapter_id == 11:
            # Market: Price comparison
            charts = self._build_market_charts(registry, data_source_ids)
        else:
            # Default: Chapter-specific charts
            charts = self._build_default_charts(chapter_id, registry, chapter_data, data_source_ids)
        
        # Determine if applicable
        not_applicable = len(charts) == 0
        
        return PlaneAVisualModel(
            charts=charts,
            data_source_ids=data_source_ids,
            not_applicable=not_applicable,
            not_applicable_reason="Geen visuele data beschikbaar" if not_applicable else None
        )
    
    def _generate_plane_b(
        self, 
        chapter_id: int, 
        ai_narrative: Optional[str],
        chapter_data: Dict[str, Any]
    ) -> PlaneBNarrativeModel:
        """Generate Plane B (Narrative Reasoning)."""
        # Use provided AI narrative or extract from chapter_data
        narrative_text = ai_narrative or ""
        
        # Try to extract from chapter_data if AI narrative not provided
        if not narrative_text:
            narrative = chapter_data.get("narrative", {})
            if isinstance(narrative, dict):
                narrative_text = narrative.get("text", "")
            elif isinstance(narrative, str):
                narrative_text = narrative
        
        # Calculate word count
        word_count = len(narrative_text.split()) if narrative_text else 0
        
        # =====================================================================
        # PRE-VALIDATION: Check requirements before Pydantic runs
        # This gives better error messages than Pydantic validation
        # =====================================================================
        min_words = self.MIN_WORDS_CHAPTER_0 if chapter_id == 0 else self.MIN_WORDS_CHAPTERS_1_12
        min_chars = 100  # PlaneBNarrativeModel requirement
        
        if not narrative_text or len(narrative_text) < min_chars:
            raise BackboneEnforcementError([
                BackboneViolation(
                    chapter_id=chapter_id,
                    plane="B",
                    violation_type=BackboneViolationType.PLANE_B_MISSING,
                    message=f"Narrative text is missing or too short ({len(narrative_text or '')} chars, minimum {min_chars})"
                )
            ])
        
        if word_count < min_words:
            raise BackboneEnforcementError([
                BackboneViolation(
                    chapter_id=chapter_id,
                    plane="B",
                    violation_type=BackboneViolationType.PLANE_B_INSUFFICIENT_WORDS,
                    message=f"Narrative has {word_count} words, minimum is {min_words}"
                )
            ])
        
        return PlaneBNarrativeModel(
            narrative_text=narrative_text,
            word_count=word_count,
            ai_generated=True,
            ai_provider=chapter_data.get("provenance", {}).get("provider"),
            ai_model=chapter_data.get("provenance", {}).get("model"),
            not_applicable=False  # Narrative is NEVER not applicable
        )
    
    def _generate_plane_c(self, chapter_id: int, chapter_data: Dict[str, Any]) -> PlaneCFactModel:
        """Generate Plane C (Factual Anchor)."""
        kpis = []
        missing_data = []
        
        # Get variables from chapter_data
        variables = chapter_data.get("variables", {})
        
        for key, var_data in variables.items():
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
        
        # Get registry values for this chapter if no variables
        if not kpis:
            kpis = self._get_kpis_from_registry(chapter_id)
        
        # Get missing data
        missing_data = chapter_data.get("missing_critical_data", [])
        
        return PlaneCFactModel(
            kpis=kpis,
            missing_data=missing_data,
            not_applicable=False  # Facts are NEVER not applicable
        )
    
    def _generate_plane_d(self, chapter_id: int, chapter_data: Dict[str, Any]) -> PlaneDPreferenceModel:
        """Generate Plane D (Human Preference)."""
        comparison = chapter_data.get("comparison", {})
        
        marcel_data = comparison.get("marcel", {})
        petra_data = comparison.get("petra", {})
        
        # Build persona scores
        marcel = PersonaScore(
            match_score=chapter_data.get("marcel_match_score"),
            mood=self._determine_mood(marcel_data),
            key_values=marcel_data.get("values", []) if isinstance(marcel_data, dict) else [],
            concerns=marcel_data.get("concerns", []) if isinstance(marcel_data, dict) else [],
            summary=marcel_data if isinstance(marcel_data, str) else marcel_data.get("summary") if isinstance(marcel_data, dict) else None
        )
        
        petra = PersonaScore(
            match_score=chapter_data.get("petra_match_score"),
            mood=self._determine_mood(petra_data),
            key_values=petra_data.get("values", []) if isinstance(petra_data, dict) else [],
            concerns=petra_data.get("concerns", []) if isinstance(petra_data, dict) else [],
            summary=petra_data if isinstance(petra_data, str) else petra_data.get("summary") if isinstance(petra_data, dict) else None
        )
        
        # Build comparisons
        comparisons = self._build_preference_comparisons(chapter_data)
        
        # Extract overlap and tension
        overlap_points = chapter_data.get("overlap_points", [])
        tension_points = chapter_data.get("tension_points", [])
        
        # Joint synthesis for chapter 0
        joint_synthesis = None
        if chapter_id == 0:
            joint_synthesis = chapter_data.get("joint_synthesis", 
                "Marcel en Petra benaderen deze woning vanuit verschillende perspectieven "
                "die elkaar aanvullen."
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
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _get_chapter_title(self, chapter_id: int, chapter_data: Dict[str, Any]) -> str:
        """Get chapter title."""
        titles = {
            0: "Executive Dashboard",
            1: "Kerngegevens",
            2: "Matchanalyse Marcel & Petra",
            3: "Bouwkundige Staat",
            4: "Energie & Duurzaamheid",
            5: "Indeling & Potentie",
            6: "Afwerking & Onderhoud",
            7: "Tuin & Buitenruimte",
            8: "Locatie & Bereikbaarheid",
            9: "Juridisch & Kadaster",
            10: "Financiële Analyse",
            11: "Marktpositie",
            12: "Conclusie & Advies"
        }
        return chapter_data.get("title", titles.get(chapter_id, f"Hoofdstuk {chapter_id}"))
    
    def _determine_mood(self, persona_data: Any) -> Optional[str]:
        """Determine mood from persona data."""
        if not persona_data:
            return "neutral"
        
        if isinstance(persona_data, str):
            text = persona_data.lower()
            if any(w in text for w in ["positief", "goed", "sterk", "uitstekend"]):
                return "positive"
            elif any(w in text for w in ["negatief", "slecht", "zwak", "probleem"]):
                return "negative"
            elif any(w in text for w in ["gemengd", "twijfel", "afweging"]):
                return "mixed"
        
        return "neutral"
    
    def _build_preference_comparisons(self, chapter_data: Dict[str, Any]) -> List[PreferenceComparison]:
        """Build preference comparisons from chapter data."""
        comparisons = []
        comparison_data = chapter_data.get("comparison", {})
        
        aspects = ["locatie", "indeling", "prijs", "toekomst", "sfeer"]
        
        for aspect in aspects:
            if aspect in comparison_data:
                marcel_view = comparison_data.get("marcel", {})
                petra_view = comparison_data.get("petra", {})
                
                if isinstance(marcel_view, dict):
                    marcel_view = marcel_view.get(aspect, "Geen specifieke mening")
                else:
                    marcel_view = str(marcel_view)[:100] if marcel_view else "Geen specifieke mening"
                    
                if isinstance(petra_view, dict):
                    petra_view = petra_view.get(aspect, "Geen specifieke mening")
                else:
                    petra_view = str(petra_view)[:100] if petra_view else "Geen specifieke mening"
                
                alignment = "aligned" if marcel_view == petra_view else "complementary"
                
                comparisons.append(PreferenceComparison(
                    aspect=aspect.title(),
                    marcel_view=str(marcel_view)[:100],
                    petra_view=str(petra_view)[:100],
                    alignment=alignment,
                    requires_discussion=False
                ))
        
        return comparisons[:5]
    
    def _get_kpis_from_registry(self, chapter_id: int) -> List[FactualKPI]:
        """Get KPIs from registry for a chapter."""
        kpis = []
        registry = self.ctx.registry
        
        # Core KPIs for most chapters
        core_keys = {
            0: ["asking_price_eur", "living_area_m2", "energy_label", "build_year"],
            1: ["asking_price_eur", "living_area_m2", "plot_area_m2", "rooms", "bedrooms"],
            10: ["asking_price_eur", "price_per_m2", "woz_value"],
            11: ["asking_price_eur", "price_per_m2"],
        }
        
        keys = core_keys.get(chapter_id, ["asking_price_eur", "living_area_m2"])
        
        for key in keys:
            value = self.ctx.get_registry_value(key)
            if value is not None:
                kpis.append(FactualKPI(
                    key=key,
                    label=key.replace("_", " ").title(),
                    value=value,
                    provenance="fact",
                    completeness=True
                ))
        
        return kpis
    
    def _build_summary_charts(self, registry: CanonicalRegistry, data_source_ids: List[str]) -> List[ChartConfig]:
        """Build summary charts for Chapter 0."""
        charts = []
        
        # Match score gauge
        match_score = self.ctx.get_registry_value("total_match_score")
        if match_score is not None:
            charts.append(ChartConfig(
                chart_type="gauge",
                title="Match Score",
                data=[VisualDataPoint(label="Match", value=float(match_score))],
                max_value=100
            ))
            data_source_ids.append("total_match_score")
        
        return charts
    
    def _build_match_charts(
        self, 
        registry: CanonicalRegistry, 
        chapter_data: Dict[str, Any],
        data_source_ids: List[str]
    ) -> List[ChartConfig]:
        """Build match charts for Chapter 2."""
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
            
            radar_data.append(VisualDataPoint(label=dim.title(), value=value))
        
        if radar_data:
            charts.append(ChartConfig(
                chart_type="radar",
                title="Woningprofiel",
                data=radar_data,
                max_value=100
            ))
        
        return charts
    
    def _build_market_charts(self, registry: CanonicalRegistry, data_source_ids: List[str]) -> List[ChartConfig]:
        """Build market charts for Chapter 11."""
        charts = []
        
        price = self.ctx.get_registry_value("asking_price_eur")
        if price is not None:
            charts.append(ChartConfig(
                chart_type="bar",
                title="Prijsvergelijking",
                data=[
                    VisualDataPoint(label="Vraagprijs", value=float(price) / 1000, unit="k"),
                ],
                show_legend=True
            ))
            data_source_ids.append("asking_price_eur")
        
        return charts
    
    def _build_default_charts(
        self,
        chapter_id: int,
        registry: CanonicalRegistry,
        chapter_data: Dict[str, Any],
        data_source_ids: List[str]
    ) -> List[ChartConfig]:
        """Build default charts for other chapters."""
        charts = []
        
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
                title=f"Data Hoofdstuk {chapter_id}",
                data=bar_data[:6]
            ))
        
        return charts


# =============================================================================
# PUBLIC API
# =============================================================================

def generate_four_plane_chapter(
    ctx: PipelineContext,
    chapter_id: int,
    ai_narrative: Optional[str] = None,
    chapter_data: Optional[Dict[str, Any]] = None
) -> ChapterPlaneComposition:
    """
    Generate a 4-plane chapter composition.
    
    This is the PUBLIC API for 4-plane chapter generation.
    
    Args:
        ctx: Pipeline context with locked registry
        chapter_id: Chapter number (0-12)
        ai_narrative: Optional AI-generated narrative
        chapter_data: Optional additional chapter data
    
    Returns:
        ChapterPlaneComposition with all 4 planes validated
    
    Raises:
        BackboneEnforcementError: If plane validation fails
        PipelineViolation: If registry not locked
    """
    backbone = FourPlaneBackbone(ctx)
    return backbone.generate_chapter(chapter_id, ai_narrative, chapter_data)


def convert_plane_composition_to_dict(composition: ChapterPlaneComposition) -> Dict[str, Any]:
    """
    Convert a ChapterPlaneComposition to a dict for API/frontend.
    
    Args:
        composition: The validated plane composition
    
    Returns:
        Dict suitable for JSON serialization and frontend rendering
    """
    return {
        "id": str(composition.chapter_id),
        "title": composition.chapter_title,
        "plane_structure": True,  # Marker for 4-plane structure
        
        # Plane A
        "plane_a": {
            "plane": composition.plane_a.plane,
            "charts": [
                {
                    "chart_type": c.chart_type,
                    "title": c.title,
                    "data": [{"label": d.label, "value": d.value, "unit": d.unit} for d in c.data],
                    "max_value": c.max_value,
                }
                for c in composition.plane_a.charts
            ],
            "trends": composition.plane_a.trends,
            "comparisons": composition.plane_a.comparisons,
            "data_source_ids": composition.plane_a.data_source_ids,
            "not_applicable": composition.plane_a.not_applicable,
            "not_applicable_reason": composition.plane_a.not_applicable_reason,
        },
        
        # Plane B
        "plane_b": {
            "plane": composition.plane_b.plane,
            "narrative_text": composition.plane_b.narrative_text,
            "word_count": composition.plane_b.word_count,
            "not_applicable": composition.plane_b.not_applicable,
            "ai_generated": composition.plane_b.ai_generated,
            "ai_provider": composition.plane_b.ai_provider,
            "ai_model": composition.plane_b.ai_model,
        },
        
        # Plane C
        "plane_c": {
            "plane": composition.plane_c.plane,
            "kpis": [
                {
                    "key": k.key,
                    "label": k.label,
                    "value": k.value,
                    "unit": k.unit,
                    "provenance": k.provenance,
                    "completeness": k.completeness,
                }
                for k in composition.plane_c.kpis
            ],
            "missing_data": composition.plane_c.missing_data,
            "uncertainties": composition.plane_c.uncertainties,
            "not_applicable": composition.plane_c.not_applicable,
        },
        
        # Plane D
        "plane_d": {
            "plane": composition.plane_d.plane,
            "marcel": {
                "match_score": composition.plane_d.marcel.match_score,
                "mood": composition.plane_d.marcel.mood,
                "key_values": composition.plane_d.marcel.key_values,
                "concerns": composition.plane_d.marcel.concerns,
                "summary": composition.plane_d.marcel.summary,
            },
            "petra": {
                "match_score": composition.plane_d.petra.match_score,
                "mood": composition.plane_d.petra.mood,
                "key_values": composition.plane_d.petra.key_values,
                "concerns": composition.plane_d.petra.concerns,
                "summary": composition.plane_d.petra.summary,
            },
            "comparisons": [
                {
                    "aspect": c.aspect,
                    "marcel_view": c.marcel_view,
                    "petra_view": c.petra_view,
                    "alignment": c.alignment,
                    "requires_discussion": c.requires_discussion,
                }
                for c in composition.plane_d.comparisons
            ],
            "overlap_points": composition.plane_d.overlap_points,
            "tension_points": composition.plane_d.tension_points,
            "joint_synthesis": composition.plane_d.joint_synthesis,
            "not_applicable": composition.plane_d.not_applicable,
        },
        
        # Legacy compatibility fields
        "narrative": {
            "text": composition.plane_b.narrative_text,
            "word_count": composition.plane_b.word_count,
        },
        "chapter_data": {
            "title": composition.chapter_title,
            "narrative": {
                "text": composition.plane_b.narrative_text,
                "word_count": composition.plane_b.word_count,
            },
        },
        "grid_layout": {
            "main": {"content": composition.plane_b.narrative_text},
        },
    }
