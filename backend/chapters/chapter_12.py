"""
Chapter 12: Advice & Conclusion

ARCHITECTURAL INVARIANTS (NON-NEGOTIABLE):
1. NO arithmetic operations
2. NO value derivation (e.g., fit_score * 10, reno_cost calculations)
3. All values MUST come from registry (via ctx)
4. This class is PRESENTATION ONLY

All calculations (fit_score, reno_cost, energy_risk, etc.) are 
now performed in enrichment.py and read from registry.
"""

from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine
import logging

logger = logging.getLogger(__name__)


class AdviceConclusion(BaseChapter):
    def get_title(self) -> str:
        return "Advies & Conclusie"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(12, ctx)
        
        hero = {
            "address": ctx.get('adres', ctx.get('address', 'Adres Onbekend')),
            "price": "Eindoordeel",
            "status": "Samenvatting",
            "labels": ["Koopadvies", "Strategie"]
        }
        
        main_content = self._render_rich_narrative(narrative)
        
        # === ALL VALUES FROM REGISTRY (NO COMPUTATION) ===
        ai_score = ctx.get('ai_score', 0)
        total_match_score = ctx.get('total_match_score', 0)
        label = ctx.get('energy_label', '?')
        estimated_reno = ctx.get('estimated_reno_cost', 0)
        valuation_status = ctx.get('valuation_status', 'Onbekend')
        
        # Metrics - using pre-computed values only
        metrics = [
            {
                "id": "final", 
                "label": "AI Score", 
                "value": f"{ai_score}/100",
                "icon": "trophy", 
                "color": "blue" if ai_score >= 70 else "orange" if ai_score >= 40 else "red"
            },
            {
                "id": "match", 
                "label": "Match Score", 
                "value": f"{total_match_score}%",
                "icon": "heart", 
                "color": "green" if total_match_score >= 70 else "orange" if total_match_score >= 40 else "red"
            },
            {
                "id": "energy", 
                "label": "Energielabel", 
                "value": label,
                "icon": "leaf", 
                "color": "green" if label in ["A", "B"] else "orange" if label in ["C", "D"] else "red"
            },
            {
                "id": "reno", 
                "label": "Geschatte Renovatie", 
                "value": f"€ {estimated_reno:,}" if estimated_reno else "€ 0",
                "icon": "hammer",
                "color": "green" if estimated_reno == 0 else "orange"
            }
        ]
        
        left_sidebar = [
            {
                "type": "highlight_card",
                "icon": "checkmark-circle",
                "title": "Aanbeveling",
                "content": f"AI Score: {ai_score}/100 - {valuation_status}"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Eindconclusie", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [
                {
                    "type": "advisor_card", 
                    "title": "Vervolgstappen", 
                    "style": "gradient", 
                    "content": narrative.get('conclusion', '1. Bezichtigen 2. Documenten 3. Bieden')
                }
            ]
        }

        return ChapterOutput(
            title="12. Advies & Conclusie",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative
        )
