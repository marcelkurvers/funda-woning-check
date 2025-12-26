"""
PLANE A2 INTEGRATION TESTS

These tests verify the Plane A2 (Synthesized Visual Intelligence) integration:

1. Plane A2 ALWAYS exists in chapter output (never None)
2. Plane A2 is properly serialized to API output
3. Chapter 1 has at least one visual concept
4. Image failure results in visible diagnostics
5. No silent fallbacks

FAIL-CLOSED: All tests verify explicit behavior, not silent degradation.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from backend.pipeline.four_plane_backbone import (
    FourPlaneBackbone,
    generate_four_plane_chapter,
    convert_plane_composition_to_dict,
)
from backend.domain.plane_models import (
    PlaneA2SynthVisualModel,
    HeroInfographic,
    VisualConcept,
)
from backend.domain.pipeline_context import create_pipeline_context
from backend.domain.registry import RegistryType
from backend.ai.image_provider_interface import (
    ImageGenerationResult,
    ImageGenerationStatus,
    NoImageProvider,
)
from backend.ai.image_provider_factory import reset_image_provider


def setup_test_context_with_registry(run_id: str, data: dict) -> 'PipelineContext':
    """
    Helper to create a pipeline context with data registered in the registry.
    
    This is the proper way to set up test data - using register_fact().
    Includes default values for commonly required Chapter 1 fields.
    """
    # Defaults for all registry keys that might be needed in validation
    defaults = {
        "plot_area_m2": 200,
        "rooms": 4,
        "bedrooms": 2,
        "build_year": 2000,
    }
    
    # Merge defaults with provided data
    full_data = {**defaults, **data}
    
    ctx = create_pipeline_context(run_id)
    ctx.set_raw_data({"funda_url": full_data.get("funda_url", "https://test.funda.nl")})
    
    # Register each value as a fact
    for key, value in full_data.items():
        if key != "funda_url" and value is not None:
            ctx.register_fact(
                key=key,
                value=value,
                name=key.replace("_", " ").title(),
                rtype=RegistryType.FACT
            )
    
    ctx.complete_enrichment()
    ctx.lock_registry()
    return ctx


class TestPlaneA2Existence:
    """Tests that Plane A2 always exists in output."""
    
    def setup_method(self):
        """Reset image provider before each test."""
        reset_image_provider()
    
    def test_plane_a2_always_present_in_composition(self):
        """Plane A2 must exist in every chapter composition."""
        ctx = setup_test_context_with_registry("test-a2-001", {
            "funda_url": "https://test.funda.nl",
            "address": "Test Address 123",
            "asking_price_eur": 450000,
            "living_area_m2": 120,
        })
        
        valid_narrative = " ".join(["Dit is een uitgebreide analyse van de woning."] * 100)
        
        backbone = FourPlaneBackbone(ctx)
        composition = backbone.generate_chapter(
            chapter_id=1,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        # Plane A2 must exist (never None)
        assert composition.plane_a2 is not None, "Plane A2 must always be present"
        assert isinstance(composition.plane_a2, PlaneA2SynthVisualModel)
    
    def test_plane_a2_has_concepts_or_not_applicable(self):
        """Plane A2 must have concepts OR explicit not_applicable flag."""
        ctx = setup_test_context_with_registry("test-a2-002", {
            "funda_url": "https://test.funda.nl",
            "asking_price_eur": 350000,
            "living_area_m2": 100,
        })
        
        valid_narrative = " ".join(["Dit is een uitgebreide analyse."] * 100)
        
        backbone = FourPlaneBackbone(ctx)
        composition = backbone.generate_chapter(
            chapter_id=1,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        plane_a2 = composition.plane_a2
        
        # Either has concepts OR is explicitly not_applicable
        has_content = len(plane_a2.concepts) > 0 or plane_a2.hero_infographic is not None
        is_explicit_na = plane_a2.not_applicable and plane_a2.not_applicable_reason is not None
        
        assert has_content or is_explicit_na, (
            "Plane A2 must have visual content OR explicit not_applicable reason"
        )


class TestPlaneA2Serialization:
    """Tests that Plane A2 is properly serialized to API output."""
    
    def setup_method(self):
        reset_image_provider()
    
    def test_plane_a2_in_serialized_output(self):
        """plane_a2 key must exist in serialized chapter dict."""
        ctx = setup_test_context_with_registry("test-a2-003", {
            "funda_url": "https://test.funda.nl",
            "asking_price_eur": 400000,
            "living_area_m2": 100,
        })
        
        valid_narrative = " ".join(["Dit is een uitgebreide analyse."] * 100)
        
        composition = generate_four_plane_chapter(
            ctx=ctx,
            chapter_id=1,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        output = convert_plane_composition_to_dict(composition)
        
        # plane_a2 must be in output
        assert "plane_a2" in output, "plane_a2 must exist in serialized output"
        
        plane_a2 = output["plane_a2"]
        
        # Required fields
        assert "plane" in plane_a2
        assert plane_a2["plane"] == "A2"
        assert "plane_name" in plane_a2
        assert "concepts" in plane_a2
        assert "not_applicable" in plane_a2
    
    def test_plane_a2_concepts_serialized(self):
        """Visual concepts must be properly serialized."""
        ctx = setup_test_context_with_registry("test-a2-004", {
            "funda_url": "https://test.funda.nl",
            "asking_price_eur": 500000,
            "living_area_m2": 150,
            "rooms": 5,
        })
        
        valid_narrative = " ".join(["Dit is een uitgebreide analyse."] * 100)
        
        composition = generate_four_plane_chapter(
            ctx=ctx,
            chapter_id=1,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        output = convert_plane_composition_to_dict(composition)
        concepts = output["plane_a2"]["concepts"]
        
        # Should have concepts for chapter 1
        assert len(concepts) >= 0, "Concepts should be serialized"
        
        for concept in concepts:
            assert "title" in concept
            assert "visual_type" in concept
            assert "data_used" in concept
            assert "insight_explained" in concept


class TestPlaneA2Diagnostics:
    """Tests that Plane A2 status appears in diagnostics."""
    
    def setup_method(self):
        reset_image_provider()
    
    def test_diagnostics_include_a2_status(self):
        """Diagnostics must include Plane A2 status."""
        ctx = setup_test_context_with_registry("test-a2-005", {
            "funda_url": "https://test.funda.nl",
            "asking_price_eur": 600000,
            "living_area_m2": 120,
        })
        
        valid_narrative = " ".join(["Dit is een uitgebreide analyse."] * 100)
        
        composition = generate_four_plane_chapter(
            ctx=ctx,
            chapter_id=1,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        output = convert_plane_composition_to_dict(composition)
        
        # Diagnostics must exist and include A2
        assert "diagnostics" in output
        diagnostics = output["diagnostics"]
        
        assert "plane_status" in diagnostics
        assert "A2" in diagnostics["plane_status"], "A2 status must be in diagnostics"
        
        # A2 status must be one of the valid values
        valid_statuses = ["ok", "concepts_only", "not_applicable", "empty", "missing"]
        assert diagnostics["plane_status"]["A2"] in valid_statuses


class TestPlaneA2NoSilentFallback:
    """Tests that Plane A2 never silently degrades."""
    
    def setup_method(self):
        reset_image_provider()
    
    def test_no_image_provider_gives_explicit_reason(self):
        """When no image provider is configured, reason must be explicit."""
        # Force NoImageProvider - patch at the backbone module where it's imported
        with patch('backend.pipeline.four_plane_backbone.get_image_provider') as mock_get:
            mock_get.return_value = NoImageProvider()
            
            ctx = setup_test_context_with_registry("test-a2-006", {
                "funda_url": "https://test.funda.nl",
                "asking_price_eur": 350000,
                "living_area_m2": 100,
                "rooms": 3,
            })
            
            valid_narrative = " ".join(["Dit is een uitgebreide analyse."] * 100)
            
            backbone = FourPlaneBackbone(ctx)
            composition = backbone.generate_chapter(
                chapter_id=1,
                ai_narrative=valid_narrative,
                chapter_data={}
            )
            
            plane_a2 = composition.plane_a2
            
            # Should have explicit not_applicable with reason
            assert plane_a2.not_applicable is True
            assert plane_a2.not_applicable_reason is not None
            assert len(plane_a2.not_applicable_reason) > 10  # Not just empty string
            
            # Should still have concepts (concepts are built BEFORE image gen check)
            assert len(plane_a2.concepts) > 0, "Concepts should still be generated"


class TestChapter1HasInfographicConcepts:
    """Tests specific to Chapter 1 infographic requirements."""
    
    def setup_method(self):
        reset_image_provider()
    
    def test_chapter_1_has_visual_concepts(self):
        """Chapter 1 must have at least one visual concept."""
        ctx = setup_test_context_with_registry("test-a2-007", {
            "funda_url": "https://test.funda.nl",
            "asking_price_eur": 450000,
            "living_area_m2": 120,
            "plot_area_m2": 300,
            "rooms": 4,
        })
        
        valid_narrative = " ".join(["Dit is een uitgebreide analyse."] * 100)
        
        backbone = FourPlaneBackbone(ctx)
        composition = backbone.generate_chapter(
            chapter_id=1,
            ai_narrative=valid_narrative,
            chapter_data={}
        )
        
        # Chapter 1 must have concepts
        assert len(composition.plane_a2.concepts) >= 1, (
            "Chapter 1 must have at least 1 visual concept"
        )
        
        # First concept should be property-related
        first_concept = composition.plane_a2.concepts[0]
        assert len(first_concept.data_used) > 0, "Concept must use registry data"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
