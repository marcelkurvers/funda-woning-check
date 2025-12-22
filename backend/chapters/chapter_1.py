
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class GeneralFeatures(BaseChapter):
    def get_title(self) -> str:
        ctx = self.context
        p_type = ctx.get('property_type', '').lower()
        if 'appartement' in p_type:
            return "Kenmerken Appartement"
        elif 'vrijstaand' in p_type or 'villa' in p_type:
            return "Kenmerken Vrijstaande Woning"
        return "Algemene Woningkenmerken"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        
        # 1. Ask Intelligence Engine for Dynamic Narrative
        narrative = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # 2. Key Metrics - Use new fields with fallback to old names
        living_area = IntelligenceEngine._parse_int(
            ctx.get('living_area_m2') or ctx.get('oppervlakte', '0')
        )
        plot_area = IntelligenceEngine._parse_int(
            ctx.get('plot_area_m2') or ctx.get('perceel', '0')
        )
        # Volume Calculation (Use actual value or estimate carefully)
        # Use abs() to ensure positive volume if bad math occurs
        volume = abs(living_area * 3)
        
        # Use actual parsed bedrooms if available, otherwise estimate
        bedrooms = ctx.get('bedrooms')
        rooms_count = IntelligenceEngine._parse_int(bedrooms) if bedrooms else max(3, int(living_area / 25))
        
        bathrooms = ctx.get('bathrooms', '?')
        property_type = ctx.get('property_type', 'Woonhuis')
        
        # Additional calculations for new metrics
        price_val = IntelligenceEngine._parse_int(
            ctx.get('asking_price_eur') or ctx.get('prijs') or '0'
        )
        price_m2 = round(price_val / living_area) if living_area else 0
        market_avg_m2 = int(ctx.get('avg_m2_price', 4800) or 4800)
        label = ctx.get('energy_label') or ctx.get('label') or '?'
        reno_cost = 45000 if "F" in label or "G" in label else 25000 if "D" in label or "E" in label else 0
        construction_year = IntelligenceEngine._parse_int(
            ctx.get('build_year') or ctx.get('bouwjaar') or '0'
        )
        
        # 3. Layout Construction (Modern Dashboard)
        hero = {
            "address": ctx.get('address') or ctx.get('adres', 'Adres Onbekend'),
            "price": ctx.get('asking_price_eur') or ctx.get('prijs', 'Prijs op aanvraag'),
            "status": "Woninginformatie",
            "labels": [property_type, f"{construction_year} Bouwjaar"]
        }

        metrics = [
            {"id": "living", "label": "Woonoppervlakte", "value": f"{living_area} m²", "icon": "expand", "color": "blue"},
            {"id": "bedrooms", "label": "Slaapkamers", "value": f"{rooms_count}", "icon": "bed", "color": "blue"},
            {"id": "energy", "label": "Label", "value": ctx.get('energy_label', '?'), "icon": "leaf", "color": "green"}
        ]
        
        
        main_content = self._render_rich_narrative(narrative)
        
        specs_card = {
            "type": "advisor_card", 
            "title": "Object Paspoort",
            "content": f"""
            <ul class="specs-list">
            <li><strong>Soort:</strong> {property_type}</li>
            <li><strong>Bouwtype:</strong> {ctx.get('construction_type', 'Onbekend')}</li>
            <li><strong>Bouwjaar:</strong> {construction_year}</li>
            <li><strong>Energielabel:</strong> {label}</li>
            <li><strong>Verwarming:</strong> {(ctx.get('heating') or 'Onbekend')[:50]}...</li>
            <li><strong>Isolatie:</strong> {ctx.get('insulation') or 'Onbekend'}</li>
            <li><strong>Garage:</strong> {ctx.get('garage') or 'Onbekend'}</li>
            </ul>
            """
        }
        
        # CONTEXTUAL WIDGETS
        advisor_title = "Makelaars Blik"
        advisor_content = "Een ruime woning met veel mogelijkheden. Controleer altijd de NEN2580 meetrapporten."
        
        if construction_year < 1980:
            advisor_title = "Renovatie Advies"
            advisor_content = "Gezien de leeftijd is een bouwkundige keuring sterk aanbevolen. Let op isolatie en leidingwerk."
        elif property_type.lower() == "appartement":
            advisor_title = "VvE Check"
            advisor_content = "Controleer de VvE-stukken: notulen, meerjarenonderhoudsplan (MJOP) en reservefonds."

        sidebar_advisor = {
            "type": "advisor",
            "title": advisor_title,
            "content": advisor_content,
        }

        # Left sidebar: Space-focused metrics
        left_sidebar = [
            {
                "type": "highlight_card",
                "icon": "home",
                "title": "Woningtype",
                "content": f"{property_type} uit {construction_year}"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Algemene Kenmerken", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [specs_card, sidebar_advisor]
        }

        return ChapterOutput(
            title="1. Algemene Woningkenmerken",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative # Populate chapter data for tests and reuse
        )
