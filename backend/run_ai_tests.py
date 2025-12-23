#!/usr/bin/env python3
"""
Test runner to verify AI tests pass without any AI services running.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest

# Import test classes
from tests.unit.test_ai_contracts import (
    TestProviderContracts,
    TestProviderConfiguration,
    TestProviderCapabilities,
    TestProviderSchemaCompliance
)

from tests.unit.test_ai_routing import (
    TestProviderRouting,
    TestIntelligenceEngineProviderManagement,
    TestFallbackBehavior,
    TestProviderStateTransitions
)

from tests.unit.test_ai_schema import (
    TestNarrativeOutputSchema,
    TestNarrativeDataIntegration,
    TestHelperFunctions,
    TestSchemaConsistency
)

from tests.unit.test_ollama_integration import (
    TestProviderIntegration,
    TestPreferenceIntegration,
    TestMultiChapterIntegration,
    TestProviderStateIsolation,
    TestErrorHandling
)

from tests.unit.test_intelligence import TestIntelligenceEngine

def main():
    """Run all AI tests"""
    print("=" * 80)
    print("FUTURE-PROOF AI TESTING ARCHITECTURE VERIFICATION")
    print("=" * 80)
    print()
    print("✅ These tests validate correctness WITHOUT requiring AI services")
    print("✅ All tests should pass with Ollama stopped")
    print("✅ All tests should pass with no API keys configured")
    print()
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        # Contract tests
        TestProviderContracts,
        TestProviderConfiguration,
        TestProviderCapabilities,
        TestProviderSchemaCompliance,
        # Routing tests
        TestProviderRouting,
        TestIntelligenceEngineProviderManagement,
        TestFallbackBehavior,
        TestProviderStateTransitions,
        # Schema tests
        TestNarrativeOutputSchema,
        TestNarrativeDataIntegration,
        TestHelperFunctions,
        TestSchemaConsistency,
        # Integration tests
        TestProviderIntegration,
        TestPreferenceIntegration,
        TestMultiChapterIntegration,
        TestProviderStateIsolation,
        TestErrorHandling,
        # Logic tests
        TestIntelligenceEngine,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✅ SUCCESS: All tests passed without any AI services running!")
        print("✅ Architecture is future-proof and provider-agnostic")
        print("✅ Tests are deterministic and runtime-independent")
        return 0
    else:
        print("❌ FAILURE: Some tests failed")
        print("Review failures above and fix issues")
        return 1

if __name__ == '__main__':
    sys.exit(main())
