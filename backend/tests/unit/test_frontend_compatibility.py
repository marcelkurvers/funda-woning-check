# TEST_REGIME: STRUCTURAL
# REQUIRES: offline_structural_mode=True
"""
Frontend Compatibility Tests - Using Correct Pipeline API

Tests that verify generated chapters have correct structure for frontend.
All tests use execute_report_pipeline() - the ONLY valid path.
"""
import unittest
import os
import sys

# Set test mode BEFORE imports
os.environ["PIPELINE_TEST_MODE"] = "true"

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.pipeline.bridge import execute_report_pipeline


class TestRegression(unittest.TestCase):
    
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
            source="test_frontend_compatibility"
        )
        
        cls.core_data = {
            "address": "Test Street 1",
            "asking_price_eur": 500000,
            "living_area_m2": 100,
            "description": "Test property"
        }
        cls.chapters, cls.kpis, cls.enriched, cls.core_summary = execute_report_pipeline(
            run_id="test-frontend-compat",
            raw_data=cls.core_data,
            preferences={}
        )

    @classmethod
    def tearDownClass(cls):
        from backend.domain.governance_state import GovernanceStateManager
        # Reset singleton so the next test gets a fresh state
        GovernanceStateManager._instance = None
    
    def test_chapter_id_present(self):
        """Verify that every generated chapter has an 'id' field for frontend sorting."""
        for i in range(14):
            key = str(i)
            self.assertIn(key, self.chapters, f"Chapter {key} should be in chapters dict")
            self.assertIn("id", self.chapters[key], f"Chapter {key} MISSING 'id' field")
            self.assertEqual(self.chapters[key]["id"], key, f"Chapter {key} id mismatch")

    def test_chapter_has_title(self):
        """Verify that every generated chapter has a 'title' field."""
        for i in range(14):
            key = str(i)
            self.assertIn("title", self.chapters[key], f"Chapter {key} MISSING 'title' field")
            self.assertIsNotNone(self.chapters[key]["title"], f"Chapter {key} has None title")

    def test_chapter_has_grid_layout(self):
        """Verify that every generated chapter has a 'grid_layout' field."""
        for i in range(14):
            key = str(i)
            self.assertIn("grid_layout", self.chapters[key], f"Chapter {key} MISSING 'grid_layout' field")


if __name__ == "__main__":
    unittest.main()
