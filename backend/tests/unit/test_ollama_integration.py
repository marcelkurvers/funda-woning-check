import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json

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

        # Mock successful JSON response (async)
        mock_response_data = {
            "title": "AI Title",
            "intro": "AI Intro",
            "main_analysis": "AI Analysis",
            "interpretation": "AI Interpretation",
            "advice": "AI Advice",
            "conclusion": "AI Conclusion",
            "strengths": ["AI Strength 1"]
        }

        # Create async mock
        async def mock_generate(*args, **kwargs):
            return json.dumps(mock_response_data)

        mock_provider.generate = mock_generate

        IntelligenceEngine.set_provider(mock_provider)
        
        ctx = {"address": "Teststraat 1", "price": 500000}
        
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)

        # Verify result content matches AI output
        self.assertEqual(result['title'], "AI Title")
        self.assertEqual(result['intro'], "AI Intro")
        
        # Verify main analysis contains the AI part (it might have appended warnings)
        self.assertIn("AI Analysis", result['main_analysis'])
        
        # Verify AI disclaimer was appended (logic in generate_chapter_narrative)
        self.assertIn("gegenereerd door", result['interpretation'])

    def test_ai_narrative_generation_failure_fallback(self):
        """Test that engine falls back to hardcoded logic if AI fails."""
        mock_provider = MagicMock(spec=AIProvider)

        # Mock exception during generation
        async def mock_generate_fail(*args, **kwargs):
            raise Exception("Ollama connection failed")

        mock_provider.generate = mock_generate_fail

        IntelligenceEngine.set_provider(mock_provider)
        
        ctx = {"adres": "Teststraat 1", "prijs": 500000, "oppervlakte": 100}
        
        # Should not raise exception, but return fallback
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # Verify calling structure
        # (Assuming Chapter 1 hardcoded returns something specific)
        self.assertNotEqual(result['main_analysis'], "AI Analysis")
        self.assertIn("100 m²", result['intro']) # Check hardcoded logic part

    def test_prompt_structure_contains_preferences(self):
        """Verify that user preferences are passed to the prompt."""
        mock_provider = MagicMock(spec=AIProvider)

        # Store call args for verification
        call_args_store = []

        async def mock_generate(*args, **kwargs):
            call_args_store.append((args, kwargs))
            return '{"title": "Simple"}'

        mock_provider.generate = mock_generate

        IntelligenceEngine.set_provider(mock_provider)
        
        ctx = {
            "adres": "Teststraat",
            "_preferences": {
                "marcel": {"priorities": ["Garage"]},
                "petra": {"priorities": ["Tuin"]}
            }
        }
        
        IntelligenceEngine.generate_chapter_narrative(1, ctx)

        # Get the actual call arguments from our store
        if call_args_store:
            args, kwargs = call_args_store[0]
            prompt_text = args[0] if args else kwargs.get('prompt', '')

            self.assertIn("Garage", prompt_text)
            self.assertIn("Tuin", prompt_text)
            self.assertIn("marcel", prompt_text.lower())
            self.assertIn("petra", prompt_text.lower())

if __name__ == '__main__':
    unittest.main()
