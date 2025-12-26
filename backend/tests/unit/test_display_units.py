# TEST_REGIME: STRUCTURAL
# REQUIRES: offline_structural_mode=True
"""
Display Units Tests - Using Correct Pipeline API

Test that units (m², €, etc.) are not duplicated in display.
All tests use execute_report_pipeline() - the ONLY valid path.
"""
import os
import unittest
import re

# Set test mode BEFORE imports
os.environ["PIPELINE_TEST_MODE"] = "true"

from backend.pipeline.bridge import execute_report_pipeline


class TestDisplayUnits(unittest.TestCase):
    """Test that units (m², €, etc.) are not duplicated in display"""
    
    @classmethod
    def setUpClass(cls):
        # T4f: Enable Offline Structural Mode
        # MUST reset singleton FIRST to ensure it reads TEST environment
        from backend.domain.governance_state import GovernanceStateManager
        GovernanceStateManager._instance = None
        
        from backend.domain.governance_state import get_governance_state
        from backend.domain.config import GovernanceConfig, DeploymentEnvironment
        cls.gov_state = get_governance_state()
        cls.original_config = cls.gov_state.get_current_config()
        cls.gov_state.apply_config(
            GovernanceConfig(
                environment=DeploymentEnvironment.TEST,
                offline_structural_mode=True
            ),
            source="test_display_units"
        )
        
        cls.core_data = {
            "address": "Teststraat 123",
            "asking_price_eur": 500000,
            "living_area_m2": 165,
            "plot_area_m2": 634,
            "build_year": 1988,
            "energy_label": "B",
            "rooms": 5,
            "description": "Test property description"
        }
        cls.chapters, cls.kpis, cls.enriched, cls.core_summary = execute_report_pipeline(
            run_id="test-display-units",
            raw_data=cls.core_data,
            preferences={}
        )

    @classmethod
    def tearDownClass(cls):
        from backend.domain.governance_state import GovernanceStateManager
        # Reset singleton so the next test gets a fresh state
        GovernanceStateManager._instance = None
    
    def test_no_duplicate_m2_in_metrics(self):
        """Check that m² is not duplicated in metric displays"""
        for ch_id, ch_data in self.chapters.items():
            if not ch_data.get("grid_layout"):
                continue
            
            metrics = ch_data["grid_layout"].get("metrics", [])
            for metric in metrics:
                value = str(metric.get("value", ""))
                label = metric.get("label", "")
                
                # Check for duplicate m²
                if "m²" in value or "m2" in value:
                    m2_count = value.count("m²") + value.count("m2")
                    self.assertLessEqual(m2_count, 1, 
                        f"Chapter {ch_id}, metric '{label}': Duplicate m² in value '{value}'")
    
    def test_no_duplicate_m2_in_hero(self):
        """Check that m² is not duplicated in hero labels"""
        for ch_id, ch_data in self.chapters.items():
            if not ch_data.get("grid_layout"):
                continue
            
            hero = ch_data["grid_layout"].get("hero", {})
            labels = hero.get("labels", [])
            
            for label in labels:
                if "m²" in str(label) or "m2" in str(label):
                    m2_count = str(label).count("m²") + str(label).count("m2")
                    self.assertLessEqual(m2_count, 1,
                        f"Chapter {ch_id}, hero label: Duplicate m² in '{label}'")
    
    def test_kpis_have_correct_values(self):
        """Verify KPIs contain expected metrics"""
        self.assertIn("dashboard_cards", self.kpis)
        self.assertGreater(len(self.kpis["dashboard_cards"]), 0)
    
    def test_enriched_core_prices_are_numeric(self):
        """Verify that enriched core has numeric prices"""
        price = self.enriched.get("asking_price_eur")
        if price is not None:
            self.assertIsInstance(price, (int, float))


if __name__ == "__main__":
    unittest.main()
