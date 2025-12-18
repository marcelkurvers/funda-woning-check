from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class PreferenceMatch(BaseChapter):
    def get_title(self) -> str:
        return "Persoonlijke Eisen & Match"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        
        # 1. Ask Intelligence Engine for Dynamic Narrative
        # Chapter 2 in IntelligenceEngine is the Match Analyse
        narrative = IntelligenceEngine.generate_chapter_narrative(2, ctx)
        
        # 2. Extract keywords for metrics
        prefs = ctx.get('_preferences', {})
        marcel = prefs.get('marcel', {})
        petra = prefs.get('petra', {})
        
        # Calculate a match score (could be improved)
        match_score = 80 # default
        if "score" in narrative.get('intro', ''):
             try:
                 # Extract percentage from intro "match van 85%"
                 match_score = int(narrative['intro'].split('match van ')[1].split('%')[0])
             except: pass

        # 3. Metrics for the Match Analyse
        metrics = [
            {"id": "match_total", "label": "Totale Match", "value": f"{match_score}%", "icon": "heart", "color": "green" if match_score > 70 else "orange", "explanation": "Overeenkomst met profiel"},
            {"id": "marcel_hits", "label": "Marcel Tech", "value": "Check", "icon": "hardware-chip", "color": "blue", "explanation": "Infrastructuur & Infra"},
            {"id": "petra_hits", "label": "Petra Sfeer", "value": "Check", "icon": "color-palette", "color": "pink", "explanation": "Esthetiek & Comfort"},
            {"id": "priorities", "label": "Prioriteiten", "value": f"{len(marcel.get('priorities', [])) + len(petra.get('priorities', []))}", "icon": "list", "explanation": "Totaal aantal wensen"}
        ]
        
        # 4. Hero
        hero = {
            "address": ctx.get('adres', 'Object Analyse'),
            "price": f"Match Score: {match_score}%",
            "status": "Persoonlijk Profiel",
            "labels": ["Marcel & Petra", "Maatwerk Analyse"]
        }

        # 5. Sidebar Advisor
        sidebar = [
             {
                "type": "advisor_score", 
                "title": "Woning Match", 
                "score": match_score, 
                "content": f"Deze woning voldoet voor {match_score}% aan de gecombineerde eisen van Marcel en Petra."
            },
            {
                "type": "advisor_card", 
                "title": "Prioriteit Focus", 
                "content": "Focus bij de bezichtiging op de 'niet-direct zichtbare' techniek voor Marcel en de 'lichtinval' voor Petra."
            }
        ]
        
        # Left sidebar icon
        left_sidebar = [
            {
                "type": "highlight_card",
                "icon": "people",
                "title": "Profiel Match",
                "content": f"Score: {match_score}%"
            }
        ]

        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Marcel & Petra Matchoverzicht", "content": self._render_rich_narrative(narrative)},
            "left_sidebar": left_sidebar,
            "sidebar": sidebar
        }

        return ChapterOutput(
            title="2. Persoonlijke eisen & matchanalyse",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative
        )
