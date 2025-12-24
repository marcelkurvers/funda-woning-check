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


class NarrativeContract(BaseModel):
    """
    Mandatory narrative contract for each chapter.
    
    This field is REQUIRED.
    There is no default.
    There is no fallback.
    
    Every chapter (0-12) MUST produce a narrative of at least 300 words.
    """
    text: str = Field(..., description="The narrative text, minimum 300 words")
    word_count: int = Field(..., ge=0, description="Word count of the narrative")
    
    def validate_minimum(self, minimum: int = 300) -> bool:
        """Check if narrative meets minimum word requirement."""
        return self.word_count >= minimum


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
    layout_type: str = "modern_dashboard"
    # Legacy / Directional
    left: List[UIComponent] = []
    center: List[UIComponent] = []
    right: List[UIComponent] = []
    # Semantic (Modern 4K) - These alias to directional in usage logic usually
    metrics: List[UIComponent] = []
    main: Dict[str, Any] = {} # Content often is complex, or UIComponent list. Test expects dict with 'content' or list.
    sidebar: List[UIComponent] = []


class ChapterOutput(BaseModel):
    """
    Chapter output model with mandatory narrative.
    
    ARCHITECTURAL REQUIREMENT:
    - narrative field is REQUIRED for chapters 0-12
    - narrative must contain at least 300 words
    - pipeline MUST fail if narrative is missing or too short
    """
    id: Optional[str] = None
    title: str
    grid_layout: Any 
    blocks: List[Dict[str, Any]] = []
    chapter_data: Optional[Dict[str, Any]] = None
    segment: Optional[str] = None
    provenance: Optional[AIProvenance] = None
    missing_critical_data: List[str] = []
    # MANDATORY NARRATIVE FIELD
    narrative: Optional[NarrativeContract] = Field(
        default=None,
        description="Mandatory narrative text (300+ words). Required for chapters 0-12."
    )
