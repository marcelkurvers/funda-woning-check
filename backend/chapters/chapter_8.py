
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class ParkingAccessibility(BaseChapter):
    def get_title(self) -> str:
        return "Parkeren & Bereikbaarheid"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(8, ctx)
        address = ctx.get('adres', '')
        parking_status = "Openbaar"
        if "laan" in address or "weg" in address: parking_status = "Oprit?"
        
        hero = {
            "address": address,
            "price": "Mobiliteit",
            "status": "Goed Bereikbaar",
            "labels": ["Auto", "OV", "Fiets"]
        }
        
        metrics = [
            {"id": "parking", "label": "Parkeren", "value": parking_status, "icon": "car"},
            {"id": "ev", "label": "Laadpaal", "value": "Mogelijk", "icon": "flash"},
            {"id": "highway", "label": "Snelweg", "value": "< 10 min", "icon": "speedometer"},
            {"id": "public", "label": "OV Halte", "value": "Nabij", "icon": "bus"}
        ]
        
        main_content = f"""
        <div class="chapter-intro">
            <h3>Mobiliteitsscan</h3>
            <p>{narrative['intro']}</p>
        </div>
        <div class="analysis-section">
            {narrative['main_analysis']}
        </div>
        <ul class="check-list">
            <li>Check parkeervergunning wachttijden bij gemeente.</li>
            <li>Is er ruimte voor een laadpaal op eigen terrein?</li>
            <li>Hoe druk is de straat tijdens spitsuur?</li>
        </ul>
        <div class="ai-conclusion-box">
            {narrative['conclusion']}
        </div>
        """
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Parkeren & Mobiliteit", "content": main_content},
            "sidebar": [{"type": "advisor", "title": "Toekomst", "content": "Elektrisch rijden neemt toe. Een eigen oprit is goud waard."}]
        }

        return ChapterOutput(
            title="8. Parkeren & Bereikbaarheid",
            grid_layout=layout, 
            blocks=[]
        )
