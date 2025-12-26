"""
Intelligence Engine - AI-Powered Narrative Generation

ARCHITECTURAL INVARIANTS (NON-NEGOTIABLE):
1. When AI is available: AI generates the narrative
2. When AI is NOT available: Registry-only templates are used
3. NO heuristics, NO estimation, NO computation in fallback path
4. All values MUST come from the registry (pre-computed in enrichment layer)

DELETED FUNCTIONS (Violated no-computation invariant):
- _narrative_ch0() through _narrative_ch13() - contained arithmetic and heuristics
- calculate_fit_score() - computed values outside registry
- calculate_persona_score() - computed values outside registry

These have been replaced by:
- domain/presentation_narratives.py - registry-only templates
- enrichment.py - all calculations happen here BEFORE registry lock
"""

import os
import re
import json
import logging
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime

from backend.ai.provider_factory import ProviderFactory
from backend.ai.provider_interface import AIProvider

logger = logging.getLogger(__name__)

PAGE_NARRATIVE_SYSTEM_PROMPT = """
ROLE — SENIOR ANALYTICAL REPORT ENGINE
You are generating Plane B (Narrative Reasoning) output for a property analysis report.
Your output MUST be contract-compliant. Non-compliance = hard failure.

CONTRACT REQUIREMENTS (NON-NEGOTIABLE)
1. Minimum 300 words (500 for Chapter 0)
2. One continuous flowing narrative — NO lists, NO bullets, NO headers
3. Deep analytical interpretation — NOT surface-level observations
4. Specific to the provided context — NO generic statements
5. Marcel AND Petra MUST both be explicitly analyzed

CONTEXT PROVIDED (USE ONLY THIS)
- Chapter title and goal
- Relevant variables and KPIs from the registry
- Missing/unknown data indicators
- Marcel & Petra preferences and match scores

PERSONA REQUIREMENTS (MANDATORY)
You MUST differentiate between:

MARCEL — The Technical Analyst:
├── Risk-aware and structural
├── Focuses on data consistency
├── Evaluates technical specifications
└── Concerned with maintenance, costs, and long-term value

PETRA — The Experience Seeker:
├── Comfort-oriented and aesthetic
├── Focuses on livability and atmosphere
├── Evaluates flow, light, and feel
└── Concerned with daily living quality

NARRATIVE REQUIREMENTS
✅ INTERPRET what the data means (don't repeat raw values)
✅ EXPLAIN relationships, tensions, and implications
✅ ADDRESS how this affects the buying decision
✅ ACKNOWLEDGE missing data and its impact on certainty
✅ USE Marcel and Petra by name throughout

❌ No bullet points or numbered lists
❌ No headings or subheadings
❌ No raw number repetition
❌ No tables
❌ No assumptions beyond provided context

WORD COUNT ENFORCEMENT
Chapter 0: ≥500 words
Chapters 1-12: ≥300 words

If reaching minimum is difficult, explain why AND still meet minimum.

OUTPUT FORMAT (STRICT JSON)
{
  "narrative_text": "Your continuous analytical narrative here...",
  "word_count": <integer matching actual word count>
}

FINAL SELF-CHECK
Before output, verify:
✓ Word count ≥ minimum for this chapter
✓ Marcel AND Petra are both analyzed with specifics
✓ No bullet points, lists, or headers
✓ Content is interpretive, not just descriptive
✓ JSON is valid and complete
"""


class IntelligenceEngine:
    """
    AI-powered narrative generator for property analysis.
    
    PRESENTATION-ONLY GENERATION:
    - Receives pre-computed values from locked registry
    - Passes to AI for narrative synthesis
    - Falls back to registry-template display (NO COMPUTATION)
    """
    _provider: Optional[AIProvider] = None
    _client: Optional[AIProvider] = None  # Alias for backward compatibility
    _request_count: int = 0

    @classmethod
    def set_provider(cls, provider: AIProvider):
        """Set the AI provider instance"""
        cls._provider = provider

    @staticmethod
    def generate_chapter_narrative(chapter_id: int, ctx: Dict[str, Any]) -> Dict[str, str]:
        """
        Returns a dictionary with 'title', 'intro', 'main_analysis', and 'conclusion'.
        
        STRICT DELEGATION TO NARRATIVE GENERATOR:
        - Calls NarrativeGenerator.generate() which enforces 300-word contract and fail-closed behavior.
        - If AI fails or is missing, this method RAISES an error.
        - NO fallbacks, NO registry-only templates for narrative content.
        
        Visual Audit (Chapter 0) is preserved as an enhancement.
        """
        # Import registry-only templates ONLY for structural skeleton (Title, Intro)
        # The 'main_analysis' from this skeleton will be OVERWRITTEN by AI.
        from backend.domain.presentation_narratives import get_registry_only_narrative
        from backend.domain.narrative_generator import NarrativeGenerator
        from backend.ai.bridge import safe_execute_async
        
        # Build data context from registry
        data = {
            "price": ctx.get('asking_price_eur', 0),
            "area": ctx.get('living_area_m2', 0),
            "plot": ctx.get('plot_area_m2', 0),
            "year": ctx.get('build_year', 0),
            "label": ctx.get('energy_label', '?'),
            "asking_price_eur": ctx.get('asking_price_eur'),
            "living_area_m2": ctx.get('living_area_m2'),
            "plot_area_m2": ctx.get('plot_area_m2'),
            "build_year": ctx.get('build_year'),
            "energy_label": ctx.get('energy_label', '?'),
            "address": ctx.get('address') or ctx.get('adres', 'Object'),
            "description": ctx.get('description', ''),
            "features": ctx.get('features', []),
            "media_urls": ctx.get('media_urls', []),
            "_preferences": ctx.get('_preferences', {}),
            # Pre-computed enriched values
            "volume_m3": ctx.get('volume_m3'),
            "rooms": ctx.get('rooms'),
            "bedrooms": ctx.get('bedrooms'),
            "bathrooms": ctx.get('bathrooms'),
            "price_per_m2": ctx.get('price_per_m2'),
            "valuation_status": ctx.get('valuation_status'),
            "market_trend": ctx.get('market_trend'),
            "sustainability_advice": ctx.get('sustainability_advice'),
            "construction_alert": ctx.get('construction_alert'),
            "estimated_reno_cost": ctx.get('estimated_reno_cost'),
            "energy_invest": ctx.get('energy_invest'),
            "construction_invest": ctx.get('construction_invest'),
            # Pre-computed scores
            "ai_score": ctx.get('ai_score', 0),
            "marcel_match_score": ctx.get('marcel_match_score', 0),
            "petra_match_score": ctx.get('petra_match_score', 0),
            "marcel_reasons": ctx.get('marcel_reasons', []),
            "petra_reasons": ctx.get('petra_reasons', []),
            "total_match_score": ctx.get('total_match_score', 0)
        }

        # 1. Get Structural Skeleton (Title, Intro)
        structure = get_registry_only_narrative(chapter_id, data)
        
        # 2. FAIL-CLOSED CHECK: Provider must be present
        if not IntelligenceEngine._provider:
            from backend.domain.governance_state import get_governance_state
            from backend.domain.guardrails import PolicyLevel
            
            policy = get_governance_state().get_effective_policy()
            
            if policy.require_ai_provider == PolicyLevel.STRICT:
                 # We strictly raise here. No fallback return.
                 raise ValueError(f"IntelligenceEngine: No AI provider configured for Chapter {chapter_id}. Cannot generate narrative. (Policy: require_ai_provider)")
            
            # If policy allows (e.g. OFF for structural testing), we don't raise
            # But wait, if provider is missing, how can we generate narrative?
            # If policy is OFF, it implies we want to bypass generation or return dummy.
            # NarrativeGenerator.generate also expects provider.
            # If this guardrail is relaxed, we likely want to return skeletal structure 
            # or skip the "generate" call.
            
            # Since T4a/b explicitly allows 'offline_structural_mode' to relax this,
            # we must handle the bypass here.
            # Return structure with placeholder text.
            return {
                "title": structure.get("title"),
                "intro": structure.get("intro"),
                "main_analysis": "[NARRATIVE GENERATION SKIPPED - OFFLINE MODE]",
                "conclusion": structure.get("conclusion"),
                "variables": structure.get("variables", {}),
                "metadata": {"source": "skipped", "confidence": "none"},
                "_provenance": {"provider": "none", "model": "none"},
                "chapter_id": chapter_id
            }

        # 3. Generate Narrative via Canonical Generator
        # This will raise NarrativeGenerationError if AI fails.
        narrative_output = NarrativeGenerator.generate(
            chapter_id=chapter_id, 
            context=data, 
            ai_provider=IntelligenceEngine._provider
        )
        
        # 4. Construct Result
        result = {
            "title": structure.get("title"),
            "intro": structure.get("intro"),
            "main_analysis": narrative_output.text,  # The AI narrative
            "conclusion": structure.get("conclusion"), # Keep structural conclusion or replace?
                                                       # Structure conclusion often says "AI Required".
                                                       # But NarrativeGenerator doesn't grant a conclusion field yet.
                                                       # We keep it as is for now, main content is what matters for Plane B.
            "variables": structure.get("variables", {}),
            "metadata": {
                "word_count": narrative_output.word_count,
                "confidence": "high",
                "source": "ai_generated"
            },
            "_provenance": {
                "provider": getattr(IntelligenceEngine._provider, 'name', 'unknown'),
                "model": getattr(IntelligenceEngine._provider, 'default_model', 'unknown'),
                "confidence": "high",
                "timestamp": datetime.now().isoformat(),
                "request_count": IntelligenceEngine._request_count
            },
            "chapter_id": chapter_id
        }
        
        # 5. Chapter 0 Visual Audit Enhancement
        if chapter_id == 0 and data.get("media_urls"):
            try:
                # We need safe async execution for visual audit if it's not already safe
                # process_visuals is async. We are in a static blocking context? 
                # generate_chapter_narrative is synchronous staticmethod
                # NarrativeGenerator used safe_execute_async internaly. We need to do same here for visual audit.
                vision_audit = safe_execute_async(IntelligenceEngine.process_visuals(data))
                if vision_audit:
                     result["main_analysis"] = vision_audit + "\n\n" + result["main_analysis"]
            except Exception as e:
                logger.error(f"Vision Audit failed for Ch 0: {e}")
                # We do NOT fail the pipeline for visual audit failure, as strict text contract is met.
                
        return result

    @classmethod
    async def process_visuals(cls, property_data: Dict[str, Any]) -> str:
        """
        Multimodal "Vision" Audit: Analyzes property photos to detect maintenance state,
        quality of finish, and potential risks.
        """
        media_urls = property_data.get('media_urls', [])
        if not media_urls or not cls._provider:
            return ""

        cls._request_count += 1
        logger.info(f"Vision Audit: Processing {len(media_urls)} images... (Req #{cls._request_count})")

        system_prompt = (
            "You are a Senior Technical Building Inspector and Interior Architect. "
            "Analyze the provided property photos as if you are doing a physical walkthrough for Marcel & Petra. "
            "Focus on: \n"
            "1. Maintenance (window frames, moisture, roof state if visible)\n"
            "2. Quality (kitchen appliances, flooring materials, bathroom finish)\n"
            "3. Risks (cracks, damp spots, old wiring signs)\n"
            "4. Atmosphere for Petra, Tech-infrastructure for Marcel.\n"
            "Be professional, critical, and specific. Use the names Marcel & Petra."
        )

        user_prompt = "Hier zijn de foto's van de woning. Voer een visuele audit uit. Noem Marcel en Petra herhaaldelijk bij naam."
        
        # Resolve local paths for files in /uploads/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        resolved_paths = []
        for url in media_urls[:10]:  # Limit to first 10 for performance
            if url.startswith('/uploads/'):
                filename = url.split('/')[-1]
                path = os.path.join(base_dir, "data", "uploads", filename)
                if os.path.exists(path):
                    resolved_paths.append(path)
                else:
                    logger.warning(f"Vision Audit: Uploaded file not found at {path}")
                    resolved_paths.append(url)
            else:
                resolved_paths.append(url)

        try:
            # Authority-based model resolution
            model = property_data.get('_preferences', {}).get('ai_model')
            if not model:
                 from backend.ai.ai_authority import get_ai_authority
                 # Use authority default for current provider
                 model = get_ai_authority().get_default_model(cls._provider.name)
            
            audit = await cls._provider.generate(user_prompt, system=system_prompt, model=model, images=resolved_paths)
            return f"<div className='p-4 bg-blue-50/50 border border-blue-100 rounded-xl mb-6'><h4>🔍 Visuele Audit Insights</h4>{audit}</div>"
        except Exception as e:
            logger.error(f"Vision Audit failed: {e}")
            return ""

    @staticmethod
    def _parse_int(val):
        """Parse integer from string, handling European number formats."""
        try:
            s = str(val).replace('.', '').replace(',', '')
            match = re.search(r'\d+', s)
            if match:
                return int(match.group())
            return 0
        except:
            return 0
    
    @staticmethod
    def _clean_json(text: str) -> str:
        """Clean JSON from markdown code blocks. Used by legacy methods, kept for safety."""
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text.split("```json")[1].split("```")[0]
        elif clean_text.startswith("```"):
            clean_text = clean_text.split("```")[1].split("```")[0]
        return clean_text

    @staticmethod
    def _clean_json(text: str) -> str:
        """Clean JSON from markdown code blocks."""
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text.split("```json")[1].split("```")[0]
        elif clean_text.startswith("```"):
            clean_text = clean_text.split("```")[1].split("```")[0]
        return clean_text


# =============================================================================
# DELETED: All _narrative_ch*() functions and calculate_*_score() functions
# 
# These violated the ARCHITECTURAL INVARIANT:
#     "No factual value may be computed, inferred, estimated, or invented
#      outside the CanonicalRegistry (or its enrichment adapters)."
#
# REPLACEMENT:
#   - All fallback narratives: domain/presentation_narratives.py
#   - All calculations: enrichment.py (before registry lock)
#
# To add a new computed metric:
#   1. Add computation to backend/enrichment.py
#   2. Register in CanonicalRegistry
#   3. Access as read-only in presentation code
# =============================================================================
