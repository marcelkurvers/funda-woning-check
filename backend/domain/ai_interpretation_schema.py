"""
AI Interpretation Schema - MANDATED OUTPUT CONTRACT

CORE INVARIANT (ABSOLUTE):
    If a factual value appears in a report, it MUST come from the CanonicalRegistry.
    AI must never output factual values directly.

This schema defines the ONLY structures that AI may output.
Any output not conforming to this schema is REJECTED.

AI MAY OUTPUT ONLY:
    - Interpretations (assessments of registry values)
    - Risks (impact assessments referencing registry IDs)
    - Preference Matches (how registry values match user preferences)
    - Uncertainties (flagging missing or uncertain registry entries)

AI MAY NEVER OUTPUT:
    - Numbers (any numeric literal)
    - Computed values
    - New facts
    - Derived metrics
    - Fallback estimates
    - Free-form factual statements

If this contract is violated, the pipeline MUST fail.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS - CONTROLLED VOCABULARIES
# =============================================================================

class Assessment(str, Enum):
    """Assessment levels for interpretations."""
    HIGH = "high"
    AVERAGE = "average"
    LOW = "low"
    EXCELLENT = "excellent"
    POOR = "poor"
    UNKNOWN = "unknown"


class Impact(str, Enum):
    """Impact levels for risks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Fit(str, Enum):
    """Fit levels for preference matching."""
    GOOD = "good"
    NEUTRAL = "neutral"
    POOR = "poor"


class UncertaintyReason(str, Enum):
    """Reasons for uncertainty."""
    MISSING = "missing"
    UNCERTAIN = "uncertain"
    CONFLICTING = "conflicting"
    OUTDATED = "outdated"


# =============================================================================
# INTERPRETATION SCHEMA STRUCTURES
# =============================================================================

@dataclass
class Interpretation:
    """
    An AI interpretation of a registry entry.
    
    The AI assesses a fact but NEVER states the fact itself.
    The reasoning must be interpretive text WITHOUT numbers or facts.
    """
    registry_id: str
    assessment: Assessment
    reasoning: str  # MUST NOT contain numbers or factual statements
    
    def validate(self) -> List[str]:
        """Validate this interpretation."""
        errors = []
        
        # Check for numeric literals in reasoning
        if _contains_numeric_literal(self.reasoning):
            errors.append(
                f"FATAL: Interpretation for '{self.registry_id}' contains numeric literal. "
                f"AI may not state facts. Reasoning: '{self.reasoning[:100]}...'"
            )
        
        # Check assessment is valid
        if not isinstance(self.assessment, Assessment):
            try:
                self.assessment = Assessment(self.assessment)
            except ValueError:
                errors.append(
                    f"Invalid assessment '{self.assessment}' for '{self.registry_id}'. "
                    f"Must be one of: {[a.value for a in Assessment]}"
                )
        
        return errors


@dataclass
class Risk:
    """
    An AI-identified risk related to a registry entry.
    
    The AI explains the impact but NEVER restates the underlying fact.
    """
    registry_id: str
    impact: Impact
    explanation: str  # MUST NOT contain numbers or factual statements
    
    def validate(self) -> List[str]:
        """Validate this risk."""
        errors = []
        
        if _contains_numeric_literal(self.explanation):
            errors.append(
                f"FATAL: Risk explanation for '{self.registry_id}' contains numeric literal. "
                f"Explanation: '{self.explanation[:100]}...'"
            )
        
        if not isinstance(self.impact, Impact):
            try:
                self.impact = Impact(self.impact)
            except ValueError:
                errors.append(
                    f"Invalid impact '{self.impact}' for '{self.registry_id}'. "
                    f"Must be one of: {[i.value for i in Impact]}"
                )
        
        return errors


@dataclass
class PreferenceMatch:
    """
    An AI assessment of how a registry value matches user preferences.
    
    The AI assesses fit but NEVER restates the value or preference.
    """
    preference_id: str
    registry_id: str
    fit: Fit
    explanation: str = ""  # Optional interpretive text
    
    def validate(self) -> List[str]:
        """Validate this preference match."""
        errors = []
        
        if self.explanation and _contains_numeric_literal(self.explanation):
            errors.append(
                f"FATAL: PreferenceMatch explanation contains numeric literal. "
                f"Explanation: '{self.explanation[:100]}...'"
            )
        
        if not isinstance(self.fit, Fit):
            try:
                self.fit = Fit(self.fit)
            except ValueError:
                errors.append(
                    f"Invalid fit '{self.fit}' for preference '{self.preference_id}'. "
                    f"Must be one of: {[f.value for f in Fit]}"
                )
        
        return errors


@dataclass
class Uncertainty:
    """
    An AI-flagged uncertainty about a registry entry.
    
    The AI flags that data is missing or uncertain.
    This is meta-information, not factual assertion.
    """
    registry_id: str
    reason: UncertaintyReason
    
    def validate(self) -> List[str]:
        """Validate this uncertainty."""
        errors = []
        
        if not isinstance(self.reason, UncertaintyReason):
            try:
                self.reason = UncertaintyReason(self.reason)
            except ValueError:
                errors.append(
                    f"Invalid uncertainty reason '{self.reason}' for '{self.registry_id}'. "
                    f"Must be one of: {[r.value for r in UncertaintyReason]}"
                )
        
        return errors


@dataclass
class AIInterpretationOutput:
    """
    The complete AI interpretation output structure.
    
    This is the ONLY structure AI may produce.
    If AI output does not conform to this schema, it is REJECTED.
    """
    chapter_id: int
    interpretations: List[Interpretation] = field(default_factory=list)
    risks: List[Risk] = field(default_factory=list)
    preference_matches: List[PreferenceMatch] = field(default_factory=list)
    uncertainties: List[Uncertainty] = field(default_factory=list)
    
    # Narrative sections - interpretive text only
    title: str = ""
    summary: str = ""  # Brief interpretive summary, NO FACTS
    detailed_analysis: str = ""  # Extended interpretive text, NO FACTS
    
    # Provenance metadata
    confidence: str = "medium"
    provider: str = "unknown"
    model: str = "unknown"
    
    def validate(self, registry_ids: set) -> List[str]:
        """
        Validate the complete output against the schema and registry.
        
        Args:
            registry_ids: Set of valid registry IDs
            
        Returns:
            List of validation errors. Empty = valid.
        """
        errors = []
        
        # Validate all interpretations
        for interp in self.interpretations:
            errors.extend(interp.validate())
            if interp.registry_id not in registry_ids:
                errors.append(
                    f"FATAL: Interpretation references unknown registry_id '{interp.registry_id}'"
                )
        
        # Validate all risks
        for risk in self.risks:
            errors.extend(risk.validate())
            if risk.registry_id not in registry_ids:
                errors.append(
                    f"FATAL: Risk references unknown registry_id '{risk.registry_id}'"
                )
        
        # Validate all preference matches
        for pm in self.preference_matches:
            errors.extend(pm.validate())
            if pm.registry_id not in registry_ids:
                errors.append(
                    f"FATAL: PreferenceMatch references unknown registry_id '{pm.registry_id}'"
                )
        
        # Validate all uncertainties
        for unc in self.uncertainties:
            errors.extend(unc.validate())
            # Note: uncertainties may reference IDs that are missing from registry
            # That's the point - they flag missing data
        
        # Validate narrative sections don't contain facts
        if _contains_numeric_literal(self.summary):
            errors.append(
                f"FATAL: AI summary contains numeric literal. "
                f"Summary: '{self.summary[:100]}...'"
            )
        
        if _contains_numeric_literal(self.detailed_analysis):
            errors.append(
                f"FATAL: AI detailed_analysis contains numeric literal. "
                f"Detected in first 500 chars."
            )
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "chapter_id": self.chapter_id,
            "interpretations": [
                {
                    "registry_id": i.registry_id,
                    "assessment": i.assessment.value if isinstance(i.assessment, Assessment) else i.assessment,
                    "reasoning": i.reasoning
                }
                for i in self.interpretations
            ],
            "risks": [
                {
                    "registry_id": r.registry_id,
                    "impact": r.impact.value if isinstance(r.impact, Impact) else r.impact,
                    "explanation": r.explanation
                }
                for r in self.risks
            ],
            "preference_matches": [
                {
                    "preference_id": pm.preference_id,
                    "registry_id": pm.registry_id,
                    "fit": pm.fit.value if isinstance(pm.fit, Fit) else pm.fit,
                    "explanation": pm.explanation
                }
                for pm in self.preference_matches
            ],
            "uncertainties": [
                {
                    "registry_id": u.registry_id,
                    "reason": u.reason.value if isinstance(u.reason, UncertaintyReason) else u.reason
                }
                for u in self.uncertainties
            ],
            "title": self.title,
            "summary": self.summary,
            "detailed_analysis": self.detailed_analysis,
            "confidence": self.confidence,
            "provider": self.provider,
            "model": self.model
        }


# =============================================================================
# NUMERIC DETECTION - THE CORE ENFORCEMENT MECHANISM
# =============================================================================

# Pattern to detect numeric literals in text
# Matches: 500000, 500.000, €500.000, 120m², 85%, etc.
NUMERIC_PATTERN = re.compile(
    r"""
    (?:
        # Currency amounts: €500.000, $1,234.56
        [€$£]\s*\d[\d.,]*\d |
        
        # Percentages: 85%, 12.5%
        \d+(?:[.,]\d+)?\s*% |
        
        # Measurements: 120m², 45m2, 150 m²
        \d+(?:[.,]\d+)?\s*m[²2³3]? |
        
        # Years: 1920, 2024 (4-digit numbers)
        (?<!\w)\d{4}(?!\w) |
        
        # Large numbers: 500000, 500.000, 1,234,567
        (?<!\w)\d{1,3}(?:[.,]\d{3})+(?!\w) |
        
        # Standalone numbers >= 100 (to avoid false positives like "2 bedrooms")
        (?<!\w)\d{3,}(?!\w)
    )
    """,
    re.VERBOSE
)

# Exceptions - numbers that are allowed in interpretive text
ALLOWED_NUMERIC_PATTERNS = [
    r"Chapter \d+",  # "Chapter 5"
    r"hoofdstuk \d+",  # Dutch "Chapter 5"
    r"stap \d+",  # "step 3"
    r"punt \d+",  # "point 2"
    r"#\d+",  # "#1 priority"
]


def _contains_numeric_literal(text: str) -> bool:
    """
    Check if text contains a numeric literal that should not be in AI output.
    
    This is the core enforcement mechanism. AI may not output facts.
    
    Args:
        text: The text to check
        
    Returns:
        True if forbidden numeric literals found
    """
    if not text:
        return False
    
    # First, mask allowed patterns
    masked_text = text
    for pattern in ALLOWED_NUMERIC_PATTERNS:
        masked_text = re.sub(pattern, "___ALLOWED___", masked_text, flags=re.IGNORECASE)
    
    # Now check for forbidden numerics
    return bool(NUMERIC_PATTERN.search(masked_text))


# =============================================================================
# PARSING - CONVERT RAW AI OUTPUT TO SCHEMA
# =============================================================================

def parse_ai_output(raw_output: Dict[str, Any], chapter_id: int) -> AIInterpretationOutput:
    """
    Parse raw AI output into the interpretation schema.
    
    This converts freeform AI output into the mandated structure.
    If the output cannot be parsed, returns empty interpretation.
    
    Args:
        raw_output: Raw dictionary from AI
        chapter_id: The chapter this output is for
        
    Returns:
        AIInterpretationOutput instance
    """
    result = AIInterpretationOutput(chapter_id=chapter_id)
    
    # Parse interpretations
    if "interpretations" in raw_output:
        for item in raw_output.get("interpretations", []):
            if isinstance(item, dict):
                try:
                    result.interpretations.append(Interpretation(
                        registry_id=item.get("registry_id", ""),
                        assessment=Assessment(item.get("assessment", "unknown")),
                        reasoning=item.get("reasoning", "")
                    ))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Failed to parse interpretation: {e}")
    
    # Parse risks
    if "risks" in raw_output:
        for item in raw_output.get("risks", []):
            if isinstance(item, dict):
                try:
                    result.risks.append(Risk(
                        registry_id=item.get("registry_id", ""),
                        impact=Impact(item.get("impact", "medium")),
                        explanation=item.get("explanation", "")
                    ))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Failed to parse risk: {e}")
    
    # Parse preference matches
    if "preference_matches" in raw_output:
        for item in raw_output.get("preference_matches", []):
            if isinstance(item, dict):
                try:
                    result.preference_matches.append(PreferenceMatch(
                        preference_id=item.get("preference_id", ""),
                        registry_id=item.get("registry_id", ""),
                        fit=Fit(item.get("fit", "neutral")),
                        explanation=item.get("explanation", "")
                    ))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Failed to parse preference match: {e}")
    
    # Parse uncertainties
    if "uncertainties" in raw_output:
        for item in raw_output.get("uncertainties", []):
            if isinstance(item, dict):
                try:
                    result.uncertainties.append(Uncertainty(
                        registry_id=item.get("registry_id", ""),
                        reason=UncertaintyReason(item.get("reason", "uncertain"))
                    ))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Failed to parse uncertainty: {e}")
    
    # Parse narrative sections
    result.title = raw_output.get("title", "")
    result.summary = raw_output.get("summary", raw_output.get("intro", ""))
    result.detailed_analysis = raw_output.get("detailed_analysis", raw_output.get("main_analysis", ""))
    
    # Parse provenance
    prov = raw_output.get("_provenance", {})
    result.confidence = prov.get("confidence", "medium")
    result.provider = prov.get("provider", "unknown")
    result.model = prov.get("model", "unknown")
    
    return result


# =============================================================================
# VALIDATION ENTRY POINT
# =============================================================================

class AIOutputSchemaViolation(Exception):
    """Raised when AI output violates the interpretation schema."""
    def __init__(self, chapter_id: int, violations: List[str]):
        self.chapter_id = chapter_id
        self.violations = violations
        super().__init__(
            f"FATAL: AI output for Chapter {chapter_id} violates interpretation schema. "
            f"Violations: {violations}"
        )


def validate_ai_interpretation_output(
    output: AIInterpretationOutput,
    registry_ids: set,
    strict: bool = True
) -> List[str]:
    """
    Validate AI interpretation output against the schema.
    
    Args:
        output: The parsed AI interpretation output
        registry_ids: Set of valid registry IDs
        strict: If True, raise exception on violations
        
    Returns:
        List of validation errors
        
    Raises:
        AIOutputSchemaViolation: If strict=True and violations found
    """
    errors = output.validate(registry_ids)
    
    if errors and strict:
        raise AIOutputSchemaViolation(output.chapter_id, errors)
    
    return errors
