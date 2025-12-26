"""
4-PLANE VALIDATOR - ENFORCEMENT & REFUSAL RULES

This module enforces the 4-Plane Cognitive Model constraints.

HARD REFUSAL CONDITIONS - The system MUST reject output if:
1. KPIs appear in Plane B (Narrative)
2. Narrative appears in Plane C (Facts)
3. Visuals appear outside Plane A
4. Preferences leak into narrative
5. A chapter has <300 words narrative
6. AI invents data not in registry

Error Message (Mandatory):
PLANE VIOLATION ERROR:
Output attempted to cross cognitive planes.
Refactor required. Output rejected.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging

from backend.domain.plane_models import (
    PlaneAVisualModel,
    PlaneA2SynthVisualModel,
    PlaneBNarrativeModel, 
    PlaneCFactModel,
    PlaneDPreferenceModel,
    ChapterPlaneComposition,
    PlaneViolationError
)

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of plane violations."""
    KPI_IN_NARRATIVE = "kpi_in_narrative"
    NARRATIVE_IN_FACTS = "narrative_in_facts"
    VISUAL_OUTSIDE_PLANE_A = "visual_outside_plane_a"
    PREFERENCE_LEAK = "preference_leak"
    INSUFFICIENT_NARRATIVE = "insufficient_narrative"
    AI_INVENTED_DATA = "ai_invented_data"
    CROSS_PLANE_CONTENT = "cross_plane_content"


@dataclass
class PlaneViolation:
    """A detected plane violation."""
    chapter_id: int
    plane: str
    violation_type: ViolationType
    description: str
    severity: str  # "error" or "warning"
    

class PlaneValidator:
    """
    Validates 4-Plane Model constraints.
    
    Used at:
    1. Chapter generation time
    2. Report compilation time
    3. API response time
    
    FAIL-CLOSED: Any violation prevents output.
    """
    
    # Minimum word counts per chapter type
    MIN_WORDS_CHAPTER_0 = 500
    MIN_WORDS_CHAPTERS_1_12 = 300
    
    # Patterns that indicate KPI content (belongs in Plane C, not B)
    KPI_PATTERNS = [
        r'^\s*[A-Z][a-z]+\s*:\s*[\d€%]+',  # "Price: €500.000"
        r'^\s*•\s*[A-Z][a-z]+\s*:\s*[\d€%]+',  # "• Area: 120m²"
        r'\d+\s*(?:m²|m2|euro|€|%)',  # Numbers with units
    ]
    
    # Patterns that indicate narrative content (belongs in Plane B, not C)
    NARRATIVE_PATTERNS = [
        r'[.!?]\s+[A-Z]',  # Multiple sentences
        r'\b(?:echter|maar|ondanks|hoewel|daarom|dus)\b',  # Dutch conjunctions
        r'\b(?:however|but|although|therefore|thus)\b',  # English conjunctions
    ]
    
    # Patterns that indicate preference content (belongs in Plane D)
    PREFERENCE_PATTERNS = [
        r'\b(?:Marcel|Petra)\b',
        r'\b(?:voorkeur|preference|comfort|strategie)\b',
        r'\b(?:match.?score|match.?index)\b',
    ]
    
    def validate_chapter(
        self, 
        chapter: ChapterPlaneComposition,
        registry_ids: Optional[List[str]] = None
    ) -> List[PlaneViolation]:
        """
        Validate a single chapter for plane violations.
        
        Args:
            chapter: The chapter to validate
            registry_ids: Optional list of valid registry IDs for fact-checking
            
        Returns:
            List of violations (empty if valid)
        """
        violations = []
        
        # 1. Check Plane B (Narrative) for KPIs and preferences
        violations.extend(self._validate_plane_b(chapter))
        
        # 2. Check Plane C (Facts) for narrative content
        violations.extend(self._validate_plane_c(chapter))
        
        # 3. Check Plane A (Visual) for text content
        violations.extend(self._validate_plane_a(chapter))
        
        # 4. Check Plane D (Preference) boundaries
        violations.extend(self._validate_plane_d(chapter))
        
        # 5. Check word count requirements
        violations.extend(self._validate_word_count(chapter))
        
        # 6. Check data provenance (if registry IDs provided)
        if registry_ids:
            violations.extend(self._validate_data_provenance(chapter, registry_ids))
        
        return violations
    
    def _validate_plane_b(self, chapter: ChapterPlaneComposition) -> List[PlaneViolation]:
        """Check Plane B for content that belongs elsewhere."""
        violations = []
        
        if chapter.plane_b.not_applicable:
            return violations
            
        text = chapter.plane_b.narrative_text
        
        # Check for KPI patterns (should be in Plane C)
        kpi_matches = []
        for pattern in self.KPI_PATTERNS:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            kpi_matches.extend(matches)
        
        if len(kpi_matches) > 3:
            violations.append(PlaneViolation(
                chapter_id=chapter.chapter_id,
                plane="B",
                violation_type=ViolationType.KPI_IN_NARRATIVE,
                description=f"Narrative contains {len(kpi_matches)} KPI patterns. "
                           f"Raw KPIs belong in Plane C. Examples: {kpi_matches[:3]}",
                severity="error"
            ))
        
        # Check for Marcel/Petra scoring (should be in Plane D)
        # Note: Mentioning them in context is OK, but scoring is not
        score_patterns = [
            r'Marcel.{0,20}(?:score|punt|%|\d+)',
            r'Petra.{0,20}(?:score|punt|%|\d+)',
            r'(?:score|punt|%).{0,20}(?:Marcel|Petra)',
        ]
        
        for pattern in score_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(PlaneViolation(
                    chapter_id=chapter.chapter_id,
                    plane="B",
                    violation_type=ViolationType.PREFERENCE_LEAK,
                    description=f"Narrative contains preference scoring pattern. "
                               f"Marcel/Petra scores belong in Plane D.",
                    severity="error"
                ))
                break
        
        return violations
    
    def _validate_plane_c(self, chapter: ChapterPlaneComposition) -> List[PlaneViolation]:
        """Check Plane C for content that belongs elsewhere."""
        violations = []
        
        if chapter.plane_c.not_applicable:
            return violations
        
        # Check KPI values for narrative content
        for kpi in chapter.plane_c.kpis:
            if isinstance(kpi.value, str):
                # Check for narrative patterns
                narrative_score = 0
                for pattern in self.NARRATIVE_PATTERNS:
                    if re.search(pattern, kpi.value, re.IGNORECASE):
                        narrative_score += 1
                
                if narrative_score >= 2 or len(kpi.value) > 200:
                    violations.append(PlaneViolation(
                        chapter_id=chapter.chapter_id,
                        plane="C",
                        violation_type=ViolationType.NARRATIVE_IN_FACTS,
                        description=f"KPI '{kpi.key}' contains narrative content. "
                                   f"Interpretation belongs in Plane B.",
                        severity="error"
                    ))
        
        return violations
    
    def _validate_plane_a(self, chapter: ChapterPlaneComposition) -> List[PlaneViolation]:
        """Check Plane A for text/narrative content."""
        violations = []
        
        if chapter.plane_a.not_applicable:
            return violations
        
        # Check chart titles for excessive text
        for chart in chapter.plane_a.charts:
            if len(chart.title) > 50:
                violations.append(PlaneViolation(
                    chapter_id=chapter.chapter_id,
                    plane="A",
                    violation_type=ViolationType.VISUAL_OUTSIDE_PLANE_A,
                    description=f"Chart title '{chart.title[:30]}...' is too long. "
                               f"Explanatory text belongs in Plane B.",
                    severity="error"
                ))
        
        return violations
    
    def _validate_plane_d(self, chapter: ChapterPlaneComposition) -> List[PlaneViolation]:
        """Check Plane D boundaries."""
        violations = []
        
        if chapter.plane_d.not_applicable:
            return violations
        
        # Check that joint synthesis is not too narrative
        if chapter.plane_d.joint_synthesis:
            text = chapter.plane_d.joint_synthesis
            
            # Check for multiple paragraphs (indicates narrative)
            if text.count('\n\n') > 1:
                violations.append(PlaneViolation(
                    chapter_id=chapter.chapter_id,
                    plane="D",
                    violation_type=ViolationType.CROSS_PLANE_CONTENT,
                    description="Joint synthesis contains multiple paragraphs. "
                               "Extended narrative belongs in Plane B.",
                    severity="error"
                ))
        
        return violations
    
    def _validate_word_count(self, chapter: ChapterPlaneComposition) -> List[PlaneViolation]:
        """Check narrative word count requirements."""
        violations = []
        
        if chapter.plane_b.not_applicable:
            return violations
        
        min_words = (
            self.MIN_WORDS_CHAPTER_0 if chapter.chapter_id == 0 
            else self.MIN_WORDS_CHAPTERS_1_12
        )
        
        if chapter.plane_b.word_count < min_words:
            violations.append(PlaneViolation(
                chapter_id=chapter.chapter_id,
                plane="B",
                violation_type=ViolationType.INSUFFICIENT_NARRATIVE,
                description=f"Narrative has {chapter.plane_b.word_count} words, "
                           f"minimum is {min_words} for chapter {chapter.chapter_id}.",
                severity="error"
            ))
        
        return violations
    
    def _validate_data_provenance(
        self, 
        chapter: ChapterPlaneComposition, 
        registry_ids: List[str]
    ) -> List[PlaneViolation]:
        """Check that all visual data comes from registry."""
        violations = []
        
        if chapter.plane_a.not_applicable:
            return violations
        
        # Check that data source IDs are valid
        for source_id in chapter.plane_a.data_source_ids:
            if source_id not in registry_ids:
                violations.append(PlaneViolation(
                    chapter_id=chapter.chapter_id,
                    plane="A",
                    violation_type=ViolationType.AI_INVENTED_DATA,
                    description=f"Visual data source '{source_id}' not found in registry. "
                               f"AI may not invent data for visualizations.",
                    severity="error"
                ))
        
        return violations
    
    def enforce_or_reject(
        self, 
        chapter: ChapterPlaneComposition,
        registry_ids: Optional[List[str]] = None
    ):
        """
        Validate and raise error if violations exist.
        
        Raises:
            PlaneViolationError: If any violations are detected
        """
        violations = self.validate_chapter(chapter, registry_ids)
        errors = [v for v in violations if v.severity == "error"]
        
        if errors:
            violation_details = "\n".join([
                f"  [{v.plane}] {v.violation_type.value}: {v.description}"
                for v in errors
            ])
            
            raise PlaneViolationError(
                source_plane=errors[0].plane,
                violation_type=errors[0].violation_type.value,
                details=f"Chapter {chapter.chapter_id} has {len(errors)} violation(s):\n{violation_details}"
            )


def validate_plane_content(
    content_type: str,
    content: Any,
    target_plane: str
) -> Tuple[bool, Optional[str]]:
    """
    Quick validation check for content going to a specific plane.
    
    Args:
        content_type: Type of content ("narrative", "kpi", "visual", "preference")
        content: The content to validate
        target_plane: The target plane ("A", "B", "C", "D")
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    
    # Map content types to allowed planes
    allowed_planes = {
        "narrative": ["B"],
        "kpi": ["C"],
        "visual": ["A"],
        "preference": ["D"],
        "chart": ["A"],
        "table": ["C"],
        "comparison": ["D"],
    }
    
    if content_type in allowed_planes:
        if target_plane not in allowed_planes[content_type]:
            return False, (
                f"Content type '{content_type}' is not allowed in Plane {target_plane}. "
                f"Allowed planes: {allowed_planes[content_type]}"
            )
    
    return True, None


# Convenience function for pipeline integration
def create_validated_chapter(
    chapter_id: int,
    chapter_title: str,
    plane_a: PlaneAVisualModel,
    plane_b: PlaneBNarrativeModel,
    plane_c: PlaneCFactModel,
    plane_d: PlaneDPreferenceModel,
    plane_a2: Optional[PlaneA2SynthVisualModel] = None,
    registry_ids: Optional[List[str]] = None
) -> ChapterPlaneComposition:
    """
    Create a chapter with full validation.
    
    Args:
        chapter_id: Chapter number (0-12)
        chapter_title: Title of the chapter
        plane_a: Visual Intelligence plane (A1 - deterministic charts)
        plane_b: Narrative Reasoning plane
        plane_c: Factual Anchor plane
        plane_d: Human Preference plane
        plane_a2: Synthesized Visual Intelligence plane (A2 - AI-generated infographics)
        registry_ids: Optional list of valid registry IDs for validation
    
    Returns:
        ChapterPlaneComposition with all planes validated
    
    Raises:
        PlaneViolationError: If any plane constraints are violated
    """
    chapter = ChapterPlaneComposition(
        chapter_id=chapter_id,
        chapter_title=chapter_title,
        plane_a=plane_a,
        plane_a2=plane_a2,
        plane_b=plane_b,
        plane_c=plane_c,
        plane_d=plane_d
    )
    
    validator = PlaneValidator()
    validator.enforce_or_reject(chapter, registry_ids)
    
    return chapter

