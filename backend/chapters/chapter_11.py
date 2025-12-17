
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
        # New metrics (additive)
        price_val = IntelligenceEngine._parse_int(ctx.get('prijs') or ctx.get('asking_price_eur'))
        price_m2 = round(price_val / (IntelligenceEngine._parse_int(ctx.get('oppervlakte','0')) or 1))
        market_avg_m2 = ctx.get('avg_m2_price', 4800)
        label = ctx.get('label','?')
        reno_cost = 45000 if "F" in label or "G" in label else 25000 if "D" in label or "E" in label else 0
        construction_year = IntelligenceEngine._parse_int(ctx.get('bouwjaar') or ctx.get('build_year'))
        construction_alert = "Aandacht nodig" if construction_year < 1990 else "Relatief jong"
        if market_avg_m2:
            price_dev_pct = round(((price_m2 - market_avg_m2) / market_avg_m2) * 100)
            metrics.append({"id":"price_deviation","label":"Prijsafwijking %","value":f"{price_dev_pct:+,}%" if price_dev_pct != 0 else "0%","icon":"trend-up" if price_dev_pct>0 else "trend-down" if price_dev_pct<0 else "neutral","trend":"up" if price_dev_pct>0 else "down" if price_dev_pct<0 else "neutral","trend_text":f"{price_dev_pct:+}% vs markt"})
        future_score = 80 if label in ["A","A+","A++","B"] else 60 if label in ["C","D"] else 40
        metrics.append({"id":"energy_future","label":"Energie Toekomstscore","value":f"{future_score}","icon":"leaf","color":"green" if future_score>=70 else "orange" if future_score>=50 else "red","trend":"neutral"})
        maintenance = "Hoog" if reno_cost>30000 else "Middelmatig" if reno_cost>0 else "Laag"
        metrics.append({"id":"maintenance_intensity","label":"Onderhoudsintensiteit","value":maintenance,"icon":"hammer","trend":"neutral"})
        family = "Geschikt voor gezin" if (IntelligenceEngine._parse_int(ctx.get('oppervlakte','0')) or 0) >= 120 else "Minder geschikt voor groot gezin"
        metrics.append({"id":"family_suitability","label":"Gezinsgeschiktheid","value":family,"icon":"people","trend":"neutral"})
        lt_quality = "Hoog" if "jong" in construction_alert.lower() else "Middelmatig" if "aandacht" in construction_alert.lower() else "Laag"
        metrics.append({"id":"long_term_quality","label":"Lange-termijn kwaliteit","value":lt_quality,"icon":"shield","trend":"neutral"})
        
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
        
        # Left sidebar: Market comparison
        left_sidebar = [
             {
                "type": "highlight_card",
                "icon": "trending-up" if diff_pct > 0 else "trending-down" if diff_pct < 0 else "remove",
                "title": "Marktpositie",
                "content": f"{'Boven' if diff_pct > 0 else 'Onder' if diff_pct < 0 else 'Op'} marktgemiddelde"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Marktvergelijking", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [{"type": "advisor_score", "title": "Verkoopbaarheid", "score": 75}]
        }

        return ChapterOutput(
            title="11. Marktpositie",
            grid_layout=layout, 
            blocks=[]
        )
