from abc import ABC, abstractmethod
from typing import List, Dict, Any
import re
from domain.models import PropertyCore, ChapterOutput, ChapterLayout, UIComponent

class BaseChapter(ABC):
    def __init__(self, property_core: Dict[str, Any], id: int = 0):
        self.data = property_core
        self.id = id
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
        l_comps = [UIComponent(**x) if isinstance(x, dict) else x for x in left]
        c_comps = [UIComponent(**x) if isinstance(x, dict) else x for x in center]
        r_comps = [UIComponent(**x) if isinstance(x, dict) else x for x in right]
        
        return ChapterLayout(
            left=l_comps,
            center=c_comps,
            right=r_comps,
            # Semantic mapping for Modern 4K compliance
            metrics=l_comps,
            # Main expects a dict with content
            main={"title": self.get_title(), "content": c_comps},
            sidebar=r_comps
        )

    def get_segment_name(self) -> str:
        """Returns the stylized segment name for this chapter (e.g., 'OBJECT / ARCHITECTUUR')."""
        from chapters.formatter import EditorialEngine
        # Access the private titles dict via a helper or just use the same logic
        titles = {
            0: "EXECUTIVE / STRATEGIE",
            1: "OBJECT / ARCHITECTUUR",
            2: "SYNERGIE / MATCH",
            3: "TECHNIEK / CONDITIE",
            4: "ENERGETICA / AUDIT",
            5: "LAYOUT / POTENTIE",
            6: "AFWERKING / ONDERHOUD",
            7: "EXTERIEUR / TUIN",
            8: "MOBILITEIT / PARKEREN",
            9: "JURIDISCH / KADASTER",
            10: "FINANCIEEL / RENDEMENT",
            11: "MARKT / POSITIE",
            12: "VERDICT / STRATEGIE"
        }
        return titles.get(self.id, f"DOSSIER / SEGMENT {self.id}")

    def _render_rich_narrative(self, narrative: Dict[str, Any], extra_html: str = "") -> str:
        """
        Magazine Layout Generator v8.0: Editorial Engine Mode.
        Uses the EditorialEngine to transform raw text into premium magazine layouts.
        """
        from chapters.formatter import EditorialEngine
        
        # Determine Chapter ID from context or instance
        chapter_id = int(getattr(self, 'id', 0))
        
        # Use the Editorial Production Line
        formatted_analysis = EditorialEngine.format_narrative(
            chapter_id=chapter_id,
            narrative=narrative,
            data=self.data
        )

        return formatted_analysis

