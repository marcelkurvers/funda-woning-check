from typing import List, Optional, Any, Dict, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class AIProvenance(BaseModel):
    provider: str
    model: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    confidence: Literal["low", "medium", "high"] = "medium"
    inferred_variables: List[str] = []
    factual_variables: List[str] = []
    reasoning_summary: Optional[str] = None

class PropertyCore(BaseModel):
    address: str = "onbekend (handmatig te vullen)"
    funda_url: str
    asking_price_eur: Optional[str] = None
    living_area_m2: Optional[str] = None
    plot_area_m2: Optional[str] = None
    build_year: Optional[str] = None
    energy_label: str = "onbekend"
    scrape_error: Optional[str] = None
    # Meta fields
    source_stats: Dict[str, Literal["fact", "inferred", "unknown"]] = {}
    extra_data: Dict[str, Any] = {}

class UIComponent(BaseModel):
    type: str
    label: Optional[str] = None
    value: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    trend: Optional[str] = None # up, down, neutral
    icon: Optional[str] = None
    provenance: Optional[Literal["fact", "inferred", "unknown"]] = None

class ChapterLayout(BaseModel):
    left: List[UIComponent] = []
    center: List[UIComponent] = []
    right: List[UIComponent] = []

class ChapterOutput(BaseModel):
    id: Optional[str] = None
    title: str
    grid_layout: Any 
    blocks: List[Dict[str, Any]] = []
    chapter_data: Optional[Dict[str, Any]] = None
    provenance: Optional[AIProvenance] = None
    missing_critical_data: List[str] = []
