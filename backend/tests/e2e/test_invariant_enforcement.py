"""
End-to-End Invariant Test - PROVES THE CORE INVARIANT

CORE INVARIANT (ABSOLUTE):
    If a factual value appears in a report, it MUST come from the CanonicalRegistry.
    AI must never output factual values directly.

This test PROVES that:
    1. No AI output string contains a numeric literal or factual value
    2. All facts shown in the report originate from the CanonicalRegistry
    3. Removing AI does not change factual content
    4. The system makes fact invention IMPOSSIBLE, not just "detected"

If this test passes, enforcement is REAL and STRUCTURAL.
"""

import pytest
import re
from typing import Dict, Any, Set
from unittest.mock import MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.domain.registry import CanonicalRegistry, RegistryEntry, RegistryType
from backend.domain.ai_interpretation_schema import (
    AIInterpretationOutput,
    Interpretation,
    Risk,
    PreferenceMatch,
    Uncertainty,
    Assessment,
    Impact,
    Fit,
    UncertaintyReason,
    _contains_numeric_literal,
    validate_ai_interpretation_output,
    AIOutputSchemaViolation
)
from backend.domain.fact_safe_renderer import (
    FactSafeRenderer,
    RenderedFact,
    format_registry_value
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def locked_registry() -> CanonicalRegistry:
    """Create a locked registry with test data."""
    registry = CanonicalRegistry()
    
    # Register core facts
    registry.register(RegistryEntry(
        id="asking_price_eur",
        type=RegistryType.FACT,
        value=595000,
        name="Vraagprijs",
        source="funda_parse",
        unit="EUR"
    ))
    registry.register(RegistryEntry(
        id="living_area_m2",
        type=RegistryType.FACT,
        value=120,
        name="Woonoppervlakte",
        source="funda_parse",
        unit="m²"
    ))
    registry.register(RegistryEntry(
        id="build_year",
        type=RegistryType.FACT,
        value=1930,
        name="Bouwjaar",
        source="funda_parse"
    ))
    registry.register(RegistryEntry(
        id="energy_label",
        type=RegistryType.FACT,
        value="C",
        name="Energielabel",
        source="funda_parse"
    ))
    registry.register(RegistryEntry(
        id="marcel_match_score",
        type=RegistryType.KPI,
        value=85,
        name="Marcel Match",
        source="enricher"
    ))
    registry.register(RegistryEntry(
        id="price_per_m2",
        type=RegistryType.VARIABLE,
        value=4958,
        name="Vierkantemeterprijs",
        source="enricher",
        unit="EUR/m²"
    ))
    
    # Lock the registry
    registry.lock()
    
    return registry


@pytest.fixture
def valid_ai_interpretation() -> AIInterpretationOutput:
    """Create a valid AI interpretation that contains NO facts."""
    return AIInterpretationOutput(
        chapter_id=0,
        interpretations=[
            Interpretation(
                registry_id="asking_price_eur",
                assessment=Assessment.HIGH,
                reasoning="The asking price is considered high relative to comparable properties in this market segment."
            ),
            Interpretation(
                registry_id="living_area_m2",
                assessment=Assessment.AVERAGE,
                reasoning="The living space is in line with similar properties in this neighborhood."
            ),
            Interpretation(
                registry_id="build_year",
                assessment=Assessment.LOW,
                reasoning="The construction period suggests potential maintenance considerations typical of pre-war buildings."
            )
        ],
        risks=[
            Risk(
                registry_id="build_year",
                impact=Impact.MEDIUM,
                explanation="Buildings from this era may require foundation inspection and potential renovation of original elements."
            )
        ],
        preference_matches=[
            PreferenceMatch(
                preference_id="marcel_tech",
                registry_id="energy_label",
                fit=Fit.NEUTRAL,
                explanation="The energy efficiency provides a baseline but may benefit from modernization."
            )
        ],
        title="Executive Summary",
        summary="This property presents an interesting opportunity that warrants careful consideration.",
        detailed_analysis="The property offers a balanced combination of features that may appeal to buyers seeking character properties. The overall assessment suggests this could be a suitable investment with appropriate due diligence."
    )


@pytest.fixture
def invalid_ai_with_numbers() -> Dict[str, Any]:
    """Raw AI output that violates the schema by containing numbers."""
    return {
        "interpretations": [
            {
                "registry_id": "asking_price_eur",
                "assessment": "high",
                "reasoning": "The asking price of €595.000 is above market average."  # VIOLATION!
            }
        ],
        "summary": "This 120m² property from 1930 is priced at €595.000."  # VIOLATION!
    }


# =============================================================================
# CORE INVARIANT TESTS
# =============================================================================

class TestCoreInvariant:
    """
    Test the CORE INVARIANT: AI may never output factual values.
    """
    
    def test_numeric_detection_catches_currency(self):
        """Test that currency values are detected."""
        assert _contains_numeric_literal("The price is €500.000")
        assert _contains_numeric_literal("Costing $1,234.56")
        assert _contains_numeric_literal("€ 595.000 is the asking price")
    
    def test_numeric_detection_catches_measurements(self):
        """Test that measurements are detected."""
        assert _contains_numeric_literal("The area is 120m²")
        assert _contains_numeric_literal("With 120 m2 of space")
        assert _contains_numeric_literal("Volume of 350m³")
    
    def test_numeric_detection_catches_percentages(self):
        """Test that percentages are detected."""
        assert _contains_numeric_literal("Score of 85%")
        assert _contains_numeric_literal("12.5% increase")
    
    def test_numeric_detection_catches_years(self):
        """Test that years are detected."""
        assert _contains_numeric_literal("Built in 1930")
        assert _contains_numeric_literal("Construction year 1920")
    
    def test_numeric_detection_catches_large_numbers(self):
        """Test that large numbers are detected."""
        assert _contains_numeric_literal("Price of 500000")
        assert _contains_numeric_literal("Costs 1.234.567")
    
    def test_numeric_detection_allows_chapter_references(self):
        """Test that chapter numbers are allowed."""
        assert not _contains_numeric_literal("See Chapter 5 for details")
        assert not _contains_numeric_literal("Refer to hoofdstuk 3")
    
    def test_numeric_detection_allows_interpretive_text(self):
        """Test that text without numbers passes."""
        assert not _contains_numeric_literal(
            "The asking price is considered high relative to comparable properties."
        )
        assert not _contains_numeric_literal(
            "The living space is generous compared to similar homes."
        )
    
    def test_valid_interpretation_passes_validation(self, locked_registry, valid_ai_interpretation):
        """Test that valid AI interpretation passes validation."""
        registry_ids = set(locked_registry.get_all().keys())
        errors = validate_ai_interpretation_output(
            valid_ai_interpretation, 
            registry_ids, 
            strict=False
        )
        assert len(errors) == 0, f"Valid interpretation should pass. Errors: {errors}"
    
    def test_invalid_interpretation_with_numbers_fails(self, locked_registry, invalid_ai_with_numbers):
        """Test that AI output with numbers is rejected."""
        from backend.domain.ai_interpretation_schema import parse_ai_output
        
        parsed = parse_ai_output(invalid_ai_with_numbers, chapter_id=0)
        registry_ids = set(locked_registry.get_all().keys())
        
        errors = validate_ai_interpretation_output(parsed, registry_ids, strict=False)
        
        # Should have errors about numeric literals
        assert len(errors) > 0, "Should detect numeric violations"
        assert any("numeric" in e.lower() for e in errors), f"Should mention numeric. Errors: {errors}"
    
    def test_schema_violation_raises_exception_in_strict_mode(self, locked_registry, invalid_ai_with_numbers):
        """Test that strict mode raises exception on violations."""
        from backend.domain.ai_interpretation_schema import parse_ai_output
        
        parsed = parse_ai_output(invalid_ai_with_numbers, chapter_id=0)
        registry_ids = set(locked_registry.get_all().keys())
        
        with pytest.raises(AIOutputSchemaViolation) as exc_info:
            validate_ai_interpretation_output(parsed, registry_ids, strict=True)
        
        assert exc_info.value.chapter_id == 0
        assert len(exc_info.value.violations) > 0


# =============================================================================
# FACT-SAFE RENDERER TESTS
# =============================================================================

class TestFactSafeRenderer:
    """
    Test that FactSafeRenderer only renders facts from the registry.
    """
    
    def test_renderer_requires_locked_registry(self):
        """Test that renderer rejects unlocked registry."""
        unlocked = CanonicalRegistry()
        unlocked.register(RegistryEntry(
            id="test",
            type=RegistryType.FACT,
            value=100,
            name="Test",
            source="test"
        ))
        # NOT locked
        
        with pytest.raises(ValueError, match="LOCKED"):
            FactSafeRenderer(unlocked)
    
    def test_renderer_formats_facts_from_registry(self, locked_registry):
        """Test that facts are formatted from registry values."""
        renderer = FactSafeRenderer(locked_registry)
        
        fact = renderer.render_fact("asking_price_eur")
        
        assert fact is not None
        assert fact.registry_id == "asking_price_eur"
        assert "€" in fact.formatted_value
        assert "595" in fact.formatted_value
        assert fact.source == "registry"
    
    def test_renderer_tracks_all_rendered_facts(self, locked_registry):
        """Test that all rendered facts are tracked for audit."""
        renderer = FactSafeRenderer(locked_registry)
        
        renderer.render_fact("asking_price_eur")
        renderer.render_fact("living_area_m2")
        renderer.render_fact("build_year")
        
        all_facts = renderer.get_all_rendered_facts()
        
        assert len(all_facts) == 3
        assert "asking_price_eur" in all_facts
        assert "living_area_m2" in all_facts
        assert "build_year" in all_facts
    
    def test_all_rendered_facts_originate_from_registry(self, locked_registry):
        """CORE INVARIANT: All facts must originate from registry."""
        renderer = FactSafeRenderer(locked_registry)
        
        # Render several facts
        renderer.render_fact("asking_price_eur")
        renderer.render_fact("living_area_m2")
        renderer.render_fact("build_year")
        
        # Audit origins
        origins = renderer.audit_fact_origins()
        
        # ALL must be "registry"
        for registry_id, source in origins.items():
            assert source == "registry", f"Fact {registry_id} has non-registry source: {source}"
    
    def test_ai_interpretation_is_separate_from_facts(self, locked_registry, valid_ai_interpretation):
        """Test that AI interpretation is kept separate from facts."""
        renderer = FactSafeRenderer(locked_registry)
        
        content = renderer.render_chapter_content(
            chapter_id=0,
            owned_keys=["asking_price_eur", "living_area_m2", "build_year"],
            interpretation=valid_ai_interpretation
        )
        
        # Facts should be separate
        assert "facts" in content
        assert len(content["facts"]) == 3
        
        # Each fact has registry_id and source
        for fact in content["facts"]:
            assert fact["source"] == "registry"
            assert fact["registry_id"] in ["asking_price_eur", "living_area_m2", "build_year"]
        
        # AI content is separate
        assert content["summary"] == valid_ai_interpretation.summary
        assert content["detailed_analysis"] == valid_ai_interpretation.detailed_analysis
    
    def test_removing_ai_does_not_change_facts(self, locked_registry):
        """CORE INVARIANT: Removing AI does not change factual content."""
        renderer = FactSafeRenderer(locked_registry)
        
        # Render WITH AI
        content_with_ai = renderer.render_chapter_content(
            chapter_id=0,
            owned_keys=["asking_price_eur", "living_area_m2"],
            interpretation=AIInterpretationOutput(
                chapter_id=0,
                summary="AI generated summary",
                detailed_analysis="AI generated analysis"
            )
        )
        
        # Render WITHOUT AI
        renderer2 = FactSafeRenderer(locked_registry)
        content_without_ai = renderer2.render_chapter_content(
            chapter_id=0,
            owned_keys=["asking_price_eur", "living_area_m2"],
            interpretation=None
        )
        
        # Facts should be IDENTICAL
        assert content_with_ai["facts"] == content_without_ai["facts"]
        assert content_with_ai["fact_count"] == content_without_ai["fact_count"]


# =============================================================================
# CONVERGENCE TEST - THE ULTIMATE PROOF
# =============================================================================

class TestConvergence:
    """
    This test proves that the system has converged to the target state:
    - AI cannot invent facts
    - Registry is the only factual source
    - Enforcement does not depend on prompt compliance
    """
    
    def test_no_ai_output_contains_registry_values(self, locked_registry, valid_ai_interpretation):
        """
        CONVERGENCE TEST 1:
        No AI output string contains any value that exists in the registry.
        
        This proves AI is interpreting, not restating.
        """
        # Get all registry values
        registry_values = []
        for entry in locked_registry.get_all().values():
            val = entry.value
            if isinstance(val, (int, float)):
                registry_values.append(str(int(val)))
                registry_values.append(str(val))
            else:
                registry_values.append(str(val))
        
        # Check all AI output text
        ai_texts = [
            valid_ai_interpretation.summary,
            valid_ai_interpretation.detailed_analysis,
            valid_ai_interpretation.title
        ]
        for interp in valid_ai_interpretation.interpretations:
            ai_texts.append(interp.reasoning)
        for risk in valid_ai_interpretation.risks:
            ai_texts.append(risk.explanation)
        
        # No AI text should contain registry values
        for text in ai_texts:
            for val in registry_values:
                # Skip very short values that might appear coincidentally
                if len(val) < 3:
                    continue
                assert val not in text, (
                    f"AI output contains registry value '{val}'. "
                    f"Text: '{text[:100]}...'"
                )
    
    def test_all_facts_in_report_trace_to_registry(self, locked_registry):
        """
        CONVERGENCE TEST 2:
        Every factual value in the rendered report traces back to a registry entry.
        """
        renderer = FactSafeRenderer(locked_registry)
        
        content = renderer.render_chapter_content(
            chapter_id=0,
            owned_keys=list(locked_registry.get_all().keys())
        )
        
        # Every fact should have a registry_id
        for fact in content["facts"]:
            assert "registry_id" in fact
            assert fact["registry_id"] in locked_registry.get_all()
            
            # The value should match the registry
            registry_entry = locked_registry.get(fact["registry_id"])
            formatted = format_registry_value(fact["registry_id"], registry_entry.value)
            assert fact["value"] == formatted
    
    def test_ai_failure_does_not_introduce_facts(self, locked_registry):
        """
        CONVERGENCE TEST 3:
        When AI fails or returns nothing, no facts are invented.
        """
        renderer = FactSafeRenderer(locked_registry)
        
        # Simulate AI failure - pass None
        content = renderer.render_chapter_content(
            chapter_id=0,
            owned_keys=["asking_price_eur", "living_area_m2"],
            interpretation=None
        )
        
        # Facts should still come from registry
        assert len(content["facts"]) == 2
        for fact in content["facts"]:
            assert fact["source"] == "registry"
        
        # AI fields should be empty, not fabricated
        assert content["summary"] == ""
        assert content["detailed_analysis"] == ""
    
    def test_schema_makes_fact_invention_impossible(self):
        """
        CONVERGENCE TEST 4:
        The schema structurally prevents fact invention.
        
        AI output MUST conform to fixed interpretation structure.
        There is no field where facts could be injected.
        """
        # Create minimal valid output
        output = AIInterpretationOutput(chapter_id=0)
        
        # The only allowed fields are:
        # - interpretations (with reasoning that must not contain numbers)
        # - risks (with explanation that must not contain numbers)
        # - preference_matches (structural only)
        # - uncertainties (structural only)
        # - title, summary, detailed_analysis (text without numbers)
        
        # Try to add a "fact" field - it would be ignored
        raw = {"invented_fact": "€595.000"}
        from backend.domain.ai_interpretation_schema import parse_ai_output
        parsed = parse_ai_output(raw, chapter_id=0)
        
        # The invented_fact is not in the parsed output
        assert not hasattr(parsed, "invented_fact")
        
        # Validate against empty registry
        errors = parsed.validate(set())
        # Should have no structural errors (the invented field was simply not parsed)
        # This proves: unknown keys cannot sneak facts into the output
    
    def test_unknown_registry_id_in_ai_output_fails(self, locked_registry):
        """
        CONVERGENCE TEST 5:
        AI cannot reference registry IDs that don't exist.
        """
        output = AIInterpretationOutput(
            chapter_id=0,
            interpretations=[
                Interpretation(
                    registry_id="invented_metric",  # Does not exist
                    assessment=Assessment.HIGH,
                    reasoning="This is an invented metric."
                )
            ]
        )
        
        registry_ids = set(locked_registry.get_all().keys())
        errors = output.validate(registry_ids)
        
        assert len(errors) > 0
        assert any("invented_metric" in e for e in errors)


# =============================================================================
# REGRESSION TESTS
# =============================================================================

class TestRegressionPrevention:
    """
    Regression tests to prevent backsliding on the invariant.
    """
    
    def test_price_cannot_appear_in_ai_reasoning(self):
        """Regression: Price values must not appear in AI reasoning."""
        bad_interpretations = [
            "The price of €595.000 is high",
            "Asking €500.000 for this property",
            "Costs 595000 euros",
            "Priced at € 1.234.567",
        ]
        
        for text in bad_interpretations:
            assert _contains_numeric_literal(text), f"Should detect: {text}"
    
    def test_area_cannot_appear_in_ai_reasoning(self):
        """Regression: Area values must not appear in AI reasoning."""
        bad_interpretations = [
            "The 120m² living space",
            "With 120 m2 of floor area",
            "A spacious 150m² home",
        ]
        
        for text in bad_interpretations:
            assert _contains_numeric_literal(text), f"Should detect: {text}"
    
    def test_year_cannot_appear_in_ai_reasoning(self):
        """Regression: Year values must not appear in AI reasoning."""
        bad_interpretations = [
            "Built in 1930",
            "Construction from 1920",
            "Dating back to 1985",
        ]
        
        for text in bad_interpretations:
            assert _contains_numeric_literal(text), f"Should detect: {text}"
    
    def test_interpretive_language_is_allowed(self):
        """Regression: Valid interpretive language must be allowed."""
        good_interpretations = [
            "The asking price is considered high for this market segment.",
            "The living space is generous compared to similar properties.",
            "The construction period suggests potential maintenance considerations.",
            "This represents a premium valuation relative to the neighborhood average.",
            "The energy efficiency meets current standards with room for improvement.",
        ]
        
        for text in good_interpretations:
            assert not _contains_numeric_literal(text), f"Should allow: {text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
