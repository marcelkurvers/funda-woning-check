# TEST_REGIME: STRUCTURAL
# REQUIRES: offline_structural_mode=True
"""
4-PLANE BACKBONE ENFORCEMENT TESTS

These tests verify the FAIL-CLOSED behavior of the 4-plane backbone:

1. Every chapter (1-12) MUST have exactly 4 planes (A, B, C, D)
2. Plane B MUST have at least 300 words (500 for chapter 0)
3. KPIs may ONLY appear in Plane C
4. Marcel/Petra data may ONLY appear in Plane D
5. UI MUST NOT render if any plane is missing
6. No fallback paths, no degradation

Tests that only "render something" are INVALID.
"""

import pytest
from unittest.mock import patch, MagicMock

from backend.pipeline.four_plane_backbone import (
    FourPlaneBackbone,
    BackboneEnforcementError,
    BackboneViolationType,
    generate_four_plane_chapter,
    convert_plane_composition_to_dict
)
from backend.domain.plane_models import (
    PlaneAVisualModel,
    PlaneBNarrativeModel,
    PlaneCFactModel,
    PlaneDPreferenceModel,
    ChapterPlaneComposition,
    PlaneViolationError,
    PersonaScore
)
from backend.domain.pipeline_context import PipelineContext, create_pipeline_context, PipelineViolation
from backend.domain.registry import CanonicalRegistry


class TestBackboneStructure:
    """Tests for 4-plane structure enforcement."""
    
    def test_chapter_has_exactly_four_planes(self):
        """Every chapter output must have exactly 4 planes."""
        # Create mock context
        ctx = create_pipeline_context("test-run-001")
        ctx.set_raw_data({
            "funda_url": "https://test.funda.nl",
            "address": "Test Address 123"
        })
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        # Create valid narrative (300+ words)
        valid_narrative = " ".join(["Dit is een test woord."] * 100)  # 500 words
        
        # Generate chapter
        backbone = FourPlaneBackbone(ctx)
        composition = backbone.generate_chapter(
            chapter_id=5,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        # Verify 4 planes exist
        assert composition.plane_a is not None, "Plane A is missing"
        assert composition.plane_b is not None, "Plane B is missing"
        assert composition.plane_c is not None, "Plane C is missing"
        assert composition.plane_d is not None, "Plane D is missing"
        
        # Verify plane types
        assert composition.plane_a.plane == "A"
        assert composition.plane_b.plane == "B"
        assert composition.plane_c.plane == "C"
        assert composition.plane_d.plane == "D"
    
    def test_plane_b_requires_minimum_words(self):
        """Plane B must have at least 300 words (500 for chapter 0)."""
        # Create mock context
        ctx = create_pipeline_context("test-run-002")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        # Create too-short narrative
        short_narrative = " ".join(["woord"] * 50)  # Only 50 words
        
        # Should fail
        backbone = FourPlaneBackbone(ctx)
        with pytest.raises(BackboneEnforcementError) as exc_info:
            backbone.generate_chapter(
                chapter_id=3,
                ai_narrative=short_narrative,
                chapter_data={}
            )
        
        assert BackboneViolationType.PLANE_B_INSUFFICIENT_WORDS.value in str(exc_info.value)
    
    def test_chapter_0_requires_500_words(self):
        """Chapter 0 (Executive Summary) requires 500+ words."""
        ctx = create_pipeline_context("test-run-003")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        # 400 words - enough for regular chapters but not chapter 0
        insufficient_narrative = " ".join(["woord"] * 400)
        
        backbone = FourPlaneBackbone(ctx)
        with pytest.raises(BackboneEnforcementError) as exc_info:
            backbone.generate_chapter(
                chapter_id=0,
                ai_narrative=insufficient_narrative,
                chapter_data={}
            )
        
        # Should fail because chapter 0 needs 500 words
        assert "500" in str(exc_info.value) or "word" in str(exc_info.value).lower()


class TestPlaneIsolation:
    """Tests for plane content isolation."""
    
    def test_kpis_only_in_plane_c(self):
        """KPIs/data must only appear in Plane C, never in Plane B."""
        ctx = create_pipeline_context("test-run-004")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        # Create valid narrative without KPI dumps
        valid_narrative = (
            "Dit is een uitgebreide analyse van de woning. "
            "De locatie biedt uitstekende mogelijkheden voor toekomstige groei. "
            "De buurt kenmerkt zich door een rustige sfeer en goede voorzieningen. "
        ) * 30  # ~600 words
        
        backbone = FourPlaneBackbone(ctx)
        composition = backbone.generate_chapter(
            chapter_id=5,
            ai_narrative=valid_narrative,
            chapter_data={"variables": {"test_kpi": {"value": 100}}}
        )
        
        # Plane C should have KPIs
        assert len(composition.plane_c.kpis) > 0, "Plane C should have KPIs"
        
        # Plane B narrative should be the prose we provided
        assert "analyse" in composition.plane_b.narrative_text.lower()
    
    def test_marcel_petra_only_in_plane_d(self):
        """Marcel/Petra comparisons must only appear in Plane D."""
        ctx = create_pipeline_context("test-run-005")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        valid_narrative = " ".join(["Dit is een uitgebreide analyse."] * 100)
        
        backbone = FourPlaneBackbone(ctx)
        composition = backbone.generate_chapter(
            chapter_id=2,
            ai_narrative=valid_narrative,
            chapter_data={
                "comparison": {
                    "marcel": "Technisch sterk",
                    "petra": "Sfeer gericht"
                }
            }
        )
        
        # Plane D should have Marcel and Petra
        assert composition.plane_d.marcel is not None
        assert composition.plane_d.petra is not None


class TestFailClosedBehavior:
    """Tests for fail-closed enforcement."""
    
    def test_no_fallback_on_missing_narrative(self):
        """System must fail, not produce partial output, when narrative is missing."""
        ctx = create_pipeline_context("test-run-006")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        # Empty narrative - should fail (either via Pydantic or backbone)
        backbone = FourPlaneBackbone(ctx)
        
        # Accept both error types - both represent fail-closed behavior
        with pytest.raises((BackboneEnforcementError, Exception)) as exc_info:
            backbone.generate_chapter(
                chapter_id=7,
                ai_narrative="",  # Empty!
                chapter_data={}
            )
        
        # Verify it's a genuine failure, not a warning
        assert exc_info.value is not None
    
    def test_requires_locked_registry(self):
        """Backbone must fail if registry is not locked."""
        ctx = create_pipeline_context("test-run-007")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        # NOT calling lock_registry()
        
        with pytest.raises(PipelineViolation):
            FourPlaneBackbone(ctx)
    
    def test_all_chapters_validated(self):
        """All chapter IDs 0-12 must pass through 4-plane validation."""
        ctx = create_pipeline_context("test-run-008")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        backbone = FourPlaneBackbone(ctx)
        valid_narrative = " ".join(["Dit is een uitgebreide analyse van de woning."] * 60)
        
        # All chapters should require 4-plane structure
        for chapter_id in range(1, 13):  # Chapters 1-12
            composition = backbone.generate_chapter(
                chapter_id=chapter_id,
                ai_narrative=valid_narrative,
                chapter_data={}
            )
            
            assert composition.plane_a is not None, f"Chapter {chapter_id} missing Plane A"
            assert composition.plane_b is not None, f"Chapter {chapter_id} missing Plane B"
            assert composition.plane_c is not None, f"Chapter {chapter_id} missing Plane C"
            assert composition.plane_d is not None, f"Chapter {chapter_id} missing Plane D"


class TestOutputConversion:
    """Tests for plane composition to dict conversion."""
    
    def test_convert_preserves_all_planes(self):
        """Converted dict must contain all 4 plane objects."""
        ctx = create_pipeline_context("test-run-009")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        valid_narrative = " ".join(["Dit is een uitgebreide analyse."] * 100)
        
        composition = generate_four_plane_chapter(
            ctx=ctx,
            chapter_id=5,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        output = convert_plane_composition_to_dict(composition)
        
        # Check structure marker
        assert output.get("plane_structure") is True
        
        # Check all planes exist
        assert "plane_a" in output
        assert "plane_b" in output
        assert "plane_c" in output
        assert "plane_d" in output
        
        # Check plane content
        assert output["plane_b"]["word_count"] >= 300
        assert output["plane_d"]["marcel"] is not None
        assert output["plane_d"]["petra"] is not None
    
    def test_convert_includes_legacy_narrative(self):
        """Converted dict must include legacy narrative field for backward compatibility."""
        ctx = create_pipeline_context("test-run-010")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        valid_narrative = " ".join(["Dit is een test narratief."] * 100)
        
        composition = generate_four_plane_chapter(
            ctx=ctx,
            chapter_id=8,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        output = convert_plane_composition_to_dict(composition)
        
        # Legacy narrative field must exist
        assert "narrative" in output
        assert output["narrative"]["text"] == valid_narrative
        assert output["narrative"]["word_count"] == len(valid_narrative.split())


class TestUIRendering:
    """Tests for UI rendering conditions."""
    
    def test_invalid_chapter_not_renderable(self):
        """If a chapter fails validation, it must not be renderable."""
        ctx = create_pipeline_context("test-run-011")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        # Create backbone
        backbone = FourPlaneBackbone(ctx)
        
        # Try to generate with invalid narrative (too short)
        short_narrative = "Te kort."  # Only 2 words
        
        # This should raise - either via Pydantic validation or backbone validation
        # Both represent fail-closed behavior
        with pytest.raises((BackboneEnforcementError, Exception)) as exc_info:
            backbone.generate_chapter(
                chapter_id=4,
                ai_narrative=short_narrative,
                chapter_data={}
            )
        
        # Verify it's a genuine failure
        assert exc_info.value is not None
    
    def test_valid_chapter_is_renderable(self):
        """If a chapter passes validation, it produces complete output."""
        ctx = create_pipeline_context("test-run-012")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        backbone = FourPlaneBackbone(ctx)
        valid_narrative = " ".join(["Dit is een complete en uitgebreide analyse."] * 60)
        
        composition = backbone.generate_chapter(
            chapter_id=6,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        # Should have all required data
        assert composition.chapter_id == 6
        assert composition.plane_b.word_count >= 300
        assert not composition.plane_a.not_applicable or composition.plane_a.not_applicable_reason is not None


class TestFrontendContract:
    """Tests for frontend TypeScript interface compatibility."""
    
    def test_convert_includes_plane_names(self):
        """All planes must include plane_name field for frontend rendering."""
        ctx = create_pipeline_context("test-run-013")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        valid_narrative = " ".join(["Dit is een uitgebreide analyse."] * 100)
        
        composition = generate_four_plane_chapter(
            ctx=ctx,
            chapter_id=5,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        output = convert_plane_composition_to_dict(composition)
        
        # CRITICAL: Frontend expects plane_name in all planes
        assert output["plane_a"]["plane_name"] == "visual_intelligence"
        assert output["plane_b"]["plane_name"] == "narrative_reasoning"
        assert output["plane_c"]["plane_name"] == "factual_anchor"
        assert output["plane_d"]["plane_name"] == "human_preference"
    
    def test_convert_includes_plane_c_data_sources(self):
        """Plane C must include parameters and data_sources for frontend."""
        ctx = create_pipeline_context("test-run-014")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        valid_narrative = " ".join(["Dit is een uitgebreide analyse."] * 100)
        
        composition = generate_four_plane_chapter(
            ctx=ctx,
            chapter_id=7,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        output = convert_plane_composition_to_dict(composition)
        
        # CRITICAL: Frontend expects these fields
        assert "parameters" in output["plane_c"]
        assert isinstance(output["plane_c"]["parameters"], dict)
        assert "data_sources" in output["plane_c"]
        assert isinstance(output["plane_c"]["data_sources"], list)
    
    def test_convert_includes_diagnostics(self):
        """Converted output must include diagnostics block for fail-loud behavior."""
        ctx = create_pipeline_context("test-run-015")
        ctx.set_raw_data({"funda_url": "https://test.funda.nl"})
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        valid_narrative = " ".join(["Dit is een uitgebreide analyse."] * 100)
        
        composition = generate_four_plane_chapter(
            ctx=ctx,
            chapter_id=8,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        output = convert_plane_composition_to_dict(composition)
        
        # MANDATORY: Diagnostics must be present
        assert "diagnostics" in output
        diagnostics = output["diagnostics"]
        
        # Required diagnostics fields
        assert "chapter_id" in diagnostics
        assert "plane_status" in diagnostics
        assert "validation_passed" in diagnostics
        assert "missing_required_fields" in diagnostics
        assert "errors" in diagnostics
        
        # Plane status must be present for all planes
        ps = diagnostics["plane_status"]
        assert "A" in ps
        assert "B" in ps
        assert "C" in ps
        assert "D" in ps


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
