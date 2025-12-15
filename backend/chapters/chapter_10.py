
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine
import re

class FinancialAnalysis(BaseChapter):
    def get_title(self) -> str:
        return "Financiële Analyse"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(10, ctx)
        
        price_raw = str(ctx.get('prijs', '0'))
        price_digits = re.sub(r'[^\d]', '', price_raw)
        price_val = int(price_digits) if price_digits else 0
        
        kk_costs = int(price_val * 0.02)
        notary = 1500
        makelaar = int(price_val * 0.015)
        total_acquisition = price_val + kk_costs + notary + makelaar
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": f"€ {price_val:,}",
            "status": "Vraagprijs",
            "labels": ["Kosten Koper", "Financiering"]
        }
        
        metrics = [
            {"id": "price", "label": "Vraagprijs", "value": f"€ {price_val:,}", "icon": "pricetag"},
            {"id": "kk", "label": "Kosten Koper (est.)", "value": f"€ {(kk_costs+notary+makelaar):,}", "icon": "wallet", "color": "orange"},
            {"id": "total", "label": "Totaal Benodigd", "value": f"€ {total_acquisition:,}", "icon": "cash"},
            {"id": "monthly", "label": "Maandlast (ind.)", "value": f"€ {int(total_acquisition * 0.04 / 12):,}", "icon": "calendar"}
        ]
        
        breakdown_html = self._render_rich_narrative(narrative, extra_html=f"""
        <table style="width:100%; text-align: left;">
            <tr><td>Overdrachtsbelasting:</td><td>€ {kk_costs:,}</td></tr>
            <tr><td>Notaris:</td><td>€ {notary:,}</td></tr>
            <tr><td>Makelaar:</td><td>€ {makelaar:,}</td></tr>
            <tr><td><strong>Totaal K.K.:</strong></td><td><strong>€ {(kk_costs+notary+makelaar):,}</strong></td></tr>
        </table>
        """)

        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Kostenanalyse", "content": breakdown_html},
            "sidebar": [
                {"type": "advisor", "title": "Biedingsadvies", "content": f"Overweeg een bod rond € {int(price_val*0.95):,}.", "style": "gradient"}
            ]
        }
        
        return ChapterOutput(
            title="10. Financiële Analyse",
            grid_layout=layout, 
            blocks=[]
        )
