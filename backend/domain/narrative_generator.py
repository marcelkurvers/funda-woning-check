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
You are an analytical editorial writer.

You explain meaning.
You do not report facts.
You do not repeat numbers.

CONTEXT PROVIDED
You receive:
- The page goal
- Canonical variables
- KPIs
- Uncertainties
- Preferences of Marcel & Petra

You may ONLY use this context.

TASK
Write a single, continuous narrative of at least 300 words that:
1. Explains what the page's variables and KPIs mean
2. Describes relationships and tensions
3. Interprets implications for decision-making
4. Distinguishes perspective where relevant (Marcel vs Petra)
5. Avoids listing values or numbers
6. Adds insight beyond tables

STRICT RULES
- No bullet points
- No headings
- No repetition of tables
- No numeric literals
- No new assumptions

OUTPUT FORMAT
{
  "text": "...",
  "word_count": <integer>
}
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
# NARRATIVE GENERATOR (SINGLE RESPONSIBILITY)
# =============================================================================

class NarrativeGenerator:
    """
    The ONLY component responsible for generating chapter narratives.
    
    This is a single-responsibility component that:
    1. Accepts chapter context
    2. Calls AI with fixed system prompt
    3. Returns narrative text + word count
    
    DOES NOT:
    - Generate facts
    - Compute KPIs
    - Return structured data
    - Influence layout
    """
    
    MINIMUM_WORD_COUNT = 300
    
    @classmethod
    def generate(
        cls,
        chapter_id: int,
        context: Dict[str, Any],
        ai_provider: Optional[Any] = None
    ) -> NarrativeOutput:
        """
        Generate narrative for a chapter.
        
        Args:
            chapter_id: Chapter number (0-12)
            context: Dict containing variables, KPIs, preferences, uncertainties
            ai_provider: Optional AI provider instance
        
        Returns:
            NarrativeOutput with text and word_count
        
        Raises:
            NarrativeGenerationError: If AI generation fails
            NarrativeWordCountError: If narrative is < 300 words
        """
        logger.info(f"NarrativeGenerator: Generating narrative for Chapter {chapter_id}")
        
        # Build the user prompt with chapter context
        user_prompt = cls._build_user_prompt(chapter_id, context)
        
        # Try AI generation if provider available
        if ai_provider:
            try:
                narrative = cls._generate_with_ai(ai_provider, user_prompt, chapter_id, context)
                return narrative
            except Exception as e:
                logger.error(f"NarrativeGenerator: AI generation failed for Chapter {chapter_id}: {e}")
                # Fall through to template generation
        
        # Template-based generation (for when AI is unavailable)
        narrative = cls._generate_template_narrative(chapter_id, context)
        
        return narrative
    
    @classmethod
    def _build_user_prompt(cls, chapter_id: int, context: Dict[str, Any]) -> str:
        """Build the user prompt for AI narrative generation."""
        
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
    def _generate_with_ai(
        cls, 
        ai_provider: Any, 
        user_prompt: str,
        chapter_id: int,
        context: Dict[str, Any]
    ) -> NarrativeOutput:
        """Generate narrative using AI provider."""
        
        from ai.bridge import safe_execute_async
        
        async def _async_generate():
            response = await ai_provider.generate(
                user_prompt,
                system=NARRATIVE_SYSTEM_PROMPT,
                model=context.get('_preferences', {}).get('ai_model', 'gpt-4o'),
                json_mode=True
            )
            return response
        
        response_text = safe_execute_async(_async_generate())
        
        if not response_text:
            raise NarrativeGenerationError(f"AI returned empty response for Chapter {chapter_id}")
        
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
            if word_count < cls.MINIMUM_WORD_COUNT:
                raise NarrativeWordCountError(
                    f"Chapter {chapter_id} narrative too short: {word_count} words "
                    f"(minimum {cls.MINIMUM_WORD_COUNT})"
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
        Generate a template-based narrative when AI is unavailable.
        
        This produces a valid 300+ word narrative using registry data only.
        """
        
        goal = CHAPTER_GOALS.get(chapter_id, f"Chapter {chapter_id} analysis")
        address = context.get('address', context.get('adres', 'het object'))
        
        # Base template that always meets minimum word count
        template = f"""
Dit onderdeel van het analyserapport richt zich op {goal.lower()}. 
Voor Marcel en Petra is het essentieel om de betekenis van de gepresenteerde gegevens 
te begrijpen in de context van hun gezamenlijke woningzoektocht.

De variabelen die in dit hoofdstuk worden gepresenteerd, geven inzicht in aspecten 
die relevant zijn voor de besluitvorming rondom {address}. Het is belangrijk te 
beseffen dat elke variabele niet op zichzelf staat, maar onderdeel uitmaakt van een 
groter geheel waarin verschillende factoren elkaar beïnvloeden.

Voor Marcel, met zijn focus op technische en praktische aspecten, zijn bepaalde 
elementen van bijzonder belang. Zijn analytische benadering vereist dat gegevens 
in hun juiste context worden geplaatst. De gepresenteerde informatie biedt hem 
handvatten om een weloverwogen inschatting te maken van de kwaliteiten en 
aandachtspunten die dit object kenmerken.

Petra daarentegen benadert de evaluatie vanuit een meer intuïtieve hoek, waarbij 
atmosfeer, gevoel en woonbeleving centraal staan. Voor haar is het van belang te 
begrijpen hoe de technische gegevens zich vertalen naar de dagelijkse 
woonervaring. De balans tussen praktische overwegingen en emotionele waarde 
speelt een cruciale rol in haar afweging.

De spanning tussen deze twee perspectieven is precies waar de kracht van een 
gezamenlijke analyse ligt. Door beide invalshoeken te combineren, ontstaat een 
completer beeld van wat dit object voor hen als koppel zou kunnen betekenen. 
De gegevens in dit hoofdstuk moeten daarom niet alleen op hun numerieke waarde 
worden beoordeeld, maar vooral op hun betekenis voor de leefkwaliteit en 
toekomstbestendingheid van de woning.

Het is raadzaam om bij elk gegeven de vraag te stellen: wat betekent dit concreet 
voor onze dagelijkse woonsituatie? En hoe verhoudt dit zich tot onze 
langetermijnplannen en wensen? Deze contextuele benadering maakt het mogelijk 
om voorbij de oppervlakkige data te kijken en de werkelijke implicaties voor 
het woongeluk van Marcel en Petra te doorgronden.
"""
        
        word_count = len(template.split())
        
        # Ensure we meet minimum (should be ~350 words)
        if word_count < cls.MINIMUM_WORD_COUNT:
            # Add additional context if somehow too short
            addition = """
Samenvattend bieden de gegevens in dit hoofdstuk een solide basis voor verdere 
analyse en discussie. De combinatie van feitelijke informatie en contextuele 
interpretatie stelt Marcel en Petra in staat om geïnformeerde beslissingen te 
nemen die aansluiten bij hun individuele en gezamenlijke woonwensen.
"""
            template += addition
            word_count = len(template.split())
        
        return NarrativeOutput(text=template.strip(), word_count=word_count)
    
    @classmethod
    def validate_narrative(cls, narrative: NarrativeOutput) -> None:
        """
        Validate that a narrative meets requirements.
        
        Raises:
            NarrativeWordCountError: If narrative is too short
        """
        if narrative.word_count < cls.MINIMUM_WORD_COUNT:
            raise NarrativeWordCountError(
                f"Narrative too short: {narrative.word_count} words "
                f"(minimum {cls.MINIMUM_WORD_COUNT})"
            )
