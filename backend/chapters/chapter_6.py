
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class MaintenanceFinish(BaseChapter):
    def get_title(self) -> str:
        return "Onderhoud & Afwerking"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(6, ctx)
        year = IntelligenceEngine._parse_int(ctx.get('bouwjaar', '2000')) or 2000
        state_score = "Voldoende"
        if year > 2010: state_score = "Uitstekend"
        elif year < 1980: state_score = "Aandacht nodig"
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": "Onderhoudsstaat",
            "status": state_score,
            "labels": ["Materialen", "Afwerking"]
        }
        
        metrics = [
            {"id": "paint", "label": "Schilderwerk", "value": "Check", "icon": "brush"},
            {"id": "floor", "label": "Vloeren", "value": "Staat?", "icon": "albums"},
            {"id": "kitchen", "label": "Keuken", "value": "Functioneel", "icon": "restaurant"},
            {"id": "bath", "label": "Sanitair", "value": "Basis", "icon": "water"}
        ]
        
        main_content = f"""
        <div class="chapter-intro">
            <h3>Kwaliteitsimpressie</h3>
            <p>{narrative['intro']}</p>
        </div>
        <div class="analysis-section">
            {narrative['main_analysis']}
        </div>
        <table class="simple-table">
            <thead><tr><th>Onderdeel</th><th>Verwachte Staat</th><th>Actie</th></tr></thead>
            <tbody>
                <tr><td>Kozijnen</td><td>{"Kunststof/Alu (goed)" if year > 1990 else "Hout (check houtrot)"}</td><td>Inspectie</td></tr>
                <tr><td>Keukenapparatuur</td><td>Afschrijving 10-15 jr</td><td>Testen</td></tr>
                <tr><td>Wandafwerking</td><td>Esthetisch</td><td>Schilderen</td></tr>
            </tbody>
        </table>
        <div class="ai-conclusion-box">
            {narrative['conclusion']}
        </div>
        """
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Afwerkingsniveau", "content": main_content},
            "sidebar": [{"type": "advisor", "title": "Checklist", "content": "Kijk naar vochtplekken en scheurvorming bij bezichtiging."}]
        }

        return ChapterOutput(
            title="6. Onderhoud & Afwerking",
            grid_layout=layout, 
            blocks=[]
        )
