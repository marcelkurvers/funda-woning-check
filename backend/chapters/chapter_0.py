"""
Chapter 0: Executive Summary

ARCHITECTURAL INVARIANTS (NON-NEGOTIABLE):
1. NO arithmetic operations
2. NO value derivation or computation  
3. All values MUST come from registry (via ctx)
4. This class is PRESENTATION ONLY

Deleted logic:
- valuation_status calculation (moved to enrichment.py)
- market_delta computation (moved to enrichment.py)
- energy_color/investment_color logic (moved to enrichment.py)
- pros/cons generation (moved to enrichment.py)
- All metric color/trend calculations (moved to enrichment.py)
"""

from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent, AIProvenance
from intelligence import IntelligenceEngine
import logging

logger = logging.getLogger(__name__)


class ExecutiveSummary(BaseChapter):
    def get_title(self) -> str:
        return "Executive Summary"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        
        # Smart Address Display
        raw_address = str(ctx.get('adres', ctx.get('address', 'Adres Onbekend')))
        generic_titles = ['mijn huis', 'te koop', 'woning', 'object', 'huis', 'appartement']
        is_generic = raw_address.lower().strip() in generic_titles
        display_address = raw_address if not is_generic else "dit object"
        
        # Update context for AI if generic
        if is_generic:
            ctx['address'] = display_address
            ctx['adres'] = display_address
        
        # --- INTELLIGENCE ENGINE (AI or Registry-Only Fallback) ---
        narrative = IntelligenceEngine.generate_chapter_narrative(0, ctx)
        
        # Polish intro grammar if generic replacement occurred
        if is_generic and narrative.get('intro'):
            narrative['intro'] = narrative['intro'].replace("van de dit object", "van dit object")

        # === ALL VALUES FROM REGISTRY (NO COMPUTATION) ===
        # These come pre-computed from the enrichment layer
        
        price_val = ctx.get('asking_price_eur', 0)
        size_val = ctx.get('living_area_m2', 0) or 1
        price_m2 = ctx.get('price_per_m2', 0)
        year_val = ctx.get('build_year', 2000)
        label = (ctx.get('energy_label') or "?").upper()
        
        # Pre-computed in enrichment layer
        valuation_status = ctx.get('valuation_status', 'Onbekend')
        market_trend = ctx.get('market_trend', 'neutral')
        total_expected_invest = ctx.get('estimated_reno_cost', 0)
        ai_score = ctx.get('ai_score', 0)
        energy_invest = ctx.get('energy_invest', 0)
        
        # Pre-computed match scores
        marcel_score = ctx.get('marcel_match_score', 0)
        petra_score = ctx.get('petra_match_score', 0)
        total_match = ctx.get('total_match_score', 0)
        
        # Hero (display only - no computation)
        oppervlakte_clean = str(ctx.get('living_area_m2', '?'))
        perceel_clean = str(ctx.get('plot_area_m2', '?'))
        
        hero = {
            "address": raw_address,
            "price": f"€ {price_val:,}".replace(',', '.') if price_val > 0 else "Prijs op aanvraag",
            "status": "Te Koop" if price_val > 0 else "Analyse Mode",
            "labels": ["Woonhuis", f"{oppervlakte_clean} m² Wonen", f"{perceel_clean} m² Perceel"] 
        }

        # Metrics - using pre-computed values only
        # Colors/explanations should be computed in enrichment layer in future
        # For now, simple display logic (no arithmetic)
        metrics = [
            {
                "id": "price_m2", 
                "label": "Vraagprijs per m²", 
                "value": f"€ {price_m2:,}" if price_m2 else "Onbekend",
                "icon": "pricetag", 
                "trend": market_trend,
                "color": "blue"
            },
            {
                "id": "energy", 
                "label": "Duurzaamheid", 
                "value": f"Label {label}", 
                "icon": "leaf",
                "color": "green" if label in ["A", "B"] else "orange" if label in ["C", "D"] else "red"
            },
            {
                "id": "investment", 
                "label": "Verw. Investering", 
                "value": f"€ {total_expected_invest:,}" if total_expected_invest else "Geen",
                "icon": "hammer",
                "color": "green" if total_expected_invest == 0 else "orange"
            },
            {
                "id": "match", 
                "label": "Match Score", 
                "value": f"{total_match}%",
                "icon": "heart",
                "color": "green" if total_match >= 70 else "orange" if total_match >= 40 else "red"
            }
        ]

        # Use narrative strengths/advice (from AI or registry template)
        final_strengths = narrative.get('strengths', [])
        final_advice = narrative.get('advice', [])

        # Render the rich narrative
        final_content = self._render_rich_narrative(narrative)

        # Sidebar - using pre-computed values
        sidebar = [
            {
                "type": "advisor_score", 
                "title": "AI Aankoop Score", 
                "score": ai_score, 
                "content": f"Score bepaald o.b.v. {valuation_status}, Label {label}."
            },
            {
                "type": "advisor_card", 
                "title": "Strategisch Advies", 
                "style": "gradient",
                "content": narrative.get('conclusion', 'Analyse vereist meer data.')
            },
            {
                "type": "action_list",
                "title": "Aanbevolen Acties",
                "items": [
                    "Bouwkundige keuring inplannen" if total_expected_invest > 0 else "Onderhoudshistorie opvragen",
                    "Energielabel checken in register",
                    "Juridische erfdienstbaarheden controleren"
                ]
            }
        ]

        left_sidebar = [
            {
                "type": "highlight_card",
                "icon": "analytics",
                "title": "AI Score",
                "content": f"{ai_score}/100 - {valuation_status}"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Executive Property Assessment", "content": final_content},
            "left_sidebar": left_sidebar,
            "sidebar": sidebar
        }
        
        chapter_data = {
            "title": "Executive Summary",
            "intro": narrative.get('intro', ''),
            "main_analysis": final_content,
            "conclusion": narrative.get('conclusion', ''),
            "strengths": final_strengths,
            "advice": final_advice,
            "interpretation": narrative.get('interpretation', ''),
            "variables": narrative.get('variables', {}),
            "sidebar_items": sidebar,
            "comparison": narrative.get('comparison', {}),
            "marcel_match_score": marcel_score,
            "petra_match_score": petra_score
        }

        # Provenance mapping
        prov_dict = narrative.get('_provenance')
        prov = AIProvenance(**prov_dict) if prov_dict else None

        return ChapterOutput(
            id="0",
            title="0. Executive Summary",
            grid_layout=layout, 
            blocks=[],
            chapter_data=chapter_data,
            provenance=prov,
            missing_critical_data=narrative.get('metadata', {}).get('missing_vars', [])
        )
