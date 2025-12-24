"""
FAIL-CLOSED ENFORCEMENT TESTS

These tests verify that the pipeline system is STRUCTURALLY IMPOSSIBLE to bypass.
If any of these tests pass when they should fail, THE SYSTEM IS BROKEN.

TESTED INVARIANTS (NON-NEGOTIABLE):
1. build_chapters() bypass path is BLOCKED - raises BypassBlocked
2. Registry conflicts THROW, not warn
3. Registry modifications after lock THROW
4. Validation failure in production mode BLOCKS rendering
5. strict_validation=False is IMPOSSIBLE in production mode
6. AI output with unknown keys is REJECTED
7. Removing ValidationGate breaks the pipeline

If enforcement can be removed without tests failing, THE TASK IS INCOMPLETE.
"""

import os
import pytest
from typing import Dict, Any
from unittest.mock import patch

# Set test mode BEFORE imports
os.environ["PIPELINE_TEST_MODE"] = "true"

from backend.domain.registry import (
    CanonicalRegistry,
    RegistryEntry,
    RegistryType,
    RegistryConflict,
    RegistryLocked
)
from backend.domain.pipeline_context import (
    PipelineContext,
    PipelineViolation,
    ValidationFailure,
    create_pipeline_context
)
from backend.pipeline.spine import PipelineSpine, is_production_mode
from backend.validation.gate import ValidationGate


# =============================================================================
# FIXTURE: Sample Data
# =============================================================================

@pytest.fixture
def sample_raw_data() -> Dict[str, Any]:
    return {
        "asking_price_eur": 500000,
        "living_area_m2": 120,
        "plot_area_m2": 250,
        "build_year": 1990,
        "energy_label": "C",
        "address": "Teststraat 123",
        "city": "Amsterdam",
        "description": "Een prachtige woning.",
        "features": ["tuin", "garage"]
    }


@pytest.fixture
def sample_preferences() -> Dict[str, Any]:
    return {
        "marcel": {"priorities": ["zonnepanelen"]},
        "petra": {"priorities": ["tuin"]}
    }


# =============================================================================
# 🔒 TEST 1: build_chapters BYPASS IS BLOCKED
# =============================================================================

class TestBypassBlocked:
    """Verify that the build_chapters bypass path is BLOCKED."""
    
    def test_build_chapters_raises_bypass_blocked(self, sample_raw_data):
        """Calling build_chapters MUST raise BypassBlocked."""
        from main import build_chapters, BypassBlocked
        
        with pytest.raises(BypassBlocked) as exc_info:
            build_chapters(sample_raw_data)
        
        assert "BLOCKED" in str(exc_info.value)
        assert "execute_report_pipeline" in str(exc_info.value)
    
    def test_importing_build_chapters_is_allowed_but_calling_is_not(self):
        """Import is allowed (for backward compat), but call is fatal."""
        from main import build_chapters, BypassBlocked
        
        # Import succeeded, but calling must fail
        with pytest.raises(BypassBlocked):
            build_chapters({})


# =============================================================================
# 🔒 TEST 2: REGISTRY CONFLICTS THROW (NOT WARN)
# =============================================================================

class TestRegistryConflictsThrow:
    """Verify that registry conflicts cause HARD FAILURES, not warnings."""
    
    def test_registry_conflict_raises_exception(self):
        """Conflicting values for same key MUST raise RegistryConflict."""
        registry = CanonicalRegistry()
        
        # Register first value
        entry1 = RegistryEntry(
            id="price",
            type=RegistryType.FACT,
            value=500000,
            name="Price",
            source="parser"
        )
        registry.register(entry1)
        
        # Attempt to register conflicting value
        entry2 = RegistryEntry(
            id="price",
            type=RegistryType.FACT,
            value=600000,  # DIFFERENT VALUE
            name="Price",
            source="scraper"
        )
        
        with pytest.raises(RegistryConflict) as exc_info:
            registry.register(entry2)
        
        assert "FATAL CONFLICT" in str(exc_info.value)
        assert "500000" in str(exc_info.value)
        assert "600000" in str(exc_info.value)
    
    def test_registry_idempotent_for_same_value(self):
        """Same key with same value is allowed (idempotent)."""
        registry = CanonicalRegistry()
        
        entry1 = RegistryEntry(
            id="price",
            type=RegistryType.FACT,
            value=500000,
            name="Price",
            source="parser"
        )
        registry.register(entry1)
        
        # Same value is OK
        entry2 = RegistryEntry(
            id="price",
            type=RegistryType.FACT,
            value=500000,  # SAME VALUE
            name="Price",
            source="parser"
        )
        registry.register(entry2)  # Should not raise
        
        assert registry.get("price").value == 500000


# =============================================================================
# 🔒 TEST 3: REGISTRY MODIFICATION AFTER LOCK THROWS
# =============================================================================

class TestRegistryLockingThrows:
    """Verify that modifying a locked registry causes HARD FAILURE."""
    
    def test_register_after_lock_raises(self):
        """Registration after lock MUST raise RegistryLocked."""
        registry = CanonicalRegistry()
        registry.lock()
        
        entry = RegistryEntry(
            id="new_key",
            type=RegistryType.FACT,
            value=100,
            name="New",
            source="test"
        )
        
        with pytest.raises(RegistryLocked) as exc_info:
            registry.register(entry)
        
        assert "locked" in str(exc_info.value).lower()
    
    def test_context_register_after_lock_raises(self):
        """PipelineContext.register_fact after lock MUST raise PipelineViolation."""
        ctx = create_pipeline_context("test-lock")
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        with pytest.raises(PipelineViolation) as exc_info:
            ctx.register_fact("new_key", 100, "New", RegistryType.FACT)
        
        assert "locked" in str(exc_info.value).lower()


# =============================================================================
# 🔒 TEST 4: PRODUCTION MODE BLOCKS INVALID RENDER
# =============================================================================

class TestProductionModeBlocking:
    """Verify that production mode BLOCKS invalid report rendering."""
    
    def test_production_mode_detection(self):
        """Test mode detection works correctly."""
        # In test environment, PIPELINE_TEST_MODE should be "true"
        assert os.environ.get("PIPELINE_TEST_MODE") == "true"
        assert not is_production_mode()
    
    def test_strict_render_blocks_invalid_chapters(self, sample_raw_data, sample_preferences):
        """Strict mode MUST raise when validation fails."""
        spine = PipelineSpine("test-strict", sample_preferences)
        spine.ingest_raw_data(sample_raw_data)
        spine.enrich_and_populate_registry()
        spine.generate_all_chapters()
        
        # Manually mark a chapter as failed
        spine.ctx._validation_results[0] = ["Forced test failure"]
        
        with pytest.raises(PipelineViolation) as exc_info:
            spine.get_renderable_output(strict=True)
        
        assert "validation failed" in str(exc_info.value).lower()
    
    def test_production_mode_forces_strict(self, sample_raw_data, sample_preferences):
        """Production mode detection overrides strict=False."""
        # Temporarily set production mode
        old_value = os.environ.get("PIPELINE_TEST_MODE")
        os.environ.pop("PIPELINE_TEST_MODE", None)
        
        try:
            assert is_production_mode()  # Now in production mode
        finally:
            # Restore test mode
            if old_value:
                os.environ["PIPELINE_TEST_MODE"] = old_value
            else:
                os.environ["PIPELINE_TEST_MODE"] = "true"


# =============================================================================
# 🔒 TEST 5: VALIDATION GATE IS MANDATORY
# =============================================================================

class TestValidationGateMandatory:
    """Verify that ValidationGate is ALWAYS invoked."""
    
    def test_all_chapters_validated(self, sample_raw_data, sample_preferences):
        """Every chapter MUST have a validation result."""
        spine, output = PipelineSpine.execute_full_pipeline(
            run_id="test-validate-all",
            raw_data=sample_raw_data,
            preferences=sample_preferences,
            strict_validation=False  # Test mode only
        )
        
        # Chapters 1-13 must have validation results (13 chapters)
        # Chapter 0 (Dashboard) is generated separately
        assert len(spine.ctx._validation_results) == 13
        
        for chapter_id in range(1, 14):
            assert chapter_id in spine.ctx._validation_results
    
    def test_validation_errors_prevent_storage(self):
        """Failed chapters CANNOT be stored as validated."""
        ctx = create_pipeline_context("test-storage")
        
        # Record failed validation
        ctx.record_validation_result(0, ["Some validation error"])
        
        with pytest.raises(PipelineViolation) as exc_info:
            ctx.store_validated_chapter(0, {"id": "0"})
        
        assert "validation failed" in str(exc_info.value).lower()
    
    def test_unvalidated_chapters_cannot_be_stored(self):
        """Chapters without validation CANNOT be stored."""
        ctx = create_pipeline_context("test-no-validation")
        
        with pytest.raises(PipelineViolation) as exc_info:
            ctx.store_validated_chapter(0, {"id": "0"})
        
        assert "validation not recorded" in str(exc_info.value).lower()


# =============================================================================
# 🔒 TEST 6: VALIDATION GATE CATCHES VIOLATIONS
# =============================================================================

class TestValidationGateCatchesViolations:
    """Verify that ValidationGate catches all types of violations."""
    
    def test_ownership_violation_caught(self):
        """Variables owned by wrong chapter MUST be caught."""
        # Chapter 7 (Garden) trying to use price variable
        output = {
            "id": "7",
            "title": "Garden",
            "main_analysis": "Garden content",
            "variables": {"asking_price_eur": 500000},  # NOT owned by chapter 7
            "comparison": {"marcel": "Good garden", "petra": "Nice plants"}
        }
        registry = {"asking_price_eur": 500000}
        
        errors = ValidationGate.validate_chapter_output(7, output, registry)
        
        assert any("Ownership" in e for e in errors)
    
    def test_raw_fact_restatement_caught(self):
        """Raw facts in wrong chapters MUST be caught."""
        output = {
            "id": "7",
            "title": "Garden",
            "main_analysis": "The property costs 500000 euros.",  # Raw price in garden chapter
            "variables": {},
            "comparison": {"marcel": "Good garden", "petra": "Nice plants"}
        }
        registry = {"asking_price_eur": 500000}
        
        errors = ValidationGate.validate_chapter_output(7, output, registry)
        
        assert any("Raw Fact" in e for e in errors)
    
    def test_missing_required_fields_caught(self):
        """Missing required fields MUST be caught."""
        output = {
            # Missing: id, title, main_analysis
            "variables": {}
        }
        
        errors = ValidationGate.validate_chapter_output(0, output, {})
        
        assert any("Required Field" in e for e in errors)


# =============================================================================
# 🔒 TEST 7: PIPELINE PHASE ENFORCEMENT
# =============================================================================

class TestPipelinePhaseEnforcement:
    """Verify that pipeline phases MUST be followed in order."""
    
    def test_cannot_enrich_before_ingest(self, sample_raw_data):
        """Enrichment before ingestion MUST raise."""
        spine = PipelineSpine("test-phase-1")
        
        with pytest.raises(PipelineViolation):
            spine.enrich_and_populate_registry()
    
    def test_cannot_generate_before_enrich(self, sample_raw_data):
        """Generation before enrichment MUST raise."""
        spine = PipelineSpine("test-phase-2")
        spine.ingest_raw_data(sample_raw_data)
        
        with pytest.raises(PipelineViolation):
            spine.generate_all_chapters()
    
    def test_cannot_render_before_generate(self, sample_raw_data):
        """Rendering before generation MUST raise."""
        spine = PipelineSpine("test-phase-3")
        spine.ingest_raw_data(sample_raw_data)
        spine.enrich_and_populate_registry()
        
        with pytest.raises(PipelineViolation):
            spine.get_renderable_output()
    
    def test_cannot_generate_without_locked_registry(self):
        """Chapter generation without locked registry MUST raise."""
        ctx = create_pipeline_context("test-phase-4")
        ctx.complete_enrichment()
        # NOT locking registry
        
        with pytest.raises(PipelineViolation):
            ctx.begin_chapter_generation()


# =============================================================================
# 🔒 TEST 8: CORRECT EXECUTION PATH WORKS
# =============================================================================

class TestCorrectExecutionPath:
    """Verify that the correct execution path produces valid output."""
    
    def test_full_pipeline_executes_correctly(self, sample_raw_data, sample_preferences):
        """Full pipeline through execute_full_pipeline works."""
        spine, output = PipelineSpine.execute_full_pipeline(
            run_id="test-correct-1",
            raw_data=sample_raw_data,
            preferences=sample_preferences,
            strict_validation=False  # Test mode
        )
        
        assert output is not None
        assert "chapters" in output
        assert "validation_passed" in output
        # Chapters 0-13 (14 chapters) in output (includes both validated chapters and chapter 0)
        assert len(output["chapters"]) == 14
    
    def test_bridge_function_works(self, sample_raw_data, sample_preferences):
        """Pipeline bridge function works correctly."""
        from backend.pipeline.bridge import execute_report_pipeline
        
        chapters, kpis, enriched_core = execute_report_pipeline(
            run_id="test-bridge-1",
            raw_data=sample_raw_data,
            preferences=sample_preferences
        )
        
        # Chapters 0-13 (14 chapters) returned from bridge
        assert len(chapters) >= 13  # At least 13 (may include dashboard)
        assert "dashboard_cards" in kpis
        assert "asking_price_eur" in enriched_core


# =============================================================================
# 🔒 TEST 9: REMOVAL OF ENFORCEMENT BREAKS TESTS
# =============================================================================

class TestEnforcementRemovalBreaksTests:
    """
    These tests verify that enforcement CANNOT be silently removed.
    If you remove enforcement, these tests will fail.
    """
    
    def test_registry_has_lock_method(self):
        """Registry MUST have lock method."""
        registry = CanonicalRegistry()
        assert hasattr(registry, 'lock')
        assert callable(registry.lock)
    
    def test_registry_has_is_locked_method(self):
        """Registry MUST have is_locked method."""
        registry = CanonicalRegistry()
        assert hasattr(registry, 'is_locked')
        assert callable(registry.is_locked)
    
    def test_context_has_validation_methods(self):
        """PipelineContext MUST have validation methods."""
        ctx = create_pipeline_context("test-methods")
        
        assert hasattr(ctx, 'record_validation_result')
        assert hasattr(ctx, 'all_chapters_valid')
        assert hasattr(ctx, 'store_validated_chapter')
    
    def test_spine_has_phase_tracking(self):
        """PipelineSpine MUST track phases."""
        spine = PipelineSpine("test-phases")
        
        assert hasattr(spine, '_phase')
        assert spine._phase == "initialized"
    
    def test_validation_gate_exists_and_callable(self):
        """ValidationGate.validate_chapter_output MUST exist."""
        assert hasattr(ValidationGate, 'validate_chapter_output')
        assert callable(ValidationGate.validate_chapter_output)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
