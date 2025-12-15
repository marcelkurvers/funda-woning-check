
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
        
        main_content = f"""
        <div class="chapter-intro">
            <h3>Buitenleven</h3>
            <p>{narrative['intro']}</p>
        </div>
        <div class="analysis-section">
            {narrative['main_analysis']}
        </div>
        <div class="sun-path-widget">
            <div class="sun-icon">☀️</div>
            <div class="sun-text"><strong>Zoncheck:</strong> Open kompas-app tijdens bezichtiging. Zuid/Zuid-West is ideaal voor middag/avondzon.</div>
        </div>
        <div class="ai-conclusion-box">
            {narrative['conclusion']}
        </div>
        """
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Buitenruimte Analyse", "content": main_content},
            "sidebar": [{"type": "advisor_card", "title": "Tuinpotentie", "content": "Vergunningsvrij uitbouwen vaak mogelijk tot 4 meter."}]
        }

        return ChapterOutput(
            title="7. Tuin & Buitenruimte",
            grid_layout=layout, 
            blocks=[]
        )
