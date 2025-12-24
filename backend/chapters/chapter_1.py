"""
Chapter 1: General Property Features

ARCHITECTURAL INVARIANTS (NON-NEGOTIABLE):
1. NO arithmetic operations
2. NO value derivation (e.g., rooms_count = max(3, int(living_area / 25)))
3. All values MUST come from registry (via ctx)
4. This class is PRESENTATION ONLY
"""

from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine
import logging

logger = logging.getLogger(__name__)


class GeneralFeatures(BaseChapter):
    def get_title(self) -> str:
        ctx = self.context
        p_type = str(ctx.get('property_type', '')).lower()
        if 'appartement' in p_type:
            return "Kenmerken Appartement"
        elif 'vrijstaand' in p_type or 'villa' in p_type:
            return "Kenmerken Vrijstaande Woning"
        return "Algemene Woningkenmerken"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        
        # Generate narrative (AI or registry-only fallback)
        narrative = IntelligenceEngine.generate_chapter_narrative(1, ctx)

        # === ALL VALUES FROM REGISTRY (NO COMPUTATION) ===
        living_area = ctx.get('living_area_m2', 0)
        plot_area = ctx.get('plot_area_m2', 0)
        volume = ctx.get('volume_m3', 0)
        rooms = ctx.get('rooms', 0)  # Pre-computed in enrichment
        bedrooms = ctx.get('bedrooms', 0)
        bathrooms = ctx.get('bathrooms', '?')
        property_type = ctx.get('property_type', 'Woonhuis')
        construction_year = ctx.get('build_year', 0)
        label = ctx.get('energy_label', '?')
        
        # Hero (display only)
        hero = {
            "address": ctx.get('address', ctx.get('adres', 'Adres Onbekend')),
            "price": ctx.get('asking_price_eur', 'Prijs op aanvraag'),
            "status": "Woninginformatie",
            "labels": [property_type, f"{construction_year} Bouwjaar"] if construction_year else [property_type]
        }

        # Metrics - using pre-computed values only
        metrics = [
            {
                "id": "living", 
                "label": "Woonoppervlakte", 
                "value": f"{living_area} m²" if living_area else "Onbekend",
                "icon": "expand", 
                "color": "blue"
            },
            {
                "id": "rooms", 
                "label": "Kamers", 
                "value": str(rooms) if rooms else "Onbekend",
                "icon": "bed", 
                "color": "blue"
            },
            {
                "id": "energy", 
                "label": "Label", 
                "value": label or "?",
                "icon": "leaf", 
                "color": "green"
            }
        ]
        
        main_content = self._render_rich_narrative(narrative)
        
        specs_card = {
            "type": "advisor_card", 
            "title": "Object Paspoort",
            "content": f"""
            <ul class="specs-list">
            <li><strong>Soort:</strong> {property_type}</li>
            <li><strong>Bouwtype:</strong> {ctx.get('construction_type', 'Onbekend')}</li>
            <li><strong>Bouwjaar:</strong> {construction_year or 'Onbekend'}</li>
            <li><strong>Energielabel:</strong> {label}</li>
            <li><strong>Verwarming:</strong> {str(ctx.get('heating', 'Onbekend'))[:50]}</li>
            <li><strong>Isolatie:</strong> {ctx.get('insulation', 'Onbekend')}</li>
            <li><strong>Garage:</strong> {ctx.get('garage', 'Onbekend')}</li>
            </ul>
            """
        }
        
        # Sidebar advice - using registry values for conditional, no computation
        sidebar_advisor = {
            "type": "advisor",
            "title": "Advies",
            "content": narrative.get('conclusion', 'Analyse vereist meer data.')
        }

        left_sidebar = [
            {
                "type": "highlight_card",
                "icon": "home",
                "title": "Woningtype",
                "content": f"{property_type}" + (f" uit {construction_year}" if construction_year else "")
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
            chapter_data=narrative
        )
