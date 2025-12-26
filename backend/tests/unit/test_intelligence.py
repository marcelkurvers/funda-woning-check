"""
IntelligenceEngine Logic Tests

ARCHITECTURAL UPDATE:
These tests now validate behavior under Governance Control.
When AI is missing, we rely on 'offline_structural_mode' (via Governance)
to provide skeletal structure for testing, rather than heuristic templates.

Tests validate:
1. Data parsing helpers (_parse_int)
2. Output structure compliance (Skeleton)
3. Governance-controlled fallback behavior
"""

import unittest
import os
from backend.intelligence import IntelligenceEngine


class TestIntelligenceEngine(unittest.TestCase):
    """Test IntelligenceEngine business logic and data processing"""

    def setUp(self):
        """Ensure tests run in fallback mode with explicit governance relaxation"""
        # Set AI provider to None to force fallback path
        IntelligenceEngine.set_provider(None)
        
        # PROACTIVE GOVERNANCE: Enable offline_structural_mode to allow fallback WITHOUT provider
        from backend.domain.governance_state import get_governance_state, GovernanceStateManager, DeploymentEnvironment
        from backend.domain.config import GovernanceConfig
        
        # Force TEST environment to allow config application
        self._old_env = os.environ.get("PIPELINE_TEST_MODE")
        os.environ["PIPELINE_TEST_MODE"] = "true"
        
        state = get_governance_state()
        # Apply permissive config for testing structure without AI
        config = GovernanceConfig(
            environment=DeploymentEnvironment.TEST,
            offline_structural_mode=True # explicitly allow no-provider mode
        )
        state.apply_config(config, source="test_intelligence")

    def tearDown(self):
        """Clean up provider and governance state after tests"""
        IntelligenceEngine.set_provider(None)
        
        # Reset Governance to strict default
        from backend.domain.governance_state import get_governance_state
        state = get_governance_state()
        state.reset(source="test_intelligence_teardown")
        
        # Restore env
        if self._old_env:
            os.environ["PIPELINE_TEST_MODE"] = self._old_env
        else:
            os.environ.pop("PIPELINE_TEST_MODE", None)

    def test_parse_int_helper(self):
        """Test the robust integer parsing logic used across chapters."""
        self.assertEqual(IntelligenceEngine._parse_int("200 m²"), 200)
        self.assertEqual(IntelligenceEngine._parse_int("€ 1.500.000"), 1500000)
        self.assertEqual(IntelligenceEngine._parse_int("1995"), 1995)
        self.assertEqual(IntelligenceEngine._parse_int("invalid"), 0)
        self.assertEqual(IntelligenceEngine._parse_int(None), 0)

    def test_generate_chapter_narrative_structure(self):
        """Ensure generated structure strictly follows the schema required by the Bento Grid."""
        context = {
            'address': 'Kalverstraat 1',
            'asking_price_eur': 500000,
            'living_area_m2': 120,
            'plot_area_m2': 0,
            'build_year': 1990,
            'energy_label': 'B'
        }
        # Test Chapter 1 (General)
        narrative = IntelligenceEngine.generate_chapter_narrative(1, context)
        
        # Required Keys for Frontend Mapping - Offline Mode provides a skeleton
        self.assertIn('intro', narrative)
        self.assertIn('main_analysis', narrative)
        self.assertIn('conclusion', narrative)
        
        # Check types
        self.assertIsInstance(narrative['intro'], str)
        if 'strengths' in narrative:
            self.assertIsInstance(narrative['strengths'], list)
        
        # Offline mode content check
        # The implementation returns placeholders
        self.assertIn("OFFLINE MODE", narrative['main_analysis'])

    def test_chapter_4_energy_logic(self):
        """
        Test Chapter 4 (Energy) output structure.
        """
        # Case 1: Green Label
        ctx_green = {
            'energy_label': 'A', 
            'build_year': 2022, 
            'address': 'Test'
        }
        nar_green = IntelligenceEngine.generate_chapter_narrative(4, ctx_green)
        
        # Should have proper structure
        self.assertIn('title', nar_green)
        self.assertIn('main_analysis', nar_green)
        
        # Offline mode just ensures structure exists
        self.assertIn("OFFLINE MODE", nar_green['main_analysis'])

    def test_chapter_0_executive_summary(self):
        """
        Test Chapter 0 (Executive Summary) output structure.
        """
        # Full Data
        ctx_full = {
            'address': 'Test', 
            'asking_price_eur': 500000, 
            'living_area_m2': 100, 
            'energy_label': 'C'
        }
        nar = IntelligenceEngine.generate_chapter_narrative(0, ctx_full)
        
        # Required structure
        self.assertIn('title', nar)
        self.assertIn('intro', nar)
        self.assertIn('main_analysis', nar)
        
        # Intro should have content (from placeholder)
        self.assertGreater(len(nar['intro']), 0)

    def test_fallback_uses_offline_mode(self):
        """
        ARCHITECTURAL TEST: Verify fallback uses offline structural mode.
        """
        IntelligenceEngine.set_provider(None)
        
        ctx = {
            'address': 'Teststraat 1',
            'asking_price_eur': 450000,
            'living_area_m2': 120,
            'energy_label': 'B'
        }
        
        result = IntelligenceEngine.generate_chapter_narrative(0, ctx)
        
        # Check provenance indicates offline mode
        provenance = result.get('_provenance', {})
        self.assertEqual(provenance.get('provider'), 'none')
        self.assertEqual(provenance.get('model'), 'none')

    def test_all_chapters_have_consistent_structure(self):
        """Verify all 14 chapters return consistent structure in offline mode."""
        ctx = {
            'address': 'Test',
            'asking_price_eur': 500000,
            'living_area_m2': 120,
            'build_year': 2000,
            'energy_label': 'B'
        }
        
        for chapter_id in range(14):
            result = IntelligenceEngine.generate_chapter_narrative(chapter_id, ctx)
            
            # All should return dict
            self.assertIsInstance(result, dict, f"Chapter {chapter_id} should return dict")
            
            # All should have title and main_analysis
            self.assertIn('title', result, f"Chapter {chapter_id} missing title")
            self.assertIn('main_analysis', result, f"Chapter {chapter_id} missing main_analysis")

if __name__ == '__main__':
    unittest.main()
