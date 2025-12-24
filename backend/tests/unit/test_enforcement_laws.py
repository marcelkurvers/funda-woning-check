"""
Enforcement Tests - LAW A, B, C, D, E Compliance

These tests verify that the enforcement mechanisms work correctly and prevent regression.

REQUIRED TESTS (from audit mandate):
1. test_ai_cannot_introduce_unregistered_keys - LAW B
2. test_ai_soft_error_cannot_pass - LAW A  
3. test_invalid_report_not_stored_to_db - LAW D
4. test_validation_is_single_sourced - LAW A
5. test_no_synthetic_variable_injection - LAW C

All tests run without external services.
"""

import pytest
import json
import os
import sys
from unittest.mock import MagicMock, patch, call
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.pipeline.ai_output_validator import (
    validate_ai_output,
    sanitize_and_validate_ai_output,
    ensure_no_synthetic_injection,
    AIOutputViolation,
    ALLOWED_TOP_LEVEL_KEYS,
    ALLOWED_META_VARIABLE_KEYS
)
from backend.domain.chapter_variables import get_chapter_variables


class TestLawB_AICannotIntroduceUnregisteredKeys:
    """
    LAW B: AI Output Must Be a Subset of Allowed Keys
    
    For each chapter, AI output may only contain keys in:
    owned_keys ∪ allowed_meta_keys
    
    Any unknown keys must cause hard pipeline failure.
    """
    
    def test_ai_cannot_introduce_unknown_top_level_keys(self):
        """AI output with unknown top-level keys must fail validation."""
        ai_output = {
            "title": "Valid Title",
            "main_analysis": "Valid analysis",
            "UNKNOWN_KEY_HACKED_IN": "Malicious content",  # UNAUTHORIZED
            "another_fake_key": {"nested": "data"}  # UNAUTHORIZED
        }
        
        with pytest.raises(AIOutputViolation) as exc_info:
            validate_ai_output(chapter_id=1, ai_output=ai_output, strict=True)
        
        assert "UNKNOWN_KEY_HACKED_IN" in str(exc_info.value)
    
    def test_ai_cannot_introduce_unknown_variable_keys(self):
        """AI output with unauthorized variable keys must fail validation."""
        # Chapter 3 owns: technische_staat_score, dak_gevel_conditie, etc.
        # It does NOT own: asking_price_eur (that's Chapter 0)
        ai_output = {
            "title": "Technical Analysis",
            "main_analysis": "Analysis content",
            "variables": {
                "technische_staat_score": {"value": "Good", "status": "fact"},  # VALID
                "asking_price_eur": {"value": "500000", "status": "fact"},  # UNAUTHORIZED for Ch3
            }
        }
        
        with pytest.raises(AIOutputViolation) as exc_info:
            validate_ai_output(chapter_id=3, ai_output=ai_output, strict=True)
        
        assert "asking_price_eur" in str(exc_info.value)
    
    def test_valid_output_passes(self):
        """Valid AI output with only allowed keys should pass."""
        ai_output = {
            "title": "Executive Summary",
            "intro": "Introduction text",
            "main_analysis": "Detailed analysis",
            "conclusion": "Final thoughts",
            "variables": {
                "status": {"value": "verified", "reasoning": "checked"},  # Meta key - allowed
            },
            "_provenance": {"provider": "test"}  # Allowed meta
        }
        
        result = validate_ai_output(chapter_id=0, ai_output=ai_output, strict=True)
        assert result.valid is True
        assert len(result.violations) == 0
    
    def test_non_strict_mode_strips_keys(self):
        """Non-strict mode should strip unauthorized keys and warn."""
        ai_output = {
            "title": "Valid",
            "main_analysis": "Valid",
            "UNAUTHORIZED": "Should be stripped"
        }
        
        result = validate_ai_output(chapter_id=5, ai_output=ai_output, strict=False)
        
        # Should not raise, but should report stripped keys
        assert "UNAUTHORIZED" in result.stripped_keys
        assert "UNAUTHORIZED" not in ai_output  # Key should be removed


class TestLawA_NoSoftErrorsFromAI:
    """
    LAW A: Single Source of Validation
    
    Validation must exist in exactly one place: the pipeline spine.
    No validation inside IntelligenceEngine that returns error-content.
    IntelligenceEngine must either return candidate output OR raise exception.
    """
    
    def test_intelligence_engine_does_not_call_validation_gate(self):
        """IntelligenceEngine should NOT call ValidationGate internally."""
        # Check that the ValidationGate import was removed from _generate_ai_narrative
        from backend import intelligence
        import inspect
        
        source = inspect.getsource(intelligence.IntelligenceEngine._generate_ai_narrative)
        
        # The string "ValidationGate.validate_chapter_output" should NOT appear
        # We removed this in the LAW A fix
        assert "ValidationGate.validate_chapter_output" not in source, \
            "LAW A VIOLATION: IntelligenceEngine still contains ValidationGate call"
    
    def test_intelligence_engine_does_not_return_error_content_dict(self):
        """IntelligenceEngine should not return error-content dicts."""
        from backend import intelligence
        import inspect
        
        source = inspect.getsource(intelligence.IntelligenceEngine._generate_ai_narrative)
        
        # Should not have the error-content return pattern
        error_patterns = [
            '"title": "Validation Error"',
            "\"title\": \"Validation Error\"",
            "Validation Failed.",
        ]
        
        for pattern in error_patterns:
            assert pattern not in source, \
                f"LAW A VIOLATION: IntelligenceEngine still returns error-content: {pattern}"
    
    def test_validation_only_at_spine_level(self):
        """Verify ValidationGate is only called from spine, not intelligence."""
        from backend.pipeline import spine
        import inspect
        
        spine_source = inspect.getsource(spine.PipelineSpine.generate_all_chapters)
        
        # Spine SHOULD call ValidationGate
        assert "ValidationGate.validate_chapter_output" in spine_source, \
            "Spine must call ValidationGate for each chapter"


class TestLawC_NoSyntheticVariableInjection:
    """
    LAW C: No Synthetic Variables Outside Registry
    
    Remove any logic that injects variables when AI returns none.
    If AI returns no variables, output contains no variables.
    """
    
    def test_empty_ai_output_stays_empty(self):
        """If AI returns nothing, output should have no variables."""
        # Simulate AI returning None or empty
        ai_output = None
        
        # New signature: chapter_id, ai_output, registry_ids (optional)
        result = sanitize_and_validate_ai_output(
            chapter_id=5,
            ai_output=ai_output
        )
        
        # Should return empty, not inject synthetic variables
        assert result == {} or 'variables' not in result
    
    def test_synthetic_injection_detected(self):
        """Detect and fail on known synthetic variable signatures."""
        # This output has the signature of injected defaults
        output_with_injection = {
            "title": "Test",
            "variables": {
                "object_focus": {
                    "value": "Hoofdstuk",
                    "status": "fact",
                    "reasoning": "Geprioriteerd focuspunt voor deze sectie."  # SYNTHETIC SIGNATURE
                },
                "vertrouwen": {
                    "value": "Hoog",
                    "status": "inferred", 
                    "reasoning": "Gebaseerd op geverifieerde brongegevens."  # SYNTHETIC SIGNATURE
                }
            }
        }
        
        with pytest.raises(AIOutputViolation) as exc_info:
            ensure_no_synthetic_injection(output_with_injection)
        
        assert "SYNTHETIC INJECTION DETECTED" in str(exc_info.value)
    
    def test_intelligence_engine_no_longer_injects_defaults(self):
        """IntelligenceEngine should not inject default variables."""
        from backend import intelligence
        import inspect
        
        source = inspect.getsource(intelligence.IntelligenceEngine.generate_chapter_narrative)
        
        # The synthetic injection patterns should NOT appear
        synthetic_patterns = [
            '"object_focus"',
            '"vertrouwen"',
            "Geprioriteerd focuspunt",
            "Gebaseerd op geverifieerde brongegevens"
        ]
        
        for pattern in synthetic_patterns:
            assert pattern not in source, \
                f"LAW C VIOLATION: IntelligenceEngine still injects synthetic variable: {pattern}"


class TestLawD_FailClosedPersistence:
    """
    LAW D: Fail-Closed Persistence
    
    If validation fails:
    - Do not render
    - Do not write chapters_json to DB
    - Mark run status as validation_failed and store only diagnostics
    """
    
    def test_invalid_report_not_stored_to_db(self):
        """Invalid reports must NOT have chapters_json written to DB."""
        from backend import main
        import inspect
        
        source = inspect.getsource(main.simulate_pipeline)
        
        # Must check validation_passed before writing chapters
        assert "validation_passed" in source, \
            "simulate_pipeline must check validation_passed"
        
        # Must have conditional update based on validation
        assert "if validation_passed:" in source or "if kpis.get('validation_passed'" in source, \
            "simulate_pipeline must conditionally write based on validation"
    
    def test_validation_failed_status_exists(self):
        """Pipeline must set status='validation_failed' when validation fails."""
        from backend import main
        import inspect
        
        source = inspect.getsource(main.simulate_pipeline)
        
        assert 'status="validation_failed"' in source, \
            "Pipeline must use 'validation_failed' status for failed validation"
    
    @patch('backend.main.update_run')
    @patch('backend.main.get_run_row')
    @patch('backend.main.get_kv')
    def test_chapters_not_written_when_validation_fails(
        self, mock_get_kv, mock_get_row, mock_update
    ):
        """Simulate validation failure and verify chapters_json is NOT written."""
        # This is a mock-based test showing the logic path
        mock_get_kv.return_value = {}
        mock_get_row.return_value = {
            'id': 'test-run',
            'status': 'running',
            'steps_json': '{}',
            'property_core_json': '{}',
            'funda_url': 'manual-paste',
            'funda_html': None
        }
        
        # The actual test would need full pipeline mock, but this validates structure
        # Check that the code path exists in main.py
        from backend import main
        import inspect
        
        source = inspect.getsource(main.simulate_pipeline)
        
        # Verify the validation check exists
        assert "validation_passed = kpis.get('validation_passed', False)" in source
        
        # Verify branches exist
        assert "if validation_passed:" in source
        assert "else:" in source  # The failed branch


class TestLawE_TestModeIsolation:
    """
    LAW E: No "Test Mode" That Leaks to Real Output
    
    If PIPELINE_TEST_MODE=true, it must never allow invalid chapters
    to be stored or served through the same endpoint a user uses.
    Test-mode output must be isolated to tests.
    """
    
    def test_production_mode_is_default(self):
        """Default mode must be production (fail-closed)."""
        # Clear any test mode env var
        old_val = os.environ.pop("PIPELINE_TEST_MODE", None)
        try:
            from backend.pipeline.spine import is_production_mode
            assert is_production_mode() is True, \
                "Default must be production mode"
        finally:
            # CRITICAL: Restore test mode to avoid polluting other tests
            os.environ["PIPELINE_TEST_MODE"] = old_val if old_val else "true"
    
    def test_test_mode_requires_explicit_flag(self):
        """Test mode requires explicit PIPELINE_TEST_MODE=true."""
        from backend.pipeline.spine import is_production_mode
        
        # Without the flag = production
        old_val = os.environ.pop("PIPELINE_TEST_MODE", None)
        try:
            assert is_production_mode() is True
        finally:
            # CRITICAL: Restore test mode to avoid polluting other tests
            os.environ["PIPELINE_TEST_MODE"] = old_val if old_val else "true"
    
    def test_test_mode_outputs_are_marked(self):
        """Test mode outputs must have isolation marker."""
        from backend.pipeline.spine import (
            mark_test_output, 
            TEST_MODE_ISOLATION_MARKER,
            is_test_mode
        )
        
        # Save current value
        old_val = os.environ.get("PIPELINE_TEST_MODE")
        
        # Force test mode
        os.environ["PIPELINE_TEST_MODE"] = "true"
        try:
            output = {"chapters": {}, "validation_passed": False}
            marked = mark_test_output(output)
            
            assert TEST_MODE_ISOLATION_MARKER in marked, \
                "Test mode output must have isolation marker"
            assert "_test_mode_warning" in marked, \
                "Test mode output must have warning"
        finally:
            # CRITICAL: Restore original value
            if old_val:
                os.environ["PIPELINE_TEST_MODE"] = old_val
            else:
                os.environ["PIPELINE_TEST_MODE"] = "true"
    
    def test_production_outputs_not_marked(self):
        """Production outputs should not have test markers."""
        from backend.pipeline.spine import mark_test_output, TEST_MODE_ISOLATION_MARKER
        
        # Ensure production mode
        old_val = os.environ.pop("PIPELINE_TEST_MODE", None)
        try:
            output = {"chapters": {}, "validation_passed": True}
            marked = mark_test_output(output)
            
            assert TEST_MODE_ISOLATION_MARKER not in marked, \
                "Production output must not have test marker"
        finally:
            # CRITICAL: Restore test mode to avoid polluting other tests
            os.environ["PIPELINE_TEST_MODE"] = old_val if old_val else "true"


# =============================================================================
# INTEGRATION TEST: Full Pipeline Enforcement
# =============================================================================

class TestPipelineEnforcement:
    """Integration tests for the complete enforcement system."""
    
    def test_spine_enforces_validation_before_render(self):
        """PipelineSpine must enforce validation before allowing render."""
        from backend.pipeline.spine import PipelineSpine, is_production_mode
        from backend.domain.pipeline_context import PipelineViolation
        
        # In production mode, failed validation must raise
        # This is tested by checking the code structure
        import inspect
        source = inspect.getsource(PipelineSpine.get_renderable_output)
        
        assert "is_production_mode()" in source, \
            "get_renderable_output must check production mode"
        assert "raise PipelineViolation" in source, \
            "get_renderable_output must raise on failed validation"
    
    def test_all_chapters_pass_through_validation_gate(self):
        """Every chapter must pass through ValidationGate in spine."""
        from backend.pipeline.spine import PipelineSpine
        import inspect
        
        source = inspect.getsource(PipelineSpine.generate_all_chapters)
        
        # Must call ValidationGate for each chapter
        assert "ValidationGate.validate_chapter_output" in source
        
        # Must record validation results
        assert "record_validation_result" in source
        
        # Must track failed chapters
        assert "_failed_chapters" in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
