
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class LocationAnalysis(BaseChapter):
    def get_title(self) -> str:
        return "Locatie & Omgeving"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        vibe = "Stadsleven" if "straat" in ctx.get('adres', '').lower() else "Landelijk"
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": "Locatie Rapport",
            "status": vibe,
            "labels": ["Woonwijk", "Voorzieningen"]
        }
        
        metrics = [
            # Add colors and explanations for consistency
            {"id": "shop", "label": "Supermarkt", "value": "5 min", "icon": "cart", "trend": "neutral", "color": "green", "explanation": "Dichtbij"},
            {"id": "train", "label": "Treinstation", "value": "10 min", "icon": "train", "trend": "neutral", "color": "green", "explanation": "Fietsafstand"},
            {"id": "school", "label": "Basisschool", "value": "2 min", "icon": "school", "trend": "neutral", "color": "green", "explanation": "Zeer dichtbij"},
            {"id": "center", "label": "Centrum", "value": "15 min", "icon": "business", "trend": "neutral", "color": "orange", "explanation": "Fietsafstand"},
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
            metrics.append({"id":"price_deviation","label":"Prijsafwijking","value":f"{price_dev_pct:+,}%" if price_dev_pct != 0 else "0%","icon":"analytics","color":"green" if price_dev_pct < 5 else "orange","explanation": "vs markt"})
        future_score = 80 if label in ["A","A+","A++","B"] else 60 if label in ["C","D"] else 40
        metrics.append({"id":"energy_future","label":"Energie Toekomstscore","value":f"{future_score}","icon":"leaf","color":"green" if future_score>=70 else "orange" if future_score>=50 else "red","trend":"neutral"})
        maintenance = "Hoog" if reno_cost>30000 else "Middelmatig" if reno_cost>0 else "Laag"
        # Shorten label to prevent truncation
        metrics.append({"id":"maintenance_intensity","label":"Onderhoud","value":maintenance,"icon":"hammer","trend":"neutral", "color": "red" if reno_cost > 30000 else "green"})
        family = "Geschikt voor gezin" if (IntelligenceEngine._parse_int(ctx.get('oppervlakte','0')) or 0) >= 120 else "Minder geschikt voor groot gezin"
        metrics.append({"id":"family_suitability","label":"Gezinsgeschiktheid","value":family,"icon":"people","trend":"neutral"})
        lt_quality = "Hoog" if "jong" in construction_alert.lower() else "Middelmatig" if "aandacht" in construction_alert.lower() else "Laag"
        metrics.append({"id":"long_term_quality","label":"Lange-termijn kwaliteit","value":lt_quality,"icon":"shield","trend":"neutral"})
        
        amenity_html = self._render_rich_narrative(narrative, extra_html=f"""
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex flex-col items-center text-center">
                <div class="w-10 h-10 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-2 text-xl"><ion-icon name="cart"></ion-icon></div>
                <div class="font-bold text-slate-700 block w-full">Supermarkt</div>
                <div class="text-xs text-green-600 font-bold mt-1 block w-full">8.5 Score</div>
            </div>
            <div class="bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex flex-col items-center text-center">
                <div class="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mb-2 text-xl"><ion-icon name="train"></ion-icon></div>
                <div class="font-bold text-slate-700 block w-full">OV</div>
                <div class="text-xs text-green-600 font-bold mt-1 block w-full">7.0 Score</div>
            </div>
            <div class="bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex flex-col items-center text-center">
                <div class="w-10 h-10 bg-orange-50 text-orange-600 rounded-full flex items-center justify-center mb-2 text-xl"><ion-icon name="school"></ion-icon></div>
                <div class="font-bold text-slate-700 block w-full">Scholen</div>
                <div class="text-xs text-green-600 font-bold mt-1 block w-full">9.0 Score</div>
            </div>
            <div class="bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex flex-col items-center text-center">
                <div class="w-10 h-10 bg-rose-50 text-rose-600 rounded-full flex items-center justify-center mb-2 text-xl"><ion-icon name="restaurant"></ion-icon></div>
                <div class="font-bold text-slate-700 block w-full">Horeca</div>
                <div class="text-xs text-green-600 font-bold mt-1 block w-full">8.0 Score</div>
            </div>
        </div>
        """)
        
        # Left sidebar: Location proximity
        # Left sidebar: Location proximity
        left_sidebar = [
             {
                "type": "highlight_card",
                "icon": "location",
                "title": "Buurttype",
                "content": f"{vibe} - Rustige woonwijk met goede voorzieningen"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Locatie & Omgeving Analyse", "content": amenity_html},
            "left_sidebar": left_sidebar,
            "sidebar": [
                {"type": "advisor_score", "title": "Leefbaarheid", "score": 82, "content": "Score gebaseerd op voorzieningen en bereikbaarheid."},
                {"type": "action_list", "title": "Buurt Check", "items": ["Bestemmingsplan checken", "Parkeervergunning nodig?", "Buurtpreventie app"]}
            ]
        }

        return ChapterOutput(
            title="2. Locatie & Omgeving",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative
        )
