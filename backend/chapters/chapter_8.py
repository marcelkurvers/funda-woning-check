
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class ParkingAccessibility(BaseChapter):
    def get_title(self) -> str:
        return "Parkeren & Bereikbaarheid"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(8, ctx)
        address = ctx.get('adres', '')
        parking_status = "Openbaar"
        if "laan" in address or "weg" in address: parking_status = "Oprit?"
        
        hero = {
            "address": address,
            "price": "Mobiliteit",
            "status": "Goed Bereikbaar",
            "labels": ["Auto", "OV", "Fiets"]
        }
        
        metrics = [
            {"id": "parking", "label": "Parkeren", "value": parking_status, "icon": "car"},
            {"id": "ev", "label": "Laadpaal", "value": "Mogelijk", "icon": "flash"},
            {"id": "highway", "label": "Snelweg", "value": "< 10 min", "icon": "speedometer"},
            {"id": "public", "label": "OV Halte", "value": "Nabij", "icon": "bus"}
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
        
        main_content = self._render_rich_narrative(narrative, extra_html=f"""
        <ul class="check-list">
            <li>Check parkeervergunning wachttijden bij gemeente.</li>
            <li>Is er ruimte voor een laadpaal op eigen terrein?</li>
            <li>Hoe druk is de straat tijdens spitsuur?</li>
        </ul>
        """)
        
        # Left sidebar: Parking info
        left_sidebar = [
            {
                "type": "key_facts",
                "title": "Parkeren",
                "facts": [
                    {"label": "Type", "value": parking_status},
                    {"label": "Laadpaal", "value": "Mogelijk"},
                    {"label": "OV Afstand", "value": "Nabij"}
                ]
            },
            {
                "type": "highlight_card",
                "icon": "car",
                "title": "Mobiliteit",
                "content": "Goed bereikbaar met auto en OV"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Parkeren & Mobiliteit", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [{"type": "advisor", "title": "Toekomst", "content": "Elektrisch rijden neemt toe. Een eigen oprit is goud waard."}]
        }

        return ChapterOutput(
            title="8. Parkeren & Bereikbaarheid",
            grid_layout=layout, 
            blocks=[]
        )
