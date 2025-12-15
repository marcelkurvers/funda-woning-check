
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class EnergySustainability(BaseChapter):
    def get_title(self) -> str:
        return "Energie & Duurzaamheid"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(4, ctx)
        
        label = ctx.get('label', 'G').upper() or 'G'
        if len(label) > 1 and not label.startswith('A'): label = label[0]
        
        colors = {"A": "green", "B": "green", "C": "orange", "D": "orange", "E": "red", "F": "red", "G": "red"}
        my_color = colors.get(label[0], "grey")

        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": f"Energielabel {label}",
            "status": "Duurzaamheid",
            "labels": ["Bespaarpotentieel", "Vergroening"]
        }
        
        metrics = [
            {"id": "label", "label": "Energielabel", "value": label, "icon": "leaf", "color": my_color},
            {"id": "solar", "label": "Zonnepanelen", "value": "Geschikt", "icon": "sunny"},
            {"id": "iso", "label": "Isolatie", "value": "Check", "icon": "thermometer"},
            {"id": "heat", "label": "Verwarming", "value": "CV-Ketel", "icon": "flame"}
        ]
        
        imp_html = self._render_rich_narrative(narrative, extra_html=f"""
        <div class='eco-grid'>
            <div class="eco-card"><strong>Zonnepanelen:</strong> Tot €850 besparing/jaar.</div>
            <div class="eco-card"><strong>Hybride Warmtepomp:</strong> Tot 70% minder gasverbruik.</div>
            <div class="eco-card"><strong>Vloerisolatie:</strong> Comfortverhogend en energiebesparend.</div>
        </div>
        """)
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Verduurzamingsopties", "content": imp_html},
            "sidebar": [
                {"type": "advisor", "title": "Financiering", "content": "Gebruik het Warmtefonds of extra hypotheekruimte voor verduurzaming."}
            ]
        }

        return ChapterOutput(
            title="4. Energie & Duurzaamheid",
            grid_layout=layout, 
            blocks=[]
        )
