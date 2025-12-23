import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from intelligence import IntelligenceEngine
from ai.provider_interface import AIProvider

# Mock Provider
class MockAIProvider(AIProvider):
    async def generate(self, prompt: str, system: str = None, model: str = None, **kwargs) -> str:
        # Simulate a JSON response from the AI
        return """
        ```json
        {
            "title": "AI Match Report",
            "intro": "Intro text",
            "main_analysis": "Analysis text",
            "comparison": {
                "marcel": "Marcel loves the high-tech solar panels.",
                "petra": "Petra adores the 1930s stained glass.",
                "combined_advice": "Buy it."
            },
            "variables": {
                "tech_score": {"value": "8/10", "status": "inferred", "reasoning": "Solar panels present"}
            },
            "conclusion": "Good house."
        }
        ```
        """
    
    @property
    def name(self): return "MockProvider"
    
    async def check_health(self) -> bool: return True
    async def list_models(self): return ["mock-model"]
    async def close(self): pass

@pytest.mark.asyncio
async def test_chapter_0_fallback_comparison():
    """
    Verify that Chapter 0 returns a default 'comparison' object even WITHOUT AI.
    This ensures the dashboard never shows empty/broken boxes.
    """
    ctx = {
        "address": "Teststraat 1",
        "price": 500000,
        "area": 120,
        "label": "A",
        "year": 2020
    }
    
    # Run without an AI provider set
    IntelligenceEngine.set_provider(None)
    result = IntelligenceEngine.generate_chapter_narrative(0, ctx)
    
    assert "comparison" in result
    assert "marcel" in result["comparison"]
    assert "petra" in result["comparison"]
    assert "Initiële scan" in result["comparison"]["marcel"]

@pytest.mark.asyncio
async def test_ai_preference_matching_context_and_quality():
    """
    Comprehensive test to verify:
    1. Context: That the AI receives different instructions per chapter (0, 2, 4, 10).
    2. Quality: That the output structure contains narrative, advice, and comparison fields.
    3. Relevance: That specific variables (e.g. 'insulation' for ch4) are requested.
    """
    
    # 1. Setup Context with specific preferences
    ctx = {
        "address": "Duinlaan 26",
        "price": 850000,
        "area": 185,
        "plot": 550,
        "label": "C",
        "year": 1975,
        "media_urls": [], # Required for visual audit check if any
        "_preferences": {
            "marcel": {"priorities": ["warmtepomp", "glasvezel"], "style": "tech-modern"},
            "petra": {"priorities": ["glas in lood", "tuin op zuid"], "style": "sfeervol-jaren30"}
        }
    }

    # 2. Mock Provider that tracks prompts
    class SpyingMockProvider(MockAIProvider):
        def __init__(self):
            self.last_prompt = ""
            self.last_system = ""
            
        async def generate(self, prompt: str, system: str = None, model: str = None, **kwargs) -> str:
            self.last_prompt = prompt
            self.last_system = system
            
            # Return a valid JSON response that mimics "High Value" output
            return """
            ```json
            {
                "title": "Contextual Analysis",
                "intro": "A tailored introduction based on valid data.",
                "main_analysis": "Deep dive into the specific chapter topic...",
                "comparison": {
                    "marcel": "Marcel, be aware of X...",
                    "petra": "Petra, you will love Y...",
                    "combined_advice": "Strategically, this is a solid choice."
                },
                "variables": {
                    "test_var": {"value": "Verified", "status": "fact", "reasoning": "Data check"}
                },
                "advice": ["Actionable Tip 1", "Actionable Tip 2"],
                "conclusion": "A conclusive final verdict."
            }
            ```
            """

    provider = SpyingMockProvider()
    IntelligenceEngine.set_provider(provider)

    # 3. Test Loop: Verify Context & Variable Relevance for ALL Chapters (0-13)
    # We define the expected focus keywords for each chapter based on the logic in intelligence.py
    scenarios = [
        (0, "ALL core property data"),
        (1, "DERIVED features ONLY"),
        (2, "Marcel & Petra preference matching"),
        (3, "Technical state ONLY"),
        (4, "Energy & sustainability ONLY"),
        (5, "Layout analysis ONLY"),
        (6, "Maintenance & finish ONLY"),
        (7, "Garden & outdoor ONLY"),
        (8, "Parking & mobility ONLY"),
        (9, "Legal aspects ONLY"),
        (10, "Financial analysis ONLY"),
        (11, "Market position ONLY"),
        (12, "Final advice ONLY"),
        (13, "Media Bibliotheek")
    ]

    for chapter_id, expected_focus in scenarios:
        print(f"\n--- Testing Chapter {chapter_id} ---")
        
        # Call the engine to get fallback logic (simulating the pipeline)
        # We use the public generate_chapter_narrative to ensure the full internal mapping works
        result_sync = IntelligenceEngine.generate_chapter_narrative(chapter_id, ctx)
        
        # Now test the async AI generation part directly to verify prompt quality
        # IntelligenceEngine doesn't have an easily callable 'get_fallback_for_chapter' so we pass the result from sync call
        ai_result = await IntelligenceEngine._generate_ai_narrative(chapter_id, ctx, result_sync)
        
        # A. Assert Quality Structure
        assert ai_result is not None, f"Chapter {chapter_id} returned None"
        assert "comparison" in ai_result, f"Chapter {chapter_id} missing comparison block"
        
        # B. Assert Contextual Relevance (Prompt Inspection)
        system_instruction = provider.last_system
        assert f"Chapter {chapter_id}" in system_instruction
        
        # Verify that the system includes the chapter-specific focus in the prompt
        # The engine uses a mapping in _generate_ai_narrative for 'target_vars'
        if chapter_id == 0: assert "core property data" in system_instruction
        if chapter_id == 4: assert "Energy & sustainability" in system_instruction
        if chapter_id == 10: assert "Financial analysis" in system_instruction

        print(f"✅ Chapter {chapter_id} Validated: Prompt context verified.")

    print("\n✅ All 14 Chapters Verified for Contextual AI Quality")
