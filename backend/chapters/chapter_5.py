
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
        rooms = max(2, int(living_area / 25))
        bedrooms = max(1, rooms - 1)
        
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
        
        main_content = f"""
        <div class="chapter-intro">
            <h3>Functionele Analyse</h3>
            <p>{narrative['intro']}</p>
        </div>
        <div class="analysis-section">
            {narrative['main_analysis']}
        </div>
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
        <div class="ai-conclusion-box">
            {narrative['conclusion']}
        </div>
        """
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Indeling & Flow", "content": main_content},
            "sidebar": [{"type": "advisor_card", "title": "Flexibiliteit", "content": "Is de indeling aanpasbaar? Niet-dragende muren bieden opties."}]
        }

        return ChapterOutput(
            title="5. Indeling & Ruimtegebruik",
            grid_layout=layout, 
            blocks=[]
        )
