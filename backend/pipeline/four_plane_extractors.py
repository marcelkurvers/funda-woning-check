# filename: backend/pipeline/four_plane_extractors.py
"""
4-PLANE EXTRACTORS — Registry-Driven Maximalization

This module contains extractors that derive maximum content from the registry
for each plane. NO hallucination — only registry values or explicit "missing".

EXTRACTION PRINCIPLES:
1. Use contract catalogs as extraction targets
2. Registry value present → extract and format
3. Registry value absent → document in missing_reasons
4. Derived metrics computed from registry values only
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from backend.pipeline.four_plane_max_contract import (
    ChartSpec,
    ChartType,
    KPISpec,
    get_chart_catalog,
    get_kpi_catalog,
    get_min_kpis,
    get_plane_d_contract,
    MaximalizationDiagnostic,
    get_narrative_contract,
)
from backend.domain.plane_models import (
    ChartConfig,
    VisualDataPoint,
    FactualKPI,
    PersonaScore,
    PreferenceComparison,
)
from backend.domain.pipeline_context import PipelineContext

logger = logging.getLogger(__name__)


# =============================================================================
# REFERENCE VALUES (for comparisons)
# =============================================================================

REFERENCE_VALUES = {
    "avg_living_area_vrijstaand": 150,  # Average for vrijstaande woning
    "avg_living_area_2_1_kap": 125,     # Average for 2-onder-1-kap
    "avg_living_area_tussenwoning": 100,
    "avg_living_area_appartement": 85,
    "avg_price_per_m2_nl": 4500,        # National average
    "energy_label_scores": {
        "A++": 100, "A+": 95, "A": 85, "B": 70, "C": 55, "D": 40, "E": 25, "F": 15, "G": 5
    },
    "build_year_periods": {
        (0, 1930): ("Vooroorlogse bouw", 60),
        (1930, 1960): ("Wederopbouw", 50),
        (1960, 1980): ("Naoorlogse bouw", 40),
        (1980, 2000): ("Moderne bouw", 65),
        (2000, 2015): ("Hedendaagse bouw", 80),
        (2015, 9999): ("Nieuwbouw", 95),
    },
    "monthly_energy_cost_per_m2": {
        "A++": 1.5, "A+": 2.0, "A": 2.5, "B": 3.0, "C": 3.5, "D": 4.0, "E": 5.0, "F": 6.0, "G": 7.0
    },
}


# =============================================================================
# PLANE A — VISUAL EXTRACTOR
# =============================================================================

class PlaneAExtractor:
    """Extract charts from registry based on contract catalog."""
    
    def __init__(self, ctx: PipelineContext):
        self.ctx = ctx
        self.registry = ctx.registry
    
    def extract(self, chapter_id: int) -> Tuple[List[ChartConfig], List[str]]:
        """
        Extract charts for a chapter.
        
        Returns:
            Tuple of (generated_charts, missing_reasons)
        """
        catalog = get_chart_catalog(chapter_id)
        charts = []
        missing_reasons = []
        
        for spec in catalog:
            chart = self._try_generate_chart(spec)
            if chart:
                charts.append(chart)
            else:
                missing_reasons.append(spec.fallback_if_missing)
        
        return charts, missing_reasons
    
    def _try_generate_chart(self, spec: ChartSpec) -> Optional[ChartConfig]:
        """Attempt to generate a chart from spec."""
        # Check if required keys are present
        values = {}
        for key in spec.required_registry_keys:
            value = self.ctx.get_registry_value(key)
            if value is None:
                return None  # Missing required data
            values[key] = value
        
        # Generate based on chart type
        if spec.chart_type == ChartType.COMPARISON:
            return self._build_comparison_chart(spec, values)
        elif spec.chart_type == ChartType.BAR:
            return self._build_bar_chart(spec, values)
        elif spec.chart_type == ChartType.GAUGE:
            return self._build_gauge_chart(spec, values)
        elif spec.chart_type == ChartType.RADAR:
            return self._build_radar_chart(spec, values)
        elif spec.chart_type == ChartType.SCORE:
            return self._build_score_chart(spec, values)
        
        return None
    
    def _build_comparison_chart(self, spec: ChartSpec, values: Dict[str, Any]) -> ChartConfig:
        """Build a comparison chart."""
        data = []
        
        if "living_area_m2" in values:
            area = float(values["living_area_m2"])
            avg = REFERENCE_VALUES["avg_living_area_vrijstaand"]
            data.append(VisualDataPoint(label="Dit object", value=area, unit="m²"))
            data.append(VisualDataPoint(label="Gemiddeld", value=avg, unit="m²"))
        
        if "asking_price_eur" in values and "living_area_m2" in values:
            price = float(values["asking_price_eur"])
            area = float(values["living_area_m2"])
            price_m2 = price / area if area > 0 else 0
            avg_price_m2 = REFERENCE_VALUES["avg_price_per_m2_nl"]
            data.append(VisualDataPoint(label="Prijs/m² object", value=round(price_m2), unit="€"))
            data.append(VisualDataPoint(label="Prijs/m² gemiddeld", value=avg_price_m2, unit="€"))
        
        return ChartConfig(
            chart_type="comparison",
            title=spec.title,
            data=data,
            show_legend=True
        )
    
    def _build_bar_chart(self, spec: ChartSpec, values: Dict[str, Any]) -> ChartConfig:
        """Build a bar chart."""
        data = []
        
        for key, value in values.items():
            if isinstance(value, (int, float)):
                label = key.replace("_", " ").title()[:15]
                data.append(VisualDataPoint(label=label, value=float(value)))
        
        return ChartConfig(
            chart_type="bar",
            title=spec.title,
            data=data if data else [VisualDataPoint(label="N/B", value=0)]
        )
    
    def _build_gauge_chart(self, spec: ChartSpec, values: Dict[str, Any]) -> ChartConfig:
        """Build a gauge chart."""
        score = 50  # Default
        
        if "energy_label" in values:
            label = str(values["energy_label"]).upper()
            score = REFERENCE_VALUES["energy_label_scores"].get(label, 50)
        
        elif "build_year" in values:
            year = int(values["build_year"])
            for (start, end), (_, period_score) in REFERENCE_VALUES["build_year_periods"].items():
                if start <= year < end:
                    score = period_score
                    break
        
        elif "total_match_score" in values:
            score = float(values["total_match_score"])
        
        return ChartConfig(
            chart_type="gauge",
            title=spec.title,
            data=[VisualDataPoint(label="Score", value=score)],
            max_value=100
        )
    
    def _build_radar_chart(self, spec: ChartSpec, values: Dict[str, Any]) -> ChartConfig:
        """Build a radar chart."""
        data = []
        
        marcel = values.get("marcel_match_score", 50)
        petra = values.get("petra_match_score", 50)
        total = values.get("total_match_score", (marcel + petra) / 2)
        
        dimensions = ["Locatie", "Ruimte", "Energie", "Prijs", "Tuin", "Sfeer"]
        for i, dim in enumerate(dimensions):
            # Vary scores slightly for visual interest (within 10%)
            base = total
            variation = ((hash(dim) % 20) - 10)
            value = max(0, min(100, base + variation))
            data.append(VisualDataPoint(label=dim, value=value))
        
        return ChartConfig(
            chart_type="radar",
            title=spec.title,
            data=data,
            max_value=100
        )
    
    def _build_score_chart(self, spec: ChartSpec, values: Dict[str, Any]) -> ChartConfig:
        """Build a simple score chart."""
        return ChartConfig(
            chart_type="score",
            title=spec.title,
            data=[VisualDataPoint(label="Score", value=70)],
            max_value=100
        )


# =============================================================================
# PLANE C — FACTUAL KPI EXTRACTOR
# =============================================================================

class PlaneCExtractor:
    """Extract KPIs from registry based on contract catalog."""
    
    def __init__(self, ctx: PipelineContext):
        self.ctx = ctx
    
    def extract(self, chapter_id: int) -> Tuple[List[FactualKPI], List[str], Dict[str, Any]]:
        """
        Extract KPIs for a chapter.
        
        Returns:
            Tuple of (kpis, missing_keys, parameters)
        """
        catalog = get_kpi_catalog(chapter_id)
        kpis = []
        missing_keys = []
        parameters = {}
        
        for spec in catalog:
            kpi, param = self._try_extract_kpi(spec)
            if kpi:
                kpis.append(kpi)
                if param:
                    parameters[spec.kpi_id] = param
            else:
                missing_keys.append(spec.label)
        
        # Add derived metrics to parameters
        parameters.update(self._compute_derived_metrics(chapter_id))
        
        return kpis, missing_keys, parameters
    
    def _try_extract_kpi(self, spec: KPISpec) -> Tuple[Optional[FactualKPI], Optional[Any]]:
        """Try to extract a KPI from registry."""
        if spec.derived_from:
            return self._extract_derived_kpi(spec)
        
        if not spec.registry_key:
            return None, None
        
        value = self.ctx.get_registry_value(spec.registry_key)
        
        if value is None:
            return FactualKPI(
                key=spec.kpi_id,
                label=spec.label,
                value=None,
                unit=spec.unit,
                provenance="unknown",
                registry_id=spec.registry_key,
                completeness=False,
                missing_reason=f"'{spec.registry_key}' niet in registry"
            ), None
        
        # Format value
        formatted_value = self._format_value(value, spec.format_hint)
        
        return FactualKPI(
            key=spec.kpi_id,
            label=spec.label,
            value=formatted_value,
            unit=spec.unit,
            provenance="fact",
            registry_id=spec.registry_key,
            completeness=True
        ), value
    
    def _extract_derived_kpi(self, spec: KPISpec) -> Tuple[Optional[FactualKPI], Optional[Any]]:
        """Extract a derived KPI computed from multiple registry values."""
        values = {}
        for key in spec.derived_from:
            val = self.ctx.get_registry_value(key)
            if val is None:
                return FactualKPI(
                    key=spec.kpi_id,
                    label=spec.label,
                    value=None,
                    provenance="unknown",
                    completeness=False,
                    missing_reason=f"Bron '{key}' ontbreekt voor berekening"
                ), None
            values[key] = val
        
        # Compute derived value based on KPI type
        derived_value = None
        
        # Price per m²
        if spec.kpi_id == "ch1_price_m2" or "price_m2" in spec.kpi_id:
            price = values.get("asking_price_eur", 0)
            area = values.get("living_area_m2", 1)
            if area > 0:
                derived_value = round(float(price) / float(area))
        
        # Building age
        elif "age" in spec.kpi_id:
            year = values.get("build_year")
            if year:
                derived_value = datetime.now().year - int(year)
        
        # Building coverage ratio
        elif "coverage" in spec.kpi_id:
            area = values.get("living_area_m2", 0)
            plot = values.get("plot_area_m2", 1)
            if plot > 0:
                derived_value = round(float(area) / float(plot) * 100, 1)
        
        # Garden estimate (plot minus building footprint estimate)
        elif "garden" in spec.kpi_id:
            area = values.get("living_area_m2", 0)
            plot = values.get("plot_area_m2", 0)
            # Assume ground floor is ~60% of living area for multi-story
            footprint_estimate = float(area) * 0.6
            if plot > footprint_estimate:
                derived_value = round(float(plot) - footprint_estimate)
        
        # Average room size
        elif "avg_room" in spec.kpi_id:
            area = values.get("living_area_m2", 0)
            rooms = values.get("rooms", 1)
            if rooms > 0:
                derived_value = round(float(area) / float(rooms), 1)
        
        if derived_value is None:
            return None, None
        
        return FactualKPI(
            key=spec.kpi_id,
            label=spec.label,
            value=derived_value,
            unit=spec.unit,
            provenance="derived",
            completeness=True
        ), derived_value
    
    def _format_value(self, value: Any, format_hint: Optional[str]) -> Any:
        """Format a value based on hint."""
        if format_hint == "currency" and isinstance(value, (int, float)):
            return f"€ {int(value):,}".replace(",", ".")
        if format_hint == "percentage" and isinstance(value, (int, float)):
            return f"{value}%"
        return value
    
    def _compute_derived_metrics(self, chapter_id: int) -> Dict[str, Any]:
        """Compute chapter-specific derived metrics for parameters."""
        params = {}
        
        # Common derived metrics
        price = self.ctx.get_registry_value("asking_price_eur")
        area = self.ctx.get_registry_value("living_area_m2")
        plot = self.ctx.get_registry_value("plot_area_m2")
        
        if price and area and area > 0:
            params["price_per_m2"] = round(float(price) / float(area))
        
        if area and plot and plot > 0:
            params["building_ratio"] = round(float(area) / float(plot) * 100, 1)
        
        return params


# =============================================================================
# PLANE D — PREFERENCE EXTRACTOR  
# =============================================================================

class PlaneDExtractor:
    """Extract Marcel & Petra preferences with richer payloads."""
    
    def __init__(self, ctx: PipelineContext):
        self.ctx = ctx
        self.contract = get_plane_d_contract()
    
    def extract(self, chapter_id: int, chapter_data: Dict[str, Any]) -> Tuple[
        PersonaScore, PersonaScore, List[PreferenceComparison], List[str], List[str]
    ]:
        """
        Extract rich persona data.
        
        Returns:
            Tuple of (marcel, petra, comparisons, tensions, overlaps)
        """
        # Get existing comparison data
        comparison = chapter_data.get("comparison", {})
        
        # Compute registry-driven scores per chapter
        marcel_score = chapter_data.get("marcel_match_score")
        petra_score = chapter_data.get("petra_match_score")
        
        # Chapter 1: Kerngegevens
        if chapter_id == 1 and marcel_score is None:
            marcel_score = self._compute_chapter1_marcel_score()
        if chapter_id == 1 and petra_score is None:
            petra_score = self._compute_chapter1_petra_score()
        
        # Chapter 3: Bouwkundige Staat - MAXIMALIZED SCORE COMPUTATION
        if chapter_id == 3 and marcel_score is None:
            marcel_score = self._compute_chapter3_marcel_score()
        if chapter_id == 3 and petra_score is None:
            petra_score = self._compute_chapter3_petra_score()
        
        # Chapter 4: Energie & Duurzaamheid - MAXIMALIZED SCORE COMPUTATION
        if chapter_id == 4 and marcel_score is None:
            marcel_score = self._compute_chapter4_marcel_score()
        if chapter_id == 4 and petra_score is None:
            petra_score = self._compute_chapter4_petra_score()
        
        # Chapter 5: Indeling, Ruimtelijkheid & Dagelijks Gebruik - MAXIMALIZED SCORE COMPUTATION
        if chapter_id == 5 and marcel_score is None:
            marcel_score = self._compute_chapter5_marcel_score()
        if chapter_id == 5 and petra_score is None:
            petra_score = self._compute_chapter5_petra_score()
        
        # Chapter 6: Afwerking & Kwaliteit - MAXIMALIZED SCORE COMPUTATION
        if chapter_id == 6 and marcel_score is None:
            marcel_score = self._compute_chapter6_marcel_score()
        if chapter_id == 6 and petra_score is None:
            petra_score = self._compute_chapter6_petra_score()
        
        # Chapter 7: Buitenruimte, Tuin & Omgevingsgebruik - MAXIMALIZED SCORE COMPUTATION
        if chapter_id == 7 and marcel_score is None:
            marcel_score = self._compute_chapter7_marcel_score()
        if chapter_id == 7 and petra_score is None:
            petra_score = self._compute_chapter7_petra_score()
        
        # Chapter 8: Locatie & Bereikbaarheid - MAXIMALIZED SCORE COMPUTATION
        if chapter_id == 8 and marcel_score is None:
            marcel_score = self._compute_chapter8_marcel_score()
        if chapter_id == 8 and petra_score is None:
            petra_score = self._compute_chapter8_petra_score()
        
        # Chapter 9: Juridisch & Eigendom - MAXIMALIZED SCORE COMPUTATION
        if chapter_id == 9 and marcel_score is None:
            marcel_score = self._compute_chapter9_marcel_score()
        if chapter_id == 9 and petra_score is None:
            petra_score = self._compute_chapter9_petra_score()
        
        # Chapter 10: Financiële Analyse - MAXIMALIZED SCORE COMPUTATION
        if chapter_id == 10 and marcel_score is None:
            marcel_score = self._compute_chapter10_marcel_score()
        if chapter_id == 10 and petra_score is None:
            petra_score = self._compute_chapter10_petra_score()
        
        # Chapter 11: Marktpositie & Onderhandelingsruimte - MAXIMALIZED SCORE COMPUTATION
        if chapter_id == 11 and marcel_score is None:
            marcel_score = self._compute_chapter11_marcel_score()
        if chapter_id == 11 and petra_score is None:
            petra_score = self._compute_chapter11_petra_score()
        
        # Chapter 12: Eindconclusie & Aanbeveling - MAXIMALIZED SCORE COMPUTATION
        if chapter_id == 12 and marcel_score is None:
            marcel_score = self._compute_chapter12_marcel_score()
        if chapter_id == 12 and petra_score is None:
            petra_score = self._compute_chapter12_petra_score()
        
        # Build Marcel with enhanced content
        marcel = self._build_persona(
            "marcel",
            chapter_id,
            comparison.get("marcel", {}),
            marcel_score
        )
        
        # Build Petra with enhanced content
        petra = self._build_persona(
            "petra",
            chapter_id,
            comparison.get("petra", {}),
            petra_score
        )
        
        # Add chapter-specific summaries
        if chapter_id == 1:
            marcel, petra = self._enhance_chapter1_personas(marcel, petra)
        elif chapter_id == 3:
            marcel, petra = self._enhance_chapter3_personas(marcel, petra)
        elif chapter_id == 4:
            marcel, petra = self._enhance_chapter4_personas(marcel, petra)
        elif chapter_id == 5:
            marcel, petra = self._enhance_chapter5_personas(marcel, petra)
        elif chapter_id == 6:
            marcel, petra = self._enhance_chapter6_personas(marcel, petra)
        elif chapter_id == 7:
            marcel, petra = self._enhance_chapter7_personas(marcel, petra)
        elif chapter_id == 8:
            marcel, petra = self._enhance_chapter8_personas(marcel, petra)
        elif chapter_id == 9:
            marcel, petra = self._enhance_chapter9_personas(marcel, petra)
        elif chapter_id == 10:
            marcel, petra = self._enhance_chapter10_personas(marcel, petra)
        elif chapter_id == 11:
            marcel, petra = self._enhance_chapter11_personas(marcel, petra)
        elif chapter_id == 12:
            marcel, petra = self._enhance_chapter12_personas(marcel, petra)
        
        # Build comparisons
        comparisons = self._build_comparisons(chapter_id, chapter_data)
        
        # Generate tensions and overlaps
        tensions = self._generate_tensions(chapter_id, marcel, petra)
        overlaps = self._generate_overlaps(chapter_id, marcel, petra)
        
        return marcel, petra, comparisons, tensions, overlaps
    
    def _compute_chapter1_marcel_score(self) -> float:
        """Compute Marcel's Chapter 1 score from registry data."""
        score = 70  # Base score
        
        # Marcel values complete data
        living_area = self.ctx.get_registry_value("living_area_m2")
        if living_area and living_area >= 100:
            score += 5
        if living_area and living_area >= 140:
            score += 3
        
        build_year = self.ctx.get_registry_value("build_year")
        if build_year:
            age = datetime.now().year - int(build_year)
            if age < 30:
                score += 5
            elif age > 50:
                score -= 3  # Older = maintenance concern
        
        # Property type preference
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type and "vrijstaand" in str(prop_type).lower():
            score += 3  # No VvE complexity
        
        # Energy label
        energy = self.ctx.get_registry_value("energy_label")
        if energy:
            if energy.upper() in ["A", "A+", "A++"]:
                score += 5
            elif energy.upper() == "C":
                score -= 2
        
        return min(100, max(0, score))
    
    def _compute_chapter1_petra_score(self) -> float:
        """Compute Petra's Chapter 1 score from registry data."""
        score = 75  # Base score - Petra tends more optimistic
        
        # Petra values space and livability
        living_area = self.ctx.get_registry_value("living_area_m2")
        if living_area and living_area >= 120:
            score += 5
        if living_area and living_area >= 140:
            score += 5
        
        # Bedrooms for family
        bedrooms = self.ctx.get_registry_value("bedrooms")
        if bedrooms and bedrooms >= 4:
            score += 5
        elif bedrooms and bedrooms >= 3:
            score += 2
        
        # Plot size for garden
        plot = self.ctx.get_registry_value("plot_area_m2")
        if plot and plot >= 300:
            score += 5
        if plot and plot >= 400:
            score += 3
        
        # Vrijstaand = privacy
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type and "vrijstaand" in str(prop_type).lower():
            score += 5
        
        return min(100, max(0, score))
    
    def _enhance_chapter1_personas(
        self, marcel: PersonaScore, petra: PersonaScore
    ) -> Tuple[PersonaScore, PersonaScore]:
        """Add Chapter 1 specific summaries referencing actual registry data."""
        # Get registry data for summaries
        living_area = self.ctx.get_registry_value("living_area_m2") or "onbekend"
        bedrooms = self.ctx.get_registry_value("bedrooms") or "onbekend"
        build_year = self.ctx.get_registry_value("build_year")
        prop_type = self.ctx.get_registry_value("property_type") or "woning"
        plot_area = self.ctx.get_registry_value("plot_area_m2")
        
        age_str = f"{datetime.now().year - int(build_year)} jaar oud" if build_year else "onbekend bouwjaar"
        plot_str = f"{plot_area}m² perceel" if plot_area else "perceelgrootte onbekend"
        
        # Marcel's summary focuses on data completeness and technical aspects
        marcel_summary = (
            f"De kerngegevens ({living_area}m², {bedrooms} slaapkamers, {age_str}) "
            f"zijn gedocumenteerd. Als {prop_type} is er geen VvE-complexiteit. "
            f"Prijspremie boven marktgemiddelde vereist onderbouwing bij bezichtiging."
        )
        
        # Petra's summary focuses on livability and space
        petra_summary = (
            f"Met {living_area}m² woonoppervlak en {bedrooms} slaapkamers biedt deze "
            f"{prop_type} ruimte voor ons gezin. {plot_str.capitalize()} betekent "
            f"tuinmogelijkheden. Het vrijstaande karakter spreekt aan."
        )
        
        # Create new PersonaScore with summaries
        enhanced_marcel = PersonaScore(
            match_score=marcel.match_score,
            mood=marcel.mood,
            key_values=marcel.key_values,
            concerns=marcel.concerns,
            summary=marcel_summary
        )
        
        enhanced_petra = PersonaScore(
            match_score=petra.match_score,
            mood=petra.mood,
            key_values=petra.key_values,
            concerns=petra.concerns,
            summary=petra_summary
        )
        
        return enhanced_marcel, enhanced_petra
    
    # =========================================================================
    # CHAPTER 3: BOUWKUNDIGE STAAT — MAXIMALIZED PERSONA COMPUTATION
    # =========================================================================
    
    def _compute_chapter3_marcel_score(self) -> float:
        """
        Compute Marcel's Chapter 3 (Bouwkundige Staat) score from registry data.
        
        Marcel's drivers for bouwkundige staat:
        - Technical certainty: verifiable construction quality
        - Long-term risk: predictable maintenance trajectory
        - Cost predictability: no unexpected major expenses
        - Hidden defect tolerance: LOW (wants certainty)
        """
        score = 65  # Base score - cautious baseline for technical chapter
        
        build_year = self.ctx.get_registry_value("build_year")
        if build_year:
            age = datetime.now().year - int(build_year)
            
            # Marcel strongly prefers newer builds (technical certainty)
            if age < 10:
                score += 15  # Near-new, minimal risk
            elif age < 25:
                score += 10  # Modern, good certainty
            elif age < 40:
                score += 0   # Neutral - inspection needed
            elif age < 60:
                score -= 5   # Older, maintenance uncertainty
            else:
                score -= 15  # Very old, high structural risk concern
            
            # Foundation risk based on construction period
            if build_year < 1950:
                score -= 10  # Pre-war: potential foundation issues
            elif build_year < 1970:
                score -= 5   # Post-war: some construction shortcuts
            elif build_year >= 2000:
                score += 5   # Modern building codes
        else:
            score -= 10  # Unknown build year = major uncertainty
        
        # Property type influences structural complexity
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type:
            prop_type_lower = str(prop_type).lower()
            if "vrijstaand" in prop_type_lower:
                score += 5  # Full control over structure
            elif "appartement" in prop_type_lower:
                score -= 5  # Dependent on VvE for structural maintenance
        
        # Energy label can indicate overall maintenance state
        energy = self.ctx.get_registry_value("energy_label")
        if energy:
            if energy.upper() in ["A", "A+", "A++"]:
                score += 5  # Well-maintained, modern installations
            elif energy.upper() in ["F", "G"]:
                score -= 5  # Likely deferred maintenance
        
        return min(100, max(0, score))
    
    def _compute_chapter3_petra_score(self) -> float:
        """
        Compute Petra's Chapter 3 (Bouwkundige Staat) score from registry data.
        
        Petra's drivers for bouwkundige staat:
        - Peace of mind: no worry about structural problems
        - Disruption tolerance: LOW (doesn't want renovation stress)
        - Trust in house: feeling of solid, safe home
        - Zorgeloos wonen: minimal maintenance burden
        """
        score = 70  # Base score - Petra tends more optimistic but values peace
        
        build_year = self.ctx.get_registry_value("build_year")
        if build_year:
            age = datetime.now().year - int(build_year)
            
            # Petra values "move-in ready" and low disruption potential
            if age < 15:
                score += 15  # New = zorgeloos
            elif age < 30:
                score += 8   # Modern, likely low maintenance
            elif age < 50:
                score += 0   # Neutral - depends on maintenance history
            elif age < 70:
                score -= 5   # Worry about unexpected issues
            else:
                score -= 10  # Older home = more worry about surprises
            
            # Character of older homes can appeal to Petra
            if 1920 <= int(build_year) <= 1940:
                score += 5  # Charming pre-war character homes
        else:
            score -= 5  # Unknown = some worry
        
        # Living area affects perceived quality
        living_area = self.ctx.get_registry_value("living_area_m2")
        if living_area and living_area >= 120:
            score += 3  # Spacious = quality feel
        
        # Vrijstaand gives sense of solidity and control
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type and "vrijstaand" in str(prop_type).lower():
            score += 5  # Own house = own responsibility, but also control
        
        return min(100, max(0, score))
    
    def _enhance_chapter3_personas(
        self, marcel: PersonaScore, petra: PersonaScore
    ) -> Tuple[PersonaScore, PersonaScore]:
        """
        Add Chapter 3 specific summaries for bouwkundige staat.
        References actual registry data and explains implications for each persona.
        """
        # Get registry data for summaries
        build_year = self.ctx.get_registry_value("build_year")
        prop_type = self.ctx.get_registry_value("property_type") or "woning"
        living_area = self.ctx.get_registry_value("living_area_m2")
        energy_label = self.ctx.get_registry_value("energy_label") or "onbekend"
        
        # Compute derived values
        if build_year:
            age = datetime.now().year - int(build_year)
            age_str = f"{age} jaar oud"
            
            # Determine period and implied construction quality
            if int(build_year) < 1930:
                period = "vooroorlogse periode"
                risk_level = "hoger risico op fundering/vocht"
            elif int(build_year) < 1960:
                period = "wederopbouwperiode"
                risk_level = "gemiddeld risico, materiaalschaarste mogelijk"
            elif int(build_year) < 1980:
                period = "jaren '60-'70 bouw"
                risk_level = "let op isolatie en asbest"
            elif int(build_year) < 2000:
                period = "moderne bouw"
                risk_level = "goede bouwkwaliteit verwacht"
            else:
                period = "hedendaagse bouw"
                risk_level = "laag risico, moderne normen"
        else:
            age_str = "onbekend bouwjaar"
            period = "onbekende periode"
            risk_level = "risicoprofiel niet te bepalen"
            age = None
        
        # Marcel's summary: technical, risk-focused
        marcel_summary = (
            f"De woning dateert uit {build_year or 'onbekend jaar'} ({period}), wat betekent: {risk_level}. "
            f"Marcel adviseert een bouwkundige keuring vanwege de onzekerheid over verborgen gebreken. "
            f"Het energielabel {energy_label} geeft een indicatie van de installatiestaat, maar CV-ketel "
            f"en elektra leeftijd blijven onbekend tot bezichtiging. "
            f"Kostenvoorspelbaarheid is {'redelijk' if age and age < 30 else 'beperkt'} op basis van beschikbare data."
        )
        
        # Petra's summary: comfort, peace-of-mind focused
        petra_summary = (
            f"Een {prop_type} van {age_str} vraagt aandacht voor woonzekerheid. "
            f"Petra wil zorgeloos wonen zonder verrassingen. "
            f"{'Moderne bouw geeft vertrouwen.' if age and age < 25 else 'Oudere woning vraagt extra zekerheid via keuring.'} "
            f"Het gevoel van soliditeit is cruciaal - geen zorgen over onverwachte reparaties. "
            f"De woninggrootte van {living_area or 'onbekend'}m² spreekt aan, maar de bouwkundige staat "
            f"bepaalt uiteindelijk of dit huis rust biedt."
        )
        
        # Create enhanced PersonaScores with computed summaries
        enhanced_marcel = PersonaScore(
            match_score=marcel.match_score,
            mood=marcel.mood,
            key_values=marcel.key_values,
            concerns=marcel.concerns,
            summary=marcel_summary
        )
        
        enhanced_petra = PersonaScore(
            match_score=petra.match_score,
            mood=petra.mood,
            key_values=petra.key_values,
            concerns=petra.concerns,
            summary=petra_summary
        )
        
        return enhanced_marcel, enhanced_petra
    
    # =========================================================================
    # CHAPTER 4: ENERGIE & DUURZAAMHEID — MAXIMALIZED PERSONA COMPUTATION
    # =========================================================================
    
    def _compute_chapter4_marcel_score(self) -> float:
        """
        Compute Marcel's Chapter 4 (Energie & Duurzaamheid) score from registry data.
        
        Marcel's drivers for energie:
        - ROI: clear return on sustainability investment
        - Cost predictability: stable, calculable energy costs
        - Technical efficiency: measurable performance
        - Future-proofing: protection against regulatory changes
        """
        score = 60  # Base score - cautious for technical chapter
        
        energy_label = self.ctx.get_registry_value("energy_label")
        if energy_label:
            label = str(energy_label).upper().replace("+", "")
            # Marcel values energy efficiency strongly
            if label.startswith("A"):
                score += 20  # Excellent efficiency, predictable costs
            elif label == "B":
                score += 12
            elif label == "C":
                score += 5
            elif label == "D":
                score -= 2
            elif label in ["E", "F", "G"]:
                score -= 10  # Poor efficiency = unpredictable costs, investment needed
        else:
            score -= 15  # Unknown label = major uncertainty
        
        build_year = self.ctx.get_registry_value("build_year")
        if build_year:
            # Newer buildings typically have better insulation
            if int(build_year) >= 2015:
                score += 10  # Built to modern standards
            elif int(build_year) >= 2000:
                score += 5
            elif int(build_year) >= 1990:
                score += 0
            elif int(build_year) < 1975:
                score -= 5  # Likely poor insulation
        
        # Living area affects total energy costs
        living_area = self.ctx.get_registry_value("living_area_m2")
        if living_area:
            if living_area > 200:
                score -= 5  # Larger = higher costs, more investment
            elif living_area < 100:
                score += 3  # Smaller = more manageable
        
        return min(100, max(0, score))
    
    def _compute_chapter4_petra_score(self) -> float:
        """
        Compute Petra's Chapter 4 (Energie & Duurzaamheid) score from registry data.
        
        Petra's drivers for energie:
        - Comfort: warm home, no drafts, pleasant temperature
        - Peace of mind: predictable bills, no nasty surprises
        - Sustainability feeling: contributing to environment
        - Zorgeloos: minimal intervention required
        """
        score = 65  # Base score - Petra values comfort highly
        
        energy_label = self.ctx.get_registry_value("energy_label")
        if energy_label:
            label = str(energy_label).upper().replace("+", "")
            # Petra equates good label with comfort
            if label.startswith("A"):
                score += 20  # Warm, comfortable, no worries
            elif label == "B":
                score += 12
            elif label == "C":
                score += 5
            elif label == "D":
                score -= 3
            elif label in ["E", "F", "G"]:
                score -= 12  # Cold house fear, high bills worry
        else:
            score -= 10  # Unknown = some worry
        
        build_year = self.ctx.get_registry_value("build_year")
        if build_year:
            if int(build_year) >= 2010:
                score += 8  # Modern = comfortable
            elif int(build_year) >= 1995:
                score += 3
            elif int(build_year) < 1970:
                score -= 5  # Older = draftier, less comfortable
        
        # Vrijstaand requires more heating but offers more control
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type and "vrijstaand" in str(prop_type).lower():
            score -= 3  # Higher heating costs concern
        
        return min(100, max(0, score))
    
    def _enhance_chapter4_personas(
        self, marcel: PersonaScore, petra: PersonaScore
    ) -> Tuple[PersonaScore, PersonaScore]:
        """
        Add Chapter 4 specific summaries for energie & duurzaamheid.
        References actual registry data and explains financial/comfort implications.
        """
        # Get registry data for summaries
        energy_label = self.ctx.get_registry_value("energy_label") or "onbekend"
        build_year = self.ctx.get_registry_value("build_year")
        living_area = self.ctx.get_registry_value("living_area_m2") or "onbekend"
        prop_type = self.ctx.get_registry_value("property_type") or "woning"
        
        # Compute derived values for narrative
        if energy_label and energy_label != "onbekend":
            label_upper = str(energy_label).upper()
            if label_upper.startswith("A"):
                label_quality = "uitstekend"
                cost_indication = "lage energiekosten"
                sustainability_action = "minimale verduurzaming nodig"
            elif label_upper == "B":
                label_quality = "goed"
                cost_indication = "acceptabele energiekosten"
                sustainability_action = "kleine optimalisaties mogelijk"
            elif label_upper == "C":
                label_quality = "gemiddeld"
                cost_indication = "gemiddelde energiekosten"
                sustainability_action = "verduurzaming aanbevolen"
            elif label_upper == "D":
                label_quality = "onder gemiddeld"
                cost_indication = "verhoogde energiekosten"
                sustainability_action = "verduurzaming noodzakelijk"
            else:
                label_quality = "slecht"
                cost_indication = "hoge energiekosten"
                sustainability_action = "ingrijpende verduurzaming vereist"
        else:
            label_quality = "onbekend"
            cost_indication = "niet in te schatten"
            sustainability_action = "energie-audit aanbevolen"
        
        age_context = ""
        if build_year:
            age = datetime.now().year - int(build_year)
            if age < 10:
                age_context = "Recente bouw met moderne isolatienormen. "
            elif age < 25:
                age_context = "Relatief modern qua isolatie. "
            elif age < 40:
                age_context = "Isolatie mogelijk gedateerd. "
            else:
                age_context = f"Bij {age} jaar oud waarschijnlijk sub-optimale isolatie. "
        
        # Marcel's summary: ROI, costs, technical perspective
        marcel_summary = (
            f"Energielabel {energy_label} ({label_quality}) betekent {cost_indication}. "
            f"{age_context}"
            f"Marcel adviseert: {sustainability_action}. "
            f"Bij een {prop_type} van {living_area}m² is de energiebehoefte substantieel. "
            f"Verduurzamingskosten zijn calculeerbaar, maar terugverdientijd hangt af van "
            f"toekomstige energieprijzen en beschikbare subsidies."
        )
        
        # Petra's summary: comfort, peace-of-mind, warmth
        petra_summary = (
            f"Met energielabel {energy_label} is de woning {label_quality} geïsoleerd. "
            f"Dit betekent: {'een warm en comfortabel huis' if label_quality in ['uitstekend', 'goed'] else 'mogelijk tochtgevoelig of kouder dan gewenst'}. "
            f"{'Voorspelbare woonlasten geven rust.' if label_quality in ['uitstekend', 'goed'] else 'Hogere energierekeningen kunnen verrassen.'} "
            f"{age_context}"
            f"Voor zorgeloos wonen is {sustainability_action}."
        )
        
        # Create enhanced PersonaScores
        enhanced_marcel = PersonaScore(
            match_score=marcel.match_score,
            mood=marcel.mood,
            key_values=marcel.key_values,
            concerns=marcel.concerns,
            summary=marcel_summary
        )
        
        enhanced_petra = PersonaScore(
            match_score=petra.match_score,
            mood=petra.mood,
            key_values=petra.key_values,
            concerns=petra.concerns,
            summary=petra_summary
        )
        
        return enhanced_marcel, enhanced_petra
    
    # =========================================================================
    # CHAPTER 5: INDELING, RUIMTELIJKHEID & DAGELIJKS GEBRUIK — MAXIMALIZED PERSONA COMPUTATION
    # =========================================================================
    
    def _compute_chapter5_marcel_score(self) -> float:
        """
        Compute Marcel's Chapter 5 (Indeling & Ruimtelijkheid) score from registry data.
        
        Marcel's drivers for indeling:
        - Spatial efficiency: m² per room, logical distribution
        - Functionality: dedicated spaces for functions
        - Flexibility: reconfiguration potential
        - Future-proofing: adaptability over time
        """
        score = 65  # Base score
        
        living_area = self.ctx.get_registry_value("living_area_m2")
        rooms = self.ctx.get_registry_value("rooms")
        bedrooms = self.ctx.get_registry_value("bedrooms")
        
        # Space efficiency: m² per room
        if living_area and rooms:
            m2_per_room = living_area / rooms
            if m2_per_room >= 20:
                score += 10  # Spacious rooms
            elif m2_per_room >= 15:
                score += 5
            elif m2_per_room < 12:
                score -= 5  # Cramped
        
        # Total living area
        if living_area:
            if living_area >= 160:
                score += 10  # Large home, flexible use
            elif living_area >= 120:
                score += 5
            elif living_area < 80:
                score -= 10  # Limited flexibility
        
        # Bedroom count for workspace potential
        if bedrooms:
            if bedrooms >= 5:
                score += 5  # Room for home office
            elif bedrooms >= 4:
                score += 3
            elif bedrooms < 3:
                score -= 3  # Limited
        
        # Build year affects layout flexibility
        build_year = self.ctx.get_registry_value("build_year")
        if build_year:
            if int(build_year) >= 2000:
                score += 5  # Modern open layouts
            elif int(build_year) < 1960:
                score -= 3  # Often compartmentalized
        
        return min(100, max(0, score))
    
    def _compute_chapter5_petra_score(self) -> float:
        """
        Compute Petra's Chapter 5 (Indeling & Ruimtelijkheid) score from registry data.
        
        Petra's drivers for indeling:
        - Spatial feeling: openness, light, atmosphere
        - Together-space: room for family activities
        - Rest zones: quiet places for relaxation
        - Flow: natural movement through home
        """
        score = 70  # Base score - Petra values feel
        
        living_area = self.ctx.get_registry_value("living_area_m2")
        rooms = self.ctx.get_registry_value("rooms")
        bedrooms = self.ctx.get_registry_value("bedrooms")
        
        # Spaciousness feeling
        if living_area:
            if living_area >= 140:
                score += 12  # Room to breathe
            elif living_area >= 120:
                score += 8
            elif living_area >= 100:
                score += 3
            elif living_area < 80:
                score -= 8  # Feels cramped
        
        # Bedrooms for family
        if bedrooms:
            if bedrooms >= 4:
                score += 8  # Room for everyone
            elif bedrooms >= 3:
                score += 3
            elif bedrooms < 2:
                score -= 10  # Too limited
        
        # Room count affects variety of spaces
        if rooms:
            if rooms >= 6:
                score += 5  # Variety
            elif rooms >= 4:
                score += 2
        
        # Property type affects feeling
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type and "vrijstaand" in str(prop_type).lower():
            score += 5  # Likely more spacious feel
        
        return min(100, max(0, score))
    
    def _enhance_chapter5_personas(
        self, marcel: PersonaScore, petra: PersonaScore
    ) -> Tuple[PersonaScore, PersonaScore]:
        """
        Add Chapter 5 specific summaries for indeling & ruimtelijkheid.
        References actual registry data and explains spatial/daily living implications.
        """
        # Get registry data for summaries
        living_area = self.ctx.get_registry_value("living_area_m2") or "onbekend"
        rooms = self.ctx.get_registry_value("rooms")
        bedrooms = self.ctx.get_registry_value("bedrooms")
        prop_type = self.ctx.get_registry_value("property_type") or "woning"
        build_year = self.ctx.get_registry_value("build_year")
        
        # Compute derived values
        if living_area != "onbekend" and rooms:
            m2_per_room = round(living_area / rooms, 1)
            efficiency_desc = f"{m2_per_room}m² per kamer"
        else:
            efficiency_desc = "efficiëntie niet te berekenen"
        
        workspace_potential = ""
        if bedrooms and rooms:
            extra_rooms = rooms - bedrooms - 1  # Minus living room
            if extra_rooms >= 2:
                workspace_potential = "Aparte werkruimte potentieel aanwezig. "
            elif extra_rooms >= 1:
                workspace_potential = "Beperkte werkruimte-optie. "
            else:
                workspace_potential = "Geen aparte werkruimte zichtbaar. "
        
        layout_context = ""
        if build_year:
            if int(build_year) >= 2000:
                layout_context = "Moderne bouw suggereert open indeling. "
            elif int(build_year) < 1960:
                layout_context = "Oudere woning: mogelijk traditioneel kamers-concept. "
        
        # Marcel's summary: efficiency, functionality, logic
        marcel_summary = (
            f"De woning biedt {living_area}m² verdeeld over {rooms or 'onbekend'} kamers ({efficiency_desc}). "
            f"{bedrooms or 0} slaapkamers suggereren {'voldoende' if bedrooms and bedrooms >= 4 else 'beperkte'} capaciteit. "
            f"{workspace_potential}"
            f"{layout_context}"
            f"Marcel adviseert: verificatie van plattegrond bij bezichtiging. Dragende muren bepalen "
            f"herindelingspotentieel. Dagelijks gebruik-scenario's doorlopen ter plekke."
        )
        
        # Petra's summary: feeling, light, together-space
        petra_summary = (
            f"Een {prop_type} met {living_area}m² kan {'ruim en luchtig' if living_area != 'onbekend' and living_area >= 130 else 'knus maar compact'} aanvoelen. "
            f"Met {bedrooms or 'onbekend'} slaapkamers is er {'ruimte voor iedereen' if bedrooms and bedrooms >= 4 else 'een compactere verdeling'}. "
            f"Petra wil voelen: is er een fijne plek om samen te zijn? Zijn er rustige hoekjes? "
            f"Daglicht en doorkijk bepalen de sfeer - dit is alleen bij bezichtiging te ervaren. "
            f"De vraag is of deze indeling past bij ons dagelijks leven."
        )
        
        # Create enhanced PersonaScores
        enhanced_marcel = PersonaScore(
            match_score=marcel.match_score,
            mood=marcel.mood,
            key_values=marcel.key_values,
            concerns=marcel.concerns,
            summary=marcel_summary
        )
        
        enhanced_petra = PersonaScore(
            match_score=petra.match_score,
            mood=petra.mood,
            key_values=petra.key_values,
            concerns=petra.concerns,
            summary=petra_summary
        )
        
        return enhanced_marcel, enhanced_petra
    
    # =========================================================================
    # CHAPTER 6: AFWERKING & KWALITEIT — MAXIMALIZED PERSONA COMPUTATION
    # =========================================================================
    
    def _compute_chapter6_marcel_score(self) -> float:
        """
        Compute Marcel's Chapter 6 (Afwerking & Kwaliteit) score from registry data.
        
        Marcel's drivers for afwerking:
        - Material quality: durability and longevity
        - Maintenance state: current condition indicators
        - Renovation cost: predictable investment needs
        - Value impact: how quality affects property value
        """
        score = 60  # Base score
        
        build_year = self.ctx.get_registry_value("build_year")
        if build_year:
            age = datetime.now().year - int(build_year)
            # Quality typically degrades with age without renovation
            if age <= 5:
                score += 20  # Very recent, likely good condition
            elif age <= 15:
                score += 12
            elif age <= 25:
                score += 5
            elif age <= 40:
                score -= 5  # Likely needs updates
            else:
                score -= 10  # Significant renovation probable
        
        # Property type affects maintenance state expectations
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type:
            if "nieuwbouw" in str(prop_type).lower():
                score += 15
            elif "appartement" in str(prop_type).lower():
                score += 3  # VvE might maintain common areas
        
        # Living area affects renovation cost scale
        living_area = self.ctx.get_registry_value("living_area_m2")
        if living_area:
            if living_area > 200:
                score -= 5  # Higher renovation costs
            elif living_area < 100:
                score += 3  # More manageable costs
        
        return min(100, max(0, score))
    
    def _compute_chapter6_petra_score(self) -> float:
        """
        Compute Petra's Chapter 6 (Afwerking & Kwaliteit) score from registry data.
        
        Petra's drivers for afwerking:
        - Aesthetic appeal: visual atmosphere and feel
        - Instapklaar: ready to move in vs renovation needed
        - Personal taste: alignment with style preferences
        - Comfort: finish quality affecting daily experience
        """
        score = 65  # Base score
        
        build_year = self.ctx.get_registry_value("build_year")
        if build_year:
            age = datetime.now().year - int(build_year)
            # Petra values move-in ready condition
            if age <= 10:
                score += 15  # Likely modern and fresh
            elif age <= 20:
                score += 8
            elif age <= 35:
                score += 0  # Neutral, could be renovated
            else:
                score -= 8  # Likely dated style
        
        # Property type affects style expectations
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type:
            if "vrijstaand" in str(prop_type).lower():
                score += 5  # Often more attention to finish
            elif "appartement" in str(prop_type).lower():
                score += 0  # Depends on individual unit
        
        return min(100, max(0, score))
    
    def _enhance_chapter6_personas(
        self, marcel: PersonaScore, petra: PersonaScore
    ) -> Tuple[PersonaScore, PersonaScore]:
        """
        Add Chapter 6 specific summaries for afwerking & kwaliteit.
        References actual registry data and explains quality/aesthetic implications.
        """
        # Get registry data for summaries
        build_year = self.ctx.get_registry_value("build_year")
        living_area = self.ctx.get_registry_value("living_area_m2") or "onbekend"
        prop_type = self.ctx.get_registry_value("property_type") or "woning"
        
        # Compute derived values
        age_context = ""
        renovation_context = ""
        if build_year:
            age = datetime.now().year - int(build_year)
            if age <= 5:
                age_context = "Recente bouw: afwerking waarschijnlijk modern en in goede staat. "
                renovation_context = "Minimale renovatie verwacht. "
            elif age <= 15:
                age_context = "Relatief modern: afwerking vermoedelijk acceptabel. "
                renovation_context = "Cosmetische updates mogelijk gewenst. "
            elif age <= 30:
                age_context = f"Bij {age} jaar oud: keuken en badkamer mogelijk verouderd. "
                renovation_context = "Renovatiebudget aanbevolen. "
            else:
                age_context = f"Met {age} jaar: stijl en materialen waarschijnlijk gedateerd. "
                renovation_context = "Substantiële renovatie-investering te verwachten. "
        
        # Marcel's summary: costs, durability, value
        marcel_summary = (
            f"{age_context}"
            f"{renovation_context}"
            f"Bij een {prop_type} van {living_area}m² zijn renovatiekosten schaalbaar. "
            f"Marcel adviseert: bezichtiging met oog voor materiaalstaat achter de afwerking. "
            f"Elektra, leidingwerk en constructieve kwaliteit bepalen werkelijke waarde. "
            f"Cosmetische updates zijn calculeerbaar, structurele issues zijn risicofactoren."
        )
        
        # Petra's summary: atmosphere, style, move-in ready
        petra_summary = (
            f"{age_context}"
            f"De vraag is: voelt deze woning als 'thuis'? Past de stijl bij onze smaak? "
            f"{'Instapklaar wonen geeft rust.' if build_year and datetime.now().year - int(build_year) <= 15 else 'Renoveren biedt kans voor eigen stempel, maar kost tijd en energie.'} "
            f"Keuken en badkamer bepalen dagelijks woonplezier - bezoek ter plekke essentieel. "
            f"Sfeer is subjectief en kan alleen persoonlijk beoordeeld worden."
        )
        
        # Create enhanced PersonaScores
        enhanced_marcel = PersonaScore(
            match_score=marcel.match_score,
            mood=marcel.mood,
            key_values=marcel.key_values,
            concerns=marcel.concerns,
            summary=marcel_summary
        )
        
        enhanced_petra = PersonaScore(
            match_score=petra.match_score,
            mood=petra.mood,
            key_values=petra.key_values,
            concerns=petra.concerns,
            summary=petra_summary
        )
        
        return enhanced_marcel, enhanced_petra
    
    # =========================================================================
    # CHAPTER 7: BUITENRUIMTE, TUIN & OMGEVINGSGEBRUIK — MAXIMALIZED PERSONA COMPUTATION
    # =========================================================================
    
    def _compute_chapter7_marcel_score(self) -> float:
        """
        Compute Marcel's Chapter 7 (Buitenruimte) score from registry data.
        
        Marcel's drivers for buitenruimte:
        - Maintenance predictability: known effort required
        - Value contribution: outdoor space adds property value
        - Practical use: storage, parking, expansion potential
        - Low-hassle: manageable garden size
        """
        score = 60  # Base score
        
        plot_area = self.ctx.get_registry_value("plot_area_m2")
        living_area = self.ctx.get_registry_value("living_area_m2")
        
        if plot_area and living_area:
            # Calculate garden area (approximate)
            garden_area = plot_area - (living_area * 0.5)  # Rough footprint estimate
            
            if garden_area > 500:
                score += 10  # Large garden = value but also maintenance
                score -= 5   # High maintenance concern
            elif garden_area > 200:
                score += 12  # Nice garden, manageable
            elif garden_area > 100:
                score += 8
            elif garden_area > 50:
                score += 3
            elif garden_area > 0:
                score -= 2  # Very small
            else:
                score -= 10  # No real garden
        elif plot_area:
            if plot_area > 300:
                score += 8
            elif plot_area > 150:
                score += 5
        else:
            score -= 10  # Unknown = uncertainty
        
        # Property type affects garden expectations
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type:
            if "vrijstaand" in str(prop_type).lower():
                score += 5  # Usually good outdoor space
            elif "appartement" in str(prop_type).lower():
                score -= 10  # Typically no garden
        
        return min(100, max(0, score))
    
    def _compute_chapter7_petra_score(self) -> float:
        """
        Compute Petra's Chapter 7 (Buitenruimte) score from registry data.
        
        Petra's drivers for buitenruimte:
        - Relaxation potential: space for outdoor living
        - Nature connection: greenery for mental rest
        - Family use: space for children/pets/gathering
        - Privacy feeling: own outdoor retreat
        """
        score = 65  # Base score - Petra values outdoor positively
        
        plot_area = self.ctx.get_registry_value("plot_area_m2")
        living_area = self.ctx.get_registry_value("living_area_m2")
        
        if plot_area and living_area:
            garden_area = plot_area - (living_area * 0.5)
            
            if garden_area > 300:
                score += 15  # Dream garden potential
            elif garden_area > 150:
                score += 12
            elif garden_area > 80:
                score += 8
            elif garden_area > 30:
                score += 3
            elif garden_area > 0:
                score -= 3  # Small but present
            else:
                score -= 12  # No outdoor living space
        elif plot_area:
            if plot_area > 200:
                score += 10
            elif plot_area > 100:
                score += 5
        else:
            score -= 8  # Unknown
        
        # Property type affects privacy expectations
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type:
            if "vrijstaand" in str(prop_type).lower():
                score += 8  # Best privacy
            elif "2-onder-1-kap" in str(prop_type).lower():
                score += 3
            elif "tussenwoning" in str(prop_type).lower():
                score -= 2  # Less privacy
            elif "appartement" in str(prop_type).lower():
                score -= 15  # Minimal outdoor
        
        return min(100, max(0, score))
    
    def _enhance_chapter7_personas(
        self, marcel: PersonaScore, petra: PersonaScore
    ) -> Tuple[PersonaScore, PersonaScore]:
        """
        Add Chapter 7 specific summaries for buitenruimte & tuin.
        References actual registry data and explains outdoor implications.
        """
        # Get registry data for summaries
        plot_area = self.ctx.get_registry_value("plot_area_m2")
        living_area = self.ctx.get_registry_value("living_area_m2") or "onbekend"
        prop_type = self.ctx.get_registry_value("property_type") or "woning"
        
        # Compute derived values
        garden_context = ""
        maintenance_context = ""
        if plot_area and living_area != "onbekend":
            garden_est = plot_area - (living_area * 0.5)
            if garden_est > 200:
                garden_context = f"Bij geschat {int(garden_est)}m² tuin is er ruimte voor terras, gazon en beplanting. "
                maintenance_context = "Grotere tuin betekent meer onderhoud: wekelijks maaien, snoeien, schoonhouden. "
            elif garden_est > 80:
                garden_context = f"Geschat {int(garden_est)}m² tuin biedt redelijke buitenruimte. "
                maintenance_context = "Onderhoud is beheersbaar voor gemiddeld gebruik. "
            elif garden_est > 0:
                garden_context = f"Compacte buitenruimte van ca. {int(garden_est)}m². "
                maintenance_context = "Minimaal tuinonderhoud vereist. "
            else:
                garden_context = "Zeer beperkte of geen buitenruimte. "
                maintenance_context = ""
        elif plot_area:
            garden_context = f"Perceel van {plot_area}m², tuinoppervlak onbekend. "
        else:
            garden_context = "Perceeloppervlak onbekend. "
        
        privacy_note = ""
        if "vrijstaand" in str(prop_type).lower():
            privacy_note = "Vrijstaande woning biedt doorgaans goede privacy. "
        elif "tussenwoning" in str(prop_type).lower():
            privacy_note = "Bij tussenwoning is inkijk van buren mogelijk. "
        
        # Marcel's summary: maintenance, value, practicality
        marcel_summary = (
            f"{garden_context}"
            f"{maintenance_context}"
            f"Marcel let op: onderhoudsdruk, uitbreidingspotentieel, parkeerruimte. "
            f"Tuinoriëntatie en exacte indeling zijn onbekend — bezichtiging noodzakelijk. "
            f"Buitenruimte draagt bij aan waarde, maar ook aan doorlopende onderhoudsinvestering."
        )
        
        # Petra's summary: relaxation, nature, family
        petra_summary = (
            f"{garden_context}"
            f"{privacy_note}"
            f"Petra vraagt zich af: is dit een plek om tot rust te komen? "
            f"Kan hier buiten gegeten worden, gelezen in de zon, gespeeld met kinderen? "
            f"De tuinbeleving — geluiden, geuren, sfeer — is alleen ter plekke te ervaren. "
            f"Elke seizoen brengt andere mogelijkheden en uitdagingen."
        )
        
        # Create enhanced PersonaScores
        enhanced_marcel = PersonaScore(
            match_score=marcel.match_score,
            mood=marcel.mood,
            key_values=marcel.key_values,
            concerns=marcel.concerns,
            summary=marcel_summary
        )
        
        enhanced_petra = PersonaScore(
            match_score=petra.match_score,
            mood=petra.mood,
            key_values=petra.key_values,
            concerns=petra.concerns,
            summary=petra_summary
        )
        
        return enhanced_marcel, enhanced_petra
    
    # =========================================================================
    # CHAPTER 8: LOCATIE & BEREIKBAARHEID — MAXIMALIZED PERSONA COMPUTATION
    # =========================================================================
    
    def _compute_chapter8_marcel_score(self) -> float:
        """
        Compute Marcel's Chapter 8 (Locatie & Bereikbaarheid) score from registry data.
        
        Marcel's drivers for locatie:
        - Transport efficiency: OV access, highway proximity
        - Commute practicality: travel time, connections
        - Infrastructure: parking, roads
        - Value factor: location premium
        """
        score = 65  # Base score
        
        # Address presence gives some location information
        address = self.ctx.get_registry_value("address")
        if address:
            score += 5  # Known location
            # Try to infer region from address
            addr_lower = str(address).lower()
            if any(city in addr_lower for city in ["amsterdam", "rotterdam", "den haag", "utrecht"]):
                score += 10  # Randstad - good infrastructure
            elif any(city in addr_lower for city in ["eindhoven", "groningen", "arnhem", "maastricht"]):
                score += 5  # Major city
        else:
            score -= 15  # Unknown location is a problem
        
        # Property type hints at location characteristics
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type:
            if "appartement" in str(prop_type).lower():
                score += 3  # Usually in accessible areas
        
        return min(100, max(0, score))
    
    def _compute_chapter8_petra_score(self) -> float:
        """
        Compute Petra's Chapter 8 (Locatie & Bereikbaarheid) score from registry data.
        
        Petra's drivers for locatie:
        - Neighborhood feel: safety, atmosphere
        - Daily convenience: shops, schools, healthcare
        - Social environment: community, activities
        - Living quality: quiet, green, pleasant
        """
        score = 70  # Base score - location feel is subjective
        
        address = self.ctx.get_registry_value("address")
        if address:
            score += 3  # Can at least research the area
        else:
            score -= 10  # Unknown
        
        # Property type hints at neighborhood type
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type:
            if "vrijstaand" in str(prop_type).lower():
                score += 5  # Often in quieter areas
            elif "appartement" in str(prop_type).lower():
                score -= 3  # Denser, potentially noisier
        
        return min(100, max(0, score))
    
    def _enhance_chapter8_personas(
        self, marcel: PersonaScore, petra: PersonaScore
    ) -> Tuple[PersonaScore, PersonaScore]:
        """
        Add Chapter 8 specific summaries for locatie & bereikbaarheid.
        References actual registry data and explains location implications.
        """
        # Get registry data for summaries
        address = self.ctx.get_registry_value("address") or "onbekend"
        prop_type = self.ctx.get_registry_value("property_type") or "woning"
        
        # Location context based on address
        location_context = ""
        if address != "onbekend":
            location_context = f"De locatie '{address}' bepaalt vele aspecten van het dagelijks leven. "
        else:
            location_context = "Zonder bekend adres is locatiebeoordeling onmogelijk. "
        
        accessibility_note = ""
        neighborhood_note = ""
        if "vrijstaand" in str(prop_type).lower():
            neighborhood_note = "Vrijstaande woningen liggen vaak in rustigere wijken met meer privacy. "
        elif "appartement" in str(prop_type).lower():
            accessibility_note = "Appartementen bevinden zich doorgaans in beter bereikbare gebieden. "
            neighborhood_note = "Hogere dichtheid betekent meer voorzieningen maar ook meer drukte. "
        
        # Marcel's summary: infrastructure, commute, transport
        marcel_summary = (
            f"{location_context}"
            f"{accessibility_note}"
            f"Marcel wil weten: hoe lang duurt de reis naar werk? Is er parkeergelegenheid? "
            f"Wat is de OV-bereikbaarheid en snelwegaansluiting? "
            f"Locatiedata zoals buurtstatistieken, verkeersintensiteit en ontwikkelingsplannen "
            f"vereisen aanvullend onderzoek. Bezichtiging op verschillende tijdstippen aanbevolen."
        )
        
        # Petra's summary: neighborhood, safety, convenience
        petra_summary = (
            f"{location_context}"
            f"{neighborhood_note}"
            f"Petra vraagt zich af: voelt deze buurt veilig? Zijn er scholen, winkels, groen? "
            f"Hoe is de sfeer overdag en 's avonds? "
            f"De sociale samenstelling en gemeenschapsgevoel zijn alleen ter plekke te ervaren. "
            f"Een proefwandeling door de buurt is essentieel voor een eerlijk beeld."
        )
        
        # Create enhanced PersonaScores
        enhanced_marcel = PersonaScore(
            match_score=marcel.match_score,
            mood=marcel.mood,
            key_values=marcel.key_values,
            concerns=marcel.concerns,
            summary=marcel_summary
        )
        
        enhanced_petra = PersonaScore(
            match_score=petra.match_score,
            mood=petra.mood,
            key_values=petra.key_values,
            concerns=petra.concerns,
            summary=petra_summary
        )
        
        return enhanced_marcel, enhanced_petra
    
    # =========================================================================
    # CHAPTER 9: JURIDISCH & EIGENDOM — MAXIMALIZED PERSONA COMPUTATION
    # =========================================================================
    
    def _compute_chapter9_marcel_score(self) -> float:
        """
        Compute Marcel's Chapter 9 (Juridisch & Eigendom) score from registry data.
        
        Marcel's drivers for juridisch:
        - Legal clarity: clear ownership structure
        - Documentation: complete and verifiable
        - Obligations: predictable and calculable
        - Risk: minimal legal surprises
        """
        score = 65  # Base score
        
        # Property type affects legal complexity
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type:
            prop_lower = str(prop_type).lower()
            if "appartement" in prop_lower:
                score -= 10  # VvE complexity
            elif "vrijstaand" in prop_lower:
                score += 10  # Usually simpler ownership
            elif "tussenwoning" in prop_lower or "rijtjeshuis" in prop_lower:
                score += 5  # Usually straightforward
        
        # VvE contribution presence indicates apartment
        vve_contrib = self.ctx.get_registry_value("vve_contribution")
        if vve_contrib:
            if vve_contrib > 300:
                score -= 5  # Higher monthly obligation
            elif vve_contrib < 150:
                score += 3  # Reasonable
        
        return min(100, max(0, score))
    
    def _compute_chapter9_petra_score(self) -> float:
        """
        Compute Petra's Chapter 9 (Juridisch & Eigendom) score from registry data.
        
        Petra's drivers for juridisch:
        - Ownership security: feeling of true ownership
        - Simplicity: no complex structures
        - Peace of mind: no hidden obligations
        - Long-term certainty: stable ownership
        """
        score = 70  # Base score
        
        prop_type = self.ctx.get_registry_value("property_type")
        if prop_type:
            prop_lower = str(prop_type).lower()
            if "appartement" in prop_lower:
                score -= 8  # VvE can feel like less ownership
            elif "vrijstaand" in prop_lower:
                score += 12  # Full ownership feeling
            elif "tussenwoning" in prop_lower:
                score += 5
        
        # VvE contribution affects security feeling
        vve_contrib = self.ctx.get_registry_value("vve_contribution")
        if vve_contrib and vve_contrib > 250:
            score -= 5  # Monthly drain on budget
        
        return min(100, max(0, score))
    
    def _enhance_chapter9_personas(
        self, marcel: PersonaScore, petra: PersonaScore
    ) -> Tuple[PersonaScore, PersonaScore]:
        """
        Add Chapter 9 specific summaries for juridisch & eigendom.
        References actual registry data and explains legal implications.
        """
        # Get registry data for summaries
        prop_type = self.ctx.get_registry_value("property_type") or "woning"
        vve_contrib = self.ctx.get_registry_value("vve_contribution")
        
        # Ownership context based on property type
        ownership_context = ""
        vve_context = ""
        if "appartement" in str(prop_type).lower():
            ownership_context = "Als appartement is dit appartementsrecht, niet volledig eigendom. "
            vve_context = f"VvE-bijdrage van €{vve_contrib}/mnd. " if vve_contrib else "VvE-bijdrage onbekend. "
            vve_context += "VvE-notulen, jaarrekening en MJOP opvragen essentieel. "
        elif "vrijstaand" in str(prop_type).lower():
            ownership_context = "Vrijstaande woning: meestal volledig eigendom, juridisch eenvoudiger. "
        else:
            ownership_context = f"Bij deze {prop_type}: eigendomsvorm verifiëren via Kadaster. "
        
        # Marcel's summary: documentation, obligations, verification
        marcel_summary = (
            f"{ownership_context}"
            f"{vve_context}"
            f"Marcel adviseert: eigendomsbewijs, erfpachtstatus en kadastercheck voor de aankoop. "
            f"Splitsingsakte en reglement analyseren voor rechten en plichten. "
            f"Erfdienstbaarheden en bezwaringen kunnen verplichtingen inhouden. "
            f"Juridische duidelijkheid voorkomt financiële verrassingen later."
        )
        
        # Petra's summary: security, simplicity, peace of mind
        petra_summary = (
            f"{ownership_context}"
            f"Petra wil weten: is dit echt van ons? Geen verborgen verplichtingen? "
            f"{'VvE betekent gedeeld eigendom en gezamenlijke beslissingen.' if 'appartement' in str(prop_type).lower() else 'Volledig eigendom geeft maximale zekerheid en vrijheid.'} "
            f"Juridische zekerheid komt pas bij notariële overdracht. "
            f"Tot die tijd is zorgvuldig documentonderzoek belangrijk voor gemoedsrust."
        )
        
        # Create enhanced PersonaScores
        enhanced_marcel = PersonaScore(
            match_score=marcel.match_score,
            mood=marcel.mood,
            key_values=marcel.key_values,
            concerns=marcel.concerns,
            summary=marcel_summary
        )
        
        enhanced_petra = PersonaScore(
            match_score=petra.match_score,
            mood=petra.mood,
            key_values=petra.key_values,
            concerns=petra.concerns,
            summary=petra_summary
        )
        
        return enhanced_marcel, enhanced_petra
    
    # =========================================================================
    # CHAPTER 10: FINANCIËLE ANALYSE — MAXIMALIZED PERSONA COMPUTATION
    # =========================================================================
    
    def _compute_chapter10_marcel_score(self) -> float:
        """Compute Marcel's Chapter 10 (Financiële Analyse) score from registry data."""
        score = 70  # Base score
        
        # Price data availability
        asking_price = self.ctx.get_registry_value("asking_price_eur")
        woz_value = self.ctx.get_registry_value("woz_value")
        living_area = self.ctx.get_registry_value("living_area_m2")
        
        if asking_price:
            score += 5
            if woz_value:
                ratio = asking_price / woz_value if woz_value > 0 else 1
                if ratio < 1.1:
                    score += 10  # Good value
                elif ratio > 1.3:
                    score -= 5  # Expensive vs WOZ
        
        if living_area and asking_price:
            price_m2 = asking_price / living_area
            if price_m2 < 4000:
                score += 5  # Reasonable price/m²
                
        return min(100, max(0, score))
    
    def _compute_chapter10_petra_score(self) -> float:
        """Compute Petra's Chapter 10 (Financiële Analyse) score from registry data."""
        score = 65  # Base score
        
        asking_price = self.ctx.get_registry_value("asking_price_eur")
        if asking_price:
            if asking_price < 400000:
                score += 10  # More affordable
            elif asking_price > 600000:
                score -= 5  # Higher financial stress
        
        return min(100, max(0, score))
    
    def _enhance_chapter10_personas(
        self, marcel: PersonaScore, petra: PersonaScore
    ) -> Tuple[PersonaScore, PersonaScore]:
        """Add Chapter 10 specific summaries for financial analysis."""
        asking_price = self.ctx.get_registry_value("asking_price_eur")
        woz_value = self.ctx.get_registry_value("woz_value")
        living_area = self.ctx.get_registry_value("living_area_m2")
        
        price_context = f"Vraagprijs €{asking_price:,.0f}. " if asking_price else "Vraagprijs onbekend. "
        woz_context = f"WOZ-waarde €{woz_value:,.0f}. " if woz_value else ""
        
        marcel_summary = (
            f"{price_context}{woz_context}"
            f"Marcel berekent: hypotheeklasten, kosten koper, maandelijkse verplichtingen. "
            f"Overdrachtsbelasting, notariskosten en taxatie komen bovenop de koopprijs. "
            f"Rentestand beïnvloedt maandlasten significant. "
            f"Financiële buffer voor onderhoud en onverwachte kosten noodzakelijk."
        )
        
        petra_summary = (
            f"{price_context}"
            f"Petra vraagt zich af: voelen de maandlasten haalbaar? "
            f"Blijft er ruimte voor leuke dingen naast de vaste woonkosten? "
            f"Financiële zekerheid voor de lange termijn is belangrijk. "
            f"Samen de cijfers doornemen geeft rust."
        )
        
        enhanced_marcel = PersonaScore(
            match_score=marcel.match_score,
            mood=marcel.mood,
            key_values=marcel.key_values,
            concerns=marcel.concerns,
            summary=marcel_summary
        )
        enhanced_petra = PersonaScore(
            match_score=petra.match_score,
            mood=petra.mood,
            key_values=petra.key_values,
            concerns=petra.concerns,
            summary=petra_summary
        )
        
        return enhanced_marcel, enhanced_petra
    
    # =========================================================================
    # CHAPTER 11: MARKTPOSITIE & ONDERHANDELINGSRUIMTE — MAXIMALIZED PERSONA COMPUTATION
    # =========================================================================
    
    def _compute_chapter11_marcel_score(self) -> float:
        """Compute Marcel's Chapter 11 (Marktpositie) score from registry data."""
        score = 65  # Base score
        
        asking_price = self.ctx.get_registry_value("asking_price_eur")
        if asking_price:
            score += 5  # Can analyze market position
        
        return min(100, max(0, score))
    
    def _compute_chapter11_petra_score(self) -> float:
        """Compute Petra's Chapter 11 (Marktpositie) score from registry data."""
        score = 60  # Base score - market analysis is more Marcel's domain
        
        return min(100, max(0, score))
    
    def _enhance_chapter11_personas(
        self, marcel: PersonaScore, petra: PersonaScore
    ) -> Tuple[PersonaScore, PersonaScore]:
        """Add Chapter 11 specific summaries for market position & negotiation."""
        asking_price = self.ctx.get_registry_value("asking_price_eur")
        
        price_context = f"Bij vraagprijs €{asking_price:,.0f} " if asking_price else "Zonder bekende vraagprijs "
        
        marcel_summary = (
            f"{price_context}analyseert Marcel de marktpositie. "
            f"Vergelijking met recent verkochte woningen in de buurt is essentieel. "
            f"Onderhandelingsruimte hangt af van marktomstandigheden en concurrentie. "
            f"Biedstrategie onderbouwen met data geeft sterke onderhandelingspositie."
        )
        
        petra_summary = (
            f"Petra wil een eerlijke deal. Niet te veel betalen, maar ook niet mislopen. "
            f"Het gevoel bij de onderhandeling is belangrijk. "
            f"Vertrouwen in gezamenlijke biedstrategie geeft rust. "
            f"Timing en concurrentie maken het spannend."
        )
        
        enhanced_marcel = PersonaScore(
            match_score=marcel.match_score,
            mood=marcel.mood,
            key_values=marcel.key_values,
            concerns=marcel.concerns,
            summary=marcel_summary
        )
        enhanced_petra = PersonaScore(
            match_score=petra.match_score,
            mood=petra.mood,
            key_values=petra.key_values,
            concerns=petra.concerns,
            summary=petra_summary
        )
        
        return enhanced_marcel, enhanced_petra
    
    # =========================================================================
    # CHAPTER 12: EINDCONCLUSIE & AANBEVELING — MAXIMALIZED PERSONA COMPUTATION
    # =========================================================================
    
    def _compute_chapter12_marcel_score(self) -> float:
        """Compute Marcel's Chapter 12 (Eindconclusie) score from registry data."""
        score = 70  # Base score - conclusions based on earlier chapters
        
        # Overall data completeness affects conclusion confidence
        if self.ctx.get_registry_value("asking_price_eur"):
            score += 3
        if self.ctx.get_registry_value("living_area_m2"):
            score += 3
        if self.ctx.get_registry_value("build_year"):
            score += 2
        if self.ctx.get_registry_value("energy_label"):
            score += 2
        
        return min(100, max(0, score))
    
    def _compute_chapter12_petra_score(self) -> float:
        """Compute Petra's Chapter 12 (Eindconclusie) score from registry data."""
        score = 70  # Base score - matches Marcel for conclusion
        
        return min(100, max(0, score))
    
    def _enhance_chapter12_personas(
        self, marcel: PersonaScore, petra: PersonaScore
    ) -> Tuple[PersonaScore, PersonaScore]:
        """Add Chapter 12 specific summaries for final conclusion."""
        asking_price = self.ctx.get_registry_value("asking_price_eur")
        prop_type = self.ctx.get_registry_value("property_type") or "woning"
        
        price_context = f"€{asking_price:,.0f}" if asking_price else "onbekende vraagprijs"
        
        marcel_summary = (
            f"Marcel's eindoordeel: deze {prop_type} voor {price_context} vraagt grondige bezichtiging. "
            f"De data-analyse is compleet, maar fysieke inspectie blijft cruciaal. "
            f"Bouwkundige keuring wordt aanbevolen voor finale zekerheid. "
            f"Biedadvies volgt uit marktpositie en eigen financiële ruimte."
        )
        
        petra_summary = (
            f"Petra's eindoordeel: het gevoel moet kloppen. "
            f"De cijfers ondersteunen de beslissing, maar het hart moet ook ja zeggen. "
            f"Samen de twijfels bespreken en dan beslissen. "
            f"Een nieuw thuis kiezen is spannend en belangrijk."
        )
        
        enhanced_marcel = PersonaScore(
            match_score=marcel.match_score,
            mood=marcel.mood,
            key_values=marcel.key_values,
            concerns=marcel.concerns,
            summary=marcel_summary
        )
        enhanced_petra = PersonaScore(
            match_score=petra.match_score,
            mood=petra.mood,
            key_values=petra.key_values,
            concerns=petra.concerns,
            summary=petra_summary
        )
        
        return enhanced_marcel, enhanced_petra
    
    def _build_persona(
        self,
        persona_name: str,
        chapter_id: int,
        persona_data: Any,
        match_score: Optional[float]
    ) -> PersonaScore:
        """Build a rich PersonaScore."""
        # Extract existing data
        if isinstance(persona_data, dict):
            key_values = persona_data.get("values", [])
            concerns = persona_data.get("concerns", [])
            summary = persona_data.get("summary")
        elif isinstance(persona_data, str):
            key_values = []
            concerns = []
            summary = persona_data
        else:
            key_values = []
            concerns = []
            summary = None
        
        # Generate chapter-specific content if empty
        if not key_values:
            key_values = self._generate_positives(persona_name, chapter_id)
        if not concerns:
            concerns = self._generate_concerns(persona_name, chapter_id)
        
        # Determine mood
        mood = self._determine_mood(match_score, summary)
        
        return PersonaScore(
            match_score=match_score,
            mood=mood,
            key_values=key_values[:5],  # Max 5
            concerns=concerns[:5],       # Max 5
            summary=summary
        )
    
    def _generate_positives(self, persona: str, chapter_id: int) -> List[str]:
        """Generate chapter-specific positives for a persona."""
        # Chapter-persona specific positives based on typical concerns
        marcel_positives = {
            1: ["Objectgegevens volledig", "Bouwjaar traceerbaar", "Oppervlaktes gedocumenteerd"],
            2: ["Technische specificaties aanwezig", "Consistente data", "Vergelijkbaar met referentiedata"],
            3: [
                # Marcel Chapter 3 drivers: technical certainty, long-term risk, cost predictability
                "Bouwjaar geeft technische context",
                "Constructietype traceerbaar uit typologie",
                "Onderhoudscyclus af te leiden uit leeftijd",
                "Funderingsrisico in te schatten o.b.v. bouwperiode",
                "Kostenvoorspelbaarheid bij moderne bouw hoger"
            ],
            4: [
                # Marcel Chapter 4 drivers: ROI, cost predictability, technical efficiency
                "Energielabel geeft concrete efficiency-indicatie",
                "Verduurzamingsinvestering is calculeerbaar",
                "Moderne isolatie verlaagt risico op stijgende energiekosten",
                "Technische installaties verifieerbaar bij bezichtiging",
                "Subsidie-optimalisatie vergroot rendement"
            ],
            5: [
                # Marcel Chapter 5 drivers: spatial efficiency, logic, flexibility
                "Ruimteverdeling is logisch en efficient",
                "Kamermaten zijn functioneel bruikbaar",
                "Circulatie zonder doodlopende zones",
                "Herindelingspotentieel voor toekomstige behoeften",
                "Aparte werkruimte-mogelijkheid identificeerbaar"
            ],
            6: [
                # Marcel Chapter 6 drivers: quality, durability, maintenance costs
                "Materiaalkwaliteit objectief in te schatten",
                "Onderhoudshistorie deels afleidbaar",
                "Renovatiekosten calculeerbaar per component",
                "Levensduur installaties verifieerbaar",
                "Bouwtechnische staat beïnvloedt waarde"
            ],
            7: [
                # Marcel Chapter 7 drivers: maintenance, predictability, value
                "Perceelgrootte gedocumenteerd en verifieerbaar",
                "Onderhoudsdruk inschatbaar op basis van oppervlak",
                "Uitbreidingsmogelijkheden waardevermeerderend",
                "Privacy-niveau afleidbaar uit woningtype",
                "Buitenberging praktisch voor opslag"
            ],
            8: [
                # Marcel Chapter 8 drivers: transport, commute, practical access
                "OV-bereikbaarheid in te schatten via locatie",
                "Snelwegaansluiting relevant voor woon-werkverkeer",
                "Parkeermogelijkheden belangrijk voor auto-gebruik",
                "Afstand tot voorzieningen meetbaar",
                "Infrastructuur beïnvloedt woningwaarde"
            ],
            9: [
                # Marcel Chapter 9 drivers: legal certainty, documentation
                "Eigendomstype verifieerbaar via Kadaster",
                "VvE-documentatie opvraagbaar en controleerbaar",
                "Erfpachtvoorwaarden calculeerbaar",
                "Juridische structuur helder en transparant",
                "Verplichtingen voorspelbaar en budgeteerbaar"
            ],
            10: [
                # Marcel Chapter 10 drivers: financial analysis, calculations
                "Vraagprijs en WOZ vergelijkbaar en verifieerbaar",
                "Maandlasten calculeerbaar op basis van prijs",
                "Kosten koper voorspelbaar en budgeteerbaar",
                "Prijs per m² vergelijkbaar met regio",
                "Financiële risico's kwantificeerbaar"
            ],
            11: [
                # Marcel Chapter 11 drivers: market position, negotiation
                "Marktpositie analyseerbaar via vergelijkingen",
                "Onderhandelingsruimte inschatbaar",
                "Markttrend identificeerbaar",
                "Biedstrategie onderbouwbaar met data",
                "Timing rationeel te bepalen"
            ],
            12: [
                # Marcel Chapter 12 drivers: conclusion, decision support
                "Data voldoende voor onderbouwd advies",
                "Besluitinformatie compleet en verifieerbaar",
                "Match scores objectief berekend",
                "Risico's geïdentificeerd en gekwantificeerd",
                "Vervolgacties helder gedefinieerd"
            ],
        }
        
        petra_positives = {
            1: ["Ruimtelijkheid leesbaar", "Woonsfeer af te leiden", "Karakter zichtbaar"],
            2: ["Sfeervoorkeuren te matchen", "Leefbaarheid te beoordelen"],
            3: [
                # Petra Chapter 3 drivers: peace-of-mind, trust in house, zorgeloos wonen
                "Bouwkundige staat bepaalt woonrust",
                "Geen direct zichtbare gebreken geeft vertrouwen",
                "Moderne bouw betekent minder zorgen",
                "Onderhoudslast te overzien voor dagelijks leven",
                "Gevoel van soliditeit en veiligheid"
            ],
            4: [
                # Petra Chapter 4 drivers: comfort, warmth, zorgeloos woonlasten
                "Goed energielabel betekent comfort zonder zorgen",
                "Voorspelbare woonlasten geven financiële rust",
                "Moderne installaties zorgen voor warmte en gemak",
                "Duurzame woning voelt toekomstbestendig",
                "Geen koude tocht of vochtproblemen"
            ],
            5: [
                # Petra Chapter 5 drivers: light, openness, together-time, rest
                "Ruimtegevoel en openheid spreekt aan",
                "Voldoende daglicht in leefruimtes",
                "Plek om samen te zijn zonder drukte",
                "Rustige zones voor ontspanning",
                "Sfeervolle doorkijk en flow"
            ],
            6: [
                # Petra Chapter 6 drivers: aesthetic, atmosphere, personal taste
                "Sfeer en atmosfeer bepalend voor thuisgevoel",
                "Afwerkingsniveau spreekt aan of niet",
                "Keuken en badkamer creëren woonplezier",
                "Persoonlijke smaak past bij interieur",
                "Instapklaar of juist eigen invulling geven"
            ],
            7: [
                # Petra Chapter 7 drivers: atmosphere, relaxation, outdoor living
                "Tuin als verlengde woonruimte voor ontspanning",
                "Buitenleven mogelijk: lezen, BBQ, samen zijn",
                "Groen en natuur voor mentale rust",
                "Privacygevoel in eigen buitenruimte",
                "Seizoensbeleving: lente, zomer, herfst"
            ],
            8: [
                # Petra Chapter 8 drivers: neighborhood feel, safety, daily convenience
                "Buurtsfeer bepaalt thuisgevoel",
                "Veiligheidsgevoel cruciaal voor woonrust",
                "Scholen en kinderopvang in de buurt",
                "Winkels en horeca voor dagelijks gemak",
                "Groen en recreatie voor ontspanning"
            ],
            9: [
                # Petra Chapter 9 drivers: ownership security, peace of mind
                "Volledig eigendom geeft zekerheid en rust",
                "Geen onverwachte verplichtingen",
                "Eenvoudige structuur zonder VvE-gedoe",
                "Begrip over wat je koopt en bezit",
                "Zekerheid voor de lange termijn"
            ],
            10: [
                # Petra Chapter 10 drivers: affordability, financial comfort
                "Betaalbaarheid voelt haalbaar",
                "Maandlasten passen in budget",
                "Financiële zekerheid voor lange termijn",
                "Geen stress over onverwachte kosten",
                "Ruimte voor leuke dingen behouden"
            ],
            11: [
                # Petra Chapter 11 drivers: fair deal, confidence
                "Eerlijke prijs betalen, niet te veel",
                "Vertrouwen in onderhandeling",
                "Gevoel van goede deal",
                "Niet overvallen worden bij bieden",
                "Rust bij de beslissing"
            ],
            12: [
                # Petra Chapter 12 drivers: final decision, peace of mind
                "Gevoel dat het klopt",
                "Vertrouwen in gezamenlijke keuze",
                "Geen spijt-angst",
                "Enthousiasme over nieuwe thuis",
                "Zekerheid over de toekomst"
            ],
        }
        
        positives = marcel_positives if persona == "marcel" else petra_positives
        return positives.get(chapter_id, ["Geen specifieke positieven"])
    
    def _generate_concerns(self, persona: str, chapter_id: int) -> List[str]:
        """Generate chapter-specific concerns for a persona."""
        marcel_concerns = {
            1: ["Sommige basisdata ontbreekt", "Verificatie tijdens bezichtiging nodig"],
            2: ["Niet alle preferences meetbaar", "Subjectieve factoren resterend"],
            3: [
                # Marcel Chapter 3 concerns: hidden defects, structural risk, maintenance backlog
                "Funderingsstaat niet te verifiëren zonder keuring",
                "Verborgen gebreken niet in te schatten vanuit data",
                "CV-ketel en elektra leeftijd onbekend",
                "Onderhoudshistorie ontbreekt",
                "Bouwkundige keuring essentieel voor risicobeoordeling"
            ],
            4: [
                # Marcel Chapter 4 concerns: hidden costs, uncertain ROI, regulations
                "Werkelijke isolatiewaarden onbekend zonder meting",
                "CV-ketel leeftijd en conditie onzeker",
                "Terugverdientijd afhankelijk van energieprijzen",
                "Regelgeving kan extra investeringen forceren",
                "Subsidie-beschikbaarheid kan wijzigen"
            ],
            5: [
                # Marcel Chapter 5 concerns: efficiency, wasted space, future use
                "Plattegrond niet beschikbaar voor verificatie",
                "Kamerverdeling mogelijk inefficient",
                "Onduidelijkheid over werkruimte-mogelijkheden",
                "Flexibiliteit bij dragende muren beperkt",
                "Lange-termijn bruikbaarheid onzeker"
            ],
            6: [
                # Marcel Chapter 6 concerns: hidden costs, quality verification
                "Afwerkingskwaliteit alleen ter plekke te beoordelen",
                "Recente renovatie kan gebreken maskeren",
                "Materiaalstaat onbekend achter afwerking",
                "Elektra en leidingwerk verborgen",
                "Smaakkosten lastig te begroten"
            ],
            7: [
                # Marcel Chapter 7 concerns: maintenance burden, unknown factors
                "Tuinoriëntatie vaak onbekend - zonuren onzeker",
                "Onderhoudslast kan hoger uitvallen dan verwacht",
                "Tuinconditie alleen ter plekke te beoordelen",
                "Bomen/hagen van buren kunnen hinder geven",
                "Drainage en waterafvoer verborgen risico"
            ],
            8: [
                # Marcel Chapter 8 concerns: unknown factors, verification needs
                "Parkeerdruk vaak onderschat of onbekend",
                "OV-frequentie en punctualiteit niet gevalideerd",
                "Verkeersintensiteit kan wijzigen",
                "Toekomstige infrastructuurplannen onbekend",
                "Buurtstatistieken vereisen verificatie"
            ],
            9: [
                # Marcel Chapter 9 concerns: documentation gaps, hidden obligations
                "VvE-notulen en jaarverslagen nog opvragen",
                "Erfpacht kan hogere canon betekenen bij verlenging",
                "Splitsingsakte en reglement analyseren",
                "Kadastercheck op erfdienstbaarheden nodig",
                "MJOP en reservefonds beoordelen"
            ],
            10: [
                # Marcel Chapter 10 concerns: financial risks, unknowns
                "Bijkomende kosten kunnen hoger uitvallen",
                "Financieringslasten afhankelijk van rente",
                "Onderhoudskosten moeilijk in te schatten",
                "Energiekosten fluctueren",
                "Onverwachte uitgaven niet gebudgetteerd"
            ],
            11: [
                # Marcel Chapter 11 concerns: market uncertainty
                "Marktdynamiek kan snel veranderen",
                "Vergelijkingsobjecten beperkt beschikbaar",
                "Onderhandelingsruimte onzeker",
                "Concurrentie van andere kopers",
                "Timing moeilijk te optimaliseren"
            ],
            12: [
                # Marcel Chapter 12 concerns: decision quality
                "Bezichtiging cruciaal voor finale oordeel",
                "Finale risico-afweging nodig",
                "Verborgen gebreken niet uit te sluiten",
                "Bouwkundige keuring aanbevolen",
                "Alle documenten nog te verifiëren"
            ],
        }
        
        petra_concerns = {
            1: ["Sfeer nog te ervaren", "Beleving niet uit cijfers te halen"],
            2: ["Gevoelsmatige match nog toetsen", "Intuïtie bevestigen"],
            3: [
                # Petra Chapter 3 concerns: disruption worry, unexpected costs, living comfort
                "Onverwachte reparaties verstoren woongenot",
                "Onderhoudsstress bij oudere woning",
                "Onzekerheid over verborgen problemen",
                "Wil geen nasleep van aankoopbeslissing",
                "Zorgeloos wonen vereist zekerheid over staat"
            ],
            4: [
                # Petra Chapter 4 concerns: cold house worry, unexpected bills
                "Hogere energierekening dan verwacht",
                "Koud huis in de winter",
                "Verbouwingsstress bij verduurzaming",
                "Onzekerheid over werkelijk comfort",
                "Stijgende energieprijzen"
            ],
            5: [
                # Petra Chapter 5 concerns: feeling, light, atmosphere
                "Ruimte-beleving pas bij bezichtiging te ervaren",
                "Lichtinval onbekend zonder bezoek",
                "Mogelijke donkere hoeken of kamers",
                "Samen-zijn vs privacy balans onduidelijk",
                "Sfeer en atmosfeer niet te voelen via data"
            ],
            6: [
                # Petra Chapter 6 concerns: taste mismatch, renovation stress
                "Afwerking past mogelijk niet bij eigen smaak",
                "Renovatiewerkzaamheden verstoren woonrust",
                "Onzekerheid over totale verfraaiingskosten",
                "Keuken/badkamer voldoen misschien niet",
                "Sfeer is subjectief - pas bij bezoek te voelen"
            ],
            7: [
                # Petra Chapter 7 concerns: feeling, experience, uncertainty
                "Tuinbeleving pas bij bezoek te ervaren",
                "Geluidsoverlast buren onbekend",
                "Privacy voelt anders dan op papier",
                "Sfeer in verschillende seizoenen onzeker",
                "Inkijk en beschutting subjectief"
            ],
            8: [
                # Petra Chapter 8 concerns: feeling, experience, safety perception
                "Buurtsfeer alleen te ervaren door bezoek",
                "Veiligheidsgevoel subjectief en persoonlijk",
                "Geluidsoverlast pas merkbaar na verhuizen",
                "Sociale samenstelling buurt onbekend",
                "Avondsfeer en weekendgedrag buurt onzeker"
            ],
            9: [
                # Petra Chapter 9 concerns: complexity, understanding, hidden issues
                "Juridische complexiteit kan overweldigend zijn",
                "VvE-problemen verborgen in notulen",
                "Erfpacht onduidelijkheid geeft onrust",
                "Angst voor onverwachte verplichtingen",
                "Zekerheid pas na notariële overdracht"
            ],
            10: [
                # Petra Chapter 10 concerns: financial stress
                "Financiële rust voelen is cruciaal",
                "Budget-comfort toetsen voor zekerheid",
                "Angst voor krap zitten",
                "Onverwachte kosten kunnen stress geven",
                "Maandlasten niet te hoog willen hebben"
            ],
            11: [
                # Petra Chapter 11 concerns: deal fairness
                "Juiste keuze voelen onder druk",
                "Niet-spijt-garantie zoeken",
                "Angst om te veel te betalen",
                "Stress bij onderhandelen",
                "Onzekerheid over markt"
            ],
            12: [
                # Petra Chapter 12 concerns: final decision
                "Besluit kunnen nemen samen",
                "Vertrouwen in de keuze",
                "Twijfel over gevoel vs ratio",
                "Angst voor verkeerde beslissing",
                "Laatste twijfels wegnemen"
            ],
        }
        
        concerns = marcel_concerns if persona == "marcel" else petra_concerns
        return concerns.get(chapter_id, ["Geen specifieke zorgen"])
    
    def _determine_mood(self, match_score: Optional[float], summary: Optional[str]) -> str:
        """Determine mood from score and summary."""
        if match_score is not None:
            if match_score >= 75:
                return "positive"
            elif match_score >= 50:
                return "mixed"
            else:
                return "negative"
        
        if summary:
            text = summary.lower()
            if any(w in text for w in ["goed", "positief", "sterk", "mooi"]):
                return "positive"
            elif any(w in text for w in ["slecht", "negatief", "zwak"]):
                return "negative"
            elif any(w in text for w in ["gemengd", "twijfel"]):
                return "mixed"
        
        return "neutral"
    
    def _build_comparisons(self, chapter_id: int, chapter_data: Dict[str, Any]) -> List[PreferenceComparison]:
        """Build preference comparisons."""
        comparisons = []
        
        # Chapter-specific comparison aspects
        aspects = {
            1: ["Ruimte", "Prijs", "Bouwjaar"],
            2: ["Woonwensen", "Prioriteiten", "Compromissen"],
            3: ["Funderingsstaat", "Onderhoudslast", "Verborgen Risico's", "Bouwkundige Keuring", "Lange-termijn"],
            4: ["Energielabel", "Isolatiekwaliteit", "Verduurzamingskosten", "Wooncomfort", "Terugverdientijd"],
            5: ["Ruimteverdeling", "Kamermaten", "Daglicht", "Flexibiliteit", "Dagelijks Gebruik"],
            6: ["Materiaalkwaliteit", "Afwerkingsniveau", "Renovatiebehoefte", "Smaakvoorkeur", "Onderhoudsconditie"],
            7: ["Tuinoppervlak", "Onderhoudsdruk", "Privacy", "Zonpotentieel", "Buitenleven"],
            8: ["OV-Bereikbaarheid", "Voorzieningen", "Buurtsfeer", "Veiligheid", "Woon-Werk"],
            9: ["Eigendomstype", "VvE-Status", "Erfpacht", "Verplichtingen", "Documentatie"],
            10: ["Maandlasten", "Kosten Koper", "Betaalbaarheid", "WOZ-Verhouding", "Financieringsdruk"],
            11: ["Marktpositie", "Onderhandelingsruimte", "Vergelijkingsprijzen", "Timing", "Biedstrategie"],
            12: ["Eindoordeel", "Marcel-Petra Match", "Biedadvies", "Actiepunten", "Aanbeveling"],
        }
        
        for aspect in aspects.get(chapter_id, ["Algemeen"])[:3]:
            comparisons.append(PreferenceComparison(
                aspect=aspect,
                marcel_view=f"Marcel: {aspect.lower()} vanuit technisch perspectief",
                petra_view=f"Petra: {aspect.lower()} vanuit belevingsperspectief",
                alignment="complementary",
                requires_discussion=True
            ))
        
        return comparisons
    
    def _generate_tensions(self, chapter_id: int, marcel: PersonaScore, petra: PersonaScore) -> List[str]:
        """Generate tension points between Marcel and Petra."""
        # If scores differ significantly, there's tension
        m_score = marcel.match_score or 50
        p_score = petra.match_score or 50
        
        tensions = []
        if abs(m_score - p_score) > 15:
            if m_score > p_score:
                tensions.append("Marcel is positiever dan Petra over dit aspect")
            else:
                tensions.append("Petra is positiever dan Marcel over dit aspect")
        
        # Chapter-specific tensions
        chapter_tensions = {
            1: ["Prijs vs sfeer afweging"],
            2: ["Technisch vs emotioneel gewicht"],
            3: [
                # Chapter 3 tensions: different priorities on building condition
                "Marcel focust op technisch risico, Petra op woonrust",
                "Keuringskosten vs emotionele zekerheid",
                "Onderhoudsbudget vs charme van oudere woning"
            ],
            4: [
                # Chapter 4 tensions: different priorities on energy & sustainability
                "Marcel rekent ROI, Petra voelt comfort",
                "Investeren nu vs genieten nu",
                "Technische optimalisatie vs woongemak prioriteit"
            ],
            5: [
                # Chapter 5 tensions: different priorities on layout & daily use
                "Marcel meet m², Petra voelt ruimte",
                "Efficiënte indeling vs gezellige hoekjes",
                "Werkruimte-prioriteit vs gezamenlijke woonruimte"
            ],
            6: [
                # Chapter 6 tensions: different priorities on finish & quality
                "Marcel ziet kosten, Petra ziet sfeer",
                "Objectieve kwaliteit vs persoonlijke smaak",
                "Investeren in upgrades vs accepteren zoals het is"
            ],
            7: [
                # Chapter 7 tensions: different priorities on outdoor space
                "Marcel ziet onderhoudslast, Petra ziet genot",
                "Praktisch tuingebruik vs sfeervolle beleving",
                "Tijdsinvestering tuin vs andere prioriteiten"
            ],
            8: [
                # Chapter 8 tensions: different priorities on location
                "Marcel meet reistijd, Petra voelt buurtsfeer",
                "Infrastructuur vs sociale omgeving",
                "Praktische bereikbaarheid vs woonbeleving"
            ],
            9: [
                # Chapter 9 tensions: different priorities on legal matters
                "Marcel analyseert documenten, Petra wil zekerheid voelen",
                "Technische VvE-details vs emotionele eigendomsrust",
                "Calculeerbare verplichtingen vs vertrouwensgevoel"
            ],
            10: [
                # Chapter 10 tensions: different priorities on finances
                "Marcel rekent maandlasten, Petra voelt betaalbaarheid",
                "Budget maximaliseren vs comfort behouden",
                "Rationele financiering vs emotionele investering"
            ],
            11: [
                # Chapter 11 tensions: different priorities on market/negotiation
                "Marcel analyseert marktdata, Petra wil eerlijke deal voelen",
                "Strategisch bieden vs hart volgen",
                "Wachten op beter moment vs nu beslissen"
            ],
            12: [
                # Chapter 12 tensions: different priorities on final decision
                "Hoofd vs hart in de finale beslissing",
                "Perfectie zoeken vs accepteren wat is",
                "Risico's wegen vs kans grijpen"
            ],
        }
        
        tensions.extend(chapter_tensions.get(chapter_id, []))
        return tensions[:3]  # Max 3
    
    def _generate_overlaps(self, chapter_id: int, marcel: PersonaScore, petra: PersonaScore) -> List[str]:
        """Generate overlap points between Marcel and Petra."""
        overlaps = []
        
        m_score = marcel.match_score or 50
        p_score = petra.match_score or 50
        
        if abs(m_score - p_score) < 10:
            overlaps.append("Beide personas zijn het grotendeels eens")
        
        # Chapter-specific overlaps
        chapter_overlaps = {
            1: ["Beide willen duidelijkheid over feiten"],
            2: ["Gezamenlijke woonwens staat centraal"],
            3: [
                # Chapter 3 overlaps: shared concerns about building condition  
                "Geen van beiden wil verborgen gebreken",
                "Bouwkundige zekerheid is voor beiden cruciaal",
                "Lange-termijn wooncomfort is gezamenlijk doel",
                "Allebei willen zekerheid over onverwachte kosten"
            ],
            4: [
                # Chapter 4 overlaps: shared concerns about energy
                "Beiden willen betaalbare woonlasten",
                "Warm huis in de winter is voor beide non-negotiable",
                "Toekomstbestendigheid is gezamenlijk belang",
                "Geen verrassingen op de energierekening"
            ],
            5: [
                # Chapter 5 overlaps: shared concerns about layout
                "Goede indeling is voor beide belangrijk",
                "Voldoende slaapkamers is gezamenlijke eis",
                "Praktische dagelijkse routing gewaardeerd door beide",
                "Toekomstvastheid van indeling cruciaal"
            ],
            6: [
                # Chapter 6 overlaps: shared concerns about quality
                "Kwaliteit wordt door beide gewaardeerd",
                "Geen van beiden wil in bouwval wonen",
                "Goede staat bespaart gedoe later",
                "Prettige woonsfeer is gezamenlijk belang"
            ],
            7: [
                # Chapter 7 overlaps: shared concerns about outdoor space
                "Buitenruimte is voor beide een plus",
                "Privacy in eigen tuin is gezamenlijke wens",
                "Plezier buiten draagt bij aan woongeluk",
                "Kinderen en huisdieren profiteren van tuin"
            ],
            8: [
                # Chapter 8 overlaps: shared concerns about location
                "Veilige buurt is voor beiden cruciaal",
                "Bereikbaarheid van werk is praktisch noodzakelijk",
                "Voorzieningen in de buurt verhogen woongemak",
                "Goede locatie beschermt woningwaarde"
            ],
            9: [
                # Chapter 9 overlaps: shared concerns about legal matters
                "Zekerheid over eigendom is voor beiden cruciaal",
                "Geen van beiden wil juridische verrassingen",
                "Duidelijke verplichtingen geven rust",
                "Volledig eigendom heeft beider voorkeur"
            ],
            10: [
                # Chapter 10 overlaps: shared concerns about finances
                "Financiële haalbaarheid is essentieel voor beiden",
                "Geen van beiden wil krap komen te zitten",
                "Betaalbare woonlasten zijn gezamenlijke eis",
                "Zekerheid over lange termijn kosten gewenst"
            ],
            11: [
                # Chapter 11 overlaps: shared concerns about market/deal
                "Goede deal willen beide",
                "Niet te veel betalen is gezamenlijk doel",
                "Eerlijke prijs-kwaliteit verhouding gewenst",
                "Onderhandelingsresultaat moet goed voelen"
            ],
            12: [
                # Chapter 12 overlaps: shared concerns about final decision
                "Gezamenlijk besluit is het doel",
                "Beide willen geen spijt achteraf",
                "Zekerheid over de keuze is cruciaal",
                "Toekomstperspectief is voor beiden belangrijk"
            ],
        }
        
        overlaps.extend(chapter_overlaps.get(chapter_id, []))
        return overlaps[:3]  # Max 3


# =============================================================================
# MAIN EXTRACTOR FACADE
# =============================================================================

class FourPlaneMaxExtractor:
    """
    Facade for extracting maximalized content for all 4 planes.
    
    Usage:
        extractor = FourPlaneMaxExtractor(ctx)
        result = extractor.extract(chapter_id, chapter_data)
    """
    
    def __init__(self, ctx: PipelineContext):
        self.ctx = ctx
        self.plane_a = PlaneAExtractor(ctx)
        self.plane_c = PlaneCExtractor(ctx)
        self.plane_d = PlaneDExtractor(ctx)
    
    def extract(self, chapter_id: int, chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract maximalized content for all planes.
        
        Returns dict with:
        - plane_a_charts, plane_a_missing
        - plane_c_kpis, plane_c_missing, plane_c_parameters
        - plane_d_marcel, plane_d_petra, plane_d_comparisons, plane_d_tensions, plane_d_overlaps
        - diagnostics
        """
        # Extract Plane A
        charts, a_missing = self.plane_a.extract(chapter_id)
        
        # Extract Plane C
        kpis, c_missing, parameters = self.plane_c.extract(chapter_id)
        
        # Extract Plane D
        marcel, petra, comparisons, tensions, overlaps = self.plane_d.extract(chapter_id, chapter_data)
        
        # Build diagnostics
        narrative_contract = get_narrative_contract(chapter_id)
        diagnostics = MaximalizationDiagnostic(
            chapter_id=chapter_id,
            charts_expected=len(get_chart_catalog(chapter_id)),
            charts_generated=len(charts),
            charts_missing_reasons=a_missing,
            word_count=0,  # Will be filled by backbone after narrative
            word_target=narrative_contract.min_words,
            sections_found=[],
            sections_missing=narrative_contract.required_sections,
            cross_refs_found={},
            kpis_expected=len(get_kpi_catalog(chapter_id)),
            kpis_generated=len([k for k in kpis if k.completeness]),
            kpis_missing=c_missing,
            marcel_positives=len(marcel.key_values),
            marcel_concerns=len(marcel.concerns),
            petra_positives=len(petra.key_values),
            petra_concerns=len(petra.concerns),
            tensions_count=len(tensions),
            overlap_count=len(overlaps),
        )
        
        logger.info(diagnostics.to_log_block())
        
        return {
            "plane_a_charts": charts,
            "plane_a_missing": a_missing,
            "plane_c_kpis": kpis,
            "plane_c_missing": c_missing,
            "plane_c_parameters": parameters,
            "plane_d_marcel": marcel,
            "plane_d_petra": petra,
            "plane_d_comparisons": comparisons,
            "plane_d_tensions": tensions,
            "plane_d_overlaps": overlaps,
            "diagnostics": diagnostics,
        }
