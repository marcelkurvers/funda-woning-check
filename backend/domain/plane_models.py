"""
4-PLANE COGNITIVE MODEL - AUTHORITATIVE DEFINITION

This module implements the 4-Plane Enforced Analytical Report System.
Each plane has EXCLUSIVE responsibility. No output may cross planes. EVER.

If output crosses planes → it MUST be rejected.

PLANES:
🟦 PLANE A — VISUAL INTELLIGENCE PLANE (LEFT)
    Purpose: Pattern recognition & pre-verbal insight
    Answers: "What stands out immediately?"
    ALLOWED: Charts, graphs, trends, deltas, heatmaps, bars, timelines
    FORBIDDEN: Explanatory text, interpretation, conclusions, KPIs with meaning

🟩 PLANE B — NARRATIVE REASONING PLANE (CENTER–UPPER)
    Purpose: Meaning, interpretation, judgment
    Answers: "What does this mean, and why?"
    ALLOWED: Interpretation of KPIs, contextual reasoning, trade-offs, scenario thinking
    FORBIDDEN: Raw KPIs, tables, bullet KPI dumps, graphs, Marcel/Petra scoring
    REQUIREMENTS: Minimum 300 words per chapter

🟨 PLANE C — FACTUAL ANCHOR PLANE (CENTER–LOWER)
    Purpose: Verifiable truth & completeness
    Answers: "What do we actually know?"
    ALLOWED: KPIs, parameters, registry facts, missing data indicators, data provenance
    FORBIDDEN: Narrative prose, interpretation, opinions, preferences

🟥 PLANE D — HUMAN PREFERENCE PLANE (RIGHT)
    Purpose: Personal relevance & divergence
    Answers: "How does this land for Marcel vs Petra?"
    ALLOWED: Marcel vs Petra comparisons, comfort vs strategy, match indices, mood scores
    FORBIDDEN: Raw registry data, KPI tables, narrative explanation, visual analytics
"""

from typing import List, Optional, Any, Dict, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class PlaneType(str, Enum):
    """The four cognitive planes in the reporting system."""
    PLANE_A = "visual_intelligence"
    PLANE_B = "narrative_reasoning"
    PLANE_C = "factual_anchor"
    PLANE_D = "human_preference"


class PlaneViolationError(Exception):
    """
    PLANE VIOLATION ERROR:
    Output attempted to cross cognitive planes.
    Refactor required. Output rejected.
    """
    def __init__(self, source_plane: str, violation_type: str, details: str):
        self.source_plane = source_plane
        self.violation_type = violation_type
        self.details = details
        super().__init__(
            f"PLANE VIOLATION ERROR:\n"
            f"Output attempted to cross cognitive planes.\n"
            f"Source Plane: {source_plane}\n"
            f"Violation: {violation_type}\n"
            f"Details: {details}\n"
            f"Refactor required. Output rejected."
        )


# =============================================================================
# 🟦 PLANE A — VISUAL INTELLIGENCE PLANE (LEFT)
# =============================================================================

class VisualDataPoint(BaseModel):
    """A single data point for visualization."""
    label: str
    value: float
    unit: Optional[str] = None
    color: Optional[str] = None
    

class ChartConfig(BaseModel):
    """Configuration for a chart/visualization."""
    chart_type: Literal[
        "radar", "bar", "line", "heatmap", "area", 
        "comparison", "delta", "sparkline", "gauge",
        "score", "distribution", "trend"
    ]
    title: str
    data: List[VisualDataPoint]
    max_value: Optional[float] = None
    show_legend: bool = True


class PlaneAVisualModel(BaseModel):
    """
    🟦 PLANE A — VISUAL INTELLIGENCE PLANE
    
    Purpose: Pattern recognition & pre-verbal insight
    Answers: "What stands out immediately?"
    
    ALLOWED:
    - Charts, graphs, infographics
    - Trends, deltas, comparisons
    - Heatmaps, bars, timelines
    
    FORBIDDEN:
    - Explanatory text (no prose)
    - Interpretation (no meaning)
    - Conclusions (no judgments)
    - KPIs with semantic meaning attached
    - Preferences/opinions
    
    DATA RULE:
    - Visuals may ONLY use registry-verified data
    - No AI-generated values
    - No illustrative or inferred charts
    """
    plane: Literal["A"] = "A"
    plane_name: Literal["visual_intelligence"] = "visual_intelligence"
    
    # Visual components - ONLY charts and visual patterns
    charts: List[ChartConfig] = Field(default_factory=list)
    trends: List[Dict[str, Any]] = Field(default_factory=list)
    comparisons: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Must be sourced from registry
    data_source_ids: List[str] = Field(
        default_factory=list,
        description="Registry IDs that source this visual data"
    )
    
    # Explicit marker for not-applicable state
    not_applicable: bool = False
    not_applicable_reason: Optional[str] = None
    
    @field_validator('charts')
    @classmethod
    def validate_no_text_content(cls, v):
        """Ensure charts don't contain narrative text."""
        for chart in v:
            # Title must be brief (not narrative)
            if len(chart.title) > 50:
                raise ValueError(
                    f"PLANE A VIOLATION: Chart title too long (>{50} chars). "
                    f"Titles must be brief labels, not explanations."
                )
        return v


# =============================================================================
# 🟦 PLANE A2 — SYNTHESIZED VISUAL INTELLIGENCE (EXTENSION)
# =============================================================================

class HeroInfographic(BaseModel):
    """
    Hero infographic for a chapter - the primary synthesized visual.
    Can optionally include a generated image.
    """
    title: str = Field(..., max_length=100)
    visual_type: Literal["infographic", "diagram", "comparison_visual", "timeline"] = "infographic"
    prompt: str = Field(..., description="The prompt used to generate this infographic")
    data_used: List[str] = Field(
        default_factory=list,
        description="Registry field IDs used to generate this infographic"
    )
    insight_summary: str = Field(
        default="",
        max_length=300,
        description="Brief insight this infographic conveys (not narrative)"
    )
    uncertainties: List[str] = Field(
        default_factory=list,
        description="Data limitations or assumptions"
    )
    # Image content - either URI or base64
    image_uri: Optional[str] = Field(
        None,
        description="URI to generated image file (preferred)"
    )
    image_base64: Optional[str] = Field(
        None,
        description="Base64 encoded image data (fallback)"
    )
    generation_status: Literal["pending", "generated", "failed", "skipped"] = "pending"
    generation_error: Optional[str] = None


class VisualConcept(BaseModel):
    """A conceptual visual that could be rendered."""
    title: str = Field(..., max_length=100)
    visual_type: str
    data_used: List[str] = Field(default_factory=list)
    insight_explained: str = Field(..., max_length=500)
    uncertainty_notes: Optional[str] = None


class PlaneA2SynthVisualModel(BaseModel):
    """
    🟦 PLANE A2 — SYNTHESIZED VISUAL INTELLIGENCE
    
    Purpose: AI-assisted visual synthesis and infographics
    Answers: "What patterns can we visualize from the data?"
    
    ALLOWED:
    - AI-generated infographics based on registry data
    - Visual concepts derived from property analysis
    - Synthesized comparison visuals
    
    FORBIDDEN:
    - Invented data (must trace to registry)
    - Narrative explanations (go to Plane B)
    - KPI values without visual context
    
    DATA RULE:
    - All visuals MUST reference registry data via data_used
    - Image generation is OPTIONAL (graceful degradation)
    """
    plane: Literal["A2"] = "A2"
    plane_name: Literal["synth_visual_intelligence"] = "synth_visual_intelligence"
    
    # The hero infographic (primary visual for the chapter)
    hero_infographic: Optional[HeroInfographic] = Field(
        None,
        description="Primary generated infographic for this chapter"
    )
    
    # Additional visual concepts (2-4 per chapter)
    concepts: List[VisualConcept] = Field(
        default_factory=list,
        description="Visual concepts that could be rendered"
    )
    
    # Registry sources
    data_source_ids: List[str] = Field(
        default_factory=list,
        description="All registry IDs used across A2 visuals"
    )
    
    # Explicit marker for not-applicable state
    not_applicable: bool = False
    not_applicable_reason: Optional[str] = None


# =============================================================================
# 🟩 PLANE B — NARRATIVE REASONING PLANE (CENTER–UPPER)
# =============================================================================

class PlaneBNarrativeModel(BaseModel):
    """
    🟩 PLANE B — NARRATIVE REASONING PLANE
    
    Purpose: Meaning, interpretation, judgment
    Answers: "What does this mean, and why?"
    
    HARD REQUIREMENTS:
    - Minimum 300 words per chapter (500-700 for Chapter 0)
    - Written, continuous prose
    - Analytical, reflective, explanatory
    
    ALLOWED:
    - Interpretation of KPIs
    - Contextual reasoning
    - Trade-offs
    - Scenario thinking
    
    FORBIDDEN:
    - Raw KPIs (no numbers without context)
    - Tables (structured data goes to Plane C)
    - Bullet KPI dumps
    - Graphs (visual goes to Plane A)
    - Marcel/Petra scoring (goes to Plane D)
    
    AI ROLE:
    - AI operates ONLY in this plane
    - AI may reason, explain, contextualize
    - AI may NOT introduce new facts
    """
    plane: Literal["B"] = "B"
    plane_name: Literal["narrative_reasoning"] = "narrative_reasoning"
    
    # The narrative text - MANDATORY
    narrative_text: str = Field(
        ...,
        min_length=100,  # Enforced in validation
        description="The narrative text. Minimum 300 words for chapters 1-12."
    )
    
    # Word count for validation
    word_count: int = Field(
        ...,
        ge=0,
        description="Word count of the narrative"
    )
    
    # Explicit marker for not-applicable state
    not_applicable: bool = False
    not_applicable_reason: Optional[str] = None
    
    # AI provenance (required since AI generates this)
    ai_generated: bool = True
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    
    def validate_word_count(self, minimum: int = 300) -> bool:
        """Validate that narrative meets minimum word requirement."""
        if self.not_applicable:
            return True
        return self.word_count >= minimum
    
    @field_validator('narrative_text')
    @classmethod
    def validate_no_raw_kpis(cls, v):
        """Ensure narrative doesn't contain raw KPI dumps."""
        # Check for patterns that suggest KPI dumps
        import re
        
        # Pattern: Multiple lines with "Label: Value" format
        kpi_pattern = r'^[A-Z][a-z]+:?\s*[\d€%]+.*$'
        lines = v.split('\n')
        kpi_lines = sum(1 for line in lines if re.match(kpi_pattern, line.strip()))
        
        if kpi_lines > 3:
            raise ValueError(
                f"PLANE B VIOLATION: Narrative contains {kpi_lines} KPI-like lines. "
                f"Raw KPIs belong in Plane C (Factual Anchor), not Plane B (Narrative)."
            )
        return v


# =============================================================================
# 🟨 PLANE C — FACTUAL ANCHOR PLANE (CENTER–LOWER)
# =============================================================================

class FactualKPI(BaseModel):
    """A single KPI or fact from the registry."""
    key: str
    label: str
    value: Any
    unit: Optional[str] = None
    provenance: Literal["fact", "derived", "inferred", "unknown"] = "fact"
    registry_id: Optional[str] = None
    completeness: bool = True
    missing_reason: Optional[str] = None


class PlaneCFactModel(BaseModel):
    """
    🟨 PLANE C — FACTUAL ANCHOR PLANE
    
    Purpose: Verifiable truth & completeness
    Answers: "What do we actually know?"
    
    ALLOWED:
    - KPIs
    - Parameters
    - Registry facts
    - Missing data indicators
    - Data provenance
    
    FORBIDDEN:
    - Narrative prose (goes to Plane B)
    - Interpretation (goes to Plane B)
    - Opinions (goes to Plane D)
    - Preferences (goes to Plane D)
    
    STRUCTURE:
    - Structured blocks
    - Tables
    - Explicit "missing / unknown" markers
    """
    plane: Literal["C"] = "C"
    plane_name: Literal["factual_anchor"] = "factual_anchor"
    
    # Core KPIs for this chapter
    kpis: List[FactualKPI] = Field(default_factory=list)
    
    # Parameters (registry facts)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Data provenance tracking
    data_sources: List[str] = Field(default_factory=list)
    
    # Explicit missing data markers
    missing_data: List[str] = Field(
        default_factory=list,
        description="List of expected but missing data points"
    )
    
    # Uncertainties
    uncertainties: List[str] = Field(
        default_factory=list,
        description="Data points with low confidence"
    )
    
    # Explicit marker for not-applicable state
    not_applicable: bool = False
    not_applicable_reason: Optional[str] = None
    
    @field_validator('kpis')
    @classmethod
    def validate_no_narrative_in_kpis(cls, v):
        """Ensure KPIs don't contain narrative text."""
        for kpi in v:
            # Value should not be a long narrative string
            if isinstance(kpi.value, str) and len(kpi.value) > 200:
                raise ValueError(
                    f"PLANE C VIOLATION: KPI '{kpi.key}' has value too long (>{200} chars). "
                    f"This looks like narrative content, which belongs in Plane B."
                )
        return v


# =============================================================================
# 🟥 PLANE D — HUMAN PREFERENCE PLANE (RIGHT)
# =============================================================================

class PersonaScore(BaseModel):
    """Score and assessment for a specific persona."""
    match_score: Optional[float] = Field(None, ge=0, le=100)
    mood: Optional[Literal["positive", "neutral", "negative", "mixed"]] = None
    key_values: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    summary: Optional[str] = None


class PreferenceComparison(BaseModel):
    """A specific comparison point between Marcel and Petra."""
    aspect: str
    marcel_view: str
    petra_view: str
    alignment: Literal["aligned", "divergent", "tension", "complementary"]
    requires_discussion: bool = False


class PlaneDPreferenceModel(BaseModel):
    """
    🟥 PLANE D — HUMAN PREFERENCE PLANE
    
    Purpose: Personal relevance & divergence
    Answers: "How does this land for Marcel vs Petra?"
    
    ALLOWED:
    - Marcel vs Petra comparisons
    - Comfort vs strategy tensions
    - Aesthetic vs technical tension
    - Match indices, mood scores
    
    FORBIDDEN:
    - Raw registry data (goes to Plane C)
    - KPI tables (goes to Plane C)
    - Narrative explanation (goes to Plane B)
    - Visual analytics (goes to Plane A)
    
    RULE:
    - This plane consumes outputs from B & C
    - It never invents facts
    """
    plane: Literal["D"] = "D"
    plane_name: Literal["human_preference"] = "human_preference"
    
    # Persona assessments
    marcel: PersonaScore = Field(default_factory=PersonaScore)
    petra: PersonaScore = Field(default_factory=PersonaScore)
    
    # Comparison points
    comparisons: List[PreferenceComparison] = Field(default_factory=list)
    
    # Overlap and divergence summary
    overlap_points: List[str] = Field(
        default_factory=list,
        description="Where Marcel and Petra agree"
    )
    tension_points: List[str] = Field(
        default_factory=list,
        description="Where Marcel and Petra diverge"
    )
    
    # Joint synthesis (for Chapter 0)
    joint_synthesis: Optional[str] = Field(
        None,
        max_length=500,
        description="Brief synthesis of joint position (max 500 chars)"
    )
    
    # Explicit marker for not-applicable state
    not_applicable: bool = False
    not_applicable_reason: Optional[str] = None
    
    @field_validator('joint_synthesis')
    @classmethod
    def validate_synthesis_brevity(cls, v):
        """Ensure synthesis is brief, not a narrative."""
        if v and len(v) > 500:
            raise ValueError(
                f"PLANE D VIOLATION: Joint synthesis too long (>{500} chars). "
                f"Extended narrative belongs in Plane B."
            )
        return v


# =============================================================================
# CHAPTER PLANE COMPOSITION (All 4 planes per chapter)
# =============================================================================

class ChapterPlaneComposition(BaseModel):
    """
    Complete plane composition for a single chapter.
    
    Every chapter (0-12) MUST explicitly populate all four planes
    or explicitly mark a plane as not_applicable.
    
    Plane A2 (synthesized visuals) is OPTIONAL but recommended for chapters 1-12.
    """
    chapter_id: int = Field(..., ge=0, le=12)
    chapter_title: str
    
    # THE FOUR PLANES - ALL REQUIRED
    plane_a: PlaneAVisualModel = Field(
        ...,
        description="🟦 Visual Intelligence Plane A1 - Deterministic Charts (LEFT)"
    )
    plane_a2: Optional[PlaneA2SynthVisualModel] = Field(
        None,
        description="🟦 Visual Intelligence Plane A2 - Synthesized Visuals (LEFT)"
    )
    plane_b: PlaneBNarrativeModel = Field(
        ...,
        description="🟩 Narrative Reasoning Plane (CENTER–UPPER)"
    )
    plane_c: PlaneCFactModel = Field(
        ...,
        description="🟨 Factual Anchor Plane (CENTER–LOWER)"
    )
    plane_d: PlaneDPreferenceModel = Field(
        ...,
        description="🟥 Human Preference Plane (RIGHT)"
    )
    
    def validate_plane_isolation(self) -> List[str]:
        """
        Validate that no content crosses planes.
        Returns list of violations (empty if valid).
        """
        violations = []
        
        # Check Plane B word count
        if not self.plane_b.not_applicable:
            min_words = 500 if self.chapter_id == 0 else 300
            if self.plane_b.word_count < min_words:
                violations.append(
                    f"PLANE B: Narrative has {self.plane_b.word_count} words, "
                    f"minimum is {min_words} for chapter {self.chapter_id}"
                )
        
        # Check that Plane A has no text content
        for chart in self.plane_a.charts:
            if len(chart.title) > 50:
                violations.append(
                    f"PLANE A: Chart title '{chart.title[:30]}...' is too long. "
                    f"Explanatory text belongs in Plane B."
                )
        
        # Check that Plane C has no narrative content
        for kpi in self.plane_c.kpis:
            if isinstance(kpi.value, str) and len(kpi.value) > 200:
                violations.append(
                    f"PLANE C: KPI '{kpi.key}' value is too long. "
                    f"Narrative content belongs in Plane B."
                )
        
        # Check that Plane D has no extended narrative
        if self.plane_d.joint_synthesis and len(self.plane_d.joint_synthesis) > 500:
            violations.append(
                f"PLANE D: Joint synthesis is too long. "
                f"Extended narrative belongs in Plane B."
            )
        
        return violations
    
    def enforce_or_reject(self):
        """
        Enforce plane isolation. Raises PlaneViolationError if violated.
        """
        violations = self.validate_plane_isolation()
        if violations:
            raise PlaneViolationError(
                source_plane="MULTI",
                violation_type="CROSS_PLANE_CONTENT",
                details="\n".join(violations)
            )


# =============================================================================
# FULL REPORT STRUCTURE
# =============================================================================

class FourPlaneReport(BaseModel):
    """
    The complete 4-Plane Report structure.
    
    Chapter 0: Executive Summary
        A: High-level market visuals
        B: Strategic narrative (500–700 words)
        C: Key KPIs summary
        D: Joint Marcel/Petra synthesis
    
    Chapters 1–10: Core Analysis
        A: Chapter-specific visuals (optional but encouraged)
        B: Minimum 300 words narrative
        C: Full KPI & parameter set
        D: Explicit Marcel vs Petra interpretation
    
    Chapter 11: Market Positioning
        A: Comparative visuals mandatory
        B: Strategy narrative
        C: Price, comps, ranges
        D: Risk appetite divergence
    
    Chapter 12: Advice & Conclusion
        A: Scenario visuals
        B: Final reasoning narrative
        C: Decision KPIs
        D: Final alignment / tension
    """
    
    # Executive Summary
    chapter_0: ChapterPlaneComposition = Field(
        ...,
        description="Executive Summary - All planes required"
    )
    
    # Core Analysis Chapters (1-10)
    chapters: Dict[int, ChapterPlaneComposition] = Field(
        default_factory=dict,
        description="Chapters 1-12 indexed by chapter number"
    )
    
    # Report metadata
    property_address: str
    generated_at: str
    
    def get_chapter(self, chapter_id: int) -> Optional[ChapterPlaneComposition]:
        """Get a chapter by ID."""
        if chapter_id == 0:
            return self.chapter_0
        return self.chapters.get(chapter_id)
    
    def validate_all_planes(self) -> Dict[int, List[str]]:
        """
        Validate all chapters for plane isolation.
        Returns dict of chapter_id -> list of violations.
        """
        violations = {}
        
        # Check chapter 0
        ch0_violations = self.chapter_0.validate_plane_isolation()
        if ch0_violations:
            violations[0] = ch0_violations
        
        # Check all other chapters
        for ch_id, chapter in self.chapters.items():
            ch_violations = chapter.validate_plane_isolation()
            if ch_violations:
                violations[ch_id] = ch_violations
        
        return violations
