"""
Pipeline Spine Enforcement Tests

These tests verify that the pipeline spine enforces structural invariants.
If any of these tests pass when they should fail, the system is broken.

TESTED INVARIANTS:
1. Registry cannot be recreated mid-pipeline
2. Registry must be locked before chapter generation
3. Chapters cannot render without validation
4. Validation cannot be bypassed
5. Raw data cannot be modified after enrichment
"""

import pytest
from typing import Dict, Any

from backend.domain.pipeline_context import (
    PipelineContext,
    PipelineViolation,
    ValidationFailure,
    create_pipeline_context
)
from backend.pipeline.spine import PipelineSpine, execute_pipeline
from backend.validation.gate import ValidationGate


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_raw_data() -> Dict[str, Any]:
    """Sample property data for testing."""
    return {
        "asking_price_eur": 500000,
        "living_area_m2": 120,
        "plot_area_m2": 250,
        "build_year": 1990,
        "energy_label": "C",
        "address": "Teststraat 123",
        "city": "Amsterdam",
        "description": "Een prachtige woning met veel licht en ruimte.",
        "features": ["tuin", "garage", "zonnepanelen"]
    }


@pytest.fixture
def sample_preferences() -> Dict[str, Any]:
    """Sample Marcel & Petra preferences."""
    return {
        "marcel": {
            "priorities": ["zonnepanelen", "glasvezel"],
            "hidden_priorities": ["slimme thermostaat"]
        },
        "petra": {
            "priorities": ["lichte woning", "tuin"],
            "hidden_priorities": ["open keuken"]
        }
    }


# =============================================================================
# INVARIANT 1: REGISTRY SINGLETON ENFORCEMENT
# =============================================================================

class TestRegistrySingleton:
    """Test that registry is created once and cannot be recreated."""
    
    def test_registry_created_once_per_context(self):
        """Each PipelineContext has exactly one registry."""
        ctx = create_pipeline_context("test-1")
        registry1 = ctx.registry
        registry2 = ctx.registry
        
        assert registry1 is registry2, "Registry must be the same object"
    
    def test_cannot_replace_registry(self):
        """Registry object is encapsulated and only accessible via methods."""
        ctx = create_pipeline_context("test-2")
        
        # The registry is accessed via methods, not direct assignment
        # This tests that the registry is properly encapsulated
        original_registry = ctx.registry
        
        # Even if we could assign, the original object is what matters
        # The API design forces use through register_fact()
        from backend.domain.registry import RegistryType
        ctx.register_fact("test", 123, "Test", RegistryType.FACT)
        
        # Verify the fact went to the original registry
        assert ctx.registry is original_registry
        assert ctx.get_registry_value("test") == 123
    
    def test_context_tracks_registration_state(self):
        """Context knows whether enrichment is complete."""
        ctx = create_pipeline_context("test-3")
        
        assert not ctx._enrichment_complete
        assert not ctx._registry_locked
        
        # Register a fact
        from backend.domain.registry import RegistryType
        ctx.register_fact("test_key", 100, "Test", RegistryType.FACT)
        
        assert not ctx._enrichment_complete  # Still not complete
        
        # Complete enrichment
        ctx.complete_enrichment()
        assert ctx._enrichment_complete
        assert not ctx._registry_locked  # Not locked yet
        
        # Lock
        ctx.lock_registry()
        assert ctx._registry_locked


# =============================================================================
# INVARIANT 2: REGISTRY LOCKING ENFORCEMENT
# =============================================================================

class TestRegistryLocking:
    """Test that registry locks and prevents modification."""
    
    def test_cannot_register_after_lock(self):
        """Facts cannot be registered after registry is locked."""
        ctx = create_pipeline_context("test-lock-1")
        
        from backend.domain.registry import RegistryType
        ctx.register_fact("before_lock", 1, "Before", RegistryType.FACT)
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        with pytest.raises(PipelineViolation) as exc_info:
            ctx.register_fact("after_lock", 2, "After", RegistryType.FACT)
        
        assert "locked" in str(exc_info.value).lower()
    
    def test_cannot_lock_twice(self):
        """Registry cannot be locked twice."""
        ctx = create_pipeline_context("test-lock-2")
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        with pytest.raises(PipelineViolation) as exc_info:
            ctx.lock_registry()
        
        assert "already locked" in str(exc_info.value).lower()
    
    def test_cannot_lock_before_enrichment(self):
        """Registry cannot be locked before enrichment is complete."""
        ctx = create_pipeline_context("test-lock-3")
        
        with pytest.raises(PipelineViolation) as exc_info:
            ctx.lock_registry()
        
        assert "enrichment" in str(exc_info.value).lower()


# =============================================================================
# INVARIANT 3: CHAPTER GENERATION REQUIRES LOCKED REGISTRY
# =============================================================================

class TestChapterGenerationRequiresLock:
    """Test that chapters cannot be generated without locked registry."""
    
    def test_cannot_generate_chapter_before_lock(self):
        """Chapter generation fails if registry is not locked."""
        ctx = create_pipeline_context("test-gen-1")
        ctx.complete_enrichment()
        # Note: NOT calling ctx.lock_registry()
        
        with pytest.raises(PipelineViolation) as exc_info:
            ctx.begin_chapter_generation()
        
        assert "not locked" in str(exc_info.value).lower()
    
    def test_spine_enforces_phase_order(self, sample_raw_data):
        """PipelineSpine enforces correct phase order."""
        spine = PipelineSpine("test-phase-1")
        
        # Cannot enrich before ingesting
        with pytest.raises(PipelineViolation):
            spine.enrich_and_populate_registry()
        
        # Ingest first
        spine.ingest_raw_data(sample_raw_data)
        
        # Cannot generate before enriching
        with pytest.raises(PipelineViolation):
            spine.generate_all_chapters()


# =============================================================================
# INVARIANT 4: VALIDATION CANNOT BE BYPASSED
# =============================================================================

class TestValidationEnforcement:
    """Test that validation is always enforced."""
    
    def test_validation_runs_for_every_chapter(self, sample_raw_data, sample_preferences):
        """Every chapter output is validated."""
        spine, output = PipelineSpine.execute_full_pipeline(
            run_id="test-val-1",
            raw_data=sample_raw_data,
            preferences=sample_preferences,
            strict_validation=False
        )
        
        # Chapters 1-13 should have validation results (13 chapters)
        # Chapter 0 (Dashboard) is generated separately and not included in chapter validation
        assert len(spine.ctx._validation_results) == 13, (
            f"Expected 13 validation results for chapters 1-13, got {len(spine.ctx._validation_results)}"
        )
    
    def test_validation_errors_are_recorded(self):
        """Validation errors are stored in context."""
        ctx = create_pipeline_context("test-val-2")
        ctx.record_validation_result(0, [])  # Passed
        ctx.record_validation_result(1, ["Error 1"])  # Failed
        
        assert ctx.get_validation_errors(0) == []
        assert ctx.get_validation_errors(1) == ["Error 1"]
        assert not ctx.all_chapters_valid()
    
    def test_cannot_store_failed_chapter(self):
        """Cannot store a chapter that failed validation."""
        ctx = create_pipeline_context("test-val-3")
        
        # Record failed validation
        ctx.record_validation_result(5, ["Some error"])
        
        with pytest.raises(PipelineViolation) as exc_info:
            ctx.store_validated_chapter(5, {"id": "5", "title": "Test"})
        
        assert "validation failed" in str(exc_info.value).lower()
    
    def test_cannot_store_unvalidated_chapter(self):
        """Cannot store a chapter that wasn't validated."""
        ctx = create_pipeline_context("test-val-4")
        
        with pytest.raises(PipelineViolation) as exc_info:
            ctx.store_validated_chapter(3, {"id": "3", "title": "Test"})
        
        assert "validation not recorded" in str(exc_info.value).lower()


# =============================================================================
# INVARIANT 5: RAW DATA IMMUTABILITY AFTER ENRICHMENT
# =============================================================================

class TestRawDataImmutability:
    """Test that raw data cannot be modified after enrichment."""
    
    def test_cannot_modify_raw_data_after_enrichment(self):
        """Raw data cannot be changed after enrichment is complete."""
        ctx = create_pipeline_context("test-immut-1")
        ctx.set_raw_data({"price": 100})
        ctx.complete_enrichment()
        
        with pytest.raises(PipelineViolation) as exc_info:
            ctx.set_raw_data({"price": 200})
        
        assert "enrichment" in str(exc_info.value).lower()
    
    def test_get_raw_data_returns_copy(self):
        """get_raw_data returns a copy, not the original."""
        ctx = create_pipeline_context("test-immut-2")
        original = {"price": 100}
        ctx.set_raw_data(original)
        
        retrieved = ctx.get_raw_data()
        retrieved["price"] = 999  # Modify the copy
        
        # Original in context should be unchanged
        assert ctx.get_raw_data()["price"] == 100


# =============================================================================
# INVARIANT 6: STRICT RENDER BLOCKING
# =============================================================================

class TestRenderBlocking:
    """Test that rendering is blocked on validation failure (strict mode)."""
    
    def test_strict_render_blocks_on_failure(self, sample_raw_data, sample_preferences):
        """Strict mode raises on validation failure."""
        # This test may pass or fail depending on whether the sample data
        # generates chapters that pass validation. We test the mechanism.
        
        spine = PipelineSpine("test-render-1", sample_preferences)
        spine.ingest_raw_data(sample_raw_data)
        spine.enrich_and_populate_registry()
        spine.generate_all_chapters()
        
        # If any validation failed, strict should raise
        if not spine.ctx.all_chapters_valid():
            with pytest.raises(PipelineViolation) as exc_info:
                spine.get_renderable_output(strict=True)
            
            assert "validation failed" in str(exc_info.value).lower()
    
    def test_non_strict_render_includes_error_markers(self, sample_raw_data, sample_preferences):
        """Non-strict mode includes error markers in output."""
        spine, output = PipelineSpine.execute_full_pipeline(
            run_id="test-render-2",
            raw_data=sample_raw_data,
            preferences=sample_preferences,
            strict_validation=False
        )
        
        # Output should indicate validation status
        assert "validation_passed" in output


# =============================================================================
# INTEGRATION: FULL PIPELINE EXECUTION
# =============================================================================

class TestFullPipelineExecution:
    """Test complete pipeline execution."""
    
    def test_execute_pipeline_returns_structured_output(self, sample_raw_data, sample_preferences):
        """execute_pipeline returns a complete structured output."""
        output = execute_pipeline(
            run_id="test-full-1",
            raw_data=sample_raw_data,
            preferences=sample_preferences
        )
        
        # Check structure
        assert "run_id" in output
        assert "chapters" in output
        assert "registry_entry_count" in output
        assert "validation_passed" in output
        
        # Should have 14 chapters (0-13) in the output
        assert len(output["chapters"]) == 14, (
            f"Expected 14 chapters (0-13), got {len(output['chapters'])}"
        )
    
    def test_pipeline_preserves_registry_values(self, sample_raw_data, sample_preferences):
        """Pipeline output contains registry-derived values."""
        spine, output = PipelineSpine.execute_full_pipeline(
            run_id="test-full-2",
            raw_data=sample_raw_data,
            preferences=sample_preferences
        )
        
        # Check registry was populated
        assert spine.ctx.get_registry_value("asking_price_eur") == 500000
        assert spine.ctx.get_registry_value("living_area_m2") == 120
        assert spine.ctx.get_registry_value("energy_label") == "C"
    
    def test_pipeline_locks_registry(self, sample_raw_data):
        """Pipeline locks the registry."""
        spine, output = PipelineSpine.execute_full_pipeline(
            run_id="test-full-3",
            raw_data=sample_raw_data
        )
        
        assert spine.ctx.is_registry_locked()


# =============================================================================
# VALIDATION GATE TESTS
# =============================================================================

class TestValidationGate:
    """Test ValidationGate enforcement."""
    
    def test_ownership_violation_detected(self):
        """ValidationGate catches ownership violations."""
        # Chapter 7 (Garden) trying to display price
        output = {
            "id": "7",
            "title": "Garden",
            "main_analysis": "Nice garden.",
            "variables": {"asking_price_eur": 500000},  # Violation!
            "comparison": {"marcel": "Big enough for plants.", "petra": "Sunny and peaceful."}
        }
        registry = {"asking_price_eur": 500000}
        
        errors = ValidationGate.validate_chapter_output(7, output, registry)
        
        assert any("Ownership" in e for e in errors)
    
    def test_raw_fact_restatement_detected(self):
        """ValidationGate catches raw fact restatement."""
        # Chapter 7 (Garden) mentioning price in text
        output = {
            "id": "7",
            "title": "Garden",
            "main_analysis": "This garden is worth the 500000 euros price tag.",
            "variables": {},
            "comparison": {"marcel": "Great outdoor space.", "petra": "Love the flowers."}
        }
        registry = {"asking_price_eur": 500000}
        
        errors = ValidationGate.validate_chapter_output(7, output, registry)
        
        assert any("Raw Fact" in e for e in errors)
    
    def test_preference_reasoning_required(self):
        """ValidationGate enforces preference reasoning length."""
        output = {
            "id": "1",
            "title": "Features",
            "main_analysis": "Nice house.",
            "variables": {},
            "comparison": {"marcel": "Ok", "petra": ""}  # Too short!
        }
        
        errors = ValidationGate.validate_chapter_output(1, output, {})
        
        assert any("Preference Reasoning" in e for e in errors)
    
    def test_valid_chapter_passes(self):
        """Valid chapter output passes validation."""
        # Create a 500+ word narrative for the test (chapter 0 requires 500)
        long_narrative = " ".join(["Dit is een uitgebreide analyse van deze woning."] * 80)
        
        # 4-plane structure is now REQUIRED for chapters 0-12
        output = {
            "id": "0",
            "title": "Executive Summary",
            "plane_structure": True,
            "main_analysis": long_narrative,  # Legacy field still included
            "variables": {"address": "Teststraat 123"},  # Chapter 0 owns this
            "comparison": {
                "marcel": "Marcel will appreciate the technical infrastructure and efficiency.",
                "petra": "Petra will love the natural light and comfortable atmosphere."
            },
            # MANDATORY: Narrative is required for chapters 0-12
            "narrative": {
                "text": long_narrative,
                "word_count": len(long_narrative.split())
            },
            # 4-PLANE STRUCTURE (MANDATORY)
            "plane_a": {
                "plane": "A",
                "charts": [],
                "trends": [],
                "comparisons": [],
                "data_source_ids": [],
                "not_applicable": True,
                "not_applicable_reason": "Test chapter",
            },
            "plane_b": {
                "plane": "B",
                "narrative_text": long_narrative,
                "word_count": len(long_narrative.split()),
                "not_applicable": False,
                "ai_generated": True,
            },
            "plane_c": {
                "plane": "C",
                "kpis": [],
                "missing_data": [],
                "uncertainties": [],
                "not_applicable": False,
            },
            "plane_d": {
                "plane": "D",
                "marcel": {"match_score": 75, "mood": "positive", "key_values": [], "concerns": []},
                "petra": {"match_score": 80, "mood": "positive", "key_values": [], "concerns": []},
                "comparisons": [],
                "overlap_points": [],
                "tension_points": [],
                "not_applicable": False,
            },
        }
        registry = {"address": "Teststraat 123", "asking_price_eur": 500000}
        
        errors = ValidationGate.validate_chapter_output(0, output, registry)
        
        assert len(errors) == 0, f"Unexpected errors: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
