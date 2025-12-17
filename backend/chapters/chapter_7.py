
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class GardenOutdoor(BaseChapter):
    def get_title(self) -> str:
        return "Tuin & Buitenruimte"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(7, ctx)
        
        living_area = IntelligenceEngine._parse_int(ctx.get('oppervlakte', '0'))
        plot_area = IntelligenceEngine._parse_int(ctx.get('perceel', '0'))
        garden_size = max(0, plot_area - (living_area / 2))
        garden_size = int(garden_size)
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": f"~{garden_size} m² Buiten",
            "status": "Tuin & Balcon",
            "labels": ["Oriëntatie", "Privacy"]
        }
        
        metrics = [
            {"id": "size", "label": "Tuinoppervlak", "value": f"~{garden_size} m²", "icon": "leaf", "color": "green"},
            {"id": "sun", "label": "Zonligging", "value": "Checken", "icon": "sunny"},
            {"id": "privacy", "label": "Privacy", "value": "Gemiddeld", "icon": "eye-off"},
            {"id": "shed", "label": "Berging", "value": "Aanwezig?", "icon": "key"}
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
        <div class="sun-path-widget">
            <div class="sun-icon">☀️</div>
            <div class="sun-text"><strong>Zoncheck:</strong> Open kompas-app tijdens bezichtiging. Zuid/Zuid-West is ideaal voor middag/avondzon.</div>
        </div>
        """)
        
        # Left sidebar: Garden details
        left_sidebar = [
            {
                "type": "key_facts",
                "title": "Buitenruimte",
                "facts": [
                    {"label": "Tuinoppervlak", "value": f"~{garden_size} m²"},
                    {"label": "Perceel totaal", "value": f"{plot_area} m²"},
                    {"label": "Oriëntatie", "value": "Te checken"}
                ]
            },
            {
                "type": "highlight_card",
                "icon": "sunny",
                "title": "Zonligging",
                "content": "Check tijdens bezichtiging met kompas-app"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Buitenruimte Analyse", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [{"type": "advisor_card", "title": "Tuinpotentie", "content": "Vergunningsvrij uitbouwen vaak mogelijk tot 4 meter."}]
        }

        return ChapterOutput(
            title="7. Tuin & Buitenruimte",
            grid_layout=layout, 
            blocks=[]
        )
