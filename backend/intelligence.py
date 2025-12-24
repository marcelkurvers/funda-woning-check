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
PAGE NARRATIVE GENERATION

Rol
Je bent een analytisch redacteur die een inhoudelijke tekst schrijft voor één specifieke rapportpagina.

Je schrijft géén samenvatting.
Je schrijft géén marketingtekst.
Je schrijft een verklarende, duidende analyse.

CONTEXT (SYSTEEMGELEVERD)

Je ontvangt:

De titel en het doel van deze pagina

De relevante variabelen en KPI’s

Eventuele onzekerheden of datakwaliteit

Je mag alleen deze context gebruiken.

OPDRACHT (VERPLICHT)

Schrijf een doorlopende narratieve analyse van minimaal 300 woorden waarin je:
1. Uitlegt wat de variabelen en KPI’s op deze pagina betekenen
2. De onderlinge samenhang en implicaties beschrijft
3. Aangeeft waar sterktes, spanningen of risico’s zitten
4. Dit vertaalt naar betekenis voor de gebruiker (Marcel & Petra)

Geen tabellen herhaalt
Geen losse opsommingen maakt
Geen bullets
Geen cijfers herhalen, maar duiden

STIJL
Rustig, Analytisch, Redactioneel, Verklarend

VALIDATIECRITERIA (SYSTEEM)
Minimaal 300 woorden
Eén doorlopende tekst
Geen nieuwe aannames
Consistent met de aangeleverde context

OUTPUT FORMAT
{
  "narrative_text": "...",
  "word_count": 342
}
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
        
        ARCHITECTURAL INVARIANT (NO EXCEPTIONS):
        - When AI is available: AI generates the narrative
        - When AI is NOT available: Registry-only templates are used
        - NO heuristics, NO estimation, NO computation in fallback path
        
        All values MUST come from the registry (pre-computed in enrichment layer).
        """
        # Import registry-only fallback templates
        from backend.domain.presentation_narratives import get_registry_only_narrative
        
        # Build data context from registry (NO COMPUTATION - just passthrough)
        data = {
            # All values come from context (which comes from locked registry)
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
            # Pre-computed enriched values (from enrichment layer)
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
            # Pre-computed scores (from enrichment layer)
            "ai_score": ctx.get('ai_score', 0),
            "marcel_match_score": ctx.get('marcel_match_score', 0),
            "petra_match_score": ctx.get('petra_match_score', 0),
            "marcel_reasons": ctx.get('marcel_reasons', []),
            "petra_reasons": ctx.get('petra_reasons', []),
            "total_match_score": ctx.get('total_match_score', 0)
        }

        # REGISTRY-ONLY FALLBACK (NO COMPUTATION)
        # This is the baseline - no heuristics, no estimation
        result = get_registry_only_narrative(chapter_id, data)
        
        # For Chapter 0, include property core for dashboard
        if chapter_id == 0:
            result["property_core"] = data

        # AI OVERRIDE - If provider is available, use AI generation
        if IntelligenceEngine._provider:
            try:
                from backend.ai.bridge import safe_execute_async
                ai_result = safe_execute_async(IntelligenceEngine._generate_ai_narrative(chapter_id, data, result))
                
                if ai_result:
                    p_core = result.get("property_core")
                    result.update(ai_result)
                    if p_core: 
                        result["property_core"] = p_core
            except Exception as e:
                logger.error(f"AI Generation failed for Chapter {chapter_id}: {e}")
                raise  # Re-raise to stop pipeline - NO silent fallback to heuristics
        
        # Ensure provenance tracking (allowed metadata)
        if '_provenance' not in result:
            provider_name = IntelligenceEngine._provider.name if IntelligenceEngine._provider else "Registry Template"
            model_name = getattr(IntelligenceEngine._provider, 'default_model', 'Presentation-Only') if IntelligenceEngine._provider else "Presentation-Only"
            result['_provenance'] = { 
                "provider": provider_name.capitalize() if hasattr(provider_name, 'capitalize') else str(provider_name),
                "model": model_name, 
                "confidence": "high" if IntelligenceEngine._provider else "low",
                "request_count": IntelligenceEngine._request_count
            }
        else:
            result['_provenance']["request_count"] = IntelligenceEngine._request_count

        result['chapter_id'] = chapter_id
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
            model = property_data.get('_preferences', {}).get('ai_model', 'gpt-4o')
            if 'gpt-3.5' in model:
                model = 'gpt-4o'
            
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

    @classmethod
    async def _generate_ai_narrative(cls, chapter_id: int, data: Dict[str, Any], fallback: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Uses AI provider to generate the narrative with strict data adherence.
        Uses the PAGE_NARRATIVE_SYSTEM_PROMPT for high-quality editorial content.
        """
        if not cls._provider:
            return None

        cls._request_count += 1

        # Filter the data context to ONLY what this chapter is allowed to see/own
        from backend.domain.ownership import OwnershipMap
        scoped_data = OwnershipMap.get_chapter_context(chapter_id, data)
        
        # Get chapter-specific AI prompt
        from backend.domain.chapter_variables import get_chapter_ai_prompt, should_show_core_data
        chapter_specific_prompt = get_chapter_ai_prompt(chapter_id)
        
        # Determine variable focus
        chapter_vars_description = {
            0: "Status: Core Data. Focus: Executive overview.",
            1: "Status: Derived. Focus: Building classification & characteristics.",
            2: "Status: Matching. Focus: Marcel & Petra specific preferences.",
            3: "Status: Technical. Focus: Maintenance, construction state.",
            4: "Status: Energy. Focus: Sustainability, insulation, costs.",
            5: "Status: Layout. Focus: Space usage, light, flow.",
            6: "Status: Finish. Focus: Kitchen, bath, materials.",
            7: "Status: Outdoor. Focus: Garden, privacy, orientation.",
            8: "Status: Mobility. Focus: Parking, transport.",
            9: "Status: Legal. Focus: Ownership, VvE, obligations.",
            10: "Status: Financial. Focus: Costs, investment, TCO.",
            11: "Status: Market. Focus: Value, comparison, strategy.",
            12: "Status: Advice. Focus: Final verdict & bidding."
        }
        target_vars = chapter_vars_description.get(chapter_id, "Chapter specific variables")

        prefs = data.get('_preferences', {})
        provider_name = getattr(cls._provider, 'name', 'unknown')
        model_name = prefs.get('ai_model', 'unknown')

        # Construct User Prompt following the System Prompt structure
        user_prompt = f"""
CONTEXT (SYSTEEMGELEVERD):

TITEL EN DOEL VAN DEZE PAGINA:
Chapter {chapter_id}
Doel: {chapter_specific_prompt}

RELEVANTE VARIABELEN EN KPI'S:
{target_vars}

DATA UIT REGISTRY (ALLEEN DEZE GEBRUIKEN):
{json.dumps(scoped_data, default=str)}

ONZEKERHEDEN / DATAKWALITEIT:
Missing/Unknown: {[k for k,v in scoped_data.items() if v in [None, '?', 'onbekend', 'Onbekend']]}

GEBRUIKERS CONTEXT (Marcel & Petra):
Marcel: {json.dumps(prefs.get('marcel', {}), default=str)}
Petra: {json.dumps(prefs.get('petra', {}), default=str)}
Match Scores: Marcel={data.get('marcel_match_score', 0)}%, Petra={data.get('petra_match_score', 0)}%
"""

        try:
            # We use json_mode=True to enforce the OUTPUT FORMAT
            response_text = await cls._provider.generate(
                user_prompt, 
                system=PAGE_NARRATIVE_SYSTEM_PROMPT, 
                model=model_name, 
                json_mode=True
            )
            
            if not response_text or not isinstance(response_text, str):
                raise ValueError(f"Provider returned invalid response type: {type(response_text)}")

            result_json = json.loads(cls._clean_json(response_text))
            
            # Map the new output format to the application's expected structure
            # The prompt returns { "narrative_text": "...", "word_count": ... }
            # We map "narrative_text" to "main_analysis"
            
            narrative_text = result_json.get("narrative_text", "")
            
            final_result = {
                "main_analysis": narrative_text,
                # Preserve title/intro/conclusion from fallback or keep empty if desired
                # The user requested specific narrative generation, usually replacing the main body.
                "title": fallback.get("title"), 
                "intro": fallback.get("intro"), 
                "conclusion": fallback.get("conclusion"),
                "variables": fallback.get("variables", {}), # Keep variable list structure if present
                "metadata": {
                    "word_count": result_json.get("word_count", 0),
                    "confidence": "high",
                    "source": "ai_generated"
                }
            }
            
            # Enrich with Provenance
            final_result['_provenance'] = {
                "provider": provider_name,
                "model": model_name,
                "confidence": "high",
                "timestamp": datetime.now().isoformat()
            }

            # Vision Audit for Chapter 0 (keep existing logic)
            if chapter_id == 0 and data.get("media_urls") and IntelligenceEngine._provider:
                try:
                    vision_audit = await IntelligenceEngine.process_visuals(data)
                    if vision_audit:
                        final_result["main_analysis"] = vision_audit + "\n\n" + final_result.get("main_analysis", "")
                except Exception as e:
                    logger.error(f"Vision Audit failed for Ch 0: {e}")

            return final_result

        except Exception as e:
            logger.error(f"AI generation failed for Ch {chapter_id}: {e}")
            # Return None to trigger fallback to registry templates
            return None

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
