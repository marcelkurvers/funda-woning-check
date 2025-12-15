
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class AdviceConclusion(BaseChapter):
    def get_title(self) -> str:
        return "Advies & Conclusie"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(12, ctx)
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": "Eindoordeel",
            "status": "Samenvatting",
            "labels": ["Koopadvies", "Strategie"]
        }
        
        # Pros / Cons
        pros = ["Locatie is uitstekend", "Ruim perceel", "Energielabel acceptabel"]
        cons = ["Drukke weg?", "Onderhoud badkamer nodig"]
        
        main_content = f"""
        <div class="chapter-intro"><h3>Samenvattend</h3><p>{narrative['intro']}</p></div>
        
        <div class="conclusion-grid">
            <div class="pros-column">
                <h4><ion-icon name="thumbs-up"></ion-icon> Sterke Punten</h4>
                <ul>{''.join([f'<li>{p}</li>' for p in pros])}</ul>
            </div>
            <div class="cons-column">
                <h4><ion-icon name="thumbs-down"></ion-icon> Aandachtspunten</h4>
                 <ul>{''.join([f'<li>{c}</li>' for c in cons])}</ul>
            </div>
        </div>
        
        <div class="final-verdict">
            <h3>Financieel & Strategisch</h3>
            {narrative['main_analysis']}
        </div>
        
        <div class="ai-conclusion-box">
            {narrative['conclusion']}
        </div>
        """
        
        metrics = [
            {"id": "final", "label": "Totaalscore", "value": "7.5/10", "icon": "trophy", "color": "blue"},
            {"id": "risk", "label": "Risico", "value": "Laag", "icon": "shield-checkmark", "color": "green"},
            {"id": "action", "label": "Actie", "value": "Bezichtig", "icon": "walk"},
            {"id": "bid", "label": "Bieding", "value": "Advies", "icon": "cash"}
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Eindconclusie", "content": main_content},
            "sidebar": [{"type": "advisor_card", "title": "Vervolgstappen", "style": "gradient", "content": "1. Bezichtigen 2. Documenten 3. Bieden"}]
        }

        return ChapterOutput(
            title="12. Advies & Conclusie",
            grid_layout=layout, 
            blocks=[]
        )
