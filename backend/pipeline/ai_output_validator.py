"""
AI Output Validator - FAIL-CLOSED Schema Enforcement

This module validates AI output IMMEDIATELY after generation,
before any further processing.

LAWS ENFORCED:
    LAW A — AI Output Must Conform to Interpretation Schema
        AI output may ONLY contain:
        - Interpretations (assessments of registry values)
        - Risks (impact assessments)
        - Preference matches
        - Uncertainties
        - Narrative text WITHOUT factual values
        
    LAW B — AI Output Must Be a Subset of Allowed Keys
        AI output may only contain keys that are in the allowed schema.
        
    LAW C — AI May Not Output Numeric Literals or Facts
        Any text containing numbers, prices, measurements, or years
        is REJECTED as a schema violation.

CORE INVARIANT:
    If a factual value appears in AI output, the pipeline MUST fail.
    This is not advisory - this is a hard structural enforcement.
"""

import logging
import re
from typing import Dict, Any, Set, List
from dataclasses import dataclass

from backend.domain.chapter_variables import get_chapter_variables
from backend.domain.ai_interpretation_schema import (
    AIInterpretationOutput,
    parse_ai_output,
    validate_ai_interpretation_output,
    AIOutputSchemaViolation,
    _contains_numeric_literal
)

logger = logging.getLogger(__name__)


class AIOutputViolation(Exception):
    """Raised when AI output violates the interpretation schema."""
    def __init__(self, chapter_id: int, violations: List[str]):
        self.chapter_id = chapter_id
        self.violations = violations
        super().__init__(
            f"FATAL: AI output for Chapter {chapter_id} violates schema: {violations}"
        )


@dataclass
class OutputValidationResult:
    """Result of AI output validation."""
    valid: bool
    violations: List[str]
    stripped_keys: List[str]  # Keys removed during sanitization (only in non-strict)
    numeric_violations: List[str]  # Text fields containing numbers
    

# =============================================================================
# ALLOWED KEYS REGISTRY  
# =============================================================================

# Top-level keys that are ALWAYS allowed in AI output
ALLOWED_TOP_LEVEL_KEYS: Set[str] = {
    # New interpretation schema keys
    'interpretations',
    'risks',
    'preference_matches',
    'uncertainties',
    
    # Narrative structure (text only - validated for numeric content)
    'title',
    'intro',
    'summary',
    'main_analysis',
    'detailed_analysis',
    'conclusion',
    'interpretation',
    
    # Trust/enrichment fields
    'variables',
    'comparison',
    'strengths',
    'advice',
    
    # Metadata
    'metadata',
    '_provenance',
    'confidence',
    'provider',
    'model',
    
    # Chapter-specific allowed fields
    'property_core',  # Only for Chapter 0
    'sidebar_items',
    'metrics',
}

# Keys allowed in the 'variables' dict for ALL chapters
ALLOWED_META_VARIABLE_KEYS: Set[str] = {
    'status',           # Verification status
    'confidence',       # Confidence level
    'object_focus',     # Current focus point
    'vertrouwen',       # Trust level (Dutch)
    'reasoning',        # Explanation of inference
    'preference_match', # M&P preference matching
}


# =============================================================================
# NUMERIC DETECTION IN NARRATIVE FIELDS
# =============================================================================

# Fields that must NOT contain numeric literals (facts)
NARRATIVE_FIELDS = [
    'intro',
    'summary',
    'main_analysis', 
    'detailed_analysis',
    'conclusion',
    'interpretation',
]


def detect_numeric_violations(ai_output: Dict[str, Any]) -> List[str]:
    """
    Detect numeric literals in narrative fields.
    
    CORE INVARIANT: AI may not output factual values.
    This function detects violations of that rule.
    
    Returns:
        List of violation descriptions
    """
    violations = []
    
    for field in NARRATIVE_FIELDS:
        value = ai_output.get(field, '')
        if isinstance(value, str) and _contains_numeric_literal(value):
            violations.append(
                f"FACT_IN_AI_OUTPUT: Field '{field}' contains numeric literal. "
                f"AI may not output facts. Preview: '{value[:100]}...'"
            )
    
    # Check nested comparison texts
    comparison = ai_output.get('comparison', {})
    if isinstance(comparison, dict):
        for key in ['marcel', 'petra', 'combined_advice']:
            value = comparison.get(key, '')
            if isinstance(value, str) and _contains_numeric_literal(value):
                violations.append(
                    f"FACT_IN_AI_OUTPUT: comparison.{key} contains numeric literal. "
                    f"Preview: '{value[:100]}...'"
                )
    
    # Check advice and strengths lists for numeric content
    for list_field in ['advice', 'strengths']:
        items = ai_output.get(list_field, [])
        if isinstance(items, list):
            for i, item in enumerate(items):
                text = str(item)
                if _contains_numeric_literal(text):
                    violations.append(
                        f"FACT_IN_AI_OUTPUT: {list_field}[{i}] contains numeric literal. "
                        f"Preview: '{text[:100]}...'"
                    )
    
    return violations


# =============================================================================
# CORE VALIDATION FUNCTION
# =============================================================================

def validate_ai_output(
    chapter_id: int,
    ai_output: Dict[str, Any],
    registry_ids: Set[str] = None,
    strict: bool = True
) -> OutputValidationResult:
    """
    Validate AI output against the interpretation schema.
    
    FAIL-CLOSED BEHAVIOR:
        - Unknown keys are violations
        - Numeric literals in text are violations  
        - References to unknown registry IDs are violations
        - In strict mode, any violation raises exception
    
    Args:
        chapter_id: The chapter number (0-13)
        ai_output: Raw output from AI provider
        registry_ids: Set of valid registry IDs (for reference checking)
        strict: If True, any violation is fatal. If False, strip and warn.
        
    Returns:
        OutputValidationResult with validation status
        
    Raises:
        AIOutputViolation: If strict=True and violations found
    """
    violations = []
    stripped_keys = []
    numeric_violations = []
    
    if not isinstance(ai_output, dict):
        violations.append(f"AI output is not a dict: {type(ai_output)}")
        if strict:
            raise AIOutputViolation(chapter_id, violations)
        return OutputValidationResult(
            valid=False, 
            violations=violations, 
            stripped_keys=[], 
            numeric_violations=[]
        )
    
    # 1. Check top-level keys
    chapter_owned_vars = get_chapter_variables(chapter_id)
    
    for key in list(ai_output.keys()):
        if key not in ALLOWED_TOP_LEVEL_KEYS and key not in chapter_owned_vars:
            violations.append(f"Unknown top-level key: '{key}'")
            if not strict:
                stripped_keys.append(key)
                del ai_output[key]
    
    # 2. Check 'variables' dict if present
    if 'variables' in ai_output and isinstance(ai_output['variables'], dict):
        variables = ai_output['variables']
        allowed_for_chapter = chapter_owned_vars | ALLOWED_META_VARIABLE_KEYS
        
        for var_key in list(variables.keys()):
            if var_key not in allowed_for_chapter:
                violations.append(f"Unknown variable key in chapter {chapter_id}: '{var_key}'")
                if not strict:
                    stripped_keys.append(f"variables.{var_key}")
                    del variables[var_key]
    
    # 3. CRITICAL: Check for numeric literals in narrative fields
    numeric_violations = detect_numeric_violations(ai_output)
    violations.extend(numeric_violations)
    
    # 4. If registry_ids provided, validate interpretation schema references
    if registry_ids:
        # Parse into schema and validate
        parsed = parse_ai_output(ai_output, chapter_id)
        schema_errors = parsed.validate(registry_ids)
        violations.extend(schema_errors)
    
    # 5. Raise if strict and violations found
    if strict and violations:
        logger.error(f"AI Output Validation FAILED for Chapter {chapter_id}: {violations}")
        raise AIOutputViolation(chapter_id, violations)
    
    # 6. Log stripped keys if non-strict
    if stripped_keys:
        logger.warning(
            f"AI Output Validation: Stripped unauthorized keys from Chapter {chapter_id}: {stripped_keys}"
        )
    
    return OutputValidationResult(
        valid=len(violations) == 0,
        violations=violations,
        stripped_keys=stripped_keys,
        numeric_violations=numeric_violations
    )


def sanitize_and_validate_ai_output(
    chapter_id: int,
    ai_output: Dict[str, Any],
    registry_ids: Set[str] = None
) -> Dict[str, Any]:
    """
    Sanitize and validate AI output - SINGLE ENTRY POINT.
    
    This function MUST be called immediately after receiving AI output,
    before any further processing.
    
    FAIL-CLOSED: 
        - Unknown keys cause failure
        - Numeric literals in text cause failure
        - References to unknown registry IDs cause failure
    
    Args:
        chapter_id: The chapter number
        ai_output: Raw output from AI
        registry_ids: Set of valid registry IDs
        
    Returns:
        Validated and sanitized output
        
    Raises:
        AIOutputViolation: If output violates schema
    """
    if ai_output is None:
        # AI returned nothing - this is ALLOWED per LAW C
        # We return empty structure, NOT synthetic variables
        return {}
    
    # Validate with strict mode
    result = validate_ai_output(
        chapter_id, 
        ai_output, 
        registry_ids=registry_ids,
        strict=True
    )
    
    # Remove any keys that snuck through
    if not result.valid:
        raise AIOutputViolation(chapter_id, result.violations)
    
    return ai_output


# =============================================================================
# ENFORCEMENT: Reject Synthetic Variable Injection
# =============================================================================

def ensure_no_synthetic_injection(output: Dict[str, Any]) -> None:
    """
    Ensure no synthetic/default variables were injected.
    
    LAW C: If AI returns no variables, output contains no variables.
    
    This is called AFTER AI generation to ensure the trust pipeline
    didn't inject fake variables.
    
    Raises:
        AIOutputViolation: If synthetic variables detected
    """
    # Known synthetic variable signatures that should NOT exist
    SYNTHETIC_SIGNATURES = [
        ("object_focus", "Geprioriteerd focuspunt"),  # Injected default
        ("vertrouwen", "Gebaseerd op geverifieerde brongegevens"),  # Injected default
    ]
    
    variables = output.get('variables', {})
    if not isinstance(variables, dict):
        return
    
    for var_key, signature in SYNTHETIC_SIGNATURES:
        if var_key in variables:
            var_value = variables[var_key]
            if isinstance(var_value, dict) and signature in str(var_value.get('reasoning', '')):
                raise AIOutputViolation(
                    chapter_id=-1,  # Unknown chapter at this point
                    violations=[
                        f"SYNTHETIC INJECTION DETECTED: Variable '{var_key}' with signature '{signature}' "
                        f"appears to be injected rather than AI-generated. INVARIANT VIOLATION."
                    ]
                )


# =============================================================================
# TRANSFORM: Convert Legacy AI Output to Interpretation Schema
# =============================================================================

def transform_to_interpretation_schema(
    chapter_id: int,
    ai_output: Dict[str, Any],
    registry_ids: Set[str]
) -> AIInterpretationOutput:
    """
    Transform legacy AI output to the new interpretation schema.
    
    This is a bridge function during migration.
    Eventually, AI should output in interpretation schema directly.
    
    Args:
        chapter_id: The chapter number
        ai_output: Raw output from AI (legacy format)
        registry_ids: Set of valid registry IDs
        
    Returns:
        AIInterpretationOutput instance
    """
    return parse_ai_output(ai_output, chapter_id)
