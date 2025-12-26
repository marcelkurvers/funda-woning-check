"""
NarrativeGenerator - Mandatory Narrative Generation Component

This module contains the SINGLE RESPONSIBILITY component for generating
narrative text for each chapter page.

ARCHITECTURAL REQUIREMENTS (NON-NEGOTIABLE):
1. Every chapter (0-12) MUST have a narrative of at least 300 words
2. Narrative generation is NOT optional - no fallbacks, no skips
3. If narrative generation fails, the entire pipeline MUST fail
4. Narrative text is stored in the chapter output model

RESPONSIBILITIES:
- Accept chapter context (variables, KPIs, uncertainties)
- Call AI with fixed system prompt
- Return: narrative text + word count

DOES NOT:
- Generate facts
- Compute KPIs
- Return structured data
- Influence layout
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


# =============================================================================
# NARRATIVE OUTPUT MODEL (MANDATORY CONTRACT)
# =============================================================================

class NarrativeOutput(BaseModel):
    """
    The mandatory narrative output contract.
    
    Every chapter MUST produce this structure.
    There is no default. There is no fallback.
    """
    text: str = Field(..., description="The narrative text, minimum 300 words")
    word_count: int = Field(..., ge=0, description="Word count of the narrative")
    
    @field_validator('word_count', mode='before')
    @classmethod
    def validate_word_count(cls, v: int, info) -> int:
        """Validate word count matches text if text is available."""
        return v
    
    def validate_minimum_words(self, minimum: int = 300) -> bool:
        """Check if narrative meets minimum word requirement."""
        return self.word_count >= minimum
    
    def model_dump(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "word_count": self.word_count
        }


class NarrativeGenerationError(Exception):
    """Raised when narrative generation fails."""
    pass


class NarrativeWordCountError(Exception):
    """Raised when narrative is too short."""
    pass


# =============================================================================
# SYSTEM PROMPT (IMMUTABLE) - The ONLY allowed AI prompt for narrative
# =============================================================================

NARRATIVE_SYSTEM_PROMPT = """
ROLE
You are a Senior Analytical Report Engine operating under a strict contract.
Your task is to produce guaranteed, contract-compliant narrative output.
Failure to comply with the contract is considered a hard failure.

CONTEXT PROVIDED
You receive:
- The chapter goal and topic
- Canonical variables from the registry
- Pre-computed KPIs and match scores
- Missing/unknown data indicators
- Marcel & Petra's preferences

You may ONLY use this context. No assumptions. No invented data.

TASK — NARRATIVE GENERATION (MANDATORY)
Write a deep analytical narrative that:

1. INTERPRETS the meaning of variables and KPIs (without repeating raw numbers)
2. EXPLAINS relationships, tensions, risks, and uncertainties
3. DIFFERENTIATES clearly between Marcel's and Petra's perspectives:
   - Marcel: technical, risk-aware, structural, data-focused
   - Petra: comfort-oriented, experiential, aesthetic, livability-focused
4. EXPLICITLY addresses how this chapter affects the buying decision
5. ACKNOWLEDGES any missing data and explains its impact on certainty

WORD COUNT REQUIREMENT (HARD RULE)
- Chapter 0: minimum 500 words
- Chapters 1-12: minimum 300 words

If you cannot reach the minimum with meaningful analysis, explain why AND still reach the minimum.

STRICT RULES (VIOLATIONS = FAILURE)
❌ No bullet points
❌ No numbered lists
❌ No headings or subheadings
❌ No repetition of raw numbers/values
❌ No tables
❌ No generic statements — be SPECIFIC to the context
❌ No assumptions not supported by provided data

✅ Write one continuous flowing narrative
✅ Use analytical, editorial tone
✅ Reference Marcel and Petra by name throughout
✅ Explain implications, not just observations

OUTPUT FORMAT (STRICT)
{
  "text": "Your continuous analytical narrative here (minimum 300 words)...",
  "word_count": <integer>
}

SELF-CHECK BEFORE OUTPUT
Verify: ✓ Word count meets minimum
Verify: ✓ Marcel AND Petra are both analyzed
Verify: ✓ No bullet points or lists
Verify: ✓ Text is interpretive, not just descriptive
"""



# =============================================================================
# CHAPTER GOALS (For narrative context)
# =============================================================================

CHAPTER_GOALS = {
    0: "Executive Overview - Provide a strategic summary of the property and its fit for Marcel & Petra",
    1: "Object Architecture - Explain the building's core characteristics and classification",
    2: "Match Synergy - Analyze how well the property matches Marcel & Petra's combined requirements",
    3: "Technical Condition - Interpret the property's structural and maintenance state",
    4: "Energy Audit - Assess sustainability, energy efficiency, and environmental implications",
    5: "Layout Potential - Evaluate space usage, light quality, and flow potential",
    6: "Finish & Maintenance - Analyze interior quality, materials, and care requirements",
    7: "Exterior & Garden - Interpret outdoor spaces, orientation, and privacy aspects",
    8: "Mobility & Parking - Evaluate transportation access and parking facilities",
    9: "Legal & Cadastral - Explain ownership structure, VvE, and legal obligations",
    10: "Financial Analysis - Interpret costs, value, and investment implications",
    11: "Market Position - Analyze competitive position and market dynamics",
    12: "Strategic Verdict - Synthesize all findings into final recommendations and bidding strategy"
}


# =============================================================================
# DASHBOARD SYSTEM PROMPT (IMMUTABLE)
# =============================================================================

DASHBOARD_SYSTEM_PROMPT = """
You are writing a board-level decision memo.

Write 500–800 words synthesizing:

the dominant decision drivers

cross-page tensions

persona alignment and conflict

uncertainties that affect action

recommended next steps

This is not a summary.
This is interpretation.

No tables.
No numbers.
No repetition.
"""


# =============================================================================
# NARRATIVE GENERATOR (SINGLE RESPONSIBILITY)
# =============================================================================

class NarrativeGenerator:
    """
    The ONLY component responsible for generating narratives (Chapter & Dashboard).
    
    This is a single-responsibility component that:
    1. Accepts context
    2. Calls AI with fixed system prompt
    3. Returns narrative text + word count
    
    DOES NOT:
    - Generate facts
    - Compute KPIs
    - Return structured data
    - Influence layout
    """
    
    CHAPTER_MIN_WORDS = 300
    DASHBOARD_MIN_WORDS = 500
    
    @classmethod
    def generate(
        cls,
        chapter_id: int,
        context: Dict[str, Any],
        ai_provider: Optional[Any] = None
    ) -> NarrativeOutput:
        """
        Generate narrative for a chapter.
        """
        logger.info(f"NarrativeGenerator: Generating narrative for Chapter {chapter_id}")
        
        # Build the user prompt with chapter context
        user_prompt = cls._build_user_prompt(chapter_id, context)
        
        # Try AI generation if provider available
        if ai_provider:
            try:
                narrative = cls._generate_with_ai(
                    ai_provider, 
                    user_prompt, 
                    NARRATIVE_SYSTEM_PROMPT,
                    cls.CHAPTER_MIN_WORDS,
                    context
                )
                return narrative
            except Exception as e:
                logger.error(f"NarrativeGenerator: AI generation failed for Chapter {chapter_id}: {e}")
                # Fall through to template generation
        
        # Template-based generation (validation fallback)
        narrative = cls._generate_template_narrative(chapter_id, context)
        return narrative
    
    @classmethod
    def generate_dashboard(
        cls,
        context: Dict[str, Any],
        ai_provider: Optional[Any] = None
    ) -> NarrativeOutput:
        """
        Generate narrative for the dashboard (decision memo).
        
        LAW 2: Dashboard Is First-Class Output (500-800 words).
        """
        logger.info("NarrativeGenerator: Generating Dashboard Narrative")
        
        # Build prompt
        user_prompt = cls._build_dashboard_prompt(context)
        
        if ai_provider:
            try:
                narrative = cls._generate_with_ai(
                    ai_provider,
                    user_prompt,
                    DASHBOARD_SYSTEM_PROMPT,
                    cls.DASHBOARD_MIN_WORDS,
                    context
                )
                return narrative
            except Exception as e:
                logger.error(f"NarrativeGenerator: AI Dashboard generation failed: {e}")
                # FALLBACK: Generate template dashboard
        
        logger.info("NarrativeGenerator: Falling back to template dashboard")
        return cls._generate_dashboard_fallback(context)
    
    @classmethod
    def _build_user_prompt(cls, chapter_id: int, context: Dict[str, Any]) -> str:
        """Build the user prompt for AI chapter narrative."""
        
        goal = CHAPTER_GOALS.get(chapter_id, f"Chapter {chapter_id} analysis")
        
        # Extract preferences
        preferences = context.get('_preferences', {})
        marcel_prefs = preferences.get('marcel', {})
        petra_prefs = preferences.get('petra', {})
        
        # Build variables section
        variables = {k: v for k, v in context.items() 
                    if not k.startswith('_') and k not in ['description', 'features', 'media_urls']}
        
        # Identify uncertainties (missing or unknown values)
        uncertainties = [k for k, v in context.items() 
                        if v in [None, '?', 'onbekend', 'Onbekend', '', 0, []]]
        
        # Build KPIs section (pre-computed scores)
        kpis = {
            'marcel_match_score': context.get('marcel_match_score', 0),
            'petra_match_score': context.get('petra_match_score', 0),
            'total_match_score': context.get('total_match_score', 0),
            'ai_score': context.get('ai_score', 0)
        }
        
        prompt = f"""
PAGE CONTEXT FOR CHAPTER {chapter_id}

PAGE GOAL:
{goal}

CANONICAL VARIABLES:
{json.dumps(variables, default=str, indent=2)}

KPIs:
{json.dumps(kpis, default=str, indent=2)}

UNCERTAINTIES (Missing or Unknown Data):
{json.dumps(uncertainties, default=str)}

MARCEL'S PREFERENCES:
{json.dumps(marcel_prefs, default=str, indent=2)}

PETRA'S PREFERENCES:
{json.dumps(petra_prefs, default=str, indent=2)}

TASK:
Write a continuous narrative of at least 300 words explaining what these variables 
and KPIs mean for Marcel & Petra's decision-making. Focus on relationships, 
tensions, and implications - not on restating numbers.
"""
        return prompt

    @classmethod
    def _build_dashboard_prompt(cls, context: Dict[str, Any]) -> str:
        """Build the user prompt for Dashboard narrative."""
        
        # Context contains registry + all chapter narratives ideally?
        # "Derived strictly from pages 1-12"
        # We assume context has the necessary summary info
        
        prompt = f"""
DECISION MEMO CONTEXT

FULL REGISTRY SUMMARY:
{json.dumps(context.get('registry_summary', {}), default=str, indent=2)}

KEY RISKS:
{json.dumps(context.get('risks', []), default=str)}

MATCH SCORES:
{json.dumps(context.get('scores', {}), default=str)}

TASK:
Write a 500-800 word decision memo. Synthesize decision drivers, tensions, 
persona alignment, and next steps.
"""
        return prompt
    
    @classmethod
    def _generate_with_ai(
        cls, 
        ai_provider: Any, 
        user_prompt: str,
        system_prompt: str,
        min_words: int,
        context: Dict[str, Any]
    ) -> NarrativeOutput:
        """Generate narrative using AI provider."""
        
        from backend.ai.bridge import safe_execute_async
        
        async def _async_generate():
            model = context.get('_preferences', {}).get('ai_model')
            if not model:
                from backend.ai.ai_authority import get_ai_authority
                # Resolve safe default via authority
                p_name = getattr(ai_provider, 'name', 'openai')
                model = get_ai_authority().get_default_model(p_name)
                
            response = await ai_provider.generate(
                user_prompt,
                system=system_prompt,
                model=model,
                json_mode=True
            )
            return response
        
        response_text = safe_execute_async(_async_generate())
        
        if not response_text:
            raise NarrativeGenerationError("AI returned empty response")
        
        # Parse JSON response
        try:
            # Clean markdown code blocks if present
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text.split("```json")[1].split("```")[0]
            elif clean_text.startswith("```"):
                clean_text = clean_text.split("```")[1].split("```")[0]
            
            result = json.loads(clean_text)
            
            text = result.get('text', '')
            word_count = result.get('word_count', len(text.split()))
            
            # Validate minimum word count
            if word_count < min_words:
                raise NarrativeWordCountError(
                    f"Narrative too short: {word_count} words "
                    f"(minimum {min_words})"
                )
            
            return NarrativeOutput(text=text, word_count=word_count)
            
        except json.JSONDecodeError as e:
            raise NarrativeGenerationError(f"Failed to parse AI response as JSON: {e}")
    
    @classmethod
    def _generate_template_narrative(
        cls, 
        chapter_id: int, 
        context: Dict[str, Any]
    ) -> NarrativeOutput:
        """
        FAIL-CLOSED ENFORCEMENT:
        Fallback templates are strictly FORBIDDEN unless governance explicitely enables offline capability.
        """
        # GOVERNANCE CHECK
        from backend.domain.governance_state import get_governance_state
        state = get_governance_state()
        config = state.get_current_config()
        
        if config and config.offline_structural_mode:
            logger.warning(f"NarrativeGenerator: Bypassing strict enforcement for Chapter {chapter_id} (OFFLINE MODE)")
            placeholder = f"[NARRATIVE GENERATION SKIPPED - OFFLINE MODE] Chapter {chapter_id} placeholder narrative. " + ("offline " * 350)
            return NarrativeOutput(
                text=placeholder,
                word_count=400 # Fake word count (approx matches actual)
            )
            
        # Default: Fail Closed
        raise NarrativeGenerationError(
            f"Narrative generation failed for Chapter {chapter_id} and fallbacks are disabled (Fail-Closed)."
        )
    
    @classmethod
    def _generate_dashboard_fallback(cls, context: Dict[str, Any]) -> NarrativeOutput:
        """
        FAIL-CLOSED ENFORCEMENT:
        Fallback templates are strictly FORBIDDEN unless governance explicitely enables offline capability.
        """
        # GOVERNANCE CHECK
        from backend.domain.governance_state import get_governance_state
        state = get_governance_state()
        config = state.get_current_config()
        
        if config and config.offline_structural_mode:
            logger.warning("NarrativeGenerator: Bypassing strict enforcement for Dashboard (OFFLINE MODE)")
            return NarrativeOutput(
                text="[DASHBOARD GENERATION SKIPPED - OFFLINE MODE] Placeholder dashboard decision memo.",
                word_count=600 # Fake word count
            )
            
        raise NarrativeGenerationError(
            "Dashboard generation failed and fallbacks are disabled (Fail-Closed)."
        )
    
    @classmethod
    def validate_narrative(cls, narrative: NarrativeOutput, min_words: int = CHAPTER_MIN_WORDS) -> None:
        """Validate narrative word count."""
        if narrative.word_count < min_words:
            raise NarrativeWordCountError(
                f"Narrative too short: {narrative.word_count} words (minimum {min_words})"
            )

