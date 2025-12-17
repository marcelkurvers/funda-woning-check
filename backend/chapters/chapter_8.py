
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
            {"id": "parking", "label": "Parkeren", "value": parking_status, "icon": "car", "color": "orange" if parking_status == "Openbaar" else "green", "explanation": "Vergunning check" if parking_status == "Openbaar" else "Op eigen terrein"},
            {"id": "ev", "label": "Laadpaal", "value": "Mogelijk", "icon": "flash", "color": "green", "explanation": "Infra aanwezig"},
            {"id": "highway", "label": "Snelweg", "value": "< 10 min", "icon": "speedometer", "color": "green", "explanation": "Goede uitvalswegen"},
            {"id": "public", "label": "OV Halte", "value": "Nabij", "icon": "bus", "color": "blue", "explanation": "Loopafstand"}
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
        maintenance = "Hoog" if reno_cost>30000 else "Middelmatig" if reno_cost>0 else "Laag"
        metrics.append({"id":"maintenance_intensity","label":"Onderhoud","value":maintenance,"icon":"hammer","trend":"neutral", "color": "red" if reno_cost > 30000 else "green"})
        family = "Geschikt voor gezin" if (IntelligenceEngine._parse_int(ctx.get('oppervlakte','0')) or 0) >= 120 else "Minder geschikt voor groot gezin"
        metrics.append({"id":"family_suitability","label":"Gezinsgeschiktheid","value":family,"icon":"people","trend":"neutral"})
        lt_quality = "Hoog" if "jong" in construction_alert.lower() else "Middelmatig" if "aandacht" in construction_alert.lower() else "Laag"
        metrics.append({"id":"long_term_quality","label":"Lange-termijn kwaliteit","value":lt_quality,"icon":"shield","trend":"neutral"})
        
        main_content = self._render_rich_narrative(narrative, extra_html=f"""
        <div class="bg-slate-50 border border-slate-200 p-5 rounded-xl">
            <h4 class="font-bold text-slate-800 mb-3 flex items-center gap-2"><ion-icon name="list"></ion-icon> Aandachtspunten</h4>
            <ul class="space-y-2">
                <li class="flex items-start gap-2">
                    <ion-icon name="alert-circle" class="text-orange-500 mt-1"></ion-icon>
                    <span class="text-slate-700">Check parkeervergunning wachttijden bij gemeente.</span>
                </li>
                <li class="flex items-start gap-2">
                    <ion-icon name="help-circle" class="text-blue-500 mt-1"></ion-icon>
                    <span class="text-slate-700">Is er ruimte voor een laadpaal op eigen terrein?</span>
                </li>
                <li class="flex items-start gap-2">
                    <ion-icon name="time" class="text-slate-500 mt-1"></ion-icon>
                    <span class="text-slate-700">Hoe druk is de straat tijdens spitsuur?</span>
                </li>
            </ul>
        </div>
        """)
        
        # Left sidebar: Parking info
        left_sidebar = [
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
            blocks=[],
            chapter_data=narrative
        )
