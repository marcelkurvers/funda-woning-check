
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
            {"id": "ground", "label": "Grond", "value": "Eigen grond?", "icon": "map", "trend": "neutral", "color": "blue", "explanation": "Check kadaster"},
            {"id": "vve", "label": "VvE", "value": "Check", "icon": "people", "color": "blue", "explanation": "Indien app."}, 
            {"id": "zoning", "label": "Bestemming", "value": "Wonen", "icon": "home", "color": "green", "explanation": "Conform"},
            {"id": "permit", "label": "Vergunningen", "value": "Checken", "icon": "document", "color": "blue", "explanation": "Bij verbouwplannen"}
        ]
        # Chapter 9 UNIQUE metrics — Legal & Ownership specific
        # NOTE: These metrics must NOT overlap with other chapters per Four-Plane contract
        
        # Kadaster verificatie status (unique to Ch9)
        metrics.append({"id": "ch9_kadaster_status", "label": "Kadaster Check", "value": "Vereist", "icon": "document-text", "color": "blue", "explanation": "Nog te verifiëren"})
        
        # Erfpacht risico (unique to Ch9)
        property_type = ctx.get('property_type', 'onbekend')
        erfpacht_risk = "Onwaarschijnlijk" if "vrijstaand" in str(property_type).lower() else "Controleren"
        metrics.append({"id": "ch9_erfpacht_risk", "label": "Erfpacht Risico", "value": erfpacht_risk, "icon": "alert-circle", "color": "green" if erfpacht_risk == "Onwaarschijnlijk" else "orange", "explanation": "Afhankelijk van gemeente"})
        
        # Eigendomszekerheid (unique to Ch9)
        metrics.append({"id": "ch9_ownership_certainty", "label": "Eigendomszekerheid", "value": "Verifiëren", "icon": "shield-checkmark", "color": "blue", "explanation": "Notaris bevestigt"})
        
        # Bestemmingsplan status (unique to Ch9)
        metrics.append({"id": "ch9_zoning_status", "label": "Bestemmingsplan", "value": "Wonen", "icon": "map", "color": "green", "explanation": "Conform verwachting"})
        
        main_content = self._render_rich_narrative(narrative, extra_html=f"""
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div class="bg-blue-50 border border-blue-200 p-4 rounded-xl shadow-sm">
                <div class="font-bold text-blue-900 mb-2 flex items-center gap-2"><ion-icon name="home"></ion-icon> Eigendomssituatie</div>
                <div class="text-sm text-blue-800">
                    Volle eigendom of erfpacht? Bij erfpacht: wat is de canon en looptijd?
                </div>
            </div>
            <div class="bg-blue-50 border border-blue-200 p-4 rounded-xl shadow-sm">
                <div class="font-bold text-blue-900 mb-2 flex items-center gap-2"><ion-icon name="git-network"></ion-icon> Erfdienstbaarheden</div>
                <div class="text-sm text-blue-800">
                    Zijn er rechten van overpad of andere verplichtingen richting buren?
                </div>
            </div>
        </div>
        """)
        
        # Left sidebar: Legal checklist
        left_sidebar = [
             {
                "type": "highlight_card",
                "icon": "shield-checkmark",
                "title": "Juridische Status",
                "content": "Controleer kadaster en bestemmingsplan"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Recht & Eigendom", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [{"type": "advisor_card", "title": "Notaris", "content": "Vraag concept koopakte tijdig op voor controle."}]
        }

        return ChapterOutput(
            title="9. Juridische Aspecten",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative
        )
