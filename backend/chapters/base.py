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
        # --- MODERN MAGAZINE LAYOUT GENERATOR v2 ---
        
        # 0. PROVENANCE HEADER
        provenance = narrative.get('_provenance', {})
        prov_html = ""
        if provenance:
            conf_class = f"conf-{provenance.get('confidence', 'medium')}"
            timestamp_str = str(provenance.get('timestamp', ''))[:16]
            prov_html = f"""
            \u003cdiv class="mag-provenance-header"\u003e
                \u003cdiv class="prov-badge {conf_class}"\u003e
                    \u003cion-icon name="shield-checkmark"\u003e\u003c/ion-icon\u003e
                    AI Vertrouwen: {provenance.get('confidence', 'not set').upper()}
                \u003c/div\u003e
                \u003cdiv class="prov-details"\u003e
                    \u003cspan\u003e\u003cion-icon name="hardware-chip"\u003e\u003c/ion-icon\u003e {provenance.get('model', 'Unknown Model')}\u003c/span\u003e
                    \u003cspan\u003e\u003cion-icon name="time"\u003e\u003c/ion-icon\u003e {timestamp_str}\u003c/span\u003e
                \u003c/div\u003e
            \u003c/div\u003e
            """

        # 1. DOMAIN VARIABLES GRID
        vars_dict = narrative.get('variables', {})
        vars_html = ""
        if vars_dict:
            items_html = ""
            for name, info in vars_dict.items():
                status = info.get('status', 'unknown')
                icon = "checkmark-circle" if status == "fact" else "help-circle" if status == "unknown" else "bulb"
                items_html += f"""
                <div class="mag-var-card status-{status}">
                    <div class="mag-var-header">
                        <ion-icon name="{icon}"></ion-icon>
                        <span class="mag-var-label">{name}</span>
                    </div>
                    <div class="mag-var-value">{info.get('value', 'onbekend')}</div>
                    <div class="mag-var-reasoning">{info.get('reasoning', '')}</div>
                </div>
                """
            
            vars_html = f"""
            <div class="mag-domain-grid">
                <h4 class="mag-section-header">Domein Variabelen Check</h4>
                <div class="mag-var-container">
                    {items_html}
                </div>
            </div>
            """

        # 2. VISUALIZE STRENGTHS (Green Grid)
        strengths_html = ""
        val_strengths = narrative.get('strengths')
        if val_strengths and isinstance(val_strengths, list) and len(val_strengths) > 0:
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

        # 3. VISUALIZE RISKS (Yellow Grid)
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

        # 4. MARCEL & PETRA COMPARISON
        comparison_html = ""
        comp = narrative.get('comparison')
        if comp:
            m_text = comp.get('marcel', '')
            p_text = comp.get('petra', '')
            adv_text = comp.get('combined_advice', '')
            
            comparison_html = f"""
            <div class="mag-comparison-section">
                <h4 class="mag-section-header">
                    <ion-icon name="people-circle"></ion-icon> Marcel & Petra Perspectief
                </h4>
                <div class="mag-comparison-grid">
                    <div class="mag-persona-card marcel">
                        <div class="mag-persona-header">
                            <ion-icon name="hardware-chip" class="persona-icon"></ion-icon>
                            <span>Marcel (ROI & TCO)</span>
                        </div>
                        <div class="mag-persona-content">{m_text}</div>
                    </div>
                    <div class="mag-persona-card petra">
                        <div class="mag-persona-header">
                            <ion-icon name="color-palette" class="persona-icon"></ion-icon>
                            <span>Petra (Sfeer & Comfort)</span>
                        </div>
                        <div class="mag-persona-content">{p_text}</div>
                    </div>
                </div>
                <div class="mag-joint-advice">
                    <ion-icon name="bulb" class="advice-icon"></ion-icon>
                    <strong>Gezamenlijk Advies:</strong> {adv_text}
                </div>
            </div>
            """

        # 5. CONCLUSION (Bottom Bar)
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

        # 6. ASSEMBLE
        return f"""
        <div class="mag-layout-container">
            {prov_html}
            
            <div class="mag-intro-section">
                <div class="mag-lead-text">
                    {narrative.get('intro', '')}
                </div>
            </div>

            <div class="mag-split-grid">
                <div class="mag-col-text">
                    {vars_html}
                    <div class="mag-prose">
                        {narrative.get('main_analysis', '')}
                    </div>
                    {extra_html}
                    {comparison_html}
                    {conclusion_html}
                </div>

                <div class="mag-col-visuals">
                    {strengths_html}
                    {advice_html}
                    <div id="mag-dynamic-sidebar-target"></div> 
                </div>

            </div>
        </div>
        """
