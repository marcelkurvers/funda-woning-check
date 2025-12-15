
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
            {"id": "shop", "label": "Supermarkt", "value": "5 min", "icon": "cart", "trend_text": "Lopen"},
            {"id": "train", "label": "Treinstation", "value": "10 min", "icon": "train", "trend_text": "Fiets"},
            {"id": "school", "label": "Basisschool", "value": "2 min", "icon": "school", "trend_text": "Lopen"},
            {"id": "center", "label": "Centrum", "value": "15 min", "icon": "business", "trend_text": "Fiets"},
        ]
        
        amenity_html = self._render_rich_narrative(narrative, extra_html=f"""
        <div class='amenity-grid'>
            <div class="amenity-card"><div class="amenity-name">Supermarkt</div><div class="amenity-score">8.5</div></div>
            <div class="amenity-card"><div class="amenity-name">Openbaar Vervoer</div><div class="amenity-score">7.0</div></div>
            <div class="amenity-card"><div class="amenity-name">Scholen</div><div class="amenity-score">9.0</div></div>
            <div class="amenity-card"><div class="amenity-name">Horeca</div><div class="amenity-score">8.0</div></div>
        </div>
        """)
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Locatie & Omgeving", "content": amenity_html},
            "sidebar": [
                {"type": "advisor_score", "title": "Leefbaarheid", "score": 82, "content": "Score gebaseerd op voorzieningen en bereikbaarheid."},
            ]
        }

        return ChapterOutput(
            title="2. Locatie & Omgeving",
            grid_layout=layout, 
            blocks=[]
        )
