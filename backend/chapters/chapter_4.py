
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
        <h4 class="font-bold text-slate-700 mb-4 flex items-center gap-2"><ion-icon name="leaf"></ion-icon> Verduurzamingskansen</h4>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="bg-green-50 border border-green-200 p-4 rounded-xl flex flex-col justify-between">
                <div>
                   <div class="font-bold text-green-800 mb-1">Zonnepanelen</div>
                   <div class="text-sm text-slate-600">Geschikt dakvlak aanwezig.</div>
                </div>
                <div class="mt-3 text-green-700 font-bold text-sm">~€850 besparing/jr</div>
            </div>
            <div class="bg-green-50 border border-green-200 p-4 rounded-xl flex flex-col justify-between">
                <div>
                   <div class="font-bold text-green-800 mb-1">Hybride Warmtepomp</div>
                   <div class="text-sm text-slate-600">Combineer met HR-ketel.</div>
                </div>
                <div class="mt-3 text-green-700 font-bold text-sm">Tot 70% minder gas</div>
            </div>
            <div class="bg-green-50 border border-green-200 p-4 rounded-xl flex flex-col justify-between">
                <div>
                   <div class="font-bold text-green-800 mb-1">Vloerisolatie</div>
                   <div class="text-sm text-slate-600">Verhoogt comfort direct.</div>
                </div>
                <div class="mt-3 text-green-700 font-bold text-sm">~15% besparing</div>
            </div>
        </div>
        """)
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Verduurzamingsopties & Potentie", "content": imp_html},
            "sidebar": [
                {"type": "advisor_card", "title": "Subsidies", "content": "Voor isolatie en warmtepompen is ISDE subsidie beschikbaar (tot 30%)."},
                {"type": "advisor", "title": "Financiering", "content": "Gebruik het Warmtefonds of extra hypotheekruimte voor verduurzaming."}
            ]
        }

        return ChapterOutput(
            title="4. Energie & Duurzaamheid",
            grid_layout=layout, 
            blocks=[]
        )
