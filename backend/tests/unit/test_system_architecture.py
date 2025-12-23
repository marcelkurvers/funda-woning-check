
import sys
import os
import json
from pathlib import Path
import pytest

# Add project root to path (one level up from backend)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.domain.registry import CanonicalRegistry, RegistryEntry, RegistryType
from backend.domain.ownership import OwnershipMap
from backend.validation.gate import ValidationGate
from backend.enrichment import DataEnricher

class TestSystemArchitecture:
    """
    Verifies the 4-Layer System Enforcement Architecture.
    """

    def test_layer_1_registry(self):
        """Layer 1: Canonical Registry must exist before AI reasoning."""
        raw = {
            "asking_price_eur": 500000,
            "living_area_m2": 120,
            "energy_label": "A",
            "build_year": 1990
        }
        
        # Run Enricher
        enriched = DataEnricher.enrich(raw)
        
        assert "_layer1_complete" in enriched, "Layer 1 completion flag missing"
        assert enriched.get("valuation_status"), "Derived variable missing"
        assert "price_per_m2" in enriched, "Calculated metric missing"

    def test_layer_2_ownership(self):
        """Layer 2: Ownership & Scope Resolution must enforce data visibility."""
        
        full_ctx = {
            "asking_price_eur": 500000,
            "living_area_m2": 120,
            "garden_size": 50,
            "media_urls": ["http://ex.com/1.jpg"],
            "tuin_grootte": "50m2"
        }
        
        # Chapter 0 should see core data (Executive Summary)
        ctx_0 = OwnershipMap.get_chapter_context(0, full_ctx)
        assert "asking_price_eur" in ctx_0, "Chapter 0 blocked from core data"
        
        # Chapter 7 (Garden) should NOT see price, but should see garden vars
        ctx_7 = OwnershipMap.get_chapter_context(7, full_ctx)
        assert "asking_price_eur" not in ctx_7, "Layer 2 Failed: Chapter 7 sees asking_price_eur"
        assert "tuin_grootte" in ctx_7, "Layer 2 Failed: Chapter 7 does NOT see owned variable"

    def test_layer_4_validation(self):
        """Layer 4: Validation Gate must reject duplicates and bad structures."""
        
        chapter_id = 7 # Garden
        registry_ctx = {"asking_price_eur": 500000}
        
        # CASE A: Good output (includes required fields id and title)
        output_good = {
            "id": "7",
            "title": "Garden Analysis",
            "variables": {"tuin_grootte": "50m2"}, # assuming allowed
            "main_analysis": "Mooie tuin met veel privacy.",
            "comparison": {"marcel": "Prima tuin. Dit is top.", "petra": "Fijne tuin. Ik hou ervan."}
        }
        
        errors = ValidationGate.validate_chapter_output(chapter_id, output_good, registry_ctx)
        assert not errors, f"Good output failed validation: {errors}"
            
        # CASE B: Duplicate Fact in Output (Ownership Violation)
        output_bad_var = {
            "id": "7",
            "title": "Garden",
            "variables": {"asking_price_eur": "500000"}, # NOT allowed in Ch 7
            "main_analysis": "Duur grapje met mooie tuin.",
            "comparison": {"marcel": "x-short-text", "petra": "y-short-text"}
        }
        
        errors = ValidationGate.validate_chapter_output(chapter_id, output_bad_var, registry_ctx)
        assert any("Ownership Violation" in e for e in errors), f"Failed to catch Ownership Violation: {errors}"
            
        # CASE C: Missing Preference Reasoning
        output_bad_pref = {
            "id": "7",
            "title": "Garden",
            "variables": {},
            "main_analysis": "Some analysis here.",
            "comparison": {"marcel": "", "petra": ""} # Too short/empty
        }
        errors = ValidationGate.validate_chapter_output(chapter_id, output_bad_pref, registry_ctx)
        assert any("preference reasoning" in e.lower() for e in errors), f"Failed to catch missing preferences: {errors}"

if __name__ == "__main__":
    pytest.main([__file__])
