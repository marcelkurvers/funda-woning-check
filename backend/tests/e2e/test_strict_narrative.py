"""
Test Strict Narrative Enforcement (Laws 1, 2, 3)

This test suite rigorously validates the mandatory narrative requirements.
It acts as the 'Auditor' for the system guarantees.
"""

import pytest
import json
from unittest.mock import MagicMock, patch
from backend.domain.pipeline_context import create_pipeline_context, PipelineViolation
from backend.domain.narrative_generator import NarrativeGenerator, NarrativeOutput, NarrativeGenerationError
from backend.domain.models import NarrativeContract
from backend.pipeline.spine import PipelineSpine
from backend.pipeline.dashboard_generator import generate_dashboard_with_validation

@pytest.fixture
def mock_context():
    ctx = create_pipeline_context("test_run_id")
    # Populate minimal registry for generation
    ctx.register_fact("asking_price_eur", 500000, "Asking Price")
    ctx.register_fact("living_area_m2", 120, "Living Area")
    ctx.complete_enrichment()
    ctx.lock_registry()
    return ctx

class TestMandatoryNarrative:
    
    def test_law_1_chapter_narrative_mandatory(self, mock_context):
        """
        LAW 1: Every page MUST include a narrative.
        If AI is missing, it MUST fail (Fail-Closed).
        """
        # NarrativeGenerator must raise error if no AI provider
        with pytest.raises(NarrativeGenerationError):
            NarrativeGenerator.generate(1, mock_context.get_registry_dict())
    
    def test_law_2_dashboard_first_class(self, mock_context):
        """
        LAW 2: Dashboard is First-Class Output with 500-word narrative.
        """
        # Mock AI to avoid API calls but return valid text
        long_text = "word " * 550
        
        with patch("backend.domain.narrative_generator.NarrativeGenerator._generate_with_ai") as mock_ai:
            mock_ai.return_value = NarrativeOutput(text=long_text, word_count=550)
            
            # Need to create AI provider mock for this to be called
            mock_provider = MagicMock()
            
            # Generate directly using generator
            output = NarrativeGenerator.generate_dashboard(
                mock_context.get_registry_dict(),
                ai_provider=mock_provider
            )
            
            assert output.word_count >= 500
            assert len(output.text.split()) >= 500
    
    def test_law_3_fail_closed_on_missing_narrative(self, mock_context):
        """
        LAW 3: If narrative missing/short -> Pipeline MUST fail.
        """
        # Mock NarrativeGenerator to return short text
        with patch("backend.domain.narrative_generator.NarrativeGenerator.generate") as mock_gen:
             # This bypasses the internal validation of generator but simulates 
             # a component returning invalid data to the pipe
             mock_gen.return_value = NarrativeOutput(text="Too short", word_count=10)
             
             spine = PipelineSpine("test_run_failure")
             # Use proper ingestion method to transition phase
             spine.ingest_raw_data({})
             spine.enrich_and_populate_registry()
             
             # Should raise failure during generation
             # Note: generate_all_chapters catches validation errors and sets flag, 
             # preventing Render.
             
             # We can check generate_single_chapter for immediate raise
             with pytest.raises(Exception) as excinfo:
                 # Depending on implementation, might raise PipelineViolation or ValidationFailure
                 spine.generate_single_chapter(1)
             
             assert "validation" in str(excinfo.value).lower() or "too short" in str(excinfo.value).lower()

    def test_dashboard_generator_structure(self, mock_context):
        """Test that dashboard generator produces strict DashboardOutput."""
        
        long_text = "word " * 500
        
        # Mock NarrativeGenerator.generate_dashboard to force success
        with patch("backend.domain.narrative_generator.NarrativeGenerator.generate_dashboard") as mock_gen_dash:
            mock_gen_dash.return_value = NarrativeOutput(text=long_text, word_count=500)
            
            # Mock ctx to have valid chapters (requirement for dashboard)
            mock_context._validation_results = {1: [], 2: []} # Pretend chapters passed
            
            output = generate_dashboard_with_validation(mock_context)
            
            assert output.dashboard.narrative.text == long_text
            assert output.dashboard.narrative.word_count == 500
            assert output.dashboard.coverage is not None
            assert output.dashboard.top_decision_drivers is not None

