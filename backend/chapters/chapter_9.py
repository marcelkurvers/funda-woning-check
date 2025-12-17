
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class LegalAspects(BaseChapter):
    def get_title(self) -> str:
        return "Juridische Aspecten"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(9, ctx)
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": "Juridisch Kader",
            "status": "Onderzoek Vereist",
            "labels": ["Eigendom", "Bestemming", "Rechten"]
        }
        
        metrics = [
            {"id": "ground", "label": "Grond", "value": "Eigen grond?", "icon": "map", "trend": "neutral", "color": "blue", "explanation": "Check kadaster"},
            {"id": "vve", "label": "VvE", "value": "Check", "icon": "people", "color": "blue", "explanation": "Indien app."}, 
            {"id": "zoning", "label": "Bestemming", "value": "Wonen", "icon": "home", "color": "green", "explanation": "Conform"},
            {"id": "permit", "label": "Vergunningen", "value": "Checken", "icon": "document", "color": "blue", "explanation": "Bij verbouwplannen"}
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
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div class="bg-blue-50 border border-blue-200 p-4 rounded-xl shadow-sm">
                <div class="font-bold text-blue-900 mb-2 flex items-center gap-2"><ion-icon name="home"></ion-icon> Eigendomssituatie</div>
                <div class="text-sm text-blue-800">
                    Volle eigendom of erfpacht? Bij erfpacht: wat is de canon en looptijd?
                </div>
            </div>
            <div class="bg-blue-50 border border-blue-200 p-4 rounded-xl shadow-sm">
                <div class="font-bold text-blue-900 mb-2 flex items-center gap-2"><ion-icon name="git-network"></ion-icon> Erfdienstbaarheden</div>
                <div class="text-sm text-blue-800">
                    Zijn er rechten van overpad of andere verplichtingen richting buren?
                </div>
            </div>
        </div>
        """)
        
        # Left sidebar: Legal checklist
        left_sidebar = [
             {
                "type": "highlight_card",
                "icon": "shield-checkmark",
                "title": "Juridische Status",
                "content": "Controleer kadaster en bestemmingsplan"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Recht & Eigendom", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [{"type": "advisor_card", "title": "Notaris", "content": "Vraag concept koopakte tijdig op voor controle."}]
        }

        return ChapterOutput(
            title="9. Juridische Aspecten",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative
        )
