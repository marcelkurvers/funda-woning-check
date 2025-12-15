
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine
import re

class MarketPosition(BaseChapter):
    def get_title(self) -> str:
        return "Marktpositie"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(11, ctx)
        
        price_raw = str(ctx.get('prijs', '0'))
        price_digits = re.sub(r'[^\d]', '', price_raw)
        price_val = int(price_digits) if price_digits else 0
        living_area = IntelligenceEngine._parse_int(ctx.get('oppervlakte', '0')) or 1
        price_m2 = int(price_val / living_area) if living_area > 0 else 0
        avg_m2 = 4500 
        diff_pct = round(((price_m2 - avg_m2) / avg_m2) * 100)
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": f"€ {price_m2} / m²",
            "status": "Marktanalyse",
            "labels": [f"{diff_pct}% vs regio" if diff_pct != 0 else "Conform regio"]
        }
        
        metrics = [
            {"id": "m2", "label": "Vraagprijs/m²", "value": f"€ {price_m2}", "icon": "pricetag"},
            {"id": "avg", "label": "Gem. in buurt", "value": f"€ {avg_m2}", "icon": "stats-chart"},
            {"id": "days", "label": "Looptijd", "value": "Start", "icon": "time"},
            {"id": "comp", "label": "Concurrentie", "value": "Gemiddeld", "icon": "people"}
        ]
        
        chart_html = f"""
        <div class="market-chart">
            <div class="chart-label">Deze Woning</div>
            <div class="chart-bar-container">
                <div class="chart-bar primary" style="width: {min(100, (price_m2/5000)*100)}%;">€ {price_m2}</div>
            </div>
            
            <div class="chart-label">Gemiddeld Wijk</div>
             <div class="chart-bar-container">
                <div class="chart-bar secondary" style="width: {min(100, (avg_m2/5000)*100)}%;">€ {avg_m2}</div>
            </div>
        </div>
        """
        
        main_content = self._render_rich_narrative(narrative, extra_html=f"""
        {chart_html}
        """)
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Marktvergelijking", "content": main_content},
            "sidebar": [{"type": "advisor_score", "title": "Verkoopbaarheid", "score": 75}]
        }

        return ChapterOutput(
            title="11. Marktpositie",
            grid_layout=layout, 
            blocks=[]
        )
