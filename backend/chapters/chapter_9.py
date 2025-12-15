
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class LegalAspects(BaseChapter):
    def get_title(self) -> str:
        return "Juridische Aspecten"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(9, ctx)
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": "Juridisch Kader",
            "status": "Onderzoek Vereist",
            "labels": ["Eigendom", "Bestemming", "Rechten"]
        }
        
        metrics = [
            {"id": "ground", "label": "Grond", "value": "Eigen grond?", "icon": "map", "trend": "neutral"},
            {"id": "vve", "label": "VvE", "value": "N.v.t.", "icon": "people"}, 
            {"id": "zoning", "label": "Bestemming", "value": "Wonen", "icon": "home"},
            {"id": "permit", "label": "Vergunningen", "value": "Checken", "icon": "document"}
        ]
        
        main_content = self._render_rich_narrative(narrative, extra_html=f"""
        <div class="legal-grid">
            <div class="legal-item important">
                <strong>Eigendomssituatie:</strong> Volle eigendom of erfpacht? Bij erfpacht: wat is de canon en looptijd?
            </div>
            <div class="legal-item">
                <strong>Erfdienstbaarheden:</strong> Zijn er rechten van overpad of andere verplichtingen richting buren?
            </div>
        </div>
        """)
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Recht & Eigendom", "content": main_content},
            "sidebar": [{"type": "advisor_card", "title": "Notaris", "content": "Vraag concept koopakte tijdig op voor controle."}]
        }

        return ChapterOutput(
            title="9. Juridische Aspecten",
            grid_layout=layout, 
            blocks=[]
        )
