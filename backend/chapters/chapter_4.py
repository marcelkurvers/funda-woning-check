
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class EnergySustainability(BaseChapter):
    def get_title(self) -> str:
        return "Energie & Duurzaamheid"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(4, ctx)
        
        label = ctx.get('label', 'G').upper() or 'G'
        if len(label) > 1 and not label.startswith('A'): label = label[0]
        
        
        colors = {"A": "green", "B": "green", "C": "orange", "D": "orange", "E": "red", "F": "red", "G": "red"}
        my_color = colors.get(label[0], "grey")
        
        # Energy label explanation
        label_explanation = None
        if label[0] in ["A", "B"]:
            label_explanation = "Uitstekende energie-efficiëntie"
        elif label[0] in ["C", "D"]:
            label_explanation = "Gemiddeld, verbetering aanbevolen"
        elif label[0] in ["E", "F", "G"]:
            label_explanation = "Slecht, renovatie dringend nodig"

        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": f"Energielabel {label}",
            "status": "Duurzaamheid",
            "labels": ["Bespaarpotentieel", "Vergroening"]
        }
        
        metrics = [
            {"id": "label", "label": "Energielabel", "value": label, "icon": "leaf", "color": my_color, "explanation": label_explanation},
            {"id": "solar", "label": "Zonnepanelen", "value": "Geschikt", "icon": "sunny"},
            {"id": "iso", "label": "Isolatie", "value": "Check", "icon": "thermometer"},
            {"id": "heat", "label": "Verwarming", "value": "CV-Ketel", "icon": "flame"}
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
            price_dev_color = "green" if price_dev_pct < -5 else "orange" if price_dev_pct <= 5 else "red"
            price_dev_explanation = "Onder marktprijs" if price_dev_pct < -5 else "Rond marktprijs" if price_dev_pct <= 5 else "Boven marktprijs"
            metrics.append({"id":"price_deviation","label":"Prijsafwijking %","value":f"{price_dev_pct:+,}%" if price_dev_pct != 0 else "0%","icon":"trending-down" if price_dev_pct < 0 else "trending-up","color":price_dev_color,"explanation":price_dev_explanation,"trend":"up" if price_dev_pct>0 else "down" if price_dev_pct<0 else "neutral","trend_text":f"{price_dev_pct:+}% vs markt"})
        future_score = 80 if label in ["A","A+","A++","B"] else 60 if label in ["C","D"] else 40
        future_score_color = "green" if future_score>=70 else "orange" if future_score>=50 else "red"
        future_score_explanation = "Uitstekende toekomstbestendigheid" if future_score>=70 else "Gemiddelde toekomstbestendigheid" if future_score>=50 else "Lage toekomstbestendigheid"
        metrics.append({"id":"energy_future","label":"Energie Toekomstscore","value":f"{future_score}","icon":"leaf","color":future_score_color,"explanation":future_score_explanation,"trend":"neutral"})
        maintenance = "Hoog" if reno_cost>30000 else "Middelmatig" if reno_cost>0 else "Laag"
        maintenance_color = "red" if reno_cost>30000 else "orange" if reno_cost>0 else "green"
        maintenance_explanation = f"Hoge renovatiekosten (€{reno_cost:,})" if reno_cost>30000 else f"Gemiddelde renovatiekosten (€{reno_cost:,})" if reno_cost>0 else "Lage renovatiekosten"
        metrics.append({"id":"maintenance_intensity","label":"Onderhoudsintensiteit","value":maintenance,"icon":"hammer","color":maintenance_color,"explanation":maintenance_explanation,"trend":"neutral"})
        family = "Geschikt voor gezin" if (IntelligenceEngine._parse_int(ctx.get('oppervlakte','0')) or 0) >= 120 else "Minder geschikt voor groot gezin"
        metrics.append({"id":"family_suitability","label":"Gezinsgeschiktheid","value":family,"icon":"people","trend":"neutral"})
        lt_quality = "Hoog" if "jong" in construction_alert.lower() else "Middelmatig" if "aandacht" in construction_alert.lower() else "Laag"
        lt_quality_color = "green" if "jong" in construction_alert.lower() else "orange" if "aandacht" in construction_alert.lower() else "red"
        lt_quality_explanation = "Moderne bouw" if "jong" in construction_alert.lower() else "Oudere bouw, aandacht nodig" if "aandacht" in construction_alert.lower() else "Oude bouw, renovatie nodig"
        metrics.append({"id":"long_term_quality","label":"Lange-termijn kwaliteit","value":lt_quality,"icon":"shield","color":lt_quality_color,"explanation":lt_quality_explanation,"trend":"neutral"})
        
        imp_html = self._render_rich_narrative(narrative, extra_html=f"""
        <h4 class="font-bold text-slate-700 mb-4 flex items-center gap-2"><ion-icon name="leaf"></ion-icon> Verduurzamingskansen</h4>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="bg-green-50 border border-green-200 p-4 rounded-xl flex flex-col justify-between">
                <div>
                   <div class="font-bold text-green-800 mb-1">Zonnepanelen</div>
                   <div class="text-sm text-slate-600">Geschikt dakvlak aanwezig.</div>
                </div>
                <div class="mt-3 text-green-700 font-bold text-sm">~€850 besparing/jr</div>
            </div>
            <div class="bg-green-50 border border-green-200 p-4 rounded-xl flex flex-col justify-between">
                <div>
                   <div class="font-bold text-green-800 mb-1">Hybride Warmtepomp</div>
                   <div class="text-sm text-slate-600">Combineer met HR-ketel.</div>
                </div>
                <div class="mt-3 text-green-700 font-bold text-sm">Tot 70% minder gas</div>
            </div>
            <div class="bg-green-50 border border-green-200 p-4 rounded-xl flex flex-col justify-between">
                <div>
                   <div class="font-bold text-green-800 mb-1">Vloerisolatie</div>
                   <div class="text-sm text-slate-600">Verhoogt comfort direct.</div>
                </div>
                <div class="mt-3 text-green-700 font-bold text-sm">~15% besparing</div>
            </div>
        </div>
        """)
        
        # Assuming 'consumption' is defined elsewhere or needs to be derived from ctx
        # For the purpose of this edit, let's mock it or derive it simply if possible
        # In a real scenario, this would come from the IntelligenceEngine or ctx
        consumption = IntelligenceEngine._parse_int(ctx.get('energy_consumption_kwh', '5000')) # Example default

        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Energieprestatie", "content": imp_html},
            "left_sidebar": [
                {
                    "type": "key_facts",
                    "title": "Energielabel",
                    "facts": [
                        {"label": "Huidig Label", "value": label},
                        {"label": "Verbruik", "value": f"{consumption} kWh/jaar"},
                        {"label": "Kosten (est.)", "value": f"€ {int(consumption * 0.25):,}/jaar"}
                    ]
                },
                {
                    "type": "highlight_card",
                    "icon": "leaf",
                    "title": "Verduurzaming",
                    "content": f"Potentiële besparing: € {int(consumption * 0.15):,}/jaar"
                }
            ],
            "sidebar": [
                {"type": "advisor_card", "title": "Subsidies", "content": "Voor isolatie en warmtepompen is ISDE subsidie beschikbaar (tot 30%)."},
                {"type": "advisor", "title": "Financiering", "content": "Gebruik het Warmtefonds of extra hypotheekruimte voor verduurzaming."}
            ]
        }

        return ChapterOutput(
            title="4. Energie & Duurzaamheid",
            grid_layout=layout, 
            blocks=[]
        )
