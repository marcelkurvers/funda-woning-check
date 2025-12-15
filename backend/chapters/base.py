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
        styles = {
            "interpretation": "margin-top: 20px; padding: 15px; background-color: #f0f7ff; border-left: 4px solid #0056b3;",
            "interpretation_h4": "color: #0056b3;",
            "strengths": "margin-top: 20px;",
            "advice": "margin-top: 20px;",
            "conclusion": "margin-top: 25px; padding: 15px; background-color: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 4px;"
        }

        strengths_html = ""
        val_strengths = narrative.get('strengths')
        if val_strengths and isinstance(val_strengths, list) and len(val_strengths) > 0:
            items = "".join([f"<li>{s}</li>" for s in val_strengths])
            strengths_html = f"<div class='strengths-section' style='{styles['strengths']}'><h4>✅ Sterktes</h4><ul class='strengths-list'>{items}</ul></div>"

        interpretation_html = ""
        val_interp = narrative.get('interpretation')
        if val_interp:
            interpretation_html = f"""
            <div class="ai-interpretation-section" style="{styles['interpretation']}">
                <h4 style="{styles['interpretation_h4']}">🧠 AI Interpretatie</h4>
                {val_interp}
            </div>
            """

        advice_html = ""
        val_advice = narrative.get('advice')
        if val_advice:
            advice_html = f"""
            <div class="advice-section" style="{styles['advice']}">
                <h4>⚠️ Aandachtspunten</h4>
                {val_advice}
            </div>
            """

        return f"""
        <div class="chapter-intro">
            <h3>Toelichting</h3>
            <p>{narrative.get('intro', '')}</p>
        </div>
        
        <div class="analysis-section">
            {narrative.get('main_analysis', '')}
        </div>

        {extra_html}

        {interpretation_html}
        {strengths_html}
        {advice_html}
        
        <div class="ai-conclusion-box" style="{styles['conclusion']}">
            {narrative.get('conclusion', '')}
        </div>
        """
