# TEST_REGIME: STRUCTURAL
# REQUIRES: offline_structural_mode=True
"""
Integration Fixtures Tests - Using Correct Pipeline API

Tests using HTML fixtures to verify chapter generation.
All tests use execute_report_pipeline() - the ONLY valid path.
"""
import sys
import os

# Set test mode BEFORE imports
os.environ["PIPELINE_TEST_MODE"] = "true"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest

from parser import Parser
from backend.pipeline.bridge import execute_report_pipeline


class TestFixturesOutput(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # T4gB-FIX: Apply governance singleton pattern
        from backend.domain.governance_state import GovernanceStateManager
        GovernanceStateManager._instance = None
        
        from backend.domain.governance_state import get_governance_state
        from backend.domain.config import GovernanceConfig, DeploymentEnvironment
        cls.gov_state = get_governance_state()
        cls.gov_state.apply_config(
            GovernanceConfig(
                environment=DeploymentEnvironment.TEST,
                offline_structural_mode=True
            ),
            source="test_integration_fixtures"
        )

    @classmethod
    def tearDownClass(cls):
        from backend.domain.governance_state import GovernanceStateManager
        GovernanceStateManager._instance = None

    def test_fixtures_generation(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define directories to search
        search_dirs = [
            os.path.join(base_dir, "../fixtures"),
            os.path.join(base_dir, "../../../test-data")
        ]
        
        test_files = []
        for d in search_dirs:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.endswith(".html") or f == "test-html":
                        test_files.append(os.path.join(d, f))
                        
        if not test_files:
            self.skipTest(f"No test files found in {search_dirs}")
            
        print(f"Found {len(test_files)} test files")
        
        for fixtures_path in test_files:
            with self.subTest(file=fixtures_path):
                print(f"\n Testing file: {fixtures_path}")
                
                with open(fixtures_path, "r", encoding="utf-8") as f:
                    html_content = f.read()

                # Parse Data
                parser = Parser()
                core_data = parser.parse_html(html_content)

                # Generate Chapters through pipeline
                chapters, kpis, enriched, core_summary = execute_report_pipeline(
                    run_id=f"test-fixtures-{os.path.basename(fixtures_path)}",
                    raw_data=core_data,
                    preferences={}
                )

                # Verify Output
                chapters_found = len(chapters)
                print(f"Generated {chapters_found} chapters.")
                
                self.assertEqual(chapters_found, 14, "Should have generated 14 chapters")

                for i in range(14):
                    cid = str(i)
                    self.assertIn(cid, chapters, f"Chapter {cid} missing from output")
                    
                    ch = chapters[cid]
                    self.assertIn("title", ch, f"Chapter {cid} has no title")
                    self.assertIn("grid_layout", ch, f"Chapter {cid} has no grid_layout")


if __name__ == "__main__":
    unittest.main()
