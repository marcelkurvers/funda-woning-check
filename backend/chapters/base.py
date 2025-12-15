from abc import ABC, abstractmethod
from typing import List, Dict, Any
import re
from domain.models import PropertyCore, ChapterOutput, ChapterLayout, UIComponent

class BaseChapter(ABC):
    def __init__(self, property_core: Dict[str, Any]):
        # We accept a dict and convert to Pydantic for safety, or allow loose dicts if needed
        # For now, let's wrap it in our model or just store it.
        # The main.py passes a dict currently.
        self.data = property_core
        self.context = self._build_context()

    def _build_context(self) -> Dict[str, Any]:
        """Common context helpers used across chapters"""
        price_val = self.data.get("asking_price_eur")
        area_val = self.data.get("living_area_m2")
        price_m2 = "?"
        if price_val and area_val:
            try:
                # Robust parsing
                p = int(re.sub(r'[^\d]', '', str(price_val)) or 0)
                # Ensure no superscripts affect area (e.g. m²)
                a_str = re.sub(r'[^\d]', '', str(area_val))
                a_str_safe = re.sub(r'[^0-9]', '', str(area_val)) # purely ascii digits
                a = int(a_str_safe or 0)
                
                if a > 0: price_m2 = f"€ {int(p/a):,}"
            except: pass
            
        return {
            "adres": self.data.get("address", "het object"),
            "prijs": self.data.get("asking_price_eur", "nader te bepalen"),
            "oppervlakte": self.data.get("living_area_m2", "? m²"),
            "perceel": self.data.get("plot_area_m2", "? m²"),
            "label": self.data.get("energy_label", "onbekend"),
            "bouwjaar": self.data.get("build_year", "onbekend"),
            "prijs_m2": price_m2
        }

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def generate(self) -> ChapterOutput:
        pass
    
    def _create_layout(self, left=[], center=[], right=[]) -> ChapterLayout:
        return ChapterLayout(
            left=[UIComponent(**x) if isinstance(x, dict) else x for x in left],
            center=[UIComponent(**x) if isinstance(x, dict) else x for x in center],
            right=[UIComponent(**x) if isinstance(x, dict) else x for x in right]
        )

    def _render_rich_narrative(self, narrative: Dict[str, Any], extra_html: str = "") -> str:
        """
        Renders a consistent HTML block for the AI Driven Narrative.
        Expects keys: intro, main_analysis, interpretation, advice, strengths, conclusion.
        extra_html: Optional HTML to insert between analysis and AI sections.
        """
        
        # Strengths (Pros)
        strengths_html = ""
        val_strengths = narrative.get('strengths')
        if val_strengths and isinstance(val_strengths, list) and len(val_strengths) > 0:
            items = "".join([f"<li><ion-icon name='checkmark-circle' style='color:#10b981'></ion-icon> <span>{s}</span></li>" for s in val_strengths])
            strengths_html = f"""
            <div class="ai-card success">
                <h4 class="ai-card-title"><ion-icon name="thumbs-up"></ion-icon> Sterke Punten</h4>
                <ul class="ai-list">{items}</ul>
            </div>
            """

        # Interpretation (Brain)
        interpretation_html = ""
        val_interp = narrative.get('interpretation')
        if val_interp:
            interpretation_html = f"""
            <div class="ai-card info">
                <h4 class="ai-card-title"><ion-icon name="analytics"></ion-icon> AI Interpretatie</h4>
                <div class="text-slate-600">{val_interp}</div>
            </div>
            """

        # Advice (Warnings/Cons)
        advice_html = ""
        val_advice = narrative.get('advice')
        if val_advice:
            # Check if advice is list or string
            if isinstance(val_advice, list):
                advice_content = "<ul class='ai-list'>" + "".join([f"<li><ion-icon name='alert-circle' style='color:#f59e0b'></ion-icon> <span>{s}</span></li>" for s in val_advice]) + "</ul>"
            else:
                advice_content = f"<div class='text-slate-600'>{val_advice}</div>"

            advice_html = f"""
            <div class="ai-card warning">
                <h4 class="ai-card-title"><ion-icon name="warning"></ion-icon> Aandachtspunten</h4>
                {advice_content}
            </div>
            """

        conclusion_html = ""
        if narrative.get('conclusion'):
             conclusion_html = f"""
            <div class="ai-card dark">
                <h4 class="ai-card-title"><ion-icon name="ribbon"></ion-icon> Conclusie</h4>
                <div style="opacity:0.9">{narrative.get('conclusion')}</div>
            </div>
            """

        return f"""
        <div class="introduction text-lg font-medium text-slate-600 mb-6">
            {narrative.get('intro', '')}
        </div>
        
        <div class="analysis-section prose mb-6">
            {narrative.get('main_analysis', '')}
        </div>

        {extra_html}

        {interpretation_html}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {strengths_html}
            {advice_html}
        </div>
        
        {conclusion_html}
        """
