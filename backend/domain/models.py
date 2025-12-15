from typing import List, Optional, Any, Dict, Literal
from pydantic import BaseModel

class PropertyCore(BaseModel):
    address: str = "onbekend (handmatig te vullen)"
    funda_url: str
    asking_price_eur: Optional[str] = None
    living_area_m2: Optional[str] = None
    plot_area_m2: Optional[str] = None
    build_year: Optional[str] = None
    energy_label: str = "onbekend"
    scrape_error: Optional[str] = None
    # Extra fields can be stored in a dict if needed, but these are core
    price_deviation_percent: Optional[float] = None
    energy_future_score: Optional[float] = None
    maintenance_intensity: Optional[str] = None
    family_suitability: Optional[str] = None
    long_term_quality: Optional[str] = None
    extra_data: Dict[str, Any] = {}

class UIComponent(BaseModel):
    type: str
    # Common fields
    label: Optional[str] = None
    value: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    trend: Optional[str] = None # up, down, neutral
    icon: Optional[str] = None

class ChapterLayout(BaseModel):
    left: List[UIComponent] = []
    center: List[UIComponent] = []
    right: List[UIComponent] = []

class ChapterOutput(BaseModel):
    title: str
    grid_layout: Any # Was ChapterLayout, relaxed to Any to support Modern Dashboard dicts
    # Legacy blocks for PDF if needed
    blocks: List[Dict[str, Any]] = []
