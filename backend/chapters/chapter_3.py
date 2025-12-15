
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class TechnicalState(BaseChapter):
    def get_title(self) -> str:
        return "Bouwkundige Staat"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(3, ctx)
        
        build_year_str = str(ctx.get('bouwjaar', '2000'))
        build_year = IntelligenceEngine._parse_int(build_year_str) or 2000
        age = 2025 - build_year
            
        risk_level = "Laag"
        if build_year < 1920: risk_level = "Hoog"
        elif build_year < 1980: risk_level = "Gemiddeld"
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": f"Bouwjaar {build_year}",
            "status": f"Ouderdom: {age} jaar",
            "labels": [f"Risico: {risk_level}"]
        }
        
        metrics = [
            {"id": "year", "label": "Bouwjaar", "value": f"{build_year}", "icon": "calendar"},
            {"id": "risk", "label": "Risico Profiel", "value": risk_level, "icon": "alert", "color": "orange" if risk_level != "Laag" else "green"},
            {"id": "roof", "label": "Dak", "value": "Inspecteren", "icon": "home", "trend": "neutral"},
            {"id": "foundation", "label": "Fundering", "value": "Onbekend", "icon": "stats-chart"}
        ]
        
        risk_html = f"""
        <div class="chapter-intro">
            <h3>Bouwkundige Analyse</h3>
            <p>{narrative['intro']}</p>
        </div>
        
        <div class="analysis-section">
            {narrative['main_analysis']}
        </div>
        
        <div class='risk-grid'>
            <div class="risk-item"><strong>Fundering/Vocht:</strong> Aandachtspunt bij bouwjaar < 1980.</div>
            <div class="risk-item"><strong>Isolatie:</strong> Controleer na-isolatie maatregelen.</div>
            <div class="risk-item"><strong>Installaties:</strong> Leeftijd CV-ketel en elektra controleren.</div>
        </div>
        
        <div class="ai-conclusion-box">
            {narrative['conclusion']}
        </div>
        """
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Bouwtechnische Staat", "content": risk_html},
            "sidebar": [
                {"type": "action_list", "title": "Onderhoudsplanning", "items": ["Schilderwerk Buitencheck", "CV Ketel Inspectie", "Dakgoot reiniging"]}
            ]
        }

        return ChapterOutput(
            title="3. Bouwkundige Staat",
            grid_layout=layout, 
            blocks=[]
        )
