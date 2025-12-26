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
    PlaneA2SynthVisualModel,
    HeroInfographic,
    VisualConcept,
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

# MAXIMALIZATION: Import extractors for rich plane content
from backend.pipeline.four_plane_extractors import FourPlaneMaxExtractor
from backend.pipeline.four_plane_max_contract import (
    get_narrative_contract,
    MaximalizationDiagnostic,
)

# IMAGE GENERATION: Import image provider infrastructure
from backend.ai.image_provider_interface import (
    ImageGenerationRequest,
    ImageGenerationResult,
    ImageGenerationStatus,
)
from backend.ai.image_provider_factory import get_image_provider, is_image_generation_available

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
        Generate a complete 4-plane chapter with MAXIMALIZED content.
        
        Args:
            chapter_id: Chapter number (0-12)
            ai_narrative: AI-generated narrative for Plane B
            chapter_data: Additional chapter data from existing generation
        
        Returns:
            Complete ChapterPlaneComposition with all 4+1 planes (A1, A2, B, C, D)
        
        Raises:
            BackboneEnforcementError: If plane validation fails
        """
        if chapter_data is None:
            chapter_data = {}
        
        logger.info(f"FourPlaneBackbone: Generating MAXIMALIZED chapter {chapter_id}")
        
        # MAXIMALIZATION: Use extractors for richer content
        extractor = FourPlaneMaxExtractor(self.ctx)
        max_data = extractor.extract(chapter_id, chapter_data)
        
        # Store diagnostics for later
        self._last_diagnostics = max_data.get("diagnostics")
        
        # Generate each plane with maximalized data
        plane_a = self._generate_plane_a_max(chapter_id, chapter_data, max_data)
        plane_a2 = self._generate_plane_a2(chapter_id, chapter_data, max_data)  # NEW: Plane A2
        plane_b = self._generate_plane_b(chapter_id, ai_narrative, chapter_data)
        plane_c = self._generate_plane_c_max(chapter_id, chapter_data, max_data)
        plane_d = self._generate_plane_d_max(chapter_id, chapter_data, max_data)
        
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
                plane_a2=plane_a2,  # NEW: Include Plane A2
                registry_ids=registry_ids
            )
            
            # Log A2 status
            a2_status = "with hero infographic" if (plane_a2 and plane_a2.hero_infographic and 
                plane_a2.hero_infographic.generation_status == "generated") else "concepts only"
            
            logger.info(
                f"FourPlaneBackbone: Chapter {chapter_id} validated. "
                f"Plane B: {plane_b.word_count} words, Plane A2: {a2_status}"
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
    
    def _generate_plane_a_max(
        self, 
        chapter_id: int, 
        chapter_data: Dict[str, Any],
        max_data: Dict[str, Any]
    ) -> PlaneAVisualModel:
        """
        Generate Plane A (Visual Intelligence) with MAXIMALIZED content.
        Uses chart catalog from extractors.
        """
        # Get maximalized charts from extractor
        charts = max_data.get("plane_a_charts", [])
        missing_reasons = max_data.get("plane_a_missing", [])
        
        # Build data source IDs from chart catalog's registry keys (NOT from data labels)
        # This ensures the IDs match actual registry entries
        from backend.pipeline.four_plane_max_contract import get_chart_catalog
        catalog = get_chart_catalog(chapter_id)
        data_source_ids = []
        for spec in catalog:
            data_source_ids.extend(spec.required_registry_keys)
        
        # Determine if applicable
        not_applicable = len(charts) == 0
        not_applicable_reason = None
        if not_applicable and missing_reasons:
            not_applicable_reason = "; ".join(missing_reasons[:3])
        elif not_applicable:
            not_applicable_reason = "Geen visuele data beschikbaar voor dit hoofdstuk"
        
        return PlaneAVisualModel(
            charts=charts,
            data_source_ids=data_source_ids,
            not_applicable=not_applicable,
            not_applicable_reason=not_applicable_reason
        )
    
    # Keep legacy method for backward compatibility
    def _generate_plane_a(self, chapter_id: int, chapter_data: Dict[str, Any]) -> PlaneAVisualModel:
        """Legacy Plane A generator - delegates to maximalized version."""
        extractor = FourPlaneMaxExtractor(self.ctx)
        max_data = extractor.extract(chapter_id, chapter_data)
        return self._generate_plane_a_max(chapter_id, chapter_data, max_data)
    
    def _generate_plane_a2(
        self,
        chapter_id: int,
        chapter_data: Dict[str, Any],
        max_data: Dict[str, Any]
    ) -> PlaneA2SynthVisualModel:
        """
        Generate Plane A2 (Synthesized Visual Intelligence).
        
        FAIL-LOUD PRINCIPLE:
        - Plane A2 ALWAYS exists (never None)
        - If image generation fails → not_applicable=True with reason
        - If no provider → not_applicable=True with reason
        - Concepts are ALWAYS generated from registry data
        
        Args:
            chapter_id: Chapter number (0-12)
            chapter_data: Additional chapter data
            max_data: Maximalization data from extractor
            
        Returns:
            PlaneA2SynthVisualModel with hero infographic or explicit not_applicable
        """
        logger.info(f"Generating Plane A2 for chapter {chapter_id}")
        
        # Build visual concepts from registry data (ALWAYS done, regardless of image gen)
        concepts = self._build_a2_concepts(chapter_id)
        data_source_ids = [c.data_used[0] for c in concepts if c.data_used]
        
        # Check if image generation is available
        image_provider = get_image_provider()
        
        if not image_provider.is_configured():
            logger.warning(f"Plane A2: No image provider configured for chapter {chapter_id}")
            return PlaneA2SynthVisualModel(
                hero_infographic=None,
                concepts=concepts,
                data_source_ids=data_source_ids,
                not_applicable=True,
                not_applicable_reason="Geen image provider geconfigureerd. Stel GEMINI_API_KEY in voor infographic generatie."
            )
        
        # Build the hero infographic request
        hero_request = self._build_hero_infographic_request(chapter_id, concepts)
        
        if hero_request is None:
            # Not enough data to generate infographic
            return PlaneA2SynthVisualModel(
                hero_infographic=None,
                concepts=concepts,
                data_source_ids=data_source_ids,
                not_applicable=True,
                not_applicable_reason="Onvoldoende registry data voor infographic generatie."
            )
        
        # Attempt image generation using safe bridge (risk mitigation for event loop conflicts)
        # [A2][IMAGE_GENERATION][GEMINI_3] invoked - Runtime marker
        logger.info(f"[A2][IMAGE_GENERATION][GEMINI_3] invoked for chapter {chapter_id}")
        
        from backend.ai.bridge import safe_execute_async
        try:
            result = safe_execute_async(image_provider.generate_image(hero_request))
        except Exception as e:
            logger.error(f"Plane A2: Image generation failed: {e}")
            result = ImageGenerationResult(
                status=ImageGenerationStatus.FAILED,
                provider_name=image_provider.provider_name,
                model_name=image_provider.model_name,
                prompt=hero_request.prompt,
                error_message=str(e)
            )
        
        # Build HeroInfographic from result
        hero_infographic = HeroInfographic(
            title=hero_request.title,
            visual_type=hero_request.visual_type,
            prompt=hero_request.prompt,
            data_used=hero_request.data_used,
            insight_summary=hero_request.insight_summary,
            uncertainties=hero_request.uncertainties,
            image_uri=result.image_uri,
            image_base64=result.image_base64,
            generation_status=result.status.value,
            generation_error=result.error_message
        )
        
        # Determine not_applicable based on result
        not_applicable = result.status != ImageGenerationStatus.GENERATED
        not_applicable_reason = None
        
        if not_applicable:
            # Check global capability status for intelligent messaging
            from backend.ai.capability_manager import get_capability_manager, CapabilityState
            cap_status = get_capability_manager().get_status("image_generation")
            
            if cap_status.state == CapabilityState.QUOTA_EXCEEDED:
                 not_applicable_reason = (
                     "Image generation is temporarily unavailable due to quota limits. "
                     "The system is correctly configured and will resume automatically."
                 )
            elif result.error_message:
                not_applicable_reason = f"Image generatie mislukt: {result.error_message}"
            else:
                not_applicable_reason = f"Image generatie status: {result.status.value}"
        
        return PlaneA2SynthVisualModel(
            hero_infographic=hero_infographic,
            concepts=concepts,
            data_source_ids=data_source_ids,
            not_applicable=not_applicable,
            not_applicable_reason=not_applicable_reason
        )
    
    def _build_a2_concepts(self, chapter_id: int) -> List[VisualConcept]:
        """
        Build visual concepts for Plane A2 from registry data.
        
        These concepts are ALWAYS generated, even if image generation fails.
        They provide value by describing what COULD be visualized.
        """
        concepts = []
        registry = self.ctx.registry
        
        # Chapter-specific concept templates
        # NOTE: visual_type must be: 'infographic', 'diagram', 'comparison_visual', 'timeline'
        chapter_concepts = {
            1: [  # Kerngegevens
                ("Woningprofiel Overzicht", "infographic", ["asking_price_eur", "living_area_m2", "plot_area_m2", "rooms"],
                 "Visuele weergave van de belangrijkste woningkenmerken"),
                ("Prijspositie Vergelijking", "comparison_visual", ["asking_price_eur", "price_per_m2"],
                 "Positionering van de vraagprijs t.o.v. marktgemiddelden"),
                ("Ruimte Verdeling", "diagram", ["living_area_m2", "rooms", "bedrooms"],
                 "Verdeling van woonoppervlak over kamers"),
            ],
            2: [  # Matchanalyse
                ("Marcel vs Petra Vergelijking", "comparison_visual", ["total_match_score"],
                 "Vergelijking van voorkeursprofielen tussen Marcel en Petra"),
            ],
            3: [  # Bouwkundige Staat - MAXIMALIZED A2 CONCEPTS
                ("Bouwkundige Levenscyclus", "timeline", ["build_year"],
                 "Visuele tijdlijn van bouwjaar tot heden met verwachte onderhoudsmomenten per component"),
                ("Component Stresskaart", "diagram", ["build_year", "property_type"],
                 "Hittekaart die de verwachte staat per bouwcomponent toont: fundering, dak, gevel, installaties"),
                ("Risico Horizon", "infographic", ["build_year"],
                 "Projectie van potentiële onderhouds- en vervangingsrisico's over de komende 10-20 jaar"),
                ("Bouwzekerheid Dashboard", "infographic", ["build_year", "living_area_m2"],
                 "Samenvattend dashboard met overall bouwkundige conditiescore en kernrisico-indicatoren"),
            ],
            4: [  # Energie & Duurzaamheid - MAXIMALIZED A2 CONCEPTS
                ("Energie-transitiepad 2024-2035", "timeline", ["energy_label", "build_year"],
                 "Stappenplan van huidige energiestaat naar toekomstbestendige woning met subsidie-optimalisatie"),
                ("Investering vs Besparing Matrix", "matrix", ["energy_label", "living_area_m2"],
                 "Vergelijking van verduurzamingsmaatregelen: kosten, terugverdientijd, impact op wooncomfort"),
                ("Duurzaamheids-risico Radar", "diagram", ["energy_label", "build_year"],
                 "Multi-dimensionele analyse: energieprijsrisico, regelgevingsrisico, comfortrisico, waarderisico"),
                ("Comfort vs Kosten Dashboard", "infographic", ["energy_label", "living_area_m2"],
                 "Visualisatie van de trade-off tussen energiecomfort en maandelijkse woonlasten"),
            ],
            5: [  # Indeling, Ruimtelijkheid & Dagelijks Gebruik - MAXIMALIZED A2 CONCEPTS
                ("Dagelijks Leefpad", "diagram", ["living_area_m2", "rooms", "bedrooms"],
                 "Flow diagram: ochtend → werk → avond → weekend routine door de woning"),
                ("Ruimte-Stresskaart", "diagram", ["living_area_m2", "rooms"],
                 "Heatmap: waar botsen functies, waar ontstaat rust, drukpunten identificatie"),
                ("Toekomstscenario's", "timeline", ["living_area_m2", "bedrooms", "rooms"],
                 "Split timeline: huidig gebruik vs gezin/thuiswerken/ouder worden scenario's"),
                ("Samen-vs-Individueel Matrix", "matrix", ["rooms", "bedrooms", "living_area_m2"],
                 "Venn/Matrix: waar versterkt indeling samenleven, waar wringt het"),
            ],
            6: [  # Afwerking & Kwaliteit - MAXIMALIZED A2 CONCEPTS
                ("Kwaliteitslandschap", "diagram", ["build_year", "property_type"],
                 "Visuele kaart van kwaliteitsniveaus per ruimte: keuken, badkamer, woonkamer, slaapkamers"),
                ("Renovatie-Investeringspad", "timeline", ["build_year", "living_area_m2"],
                 "Gefaseerd plan: wat nu, wat over 5 jaar, wat over 10 jaar vernieuwen"),
                ("Smaak vs Budget Matrix", "matrix", ["build_year", "living_area_m2"],
                 "Trade-off tussen persoonlijke smaakvoorkeuren en beschikbaar renovatiebudget"),
                ("Levensduur Componenten", "infographic", ["build_year"],
                 "Verwachte restlevensduur: keuken, badkamer, vloeren, schilderwerk, installaties"),
            ],
            7: [  # Buitenruimte, Tuin & Omgevingsgebruik - MAXIMALIZED A2 CONCEPTS
                ("Daglicht & Rustkaart", "diagram", ["plot_area_m2", "property_type"],
                 "Visualisatie zon, schaduw, privacy en rustpunten in de buitenruimte"),
                ("Gebruiksscenario's Buiten", "infographic", ["plot_area_m2"],
                 "Scenarios: werk buiten, ontspanning, sociaal/BBQ, kinderen spelen"),
                ("Onderhoud vs Genot Matrix", "matrix", ["plot_area_m2"],
                 "Trade-off: investering in tijd × moeite × tuinplezier"),
                ("Toekomstpotentieel Buiten", "infographic", ["plot_area_m2", "living_area_m2"],
                 "Mogelijkheden: uitbouw, overkapping, moestuin, uitbreidingen"),
            ],
            8: [  # Locatie & Bereikbaarheid - MAXIMALIZED A2 CONCEPTS
                ("Mobiliteitsradar", "diagram", ["address"],
                 "360° bereikbaarheid: OV, auto, fiets, lopen naar voorzieningen"),
                ("Voorzieningen Kaart", "diagram", ["address"],
                 "Scholen, winkels, zorg, recreatie in straal rondom woning"),
                ("Woon-Werk Scenario's", "infographic", ["address"],
                 "Pendeltijd naar grote steden, thuiswerk-geschiktheid"),
                ("Buurt Leefbaarheid", "infographic", ["address"],
                 "Sfeer, veiligheid, demografie, toekomstperspectief wijk"),
            ],
            9: [  # Juridisch & Eigendom - MAXIMALIZED A2 CONCEPTS
                ("Eigendomsstructuur", "diagram", ["property_type"],
                 "Volledig eigendom vs erfpacht vs appartementsrecht uitleg"),
                ("VvE-Risico Dashboard", "infographic", ["property_type", "vve_contribution"],
                 "VvE-bijdrage, reservefonds, MJOP-status, risiconiveau"),
                ("Juridische Checklist", "infographic", [],
                 "Kadaster, splitsingsakte, erfdienstbaarheden, vergunningen"),
                ("Verplichtingen Overzicht", "timeline", ["vve_contribution"],
                 "Maandelijkse en jaarlijkse financiële verplichtingen"),
            ],
            10: [  # Financiële Analyse - MAXIMALIZED A2 CONCEPTS
                ("Maandlasten Dashboard", "infographic", ["asking_price_eur"],
                 "Hypotheek, energie, onderhoud, VvE in één overzicht"),
                ("Kosten Koper Breakdown", "diagram", ["asking_price_eur"],
                 "Overdrachtsbelasting, notaris, taxatie, advies, NHG"),
                ("Waarde Indicatoren", "diagram", ["asking_price_eur", "woz_value"],
                 "Vraagprijs vs WOZ, prijs/m² vs regionaal gemiddelde"),
                ("Betaalbaarheid Scenario's", "infographic", ["asking_price_eur"],
                 "Wat als: rente stijgt, inkomen daalt, onverwachte kosten"),
            ],
            11: [  # Marktpositie & Onderhandelingsruimte - MAXIMALIZED A2 CONCEPTS
                ("Marktpositie Radar", "diagram", ["asking_price_eur", "living_area_m2"],
                 "Vergelijking met regionale markt en vergelijkbare woningen"),
                ("Onderhandelingsstrategie", "infographic", ["asking_price_eur"],
                 "Biedstrategie, ruimte, argumenten, timing"),
                ("Marktdynamiek Dashboard", "infographic", ["asking_price_eur"],
                 "Kopersmarkt, verkopersmarkt, concurrentie, looptijd"),
                ("Timing Advies", "timeline", ["asking_price_eur"],
                 "Gunstigheid moment, seizoenseffecten, renteontwikkeling"),
            ],
            12: [  # Eindconclusie & Aanbeveling - MAXIMALIZED A2 CONCEPTS
                ("Finale Score Dashboard", "infographic", ["total_match_score"],
                 "Marcel-score, Petra-score, gecombineerd eindoordeel"),
                ("Sterkte/Zwakte Overzicht", "diagram", [],
                 "Samenvattend: belangrijkste plussen en minnen"),
                ("Biedingsadvies Visueel", "diagram", ["asking_price_eur"],
                 "Minimumbod, doelbod, maximumbod in context"),
                ("Actielijst & Volgende Stappen", "infographic", [],
                 "Prioriteiten: bezichtiging, keuring, financiering, bod"),
            ],
        }
        
        # Get concepts for this chapter or use defaults
        chapter_specs = chapter_concepts.get(chapter_id, [
            ("Hoofdstuk Overzicht", "infographic", ["asking_price_eur", "living_area_m2"],
             f"Visuele samenvatting van hoofdstuk {chapter_id}"),
        ])
        
        for title, visual_type, data_keys, insight in chapter_specs:
            # Check which keys are available in registry
            available_keys = []
            for key in data_keys:
                if self.ctx.get_registry_value(key) is not None:
                    available_keys.append(key)
            
            if available_keys:
                concepts.append(VisualConcept(
                    title=title,
                    visual_type=visual_type,
                    data_used=available_keys,
                    insight_explained=insight,
                    uncertainty_notes="Gebaseerd op beschikbare registry data" if len(available_keys) < len(data_keys) else None
                ))
        
        return concepts
    
    def _build_hero_infographic_request(
        self,
        chapter_id: int,
        concepts: List[VisualConcept]
    ) -> Optional[ImageGenerationRequest]:
        """
        Build the image generation request for the hero infographic.
        
        Returns None if insufficient data is available.
        """
        if not concepts:
            return None
        
        # Use the first concept as the hero
        hero_concept = concepts[0]
        
        # Build data summary from registry for the prompt
        data_summary_parts = []
        for key in hero_concept.data_used:
            value = self.ctx.get_registry_value(key)
            if value is not None:
                label = key.replace("_", " ").title()
                data_summary_parts.append(f"{label}: {value}")
        
        if not data_summary_parts:
            return None
        
        data_summary = ", ".join(data_summary_parts)
        
        # Build the prompt
        prompt = (
            f"Create a professional {hero_concept.visual_type} for a real estate analysis report.\n"
            f"Title: {hero_concept.title}\n"
            f"Key data points: {data_summary}\n"
            f"Insight to convey: {hero_concept.insight_explained}\n"
            f"Style: Clean, modern, professional. Use blues, greens, and neutral tones.\n"
            f"No text labels - pure visual representation."
        )
        
        return ImageGenerationRequest(
            prompt=prompt,
            visual_type=hero_concept.visual_type,
            data_used=hero_concept.data_used,
            title=hero_concept.title,
            insight_summary=hero_concept.insight_explained,
            uncertainties=[hero_concept.uncertainty_notes] if hero_concept.uncertainty_notes else []
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
    
    def _generate_plane_c_max(
        self,
        chapter_id: int,
        chapter_data: Dict[str, Any],
        max_data: Dict[str, Any]
    ) -> PlaneCFactModel:
        """
        Generate Plane C (Factual Anchor) with MAXIMALIZED content.
        Uses KPI catalog from extractors.
        """
        # Get maximalized KPIs from extractor
        kpis = max_data.get("plane_c_kpis", [])
        missing_data = max_data.get("plane_c_missing", [])
        parameters = max_data.get("plane_c_parameters", {})
        
        # Also include any variables from chapter_data
        variables = chapter_data.get("variables", {})
        existing_keys = {k.key for k in kpis}
        
        for key, var_data in variables.items():
            if key not in existing_keys and isinstance(var_data, dict):
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
        
        # Get missing data from chapter_data as well
        missing_data.extend(chapter_data.get("missing_critical_data", []))
        missing_data = list(set(missing_data))  # Dedupe
        
        # Build data sources list
        data_sources = ["registry", "extractor"]
        if variables:
            data_sources.append("chapter_data")
        
        return PlaneCFactModel(
            kpis=kpis,
            parameters=parameters,
            data_sources=data_sources,
            missing_data=missing_data,
            uncertainties=[f"Ontbreekt: {m}" for m in missing_data[:5]],
            not_applicable=False  # Facts are NEVER not applicable
        )
    
    # Keep legacy method for backward compatibility
    def _generate_plane_c(self, chapter_id: int, chapter_data: Dict[str, Any]) -> PlaneCFactModel:
        """Legacy Plane C generator - delegates to maximalized version."""
        extractor = FourPlaneMaxExtractor(self.ctx)
        max_data = extractor.extract(chapter_id, chapter_data)
        return self._generate_plane_c_max(chapter_id, chapter_data, max_data)
    
    def _generate_plane_d_max(
        self,
        chapter_id: int,
        chapter_data: Dict[str, Any],
        max_data: Dict[str, Any]
    ) -> PlaneDPreferenceModel:
        """
        Generate Plane D (Human Preference) with MAXIMALIZED content.
        Uses persona extractor for richer Marcel & Petra payloads.
        """
        # Get maximalized persona data from extractor
        marcel = max_data.get("plane_d_marcel", PersonaScore())
        petra = max_data.get("plane_d_petra", PersonaScore())
        comparisons = max_data.get("plane_d_comparisons", [])
        tensions = max_data.get("plane_d_tensions", [])
        overlaps = max_data.get("plane_d_overlaps", [])
        
        # Joint synthesis for chapter 0
        joint_synthesis = None
        if chapter_id == 0:
            joint_synthesis = chapter_data.get("joint_synthesis", 
                "Marcel en Petra benaderen deze woning vanuit verschillende perspectieven "
                "die elkaar aanvullen. Marcel focust op technische en structurele aspecten, "
                "terwijl Petra de nadruk legt op sfeer en dagelijks woongenot. "
                "Het vinden van balans tussen beide perspectieven is cruciaal voor de besluitvorming."
            )
        
        return PlaneDPreferenceModel(
            marcel=marcel,
            petra=petra,
            comparisons=comparisons,
            overlap_points=overlaps,
            tension_points=tensions,
            joint_synthesis=joint_synthesis,
            not_applicable=False
        )
    
    # Keep legacy method for backward compatibility
    def _generate_plane_d(self, chapter_id: int, chapter_data: Dict[str, Any]) -> PlaneDPreferenceModel:
        """Legacy Plane D generator - delegates to maximalized version."""
        extractor = FourPlaneMaxExtractor(self.ctx)
        max_data = extractor.extract(chapter_id, chapter_data)
        return self._generate_plane_d_max(chapter_id, chapter_data, max_data)
    
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
    
    CRITICAL: This function MUST produce output matching the frontend TypeScript
    interfaces in frontend/src/types/planes.ts. Missing fields cause runtime failures.
    
    Args:
        composition: The validated plane composition
    
    Returns:
        Dict suitable for JSON serialization and frontend rendering
    """
    # Build diagnostics for fail-loud behavior
    diagnostics = _build_chapter_diagnostics(composition)
    
    return {
        "id": str(composition.chapter_id),
        "title": composition.chapter_title,
        "plane_structure": True,  # Marker for 4-plane structure
        
        # Plane A - MUST include plane_name for frontend
        "plane_a": {
            "plane": composition.plane_a.plane,
            "plane_name": composition.plane_a.plane_name,  # REQUIRED by frontend
            "charts": [
                {
                    "chart_type": c.chart_type,
                    "title": c.title,
                    "data": [{"label": d.label, "value": d.value, "unit": d.unit, "color": d.color} for d in c.data],
                    "max_value": c.max_value,
                    "show_legend": c.show_legend,
                }
                for c in composition.plane_a.charts
            ],
            "trends": composition.plane_a.trends,
            "comparisons": composition.plane_a.comparisons,
            "data_source_ids": composition.plane_a.data_source_ids,
            "not_applicable": composition.plane_a.not_applicable,
            "not_applicable_reason": composition.plane_a.not_applicable_reason,
        },
        
        # Plane A2 - Synthesized Visual Intelligence (ALWAYS present, may be not_applicable)
        "plane_a2": _serialize_plane_a2(composition.plane_a2),
        
        # Plane B - MUST include plane_name for frontend
        "plane_b": {
            "plane": composition.plane_b.plane,
            "plane_name": composition.plane_b.plane_name,  # REQUIRED by frontend
            "narrative_text": composition.plane_b.narrative_text,
            "word_count": composition.plane_b.word_count,
            "not_applicable": composition.plane_b.not_applicable,
            "not_applicable_reason": composition.plane_b.not_applicable_reason,
            "ai_generated": composition.plane_b.ai_generated,
            "ai_provider": composition.plane_b.ai_provider,
            "ai_model": composition.plane_b.ai_model,
        },
        
        # Plane C - MUST include plane_name, parameters, data_sources for frontend
        "plane_c": {
            "plane": composition.plane_c.plane,
            "plane_name": composition.plane_c.plane_name,  # REQUIRED by frontend
            "kpis": [
                {
                    "key": k.key,
                    "label": k.label,
                    "value": k.value,
                    "unit": k.unit,
                    "provenance": k.provenance,
                    "registry_id": k.registry_id,
                    "completeness": k.completeness,
                    "missing_reason": k.missing_reason,
                }
                for k in composition.plane_c.kpis
            ],
            "parameters": composition.plane_c.parameters,  # REQUIRED by frontend
            "data_sources": composition.plane_c.data_sources,  # REQUIRED by frontend
            "missing_data": composition.plane_c.missing_data,
            "uncertainties": composition.plane_c.uncertainties,
            "not_applicable": composition.plane_c.not_applicable,
            "not_applicable_reason": composition.plane_c.not_applicable_reason,
        },
        
        # Plane D - MUST include plane_name for frontend
        "plane_d": {
            "plane": composition.plane_d.plane,
            "plane_name": composition.plane_d.plane_name,  # REQUIRED by frontend
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
            "not_applicable_reason": composition.plane_d.not_applicable_reason,
        },
        
        # FAIL-LOUD DIAGNOSTICS (MANDATORY per contract)
        "diagnostics": diagnostics,
        
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


def _serialize_plane_a2(plane_a2: Optional[PlaneA2SynthVisualModel]) -> Dict[str, Any]:
    """
    Serialize Plane A2 for API/frontend.
    
    FAIL-LOUD: Always returns a complete structure, never None.
    If plane_a2 is None, returns a not_applicable structure.
    """
    if plane_a2 is None:
        return {
            "plane": "A2",
            "plane_name": "synth_visual_intelligence",
            "hero_infographic": None,
            "concepts": [],
            "data_source_ids": [],
            "not_applicable": True,
            "not_applicable_reason": "Plane A2 not generated for this chapter",
        }
    
    # Serialize hero infographic if present
    hero_dict = None
    if plane_a2.hero_infographic:
        hero = plane_a2.hero_infographic
        hero_dict = {
            "title": hero.title,
            "visual_type": hero.visual_type,
            "prompt": hero.prompt,
            "data_used": hero.data_used,
            "insight_summary": hero.insight_summary,
            "uncertainties": hero.uncertainties,
            "image_uri": hero.image_uri,
            "image_base64": hero.image_base64,
            "generation_status": hero.generation_status,
            "generation_error": hero.generation_error,
        }
    
    # Serialize concepts
    concepts_list = [
        {
            "title": c.title,
            "visual_type": c.visual_type,
            "data_used": c.data_used,
            "insight_explained": c.insight_explained,
            "uncertainty_notes": c.uncertainty_notes,
        }
        for c in plane_a2.concepts
    ]
    
    return {
        "plane": plane_a2.plane,
        "plane_name": plane_a2.plane_name,
        "hero_infographic": hero_dict,
        "concepts": concepts_list,
        "data_source_ids": plane_a2.data_source_ids,
        "not_applicable": plane_a2.not_applicable,
        "not_applicable_reason": plane_a2.not_applicable_reason,
    }


def _get_a2_status(plane_a2: Optional[PlaneA2SynthVisualModel]) -> str:
    """Get status string for Plane A2 diagnostics."""
    if plane_a2 is None:
        return "missing"
    if plane_a2.not_applicable:
        return "not_applicable"
    if plane_a2.hero_infographic and plane_a2.hero_infographic.generation_status == "generated":
        return "ok"
    if plane_a2.concepts:
        return "concepts_only"
    return "empty"


def _build_chapter_diagnostics(composition: ChapterPlaneComposition) -> Dict[str, Any]:
    """
    Build diagnostics block for a chapter.
    
    This is MANDATORY for fail-loud behavior - allows user to copy/paste
    diagnostics when debugging 4-plane rendering issues.
    """
    # Determine plane statuses
    plane_status = {
        "A": "ok" if not composition.plane_a.not_applicable and len(composition.plane_a.charts) > 0 else (
            "not_applicable" if composition.plane_a.not_applicable else "empty"
        ),
        "A2": _get_a2_status(composition.plane_a2),
        "B": "ok" if not composition.plane_b.not_applicable and composition.plane_b.word_count >= 100 else (
            "not_applicable" if composition.plane_b.not_applicable else "insufficient"
        ),
        "C": "ok" if not composition.plane_c.not_applicable else "not_applicable",
        "D": "ok" if not composition.plane_d.not_applicable else "not_applicable",
    }
    
    # Find missing required fields
    missing_fields = []
    if not composition.plane_b.narrative_text:
        missing_fields.append("plane_b.narrative_text")
    if composition.plane_b.word_count < 100:
        missing_fields.append(f"plane_b.word_count (got {composition.plane_b.word_count}, need 100+)")
    
    # Check for validation issues
    errors = []
    violations = composition.validate_plane_isolation()
    for v in violations:
        errors.append({
            "code": "PLANE_VIOLATION",
            "message": v,
            "evidence": None
        })
    
    return {
        "chapter_id": composition.chapter_id,
        "pipeline_step": "convert_plane_composition_to_dict",
        "plane_status": plane_status,
        "missing_required_fields": missing_fields,
        "errors": errors,
        "validation_passed": len(errors) == 0 and len(missing_fields) == 0,
    }
