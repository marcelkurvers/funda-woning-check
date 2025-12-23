import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json
import asyncio

# Adjust path to include backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from intelligence import IntelligenceEngine
from ai.provider_interface import AIProvider

class TestOllamaIntegration(unittest.TestCase):

    def setUp(self):
        # Reset provider before each test
        IntelligenceEngine.set_provider(None)

    def tearDown(self):
        # Ensure provider is reset after tests too
        IntelligenceEngine.set_provider(None)

    def test_provider_injection(self):
        """Test that the provider can be injected into the engine."""
        mock_provider = MagicMock(spec=AIProvider)
        IntelligenceEngine.set_provider(mock_provider)
        self.assertIsNotNone(IntelligenceEngine._provider)
        self.assertEqual(IntelligenceEngine._provider, mock_provider)

    def test_ai_narrative_generation_success(self):
        """Test successful AI generation overrides hardcoded logic."""
        mock_provider = MagicMock(spec=AIProvider)
        mock_provider.name = "ollama"

        # Mock successful JSON response (async)
        # Matches the structure expected by IntelligenceEngine._generate_ai_narrative
        mock_response_data = {
            "title": "AI Title",
            "intro": "AI Intro",
            "main_analysis": "AI Analysis",
            "variables": {
                "var1": {"value": "val1", "status": "fact", "reasoning": "r1"}
            },
            "comparison": {"marcel": "m1", "petra": "p1"},
            "strengths": ["AI Strength 1"],
            "advice": ["AI Advice 1"],
            "conclusion": "AI Conclusion",
            "metadata": {
                "confidence": "high",
                "inferred_vars": [],
                "missing_vars": []
            }
        }

        # Create async mock
        async def mock_generate(*args, **kwargs):
            return json.dumps(mock_response_data)

        mock_provider.generate = mock_generate

        IntelligenceEngine.set_provider(mock_provider)
        
        ctx = {"address": "Teststraat 1", "price": 500000}
        
        # We need to mock safe_execute_async if we are in a sync test context
        import asyncio
        with patch('ai.bridge.safe_execute_async', side_effect=lambda coro: asyncio.run(coro)):
            result = IntelligenceEngine.generate_chapter_narrative(1, ctx)

        # Verify result content matches AI output
        self.assertEqual(result['title'], "AI Title")
        self.assertEqual(result['intro'], "AI Intro")
        
        # Verify main analysis contains the AI part
        self.assertIn("AI Analysis", result['main_analysis'])
        
        # Verify AI disclaimer was appended (logic in generate_chapter_narrative)
        self.assertIn("gegenereerd door", result['interpretation'])

    def test_ai_narrative_generation_failure_raises(self):
        """Test that engine raises exception if AI fails, as requested by current implementation."""
        mock_provider = MagicMock(spec=AIProvider)

        # Mock exception during generation
        async def mock_generate_fail(*args, **kwargs):
            raise Exception("Ollama connection failed")

        mock_provider.generate = mock_generate_fail

        IntelligenceEngine.set_provider(mock_provider)
        
        ctx = {"adres": "Teststraat 1", "prijs": 500000, "oppervlakte": 100}
        
        # Now it re-raises as requested in the current code
        with patch('ai.bridge.safe_execute_async', side_effect=lambda coro: asyncio.run(coro)):
            with self.assertRaises(Exception):
                IntelligenceEngine.generate_chapter_narrative(1, ctx)

    def test_prompt_structure_contains_preferences(self):
        """Verify that user preferences are passed to the prompt."""
        mock_provider = MagicMock(spec=AIProvider)
        mock_provider.name = "ollama"

        # Store call args for verification
        call_args_store = []

        async def mock_generate(*args, **kwargs):
            call_args_store.append((args, kwargs))
            return '{"title": "Simple", "metadata": {"confidence": "high"}}'

        mock_provider.generate = mock_generate

        IntelligenceEngine.set_provider(mock_provider)
        
        ctx = {
            "adres": "Teststraat",
            "_preferences": {
                "marcel": {"priorities": ["Garage"]},
                "petra": {"priorities": ["Tuin"]}
            }
        }
        
        with patch('ai.bridge.safe_execute_async', side_effect=lambda coro: asyncio.run(coro)):
            IntelligenceEngine.generate_chapter_narrative(1, ctx)

        # Get the actual call arguments from our store
        if call_args_store:
            args, kwargs = call_args_store[0]
            prompt_text = args[0] if args else kwargs.get('prompt', '')

            self.assertIn("Garage", prompt_text)
            self.assertIn("Tuin", prompt_text)
            self.assertIn("Marcel", prompt_text) # Prompt uses "Marcel" instead of "marcel" keys
            self.assertIn("Petra", prompt_text)

if __name__ == '__main__':
    unittest.main()
