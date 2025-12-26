
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
            {"id": "parking", "label": "Parkeren", "value": parking_status, "icon": "car", "color": "orange" if parking_status == "Openbaar" else "green", "explanation": "Vergunning check" if parking_status == "Openbaar" else "Op eigen terrein"},
            {"id": "ev", "label": "Laadpaal", "value": "Mogelijk", "icon": "flash", "color": "green", "explanation": "Infra aanwezig"},
            {"id": "highway", "label": "Snelweg", "value": "< 10 min", "icon": "speedometer", "color": "green", "explanation": "Goede uitvalswegen"},
            {"id": "public", "label": "OV Halte", "value": "Nabij", "icon": "bus", "color": "blue", "explanation": "Loopafstand"}
        ]
        # Chapter 8 UNIQUE metrics — Location & Accessibility specific
        # NOTE: These metrics must NOT overlap with other chapters per Four-Plane contract
        
        # Woon-werk bereikbaarheid (unique to Ch8)
        metrics.append({"id": "ch8_commute_score", "label": "Woon-Werk Score", "value": "Goed", "icon": "briefcase", "color": "green", "explanation": "Brainport-bereikbaar"})
        
        # Voorzieningen radius (unique to Ch8)
        metrics.append({"id": "ch8_amenities_radius", "label": "Voorzieningen", "value": "Compleet", "icon": "storefront", "color": "green", "explanation": "Scholen, winkels, zorg nabij"})
        
        # Fietsvriendelijkheid (unique to Ch8)
        metrics.append({"id": "ch8_bike_friendly", "label": "Fietsinfra", "value": "Goed", "icon": "bicycle", "color": "green", "explanation": "Fietspadennetwerk"})
        
        # Buurt leefbaarheid (unique to Ch8)
        metrics.append({"id": "ch8_neighborhood_score", "label": "Buurtscore", "value": "Rustig", "icon": "home", "color": "green", "explanation": "Woonwijk karakter"})
        
        main_content = self._render_rich_narrative(narrative, extra_html=f"""
        <div class="bg-slate-50 border border-slate-200 p-5 rounded-xl">
            <h4 class="font-bold text-slate-800 mb-3 flex items-center gap-2"><ion-icon name="list"></ion-icon> Aandachtspunten</h4>
            <ul class="space-y-2">
                <li class="flex items-start gap-2">
                    <ion-icon name="alert-circle" class="text-orange-500 mt-1"></ion-icon>
                    <span class="text-slate-700">Check parkeervergunning wachttijden bij gemeente.</span>
                </li>
                <li class="flex items-start gap-2">
                    <ion-icon name="help-circle" class="text-blue-500 mt-1"></ion-icon>
                    <span class="text-slate-700">Is er ruimte voor een laadpaal op eigen terrein?</span>
                </li>
                <li class="flex items-start gap-2">
                    <ion-icon name="time" class="text-slate-500 mt-1"></ion-icon>
                    <span class="text-slate-700">Hoe druk is de straat tijdens spitsuur?</span>
                </li>
            </ul>
        </div>
        """)
        
        # Left sidebar: Parking info
        left_sidebar = [
             {
                "type": "highlight_card",
                "icon": "car",
                "title": "Mobiliteit",
                "content": "Goed bereikbaar met auto en OV"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Parkeren & Mobiliteit", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [{"type": "advisor", "title": "Toekomst", "content": "Elektrisch rijden neemt toe. Een eigen oprit is goud waard."}]
        }

        return ChapterOutput(
            title="8. Parkeren & Bereikbaarheid",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative
        )
