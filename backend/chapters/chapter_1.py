
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
