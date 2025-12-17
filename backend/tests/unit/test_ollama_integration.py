import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json

# Adjust path to include backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from intelligence import IntelligenceEngine
from ollama_client import OllamaClient

class TestOllamaIntegration(unittest.TestCase):
    
    def setUp(self):
        # Reset client before each test
        IntelligenceEngine.set_client(None)
    
    def test_client_injection(self):
        """Test that the client can be injected into the engine."""
        mock_client = MagicMock(spec=OllamaClient)
        IntelligenceEngine.set_client(mock_client)
        self.assertIsNotNone(IntelligenceEngine._client)
        self.assertEqual(IntelligenceEngine._client, mock_client)

    def test_ai_narrative_generation_success(self):
        """Test successful AI generation overrides hardcoded logic."""
        mock_client = MagicMock(spec=OllamaClient)
        
        # Mock successful JSON response
        mock_response_data = {
            "title": "AI Title",
            "intro": "AI Intro",
            "main_analysis": "AI Analysis",
            "interpretation": "AI Interpretation",
            "advice": "AI Advice",
            "conclusion": "AI Conclusion",
            "strengths": ["AI Strength 1"]
        }
        mock_client.generate.return_value = json.dumps(mock_response_data)
        
        IntelligenceEngine.set_client(mock_client)
        
        ctx = {"address": "Teststraat 1", "price": 500000}
        
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # Verify client was called
        mock_client.generate.assert_called_once()
        
        # Verify result content matches AI output
        self.assertEqual(result['title'], "AI Title")
        self.assertEqual(result['intro'], "AI Intro")
        
        # Verify main analysis contains the AI part (it might have appended warnings)
        self.assertIn("AI Analysis", result['main_analysis'])
        
        # Verify AI disclaimer was appended (logic in generate_chapter_narrative)
        self.assertIn("Deze analyse is gegenereerd met behulp van een AI", result['interpretation'])

    def test_ai_narrative_generation_failure_fallback(self):
        """Test that engine falls back to hardcoded logic if AI fails."""
        mock_client = MagicMock(spec=OllamaClient)
        
        # Mock exception during generation
        mock_client.generate.side_effect = Exception("Ollama connection failed")
        
        IntelligenceEngine.set_client(mock_client)
        
        ctx = {"adres": "Teststraat 1", "prijs": 500000, "oppervlakte": 100}
        
        # Should not raise exception, but return fallback
        result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # Verify calling structure
        # (Assuming Chapter 1 hardcoded returns something specific)
        self.assertNotEqual(result['main_analysis'], "AI Analysis")
        self.assertIn("100 m²", result['intro']) # Check hardcoded logic part

    def test_prompt_structure_contains_preferences(self):
        """Verify that user preferences are passed to the prompt."""
        mock_client = MagicMock(spec=OllamaClient)
        mock_client.generate.return_value = '{"title": "Simple"}' # Min valid JSON
        
        IntelligenceEngine.set_client(mock_client)
        
        ctx = {
            "adres": "Teststraat",
            "_preferences": {
                "marcel": {"priorities": ["Garage"]},
                "petra": {"priorities": ["Tuin"]}
            }
        }
        
        IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # Get the actual call arguments
        call_args = mock_client.generate.call_args
        prompt_text = call_args[0][0] # First arg is the user prompt
        
        self.assertIn("Garage", prompt_text)
        self.assertIn("Tuin", prompt_text)
        self.assertIn("marcel", prompt_text.lower())
        self.assertIn("petra", prompt_text.lower())

if __name__ == '__main__':
    unittest.main()
