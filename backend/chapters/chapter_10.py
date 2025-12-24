"""
Chapter 10: Financial Analysis

ARCHITECTURAL INVARIANTS (NON-NEGOTIABLE):
1. NO arithmetic operations (kk_costs, notary, makelaar, etc.)
2. NO value derivation or computation
3. All values MUST come from registry (via ctx)
4. This class is PRESENTATION ONLY

All financial calculations are now performed in enrichment.py
and registered in the CanonicalRegistry BEFORE this chapter runs.
"""

from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine
import logging

logger = logging.getLogger(__name__)


class FinancialAnalysis(BaseChapter):
    def get_title(self) -> str:
        return "Financiële Analyse"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(10, ctx)
        
        # === ALL VALUES FROM REGISTRY (NO COMPUTATION) ===
        # Ensure numeric types for formatting
        price_val = ctx.get('asking_price_eur', 0)
        if isinstance(price_val, str):
            price_val = int(''.join(filter(str.isdigit, price_val)) or '0')
        price_val = int(price_val) if price_val else 0
        
        price_m2 = ctx.get('price_per_m2', 0)
        if isinstance(price_m2, str):
            price_m2 = int(''.join(filter(str.isdigit, price_m2)) or '0')
        price_m2 = int(price_m2) if price_m2 else 0
        
        label = ctx.get('energy_label', '?')
        year = ctx.get('build_year', 0)
        
        # Pre-computed financial values (from enrichment layer)
        estimated_kk = ctx.get('estimated_kk', 0)
        estimated_total = ctx.get('estimated_total_cost', price_val)
        valuation_status = ctx.get('valuation_status', 'Onbekend')
        energy_invest = ctx.get('energy_invest', 0)
        construction_invest = ctx.get('construction_invest', 0)
        estimated_reno = ctx.get('estimated_reno_cost', 0)
        
        # Hero (display only)
        hero = {
            "address": ctx.get('adres', ctx.get('address', 'Adres Onbekend')),
            "price": f"€ {price_val:,}".replace(',', '.') if price_val else "Onbekend",
            "status": "Vraagprijs",
            "labels": ["Kosten Koper", "Financiering"]
        }
        
        # Metrics - using pre-computed values only
        metrics = [
            {
                "id": "price", 
                "label": "Vraagprijs", 
                "value": f"€ {price_val:,}".replace(',', '.') if price_val else "Onbekend",
                "icon": "pricetag", 
                "color": "blue",
                "explanation": "Kosten Koper excl."
            },
            {
                "id": "price_m2", 
                "label": "Prijs per m²", 
                "value": f"€ {price_m2:,}" if price_m2 else "Onbekend",
                "icon": "analytics", 
                "color": "blue"
            },
            {
                "id": "reno", 
                "label": "Geschatte Renovatie", 
                "value": f"€ {estimated_reno:,}" if estimated_reno else "€ 0",
                "icon": "hammer", 
                "color": "orange" if estimated_reno > 0 else "green"
            },
            {
                "id": "valuation", 
                "label": "Marktwaardering", 
                "value": valuation_status,
                "icon": "trending-up", 
                "color": "blue"
            }
        ]
        
        # Main content from narrative (AI or registry template)
        breakdown_html = self._render_rich_narrative(narrative)

        left_sidebar = [
            {
                "type": "highlight_card",
                "icon": "cash",
                "title": "Vraagprijs",
                "content": f"€ {price_val:,}".replace(',', '.') if price_val else "Onbekend"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Kostenanalyse", "content": breakdown_html},
            "left_sidebar": left_sidebar,
            "sidebar": [
                {
                    "type": "advisor", 
                    "title": "Financieel Advies", 
                    "content": narrative.get('conclusion', 'Analyse vereist meer data.'),
                    "style": "gradient"
                }
            ]
        }
        
        return ChapterOutput(
            title="10. Financiële Analyse",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative
        )
