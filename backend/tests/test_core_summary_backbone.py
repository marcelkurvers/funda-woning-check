"""
Test CoreSummary Backbone Contract

This test suite enforces the MANDATORY CoreSummary contract.

ARCHITECTURAL LAWS TESTED:
1. CoreSummary is ALWAYS present in pipeline output
2. CoreSummary is built from CanonicalRegistry ONLY (never AI/chapters)
3. CoreSummary is constructed BEFORE any AI/chapter generation
4. API responses MUST contain CoreSummary
5. Dashboard KPIs come EXCLUSIVELY from CoreSummary

If any test fails, the backbone contract is violated.
"""

import pytest
import json
from backend.domain.core_summary import CoreSummary, CoreSummaryBuilder, CoreField, DataStatus
from backend.domain.registry import CanonicalRegistry, RegistryEntry, RegistryType
from backend.domain.pipeline_context import create_pipeline_context, PipelineViolation


class TestCoreSummaryBackboneContract:
    """
    Test suite for CoreSummary backbone contract enforcement.
    """
    
    def test_core_summary_always_built_after_registry_lock(self):
        """
        LAW 1: CoreSummary is ALWAYS built when registry is locked.
        
        This ensures CoreSummary exists before any AI/chapter work.
        """
        # Create context
        ctx = create_pipeline_context("test-run-001")
        
        # Add some data
        ctx.set_raw_data({"asking_price_eur": "500000", "living_area_m2": "120"})
        
        # Register facts
        ctx.register_fact("asking_price_eur", "500000", "Asking Price", RegistryType.FACT)
        ctx.register_fact("living_area_m2", "120", "Living Area", RegistryType.FACT)
        ctx.register_fact("address", "Amsterdam", "Address", RegistryType.FACT)
        ctx.register_fact("total_match_score", "75", "Match Score", RegistryType.KPI)
        
        # Complete enrichment and lock
        ctx.complete_enrichment()
        ctx.lock_registry()
        
        # === ASSERTION: CoreSummary MUST exist after lock ===
        core_summary = ctx.get_core_summary()
        assert core_summary is not None, "CoreSummary MUST be built after registry lock"
        assert isinstance(core_summary, CoreSummary), "CoreSummary must be a CoreSummary instance"
        
        # Verify required fields are present
        assert core_summary.asking_price is not None
        assert core_summary.living_area is not None
        assert core_summary.location is not None
        assert core_summary.match_score is not None
    
    def test_core_summary_fails_before_registry_lock(self):
        """
        LAW 2: CoreSummary is NOT available before registry is locked.
        
        This ensures proper pipeline ordering.
        """
        ctx = create_pipeline_context("test-run-002")
        ctx.set_raw_data({"asking_price_eur": "500000"})
        
        # === ASSERTION: Getting CoreSummary before lock MUST fail ===
        with pytest.raises(PipelineViolation, match="CoreSummary not available"):
            ctx.get_core_summary()
    
    def test_core_summary_built_from_registry_only(self):
        """
        LAW 3: CoreSummary is built DIRECTLY from CanonicalRegistry.
        
        It NEVER uses AI, chapters, or external data.
        """
        # Create a registry
        registry = CanonicalRegistry()
        
        # Register facts
        registry.register(RegistryEntry(
            id="asking_price_eur",
            type=RegistryType.FACT,
            value="450000",
            name="Asking Price",
            source="parser"
        ))
        registry.register(RegistryEntry(
            id="living_area_m2",
            type=RegistryType.FACT,
            value="95",
            name="Living Area",
            source="parser"
        ))
        registry.register(RegistryEntry(
            id="address",
            type=RegistryType.FACT,
            value="Rotterdam, Zuid-Holland",
            name="Address",
            source="parser"
        ))
        registry.register(RegistryEntry(
            id="total_match_score",
            type=RegistryType.KPI,
            value="82",
            name="Match Score",
            source="enricher"
        ))
        
        registry.lock()
        
        # === ASSERTION: Build CoreSummary from registry ===
        core_summary = CoreSummaryBuilder.build_from_registry(registry)
        
        assert core_summary is not None
        assert core_summary.asking_price.value == "€ 450.000"  # Formatted
        assert core_summary.asking_price.status == DataStatus.PRESENT
        assert core_summary.asking_price.source == "asking_price_eur"
        
        assert core_summary.living_area.value == "95 m²"  # Formatted
        assert core_summary.living_area.status == DataStatus.PRESENT
        
        assert core_summary.match_score.value == "82%"  # Formatted
        assert core_summary.match_score.status == DataStatus.PRESENT
    
    def test_core_summary_handles_missing_data_gracefully(self):
        """
        LAW 4: CoreSummary NEVER fails - missing data is marked as UNKNOWN.
        
        This ensures fail-closed behavior without breaking the pipeline.
        """
        # Create empty registry
        registry = CanonicalRegistry()
        registry.lock()
        
        # === ASSERTION: CoreSummary can be built even with no data ===
        core_summary = CoreSummaryBuilder.build_from_registry(registry)
        
        assert core_summary is not None
        assert core_summary.asking_price.status == DataStatus.UNKNOWN
        assert core_summary.asking_price.value == "onbekend"
        assert core_summary.living_area.status == DataStatus.UNKNOWN
        assert core_summary.location.status == DataStatus.UNKNOWN
        assert core_summary.match_score.status == DataStatus.UNKNOWN
        
        # Completeness should be 0.0
        assert core_summary.completeness_score == 0.0
    
    def test_core_summary_completeness_calculation(self):
        """
        LAW 5: CoreSummary tracks data completeness accurately.
        """
        registry = CanonicalRegistry()
        
        # Add 2 out of 4 required fields
        registry.register(RegistryEntry(
            id="asking_price_eur",
            type=RegistryType.FACT,
            value="300000",
            name="Price",
            source="parser"
        ))
        registry.register(RegistryEntry(
            id="living_area_m2",
            type=RegistryType.FACT,
            value="80",
            name="Area",
            source="parser"
        ))
        # address and total_match_score are missing
        
        registry.lock()
        core_summary = CoreSummaryBuilder.build_from_registry(registry)
        
        # === ASSERTION: Completeness reflects actual data availability ===
        # 2 present out of 4 required = 0.5
        assert core_summary.completeness_score == 0.5
    
    def test_core_summary_provenance_tracking(self):
        """
        LAW 6: CoreSummary tracks provenance for every field.
        
        This ensures traceability back to the registry.
        """
        registry = CanonicalRegistry()
        registry.register(RegistryEntry(
            id="asking_price_eur",
            type=RegistryType.FACT,
            value="600000",
            name="Price",
            source="parser"
        ))
        registry.lock()
        
        core_summary = CoreSummaryBuilder.build_from_registry(registry)
        
        # === ASSERTION: Provenance is tracked ===
        assert "asking_price" in core_summary.provenance
        assert core_summary.provenance["asking_price"] == "asking_price_eur"
        assert core_summary.asking_price.source == "asking_price_eur"
    
    def test_core_summary_serialization(self):
        """
        LAW 7: CoreSummary can be serialized to dict for API responses.
        """
        registry = CanonicalRegistry()
        registry.register(RegistryEntry(
            id="asking_price_eur",
            type=RegistryType.FACT,
            value="550000",
            name="Price",
            source="parser"
        ))
        registry.register(RegistryEntry(
            id="living_area_m2",
            type=RegistryType.FACT,
            value="110",
            name="Area",
            source="parser"
        ))
        registry.register(RegistryEntry(
            id="address",
            type=RegistryType.FACT,
            value="Utrecht",
            name="Address",
            source="parser"
        ))
        registry.register(RegistryEntry(
            id="total_match_score",
            type=RegistryType.KPI,
            value="68",
            name="Match",
            source="enricher"
        ))
        registry.lock()
        
        core_summary = CoreSummaryBuilder.build_from_registry(registry)
        
        # === ASSERTION: Can serialize to dict ===
        data = core_summary.model_dump()
        
        assert isinstance(data, dict)
        assert "asking_price" in data
        assert "living_area" in data
        assert "location" in data
        assert "match_score" in data
        assert "completeness_score" in data
        assert "provenance" in data
        
        # Can be JSON serialized
        json_str = json.dumps(data)
        assert json_str is not None
        
        # Can be deserialized
        restored = json.loads(json_str)
        assert restored["asking_price"]["value"] == "€ 550.000"
    
    def test_core_summary_fallback_from_dict(self):
        """
        LAW 8: CoreSummary can be built from legacy dict for backward compatibility.
        """
        legacy_data = {
            "asking_price_eur": "400000",
            "living_area_m2": "90",
            "address": "Den Haag, Zuid-Holland",
            "total_match_score": "71"
        }
        
        # === ASSERTION: Can build from dict ===
        core_summary = CoreSummaryBuilder.build_from_dict(legacy_data)
        
        assert core_summary is not None
        assert core_summary.asking_price.status == DataStatus.PRESENT
        assert "400" in core_summary.asking_price.value
        assert core_summary.living_area.status == DataStatus.PRESENT
        assert "90" in core_summary.living_area.value


class TestCoreSummaryPipelineIntegration:
    """
    Integration tests for CoreSummary in the full pipeline.
    """
    
    def test_pipeline_output_contains_core_summary(self):
        """
        LAW 9: Pipeline output MUST contain CoreSummary.
        
        This is tested via the spine's get_renderable_output.
        """
        from backend.pipeline.spine import PipelineSpine
        
        spine = PipelineSpine("test-integration-001")
        
        # Ingest minimal data
        spine.ingest_raw_data({
            "asking_price_eur": "350000",
            "living_area_m2": "75",
            "address": "Eindhoven"
        })
        
        # Enrich and lock
        spine.enrich_and_populate_registry()
        
        # === ASSERTION: CoreSummary exists after enrichment ===
        core_summary = spine.ctx.get_core_summary()
        assert core_summary is not None, "CoreSummary must exist after enrichment"
        assert core_summary.asking_price.status == DataStatus.PRESENT
        assert core_summary.living_area.status == DataStatus.PRESENT
        
        # Begin chapter generation (required before rendering)
        spine.ctx.begin_chapter_generation()
        
        # Mark phase as complete (simulate chapter generation)
        spine._phase = "chapters_generated"
        
        # === ASSERTION: Output contains core_summary ===
        output = spine.get_renderable_output(strict=False)
        
        assert "core_summary" in output, "Pipeline output MUST contain core_summary"
        assert output["core_summary"] is not None
        assert "asking_price" in output["core_summary"]
        assert "living_area" in output["core_summary"]
        assert "location" in output["core_summary"]
        assert "match_score" in output["core_summary"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
