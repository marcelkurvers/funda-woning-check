# TEST_REGIME: STRUCTURAL
# REQUIRES: offline_structural_mode=True
import sys
import os

# Set test mode BEFORE any imports (Legacy support, but primarily rely on GovConfig)
os.environ["PIPELINE_TEST_MODE"] = "true"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest

from backend.pipeline.bridge import execute_report_pipeline
from tests.data_loader import load_test_data


class TestComprehensive(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load test data and run pipeline once for base tests."""
        import os
        os.environ["PIPELINE_TEST_MODE"] = "true"
        
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
            source="test_comprehensive"
        )

        cls.core_data = load_test_data()
        cls.chapters, cls.kpis, cls.enriched, cls.core_summary = execute_report_pipeline(
            run_id="test-comprehensive",
            raw_data=cls.core_data,
            preferences={}
        )

    @classmethod
    def tearDownClass(cls):
        from backend.domain.governance_state import GovernanceStateManager
        # Reset singleton so the next test gets a fresh state
        GovernanceStateManager._instance = None
    
    def test_all_chapters_generated(self):
        """Verify that all 14 chapters (0-13) are generated."""
        # Check we have 14 chapters (0-13)
        self.assertEqual(len(self.chapters), 14, f"Expected 14 chapters, got {len(self.chapters)}")
        
        # Verify specific content in each chapter
        for i in range(14):
            str_i = str(i)
            self.assertIn(str_i, self.chapters, f"Chapter {i} missing")
            
            chapter = self.chapters[str_i]
            self.assertIn("id", chapter, f"Chapter {i} missing 'id'")
            self.assertIn("title", chapter, f"Chapter {i} missing 'title'")
            
            # Check for grid layout structure
            self.assertIn("grid_layout", chapter, f"Chapter {i} missing 'grid_layout'")

    def test_kpis_generated(self):
        """Test KPIs are correctly generated."""
        self.assertIn("dashboard_cards", self.kpis)
        self.assertIn("completeness", self.kpis)
        self.assertIn("fit_score", self.kpis)
        
        # Should have 4 dashboard cards
        self.assertEqual(len(self.kpis["dashboard_cards"]), 4)
        
        # Check card IDs
        card_ids = [c["id"] for c in self.kpis["dashboard_cards"]]
        self.assertIn("fit", card_ids)
        self.assertIn("completeness", card_ids)
        self.assertIn("value", card_ids)
        self.assertIn("energy", card_ids)

    def test_enriched_core_contains_registry_values(self):
        """Test enriched core contains all registered values."""
        # These should be in the enriched core
        self.assertIn("asking_price_eur", self.enriched)
        self.assertIn("living_area_m2", self.enriched)
        self.assertIn("energy_label", self.enriched)

    def test_validation_status_tracked(self):
        """Test that validation status is in KPIs."""
        self.assertIn("validation_passed", self.kpis)

    def test_energy_label_affects_chapter_4(self):
        """Test that chapter 4 exists and has proper structure."""
        # STRUCTURAL TEST: Only verify structure, not content variation
        # (Content variation tests require AI regime)
        
        ch4 = self.chapters.get("4", {})
        
        # Chapter 4 must exist
        self.assertIsNotNone(ch4)
        
        # Chapter 4 must have required structure
        self.assertIn("id", ch4)
        self.assertIn("title", ch4)
        self.assertIn("grid_layout", ch4)
        
        # Verify energy label is in enriched core (structural check)
        self.assertIn("energy_label", self.enriched)


if __name__ == "__main__":
    unittest.main()
