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
        
        # Build context with ALL fields from data, plus backward-compatible aliases
        context = {
            # Backward compatible field names (old names)
            "adres": self.data.get("address", "het object"),
            "prijs": self.data.get("asking_price_eur", "nader te bepalen"),
            "oppervlakte": self.data.get("living_area_m2", "? m²"),
            "perceel": self.data.get("plot_area_m2", "? m²"),
            "label": self.data.get("energy_label", "onbekend"),
            "bouwjaar": self.data.get("build_year", "onbekend"),
            "prijs_m2": price_m2,
        }
        
        # Add ALL fields from the parsed data (new fields pass through)
        for key, value in self.data.items():
            if key not in context:  # Don't override backward-compatible aliases
                context[key] = value
        
        return context

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
        # --- MODERN MAGAZINE LAYOUT GENERATOR ---
        
        # 1. VISUALIZE STRENGTHS (Green Grid)
        strengths_html = ""
        val_strengths = narrative.get('strengths')
        if val_strengths and isinstance(val_strengths, list) and len(val_strengths) > 0:
            # Convert list to an Icon Grid
            items = "".join([f"""
                <div class="mag-feature-item success">
                    <div class="mag-icon-box success"><ion-icon name="checkmark-circle"></ion-icon></div>
                    <span class="mag-feature-text">{s}</span>
                </div>
            """ for s in val_strengths])
            
            strengths_html = f"""
            <div class="mag-widget-card">
                <h4 class="mag-widget-title text-emerald-700"><ion-icon name="thumbs-up"></ion-icon> Sterke Punten</h4>
                <div class="mag-feature-grid">
                    {items}
                </div>
            </div>
            """

        # 2. VISUALIZE RISKS (Yellow Grid)
        advice_html = ""
        val_advice = narrative.get('advice')
        if val_advice:
            if isinstance(val_advice, list):
                items = "".join([f"""
                <div class="mag-feature-item warning">
                    <div class="mag-icon-box warning"><ion-icon name="alert-circle"></ion-icon></div>
                    <span class="mag-feature-text">{s}</span>
                </div>
                """ for s in val_advice])
                content = f'<div class="mag-feature-grid">{items}</div>'
            else:
                content = f'<div class="mag-text-content">{val_advice}</div>'

            advice_html = f"""
            <div class="mag-widget-card">
                <h4 class="mag-widget-title text-amber-700"><ion-icon name="warning"></ion-icon> Aandachtspunten</h4>
                {content}
            </div>
            """

        # 3. AI INTERPRETATION (The "Hero" Insight)
        interpretation_html = ""
        val_interp = narrative.get('interpretation')
        if val_interp:
            interpretation_html = f"""
            <div class="mag-hero-card gradient-blue">
                <div class="mag-hero-header">
                    <ion-icon name="analytics" class="mag-hero-icon"></ion-icon>
                    <h4 class="mag-hero-title">AI Interpretatie</h4>
                </div>
                <div class="mag-hero-body">
                    {val_interp}
                </div>
            </div>
            """

        # 4. CONCLUSION (Bottom Bar)
        conclusion_html = ""
        if narrative.get('conclusion'):
             conclusion_html = f"""
            <div class="mag-conclusion-bar">
                <div class="mag-conclusion-icon"><ion-icon name="ribbon"></ion-icon></div>
                <div class="mag-conclusion-text">
                    <strong>Conclusie:</strong> {narrative.get('conclusion')}
                </div>
            </div>
            """

        # 5. ASSEMBLE THE MAGAZINE LAYOUT
        # Structure:
        # [   HEADER (Intro)   ]
        # [ TEXT (L) | VIS (R) ]
            
        return f"""
        <div class="mag-layout-container">
            
            <!-- 1. HERO INTRO -->
            <div class="mag-intro-section">
                <div class="mag-lead-text">
                    {narrative.get('intro', '')}
                </div>
            </div>

            <!-- 2. SPLIT CONTENT AREA -->
            <div class="mag-split-grid">
                
                <!-- LEFT COL: Narrative Text -->
                <div class="mag-col-text">
                    <div class="mag-prose">
                        {narrative.get('main_analysis', '')}
                    </div>
                    {extra_html} <!-- e.g. Verduurzamingskansen injected here -->
                    {conclusion_html}
                </div>

                <!-- RIGHT COL: Visuals & Widgets -->
                <div class="mag-col-visuals">
                    {interpretation_html}
                    {strengths_html}
                    {advice_html}
                    <!-- Right Sidebar items will be injected here by JS if possible, 
                         or they sit in the sidebar. Ideally we merge them here. -->
                    <div id="mag-dynamic-sidebar-target"></div> 
                </div>

            </div>
        </div>
        """
