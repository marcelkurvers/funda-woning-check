"""
Tests for Mandatory Narrative Generation

These tests verify that:
1. Every chapter (0-12) MUST have a narrative of at least 300 words
2. NarrativeGenerator produces valid narratives
3. ValidationGate rejects chapters without narratives
4. Pipeline fails if narrative is missing or too short
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from domain.narrative_generator import (
    NarrativeGenerator,
    NarrativeOutput,
    NarrativeGenerationError,
    NarrativeWordCountError,
    NARRATIVE_SYSTEM_PROMPT,
    CHAPTER_GOALS
)
from domain.models import NarrativeContract, ChapterOutput
from validation.gate import ValidationGate


class TestNarrativeContract:
    """Test the NarrativeContract data model."""
    
    def test_narrative_contract_requires_text(self):
        """NarrativeContract must have text field."""
        with pytest.raises(Exception):  # pydantic ValidationError
            NarrativeContract(word_count=300)
    
    def test_narrative_contract_requires_word_count(self):
        """NarrativeContract must have word_count field."""
        with pytest.raises(Exception):
            NarrativeContract(text="Some text")
    
    def test_narrative_contract_valid(self):
        """Valid NarrativeContract creation."""
        narrative = NarrativeContract(text="This is a test", word_count=4)
        assert narrative.text == "This is a test"
        assert narrative.word_count == 4
    
    def test_validate_minimum_passes(self):
        """validate_minimum returns True when word count >= minimum."""
        narrative = NarrativeContract(text="x " * 300, word_count=300)
        assert narrative.validate_minimum(300) is True
    
    def test_validate_minimum_fails(self):
        """validate_minimum returns False when word count < minimum."""
        narrative = NarrativeContract(text="short text", word_count=2)
        assert narrative.validate_minimum(300) is False


class TestNarrativeGenerator:
    """Test the NarrativeGenerator component."""
    
    @pytest.fixture
    def sample_context(self):
        """Sample context for narrative generation."""
        return {
            'address': 'Teststraat 123, Amsterdam',
            'asking_price_eur': 450000,
            'living_area_m2': 120,
            'plot_area_m2': 200,
            'build_year': 1990,
            'energy_label': 'B',
            'marcel_match_score': 75,
            'petra_match_score': 82,
            'total_match_score': 78,
            '_preferences': {
                'marcel': {'min_area': 100},
                'petra': {'garden': True}
            }
        }
    
    def test_generate_fails_without_provider(self, sample_context):
        """NarrativeGenerator.generate raises error without AI provider (Fail-Closed)."""
        with pytest.raises(NarrativeGenerationError):
            NarrativeGenerator.generate(
                chapter_id=1,
                context=sample_context,
                ai_provider=None
            )
    
    def test_generate_fails_for_all_chapters_without_ai(self, sample_context):
        """All chapters raise error without AI (no partial fallbacks)."""
        for chapter_id in range(13):
            with pytest.raises(NarrativeGenerationError):
                NarrativeGenerator.generate(
                    chapter_id=chapter_id,
                    context=sample_context,
                    ai_provider=None
                )
    
    def test_generate_raises_on_missing_ai(self, sample_context):
        """NarrativeGenerator raises error if no AI provider."""
        with pytest.raises(NarrativeGenerationError):
             NarrativeGenerator.generate(
                chapter_id=0,
                context=sample_context,
                ai_provider=None
            )
    
    def test_narrative_word_count_fails_without_ai(self, sample_context):
        """Cannot check word count if generation fails."""
        with pytest.raises(NarrativeGenerationError):
            NarrativeGenerator.generate(
                chapter_id=5,
                context=sample_context,
                ai_provider=None
            )
    
    def test_validate_narrative_raises_on_short(self):
        """validate_narrative raises NarrativeWordCountError for short text."""
        short_narrative = NarrativeOutput(text="Too short", word_count=2)
        with pytest.raises(NarrativeWordCountError):
            NarrativeGenerator.validate_narrative(short_narrative)
    
    def test_validate_narrative_passes_on_long(self):
        """validate_narrative passes for 300+ word text."""
        long_text = "word " * 350
        long_narrative = NarrativeOutput(text=long_text, word_count=350)
        NarrativeGenerator.validate_narrative(long_narrative)  # Should not raise


class TestValidationGateNarrative:
    """Test ValidationGate narrative validation."""
    
    def test_validation_fails_when_narrative_missing(self):
        """ValidationGate fails chapters 0-12 without narrative."""
        output = {
            "id": "1",
            "title": "Test Chapter",
            "main_analysis": "<p>Some content</p>",
            "chapter_data": {"main_analysis": "<p>Some content</p>"}
            # No narrative field
        }
        
        errors = ValidationGate.validate_chapter_output(1, output, {})
        
        # Should have a narrative missing error
        narrative_errors = [e for e in errors if "Narrative Missing" in e]
        assert len(narrative_errors) > 0, f"Expected narrative error, got: {errors}"
    
    def test_validation_fails_when_narrative_too_short(self):
        """ValidationGate fails chapters with < 300 word narrative."""
        output = {
            "id": "2",
            "title": "Test Chapter",
            "main_analysis": "<p>Content</p>",
            "chapter_data": {"main_analysis": "<p>Content</p>"},
            "narrative": {
                "text": "This is too short",
                "word_count": 4
            }
        }
        
        errors = ValidationGate.validate_chapter_output(2, output, {})
        
        # Should have a narrative too short error
        short_errors = [e for e in errors if "Narrative Too Short" in e]
        assert len(short_errors) > 0, f"Expected short narrative error, got: {errors}"
    
    def test_validation_passes_with_valid_narrative(self):
        """ValidationGate passes chapters with 300+ word narrative."""
        long_text = "word " * 350
        output = {
            "id": "3",
            "title": "Test Chapter",
            "main_analysis": "<p>Content</p>",
            "chapter_data": {
                "main_analysis": "<p>Content</p>",
                "comparison": {"marcel": "Long enough", "petra": "Long enough"}
            },
            "narrative": {
                "text": long_text,
                "word_count": 350
            }
        }
        
        errors = ValidationGate.validate_chapter_output(3, output, {})
        
        # Should NOT have narrative errors
        narrative_errors = [e for e in errors if "Narrative" in e]
        assert len(narrative_errors) == 0, f"Unexpected narrative errors: {narrative_errors}"
    
    def test_chapter_13_does_not_require_narrative(self):
        """Chapter 13 (media) does not require narrative."""
        output = {
            "id": "13",
            "title": "Media Gallery",
            "main_analysis": "<p>Media content</p>",
            "chapter_data": {"main_analysis": "<p>Media content</p>"}
            # No narrative
        }
        
        errors = ValidationGate.validate_chapter_output(13, output, {})
        
        # Should NOT have narrative missing error
        narrative_errors = [e for e in errors if "Narrative" in e]
        assert len(narrative_errors) == 0


class TestNarrativeSystemPrompt:
    """Test that the system prompt is properly defined."""
    
    def test_system_prompt_exists(self):
        """NARRATIVE_SYSTEM_PROMPT is defined."""
        assert NARRATIVE_SYSTEM_PROMPT is not None
        assert len(NARRATIVE_SYSTEM_PROMPT) > 100
    
    def test_system_prompt_mentions_300_words(self):
        """System prompt specifies 300 word minimum."""
        assert "300" in NARRATIVE_SYSTEM_PROMPT
    
    def test_system_prompt_forbids_bullets(self):
        """System prompt forbids bullet points."""
        assert "bullet" in NARRATIVE_SYSTEM_PROMPT.lower()
    
    def test_system_prompt_specifies_output_format(self):
        """System prompt specifies JSON output format."""
        assert "word_count" in NARRATIVE_SYSTEM_PROMPT


class TestChapterGoals:
    """Test that chapter goals are properly defined."""
    
    def test_all_chapters_have_goals(self):
        """All chapters 0-12 have defined goals."""
        for chapter_id in range(13):
            assert chapter_id in CHAPTER_GOALS, f"Chapter {chapter_id} missing goal"
    
    def test_goals_are_descriptive(self):
        """Chapter goals are descriptive strings."""
        for chapter_id, goal in CHAPTER_GOALS.items():
            assert isinstance(goal, str)
            assert len(goal) > 20, f"Chapter {chapter_id} goal too short"


class TestNarrativeEnforcement:
    """Integration tests for narrative enforcement in the pipeline."""
    
    def test_narrative_output_is_serializable(self):
        """NarrativeOutput can be serialized to dict."""
        narrative = NarrativeOutput(text="Test text", word_count=2)
        result = narrative.model_dump()
        assert result == {"text": "Test text", "word_count": 2}
    
    def test_narrative_contract_in_chapter_output(self):
        """ChapterOutput model includes narrative field."""
        chapter = ChapterOutput(
            title="Test",
            grid_layout={},
            narrative=NarrativeContract(text="test", word_count=1)
        )
        assert chapter.narrative is not None
        assert chapter.narrative.text == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
