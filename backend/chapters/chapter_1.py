
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class GeneralFeatures(BaseChapter):
    def get_title(self) -> str:
        return "Algemene Woningkenmerken"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        
        # 1. Ask Intelligence Engine for Dynamic Narrative
        narrative = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # 2. Key Metrics
        living_area = IntelligenceEngine._parse_int(ctx.get('oppervlakte', '0'))
        plot_area = IntelligenceEngine._parse_int(ctx.get('perceel', '0'))
        volume = living_area * 3
        rooms_estimated = max(3, int(living_area / 25))
        # Additional calculations for new metrics
        price_val = IntelligenceEngine._parse_int(ctx.get('prijs') or ctx.get('asking_price_eur'))
        price_m2 = round(price_val / living_area) if living_area else 0
        market_avg_m2 = ctx.get('avg_m2_price', 4800)
        label = ctx.get('label', '?')
        reno_cost = 45000 if "F" in label or "G" in label else 25000 if "D" in label or "E" in label else 0
        construction_year = IntelligenceEngine._parse_int(ctx.get('bouwjaar') or ctx.get('build_year'))
        construction_alert = "Aandacht nodig" if construction_year < 1990 else "Relatief jong"
        
        # 3. Layout Construction (Modern Dashboard)
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": ctx.get('prijs', 'Prijs op aanvraag'),
            "status": "Woninginformatie",
            "labels": ["Woonhuis", f"{ctx.get('bouwjaar','?')} Bouwjaar"]
        }

        metrics = [
            {"id": "living", "label": "Woonoppervlakte", "value": f"{living_area} m²", "icon": "expand", "color": "blue"},
            {"id": "plot", "label": "Perceeloppervlakte", "value": f"{plot_area} m²", "icon": "image", "color": "green"},
            {"id": "volume", "label": "Inhoud (est.)", "value": f"~{volume} m³", "icon": "cube", "trend": "neutral"},
            {"id": "rooms", "label": "Kamers (est.)", "value": f"{rooms_estimated}", "icon": "bed"}
        ]
        # New metrics (additive)
        if market_avg_m2:
            price_dev_pct = round(((price_m2 - market_avg_m2) / market_avg_m2) * 100)
            metrics.append({"id": "price_deviation", "label": "Prijsafwijking %", "value": f"{price_dev_pct:+,}%" if price_dev_pct != 0 else "0%", "icon": "trend-up" if price_dev_pct > 0 else "trend-down" if price_dev_pct < 0 else "neutral", "trend": "up" if price_dev_pct > 0 else "down" if price_dev_pct < 0 else "neutral", "trend_text": f"{price_dev_pct:+}% vs markt"})
        future_score = 80 if label in ["A","A+","A++","B"] else 60 if label in ["C","D"] else 40
        metrics.append({"id": "energy_future", "label": "Energie Toekomstscore", "value": f"{future_score}", "icon": "leaf", "color": "green" if future_score >= 70 else "orange" if future_score >= 50 else "red", "trend": "neutral"})
        maintenance = "Hoog" if reno_cost > 30000 else "Middelmatig" if reno_cost > 0 else "Laag"
        metrics.append({"id": "maintenance_intensity", "label": "Onderhoudsintensiteit", "value": maintenance, "icon": "hammer", "trend": "neutral"})
        family = "Geschikt voor gezin" if living_area >= 120 and rooms_estimated > 0 else "Minder geschikt voor groot gezin"
        metrics.append({"id": "family_suitability", "label": "Gezinsgeschiktheid", "value": family, "icon": "people", "trend": "neutral"})
        lt_quality = "Hoog" if "jong" in construction_alert.lower() else "Middelmatig" if "aandacht" in construction_alert.lower() else "Laag"
        metrics.append({"id": "long_term_quality", "label": "Lange-termijn kwaliteit", "value": lt_quality, "icon": "shield", "trend": "neutral"})
        
        main_content = self._render_rich_narrative(narrative)
        
        specs_card = {
            "type": "advisor_card", 
            "title": "Object Paspoort",
            "content": f"""
            <ul class="specs-list">
            <li><strong>Soort:</strong> Woonhuis</li>
            <li><strong>Bouwjaar:</strong> {ctx.get('bouwjaar', 'Onbekend')}</li>
            <li><strong>Isolatie:</strong> {"Dubbel glas (aanname)" if 'A' in ctx.get('label','') else "Standaard"}</li>
            </ul>
            """
        }
        
        sidebar_advisor = {
            "type": "advisor",
            "title": "Makelaars Blik",
            "content": "Een ruime woning met veel mogelijkheden. Controleer altijd de NEN2580 meetrapporten.",
        }

        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Algemene Kenmerken", "content": main_content},
            "sidebar": [specs_card, sidebar_advisor]
        }

        return ChapterOutput(
            title="1. Algemene Woningkenmerken",
            grid_layout=layout, 
            blocks=[]
        )
