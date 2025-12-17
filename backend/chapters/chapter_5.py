
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class LayoutAnalysis(BaseChapter):
    def get_title(self) -> str:
        return "Indeling & Ruimtegebruik"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(5, ctx)
        
        living_area = IntelligenceEngine._parse_int(ctx.get('oppervlakte', '0'))
        
        # Use explicit rooms from context if available, otherwise estimate from living area
        rooms_from_context = IntelligenceEngine._parse_int(ctx.get('rooms', '0'))
        if rooms_from_context > 0:
            rooms = rooms_from_context
        else:
            rooms = max(2, int(living_area / 25))
        
        # Calculate bedrooms with validation (max 10)
        bedrooms = min(max(1, rooms - 1), 10)
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": f"{living_area} m² Woonoppervlak",
            "status": "Indeling",
            "labels": ["Functionaliteit", "Potentie"]
        }
        
        metrics = [
            {"id": "rooms", "label": "Totaal Kamers", "value": str(rooms), "icon": "grid"},
            {"id": "bed", "label": "Slaapkamers (est)", "value": str(bedrooms), "icon": "bed"},
            {"id": "living", "label": "Leefruimte", "value": "Ruim", "icon": "resize", "color": "blue"},
            {"id": "bath", "label": "Sanitair", "value": "1+", "icon": "water"}
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
        <div class="feature-list">
            <div class="feature-item">
                <span class="icon">📐</span>
                <span class="text"><strong>Woonkamer:</strong> Centraal element, check lichtinval en zichtlijnen.</span>
            </div>
            <div class="feature-item">
                <span class="icon">🍳</span>
                <span class="text"><strong>Keuken:</strong> Mogelijkheden voor open keuken of kookeiland? Bekijk de plattegrond.</span>
            </div>
        </div>
        """)
        
        # Left sidebar: Room breakdown
        left_sidebar = [
             {
                "type": "highlight_card",
                "icon": "resize",
                "title": "Ruimte Beoordeling",
                "content": f"{'Ruim bemeten' if living_area > 120 else 'Gemiddeld' if living_area > 80 else 'Compact'} voor {rooms} kamers"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Indeling & Flow", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [{"type": "advisor_card", "title": "Flexibiliteit", "content": "Is de indeling aanpasbaar? Niet-dragende muren bieden opties."}]
        }

        return ChapterOutput(
            title="5. Indeling & Ruimtegebruik",
            grid_layout=layout, 
            blocks=[]
        )
