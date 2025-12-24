"""
Tests for 4-Plane Cognitive Model enforcement.

These tests verify:
1. PlaneAVisualModel forbids explanatory text
2. PlaneBNarrativeModel requires 300+ words
3. PlaneCFactModel forbids narrative content
4. PlaneDPreferenceModel forbids extended narrative
5. Cross-plane content is detected and rejected
6. PlaneViolationError is raised on violations
"""

import pytest
from pydantic import ValidationError
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
    PersonaScore
)
from backend.domain.plane_validator import (
    PlaneValidator,
    ViolationType,
    create_validated_chapter
)


class TestPlaneAVisualModel:
    """Tests for Plane A - Visual Intelligence."""
    
    def test_valid_chart_creation(self):
        """Plane A accepts valid chart configurations."""
        plane = PlaneAVisualModel(
            charts=[
                ChartConfig(
                    chart_type="bar",
                    title="Price Comparison",  # Short title - OK
                    data=[
                        VisualDataPoint(label="This", value=100),
                        VisualDataPoint(label="That", value=80)
                    ]
                )
            ],
            data_source_ids=["price_registry_1"]
        )
        
        assert plane.plane == "A"
        assert len(plane.charts) == 1
        assert not plane.not_applicable
    
    def test_rejects_long_chart_titles(self):
        """Plane A rejects charts with explanatory text as titles."""
        with pytest.raises(ValidationError):
            PlaneAVisualModel(
                charts=[
                    ChartConfig(
                        chart_type="bar",
                        # This title is too long - it's explanatory text
                        title="This chart shows the detailed comparison between property prices in the neighborhood with various factors taken into account",
                        data=[VisualDataPoint(label="Test", value=50)]
                    )
                ]
            )
    
    def test_not_applicable_state(self):
        """Plane A can be marked as not applicable."""
        plane = PlaneAVisualModel(
            charts=[],
            not_applicable=True,
            not_applicable_reason="No visual data available for this chapter"
        )
        
        assert plane.not_applicable is True
        assert plane.not_applicable_reason is not None


class TestPlaneBNarrativeModel:
    """Tests for Plane B - Narrative Reasoning."""
    
    def test_valid_narrative_creation(self):
        """Plane B accepts valid narrative content."""
        narrative_text = " ".join(["word"] * 350)  # 350 words
        
        plane = PlaneBNarrativeModel(
            narrative_text=narrative_text,
            word_count=350,
            ai_generated=True,
            ai_provider="test_provider"
        )
        
        assert plane.plane == "B"
        assert plane.word_count == 350
        assert plane.validate_word_count(300) is True
    
    def test_validates_minimum_word_count(self):
        """Plane B validates minimum word count via validate_word_count method."""
        # This has enough characters but not enough words
        short_narrative = "a" * 150  # 150 characters, but only ~1 word
        
        plane = PlaneBNarrativeModel(
            narrative_text=short_narrative,
            word_count=1,
            ai_generated=True
        )
        
        assert plane.validate_word_count(300) is False
    
    def test_rejects_very_short_narrative(self):
        """Plane B rejects narrative text that's too short (< 100 chars)."""
        with pytest.raises(ValidationError):
            PlaneBNarrativeModel(
                narrative_text="Too short",
                word_count=2,
                ai_generated=True
            )
    
    def test_rejects_kpi_dumps(self):
        """Plane B rejects content that looks like KPI dumps."""
        # This looks like a KPI dump - multiple lines with Label: Value format
        kpi_dump = """
        Price: €450.000
        Area: 120m²
        Year: 1985
        Energy: A++
        Rooms: 5
        """
        
        with pytest.raises(ValidationError):
            PlaneBNarrativeModel(
                narrative_text=kpi_dump,
                word_count=10,
                ai_generated=True
            )


class TestPlaneCFactModel:
    """Tests for Plane C - Factual Anchor."""
    
    def test_valid_kpi_creation(self):
        """Plane C accepts valid KPIs."""
        plane = PlaneCFactModel(
            kpis=[
                FactualKPI(
                    key="asking_price",
                    label="Vraagprijs",
                    value=450000,
                    unit="€",
                    provenance="fact"
                )
            ],
            data_sources=["funda_scrape"]
        )
        
        assert plane.plane == "C"
        assert len(plane.kpis) == 1
    
    def test_rejects_narrative_in_kpi_values(self):
        """Plane C rejects KPIs containing narrative content."""
        with pytest.raises(ValidationError):
            PlaneCFactModel(
                kpis=[
                    FactualKPI(
                        key="description",
                        label="Description",
                        # This value is too long - it's narrative content
                        value="Dit is een uitgebreide beschrijving van de woning die veel meer dan 200 tekens bevat en eigenlijk thuishoort in Plane B waar de narratieve duiding plaatsvindt. Deze lange tekst bevat interpretatie en contextualizing van de data wat niet hoort in het feitelijke ankerplane.",
                        provenance="fact"
                    )
                ]
            )
    
    def test_handles_missing_data(self):
        """Plane C properly tracks missing data."""
        plane = PlaneCFactModel(
            kpis=[],
            missing_data=["vve_bijdrage", "gemeente_belasting"],
            uncertainties=["energy_label: source uncertain"]
        )
        
        assert len(plane.missing_data) == 2
        assert len(plane.uncertainties) == 1


class TestPlaneDPreferenceModel:
    """Tests for Plane D - Human Preference."""
    
    def test_valid_persona_creation(self):
        """Plane D accepts valid persona data."""
        plane = PlaneDPreferenceModel(
            marcel=PersonaScore(
                match_score=78.5,
                mood="positive",
                key_values=["strategie", "techniek"],
                concerns=["prijs"]
            ),
            petra=PersonaScore(
                match_score=82.0,
                mood="positive",
                key_values=["sfeer", "comfort"]
            ),
            overlap_points=["locatie", "rustige buurt"],
            tension_points=["indeling"]
        )
        
        assert plane.plane == "D"
        assert plane.marcel.match_score == 78.5
        assert plane.petra.match_score == 82.0
    
    def test_rejects_long_synthesis(self):
        """Plane D rejects joint synthesis that's too long (> 500 chars)."""
        # Create a synthesis that's too long (> 500 chars)
        long_synthesis = "x" * 600
        
        with pytest.raises(ValidationError):
            PlaneDPreferenceModel(
                marcel=PersonaScore(),
                petra=PersonaScore(),
                joint_synthesis=long_synthesis
            )


class TestPlaneValidator:
    """Tests for cross-plane validation."""
    
    def test_detects_insufficient_narrative(self):
        """Validator detects narrative below minimum word count."""
        # Create a valid narrative that's long enough in chars but short in words
        short_word_content = "a" * 150  # Enough characters but only 1 "word"
        
        chapter = ChapterPlaneComposition(
            chapter_id=5,
            chapter_title="Short Chapter",
            plane_a=PlaneAVisualModel(charts=[], not_applicable=True),
            plane_b=PlaneBNarrativeModel(
                narrative_text=short_word_content,
                word_count=1,  # Only 1 word
                ai_generated=True
            ),
            plane_c=PlaneCFactModel(kpis=[]),
            plane_d=PlaneDPreferenceModel(marcel=PersonaScore(), petra=PersonaScore())
        )
        
        validator = PlaneValidator()
        violations = validator.validate_chapter(chapter)
        
        word_count_violations = [v for v in violations if v.violation_type == ViolationType.INSUFFICIENT_NARRATIVE]
        assert len(word_count_violations) == 1
        assert "1 words" in word_count_violations[0].description
    
    def test_enforce_or_reject_raises_on_violation(self):
        """enforce_or_reject raises PlaneViolationError on violations."""
        # Create a valid narrative that's long enough in chars but short in words
        short_word_content = "a" * 150  # Enough characters but only 1 "word"
        
        chapter = ChapterPlaneComposition(
            chapter_id=3,
            chapter_title="Bad Chapter",
            plane_a=PlaneAVisualModel(charts=[], not_applicable=True),
            plane_b=PlaneBNarrativeModel(
                narrative_text=short_word_content,
                word_count=1,  # Only 1 word - triggers insufficient narrative
                ai_generated=True
            ),
            plane_c=PlaneCFactModel(kpis=[]),
            plane_d=PlaneDPreferenceModel(marcel=PersonaScore(), petra=PersonaScore())
        )
        
        validator = PlaneValidator()
        
        with pytest.raises(PlaneViolationError) as exc_info:
            validator.enforce_or_reject(chapter)
        
        assert "PLANE VIOLATION ERROR" in str(exc_info.value)
    
    def test_valid_chapter_passes_validation(self):
        """A properly structured chapter passes all validation."""
        valid_narrative = " ".join(["word"] * 350)  # 350 words
        
        chapter = ChapterPlaneComposition(
            chapter_id=7,
            chapter_title="Valid Chapter",
            plane_a=PlaneAVisualModel(
                charts=[
                    ChartConfig(
                        chart_type="bar",
                        title="Comparison",
                        data=[VisualDataPoint(label="A", value=50)]
                    )
                ],
                data_source_ids=["registry_id_1"]
            ),
            plane_b=PlaneBNarrativeModel(
                narrative_text=valid_narrative,
                word_count=350,
                ai_generated=True
            ),
            plane_c=PlaneCFactModel(
                kpis=[
                    FactualKPI(
                        key="price",
                        label="Price",
                        value=500000,
                        provenance="fact"
                    )
                ]
            ),
            plane_d=PlaneDPreferenceModel(
                marcel=PersonaScore(match_score=80),
                petra=PersonaScore(match_score=75),
                overlap_points=["location"]
            )
        )
        
        validator = PlaneValidator()
        violations = validator.validate_chapter(chapter)
        
        # No violations for valid chapter
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) == 0


class TestChapterPlaneComposition:
    """Tests for complete chapter composition."""
    
    def test_chapter_0_requires_500_words(self):
        """Chapter 0 (Executive Summary) requires 500+ words."""
        short_narrative = " ".join(["word"] * 400)  # 400 words - too short for chapter 0
        
        chapter = ChapterPlaneComposition(
            chapter_id=0,
            chapter_title="Executive Summary",
            plane_a=PlaneAVisualModel(charts=[], not_applicable=True),
            plane_b=PlaneBNarrativeModel(
                narrative_text=short_narrative,
                word_count=400,
                ai_generated=True
            ),
            plane_c=PlaneCFactModel(kpis=[]),
            plane_d=PlaneDPreferenceModel(marcel=PersonaScore(), petra=PersonaScore())
        )
        
        validator = PlaneValidator()
        violations = validator.validate_chapter(chapter)
        
        # Should fail because chapter 0 needs 500+ words
        word_count_violations = [v for v in violations if v.violation_type == ViolationType.INSUFFICIENT_NARRATIVE]
        assert len(word_count_violations) == 1
        assert "500" in word_count_violations[0].description
    
    def test_all_planes_required(self):
        """All four planes must be populated or marked not_applicable."""
        valid_narrative = " ".join(["word"] * 350)
        
        # This should work - all planes present
        chapter = ChapterPlaneComposition(
            chapter_id=5,
            chapter_title="Complete Chapter",
            plane_a=PlaneAVisualModel(charts=[], not_applicable=True),
            plane_b=PlaneBNarrativeModel(
                narrative_text=valid_narrative,
                word_count=350,
                ai_generated=True
            ),
            plane_c=PlaneCFactModel(kpis=[]),
            plane_d=PlaneDPreferenceModel(
                marcel=PersonaScore(),
                petra=PersonaScore(),
                not_applicable=True
            )
        )
        
        assert chapter.plane_a is not None
        assert chapter.plane_b is not None
        assert chapter.plane_c is not None
        assert chapter.plane_d is not None


class TestCreateValidatedChapter:
    """Tests for the validated chapter creation function."""
    
    def test_creates_valid_chapter(self):
        """create_validated_chapter succeeds for valid content."""
        valid_narrative = " ".join(["word"] * 350)
        
        chapter = create_validated_chapter(
            chapter_id=4,
            chapter_title="Validated Chapter",
            plane_a=PlaneAVisualModel(charts=[], not_applicable=True),
            plane_b=PlaneBNarrativeModel(
                narrative_text=valid_narrative,
                word_count=350,
                ai_generated=True
            ),
            plane_c=PlaneCFactModel(kpis=[]),
            plane_d=PlaneDPreferenceModel(marcel=PersonaScore(), petra=PersonaScore())
        )
        
        assert chapter.chapter_id == 4
        assert chapter.chapter_title == "Validated Chapter"
    
    def test_raises_on_invalid_content(self):
        """create_validated_chapter raises on violations."""
        # Create content that passes model validation but fails plane validation
        short_word_content = "a" * 150  # Enough chars but only 1 word
        
        with pytest.raises(PlaneViolationError):
            create_validated_chapter(
                chapter_id=6,
                chapter_title="Invalid Chapter",
                plane_a=PlaneAVisualModel(charts=[], not_applicable=True),
                plane_b=PlaneBNarrativeModel(
                    narrative_text=short_word_content,
                    word_count=1,  # Triggers insufficient narrative validation
                    ai_generated=True
                ),
                plane_c=PlaneCFactModel(kpis=[]),
                plane_d=PlaneDPreferenceModel(marcel=PersonaScore(), petra=PersonaScore())
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
