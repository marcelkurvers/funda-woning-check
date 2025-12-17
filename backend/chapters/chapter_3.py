
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class TechnicalState(BaseChapter):
    def get_title(self) -> str:
        return "Bouwkundige Staat"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(3, ctx)
        
        build_year_str = str(ctx.get('bouwjaar', '2000'))
        build_year = IntelligenceEngine._parse_int(build_year_str) or 2000
        age = 2025 - build_year
            
        risk_level = "Laag"
        if build_year < 1920: risk_level = "Hoog"
        elif build_year < 1980: risk_level = "Gemiddeld"
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": f"Bouwjaar {build_year}",
            "status": f"Ouderdom: {age} jaar",
            "labels": [f"Risico: {risk_level}"]
        }
        
        metrics = [
            # Enrich metrics with color/explanation
            {"id": "year", "label": "Bouwjaar", "value": f"{build_year}", "icon": "calendar", "trend": "neutral", "color": "blue"},
            {"id": "risk", "label": "Risico Profiel", "value": risk_level, "icon": "alert", "color": "green" if risk_level == "Laag" else "orange" if risk_level == "Gemiddeld" else "red", "explanation": "Gebaseerd op leeftijd" },
            {"id": "roof", "label": "Dak", "value": "Inspecteren" if age > 20 else "Nieuwstaat", "icon": "home", "trend": "neutral", "color": "orange" if age > 20 else "green", "explanation": "Ouder dan 20 jaar" if age > 20 else "< 20 jaar oud"},
            {"id": "foundation", "label": "Fundering", "value": "Onbekend" if build_year < 1950 else "Beton", "icon": "stats-chart", "color": "orange" if build_year < 1950 else "green"}
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
        if market_avg_m2:
            price_dev_pct = round(((price_m2 - market_avg_m2) / market_avg_m2) * 100)
            metrics.append({"id":"price_deviation","label":"Prijsafwijking","value":f"{price_dev_pct:+,}%" if price_dev_pct != 0 else "0%","icon":"analytics","color":"green" if price_dev_pct < 5 else "orange","explanation": "vs markt"})
        future_score = 80 if label in ["A","A+","A++","B"] else 60 if label in ["C","D"] else 40
        metrics.append({"id":"energy_future","label":"Energie Toekomstscore","value":f"{future_score}","icon":"leaf","color":"green" if future_score>=70 else "orange" if future_score>=50 else "red","trend":"neutral"})
        maintenance = "Hoog" if reno_cost>30000 else "Middelmatig" if reno_cost>0 else "Laag"
        maintenance = "Hoog" if reno_cost>30000 else "Middelmatig" if reno_cost>0 else "Laag"
        metrics.append({"id":"maintenance_intensity","label":"Onderhoud","value":maintenance,"icon":"hammer","trend":"neutral", "color": "red" if reno_cost > 30000 else "green"})
        family = "Geschikt voor gezin" if (IntelligenceEngine._parse_int(ctx.get('oppervlakte','0')) or 0) >= 120 else "Minder geschikt voor groot gezin"
        metrics.append({"id":"family_suitability","label":"Gezinsgeschiktheid","value":family,"icon":"people","trend":"neutral"})
        lt_quality = "Hoog" if "jong" in construction_alert.lower() else "Middelmatig" if "aandacht" in construction_alert.lower() else "Laag"
        metrics.append({"id":"long_term_quality","label":"Lange-termijn kwaliteit","value":lt_quality,"icon":"shield","trend":"neutral"})
        
        risk_html = self._render_rich_narrative(narrative, extra_html=f"""
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="bg-amber-50 border border-amber-200 p-4 rounded-xl">
                <div class="font-bold text-amber-800 flex items-center gap-2 mb-2"><ion-icon name="water"></ion-icon> Fundering/Vocht</div>
                <div class="text-sm text-slate-700">Aandachtspunt bij bouwjaar < 1980. Let op optrekkend vocht.</div>
            </div>
            <div class="bg-blue-50 border border-blue-200 p-4 rounded-xl">
                <div class="font-bold text-blue-800 flex items-center gap-2 mb-2"><ion-icon name="snow"></ion-icon> Isolatie</div>
                <div class="text-sm text-slate-700">Controleer na-isolatie maatregelen (spouw, vloer).</div>
            </div>
            <div class="bg-slate-50 border border-slate-200 p-4 rounded-xl">
                <div class="font-bold text-slate-800 flex items-center gap-2 mb-2"><ion-icon name="flash"></ion-icon> Installaties</div>
                <div class="text-sm text-slate-700">Leeftijd CV-ketel en staat van elektra (groepenkast) controleren.</div>
            </div>
        </div>
        """)
        
        # Left sidebar: Construction timeline
        left_sidebar = [
            {
                "type": "highlight_card",
                "icon": "warning" if risk_level != "Laag" else "shield-checkmark",
                "title": "Inspectie Advies",
                "content": f"{'Bouwkundige keuring sterk aanbevolen' if risk_level == 'Hoog' else 'Standaard inspectie voldoende' if risk_level == 'Laag' else 'Keuring aanbevolen'}"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Bouwkundige Diepte-analyse", "content": risk_html},
            "left_sidebar": left_sidebar,
            "sidebar": [
                {"type": "advisor_card", "title": "Risico Analyse", "content": f"Gezien het bouwjaar {build_year} is het risiconiveau <strong>{risk_level}</strong>. Een bouwkundige keuring wordt { 'sterk ' if risk_level == 'Hoog' else '' }aangeraden."},
                {"type": "action_list", "title": "Onderhoudsplanning", "items": ["Schilderwerk Buitencheck", "CV Ketel Inspectie", "Dakgoot reiniging"]}
            ]
        }

        return ChapterOutput(
            title="3. Bouwkundige Staat",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative
        )
