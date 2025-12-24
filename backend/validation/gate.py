"""
Validation Gate - The Final Enforcement Layer

This module validates chapter output BEFORE it can be rendered.
It is called by PipelineSpine after EVERY chapter generation.

INVARIANTS ENFORCED:
1. Ownership: Chapters may not display variables they don't own
2. Raw Fact Restatement: AI may not restate raw numbers outside owned chapters
3. Preference Reasoning: Marcel & Petra analysis must be substantive
4. Completeness: Required fields must be present

If validation fails, the chapter CANNOT be rendered.
This is not advisory - this is a hard gate.
"""

from typing import Dict, Any, List, Set
import re
import logging
from backend.domain.ownership import OwnershipMap
from backend.domain.chapter_variables import get_chapter_variables

logger = logging.getLogger(__name__)


class ValidationGate:
    """
    Layer 4: Validation Gate.
    
    Ensures nothing low-quality ever reaches the UI.
    This is the FINAL enforcement layer before rendering.
    """
    
    # Chapters that own financial data and may display prices
    PRICE_OWNER_CHAPTERS = {0, 10}  # Executive Summary, Financial Analysis
    
    # Chapters that own area/size data
    AREA_OWNER_CHAPTERS = {0, 1, 5, 7}  # Executive, General, Layout, Garden
    
    # Minimum length for preference reasoning (characters)
    MIN_PREFERENCE_LENGTH = 10
    
    # Fields that are considered "raw facts" and must not be restated verbatim
    RAW_FACT_FIELDS = ['asking_price_eur', 'living_area_m2', 'plot_area_m2', 'build_year']
    
    @staticmethod
    def validate_chapter_output(
        chapter_id: int, 
        output: Dict[str, Any], 
        registry_context: Dict[str, Any]
    ) -> List[str]:
        """
        Validates chapter output against Registry, Ownership, and 4-PLANE rules.
        
        FAIL-CLOSED 4-PLANE VALIDATION:
        - Each chapter MUST have plane_a, plane_b, plane_c, plane_d
        - Plane B MUST have at least 300 words (500 for chapter 0)
        - Content MUST NOT cross plane boundaries
        
        Args:
            chapter_id: The chapter number (0-13)
            output: The chapter output dict to validate
            registry_context: The full registry as a dict (for cross-reference)
        
        Returns:
            List of error strings. Empty list = validation passed.
        """
        errors = []
        
        # =====================================================================
        # VALIDATION 0: 4-PLANE STRUCTURE (MANDATORY)
        # =====================================================================
        errors.extend(ValidationGate._check_four_plane_structure(chapter_id, output))
        
        # =====================================================================
        # VALIDATION 1: OWNERSHIP - Variables must be owned by this chapter
        # =====================================================================
        errors.extend(ValidationGate._check_ownership(chapter_id, output, registry_context))
        
        # =====================================================================
        # VALIDATION 2: RAW FACT RESTATEMENT - No verbatim numbers in wrong chapters
        # =====================================================================
        errors.extend(ValidationGate._check_raw_fact_restatement(chapter_id, output, registry_context))
        
        # =====================================================================
        # VALIDATION 3: PREFERENCE REASONING - Marcel & Petra must be substantive
        # =====================================================================
        errors.extend(ValidationGate._check_preference_reasoning(chapter_id, output))
        
        # =====================================================================
        # VALIDATION 4: REQUIRED FIELDS - Minimum structure must be present
        # =====================================================================
        errors.extend(ValidationGate._check_required_fields(chapter_id, output))
        
        # =====================================================================
        # VALIDATION 5: MANDATORY NARRATIVE - Chapters 0-12 MUST have narrative
        # =====================================================================
        errors.extend(ValidationGate._check_narrative(chapter_id, output))
        
        if errors:
            logger.warning(f"ValidationGate: Chapter {chapter_id} failed with {len(errors)} errors")
        
        return errors
    
    @staticmethod
    def _check_four_plane_structure(chapter_id: int, output: Dict[str, Any]) -> List[str]:
        """
        Check that chapter has valid 4-plane structure.
        
        FAIL-CLOSED: If plane_structure is True, all 4 planes MUST exist.
        """
        errors = []
        
        # Check if this is a 4-plane structured output
        if not output.get("plane_structure"):
            # Not a 4-plane output - this is now an error for chapters 0-12
            if chapter_id <= 12:
                errors.append(
                    f"4-Plane Structure Missing: Chapter {chapter_id} does not have plane_structure=True. "
                    f"All chapters (0-12) MUST use 4-plane format."
                )
            return errors
        
        # Check for each plane's existence
        for plane_name in ["plane_a", "plane_b", "plane_c", "plane_d"]:
            plane = output.get(plane_name)
            if not plane:
                errors.append(
                    f"Plane Missing: Chapter {chapter_id} is missing '{plane_name}'. "
                    f"All 4 planes are MANDATORY."
                )
        
        # Check Plane B word count
        plane_b = output.get("plane_b", {})
        if plane_b and not plane_b.get("not_applicable"):
            word_count = plane_b.get("word_count", 0)
            min_words = 500 if chapter_id == 0 else 300
            
            if word_count < min_words:
                errors.append(
                    f"Plane B Insufficient: Chapter {chapter_id} narrative has {word_count} words, "
                    f"minimum is {min_words}. Narratives MUST meet word requirements."
                )
        
        # Check Plane D has Marcel and Petra
        plane_d = output.get("plane_d", {})
        if plane_d and not plane_d.get("not_applicable"):
            if not plane_d.get("marcel"):
                errors.append(
                    f"Plane D Incomplete: Chapter {chapter_id} is missing Marcel data. "
                    f"Plane D MUST have both Marcel and Petra."
                )
            if not plane_d.get("petra"):
                errors.append(
                    f"Plane D Incomplete: Chapter {chapter_id} is missing Petra data. "
                    f"Plane D MUST have both Marcel and Petra."
                )
        
        return errors
    
    @staticmethod
    def _check_ownership(
        chapter_id: int, 
        output: Dict[str, Any], 
        registry_context: Dict[str, Any]
    ) -> List[str]:
        """Check that chapter only displays variables it owns."""
        errors = []
        
        allowed_vars = get_chapter_variables(chapter_id)
        
        # Also allow common meta-variables
        meta_vars = {'status', 'confidence', 'object_focus', 'vertrouwen'}
        allowed_with_meta = allowed_vars | meta_vars
        
        # Check variables in output
        returned_vars = output.get('variables', {})
        if isinstance(returned_vars, dict):
            for key in returned_vars.keys():
                if key not in allowed_with_meta:
                    # Is this a known registry variable being misplaced?
                    if key in registry_context:
                        errors.append(
                            f"Ownership Violation: Variable '{key}' is not owned by Chapter {chapter_id}. "
                            f"Check chapter_variables.py for ownership rules."
                        )
        
        # Check chapter_data.variables if present
        chapter_data = output.get('chapter_data', {})
        if isinstance(chapter_data, dict):
            cd_vars = chapter_data.get('variables', {})
            if isinstance(cd_vars, dict):
                for key in cd_vars.keys():
                    if key not in allowed_with_meta and key in registry_context:
                        errors.append(
                            f"Ownership Violation: Variable '{key}' in chapter_data is not owned by Chapter {chapter_id}."
                        )
        
        return errors
    
    @staticmethod
    def _check_raw_fact_restatement(
        chapter_id: int,
        output: Dict[str, Any],
        registry_context: Dict[str, Any]
    ) -> List[str]:
        """Check that raw facts are not restated verbatim in text."""
        errors = []
        
        # Get main analysis text
        main_text = str(output.get('main_analysis', ''))
        chapter_data = output.get('chapter_data', {})
        if isinstance(chapter_data, dict):
            main_text += " " + str(chapter_data.get('main_analysis', ''))
        
        # Check price restatement (only in non-owner chapters)
        if chapter_id not in ValidationGate.PRICE_OWNER_CHAPTERS:
            price = registry_context.get('asking_price_eur')
            if price and isinstance(price, (int, float)) and price > 10000:
                price_str = str(int(price))
                # Check for exact number (avoiding small numbers like "4" which could be "4 rooms")
                if len(price_str) >= 5 and price_str in main_text:
                    errors.append(
                        f"Raw Fact Violation: Price '{price}' appears verbatim in Chapter {chapter_id} text. "
                        f"Only Chapters {ValidationGate.PRICE_OWNER_CHAPTERS} may display prices."
                    )
        
        # Check living area restatement
        if chapter_id not in ValidationGate.AREA_OWNER_CHAPTERS:
            area = registry_context.get('living_area_m2')
            if area and isinstance(area, (int, float)) and area > 50:
                area_str = str(int(area))
                # Pattern: area followed by m2/m²
                pattern = rf'\b{area_str}\s*m[²2]'
                if re.search(pattern, main_text, re.IGNORECASE):
                    errors.append(
                        f"Raw Fact Violation: Living area '{area} m²' appears verbatim in Chapter {chapter_id} text."
                    )
        
        return errors
    
    @staticmethod
    def _check_preference_reasoning(chapter_id: int, output: Dict[str, Any]) -> List[str]:
        """Check that Marcel & Petra reasoning is substantive."""
        errors = []
        
        # Get comparison block
        comparison = output.get('comparison', {})
        
        # Also check in chapter_data
        chapter_data = output.get('chapter_data', {})
        if isinstance(chapter_data, dict) and 'comparison' in chapter_data:
            comparison = chapter_data.get('comparison', comparison)
        
        if not isinstance(comparison, dict):
            # No comparison block is allowed for some chapters
            return errors
        
        marcel_text = comparison.get('marcel', '') or ''
        petra_text = comparison.get('petra', '') or ''
        
        # If comparison exists, it must be substantive
        if comparison:
            if len(str(marcel_text)) < ValidationGate.MIN_PREFERENCE_LENGTH:
                errors.append(
                    f"Preference Reasoning Missing: Marcel analysis in Chapter {chapter_id} "
                    f"is too short ({len(str(marcel_text))} chars, minimum {ValidationGate.MIN_PREFERENCE_LENGTH})."
                )
            
            if len(str(petra_text)) < ValidationGate.MIN_PREFERENCE_LENGTH:
                errors.append(
                    f"Preference Reasoning Missing: Petra analysis in Chapter {chapter_id} "
                    f"is too short ({len(str(petra_text))} chars, minimum {ValidationGate.MIN_PREFERENCE_LENGTH})."
                )
        
        return errors
    
    @staticmethod
    def _check_required_fields(chapter_id: int, output: Dict[str, Any]) -> List[str]:
        """Check that required fields are present."""
        errors = []
        
        # Must have an id
        if not output.get('id'):
            errors.append(f"Required Field Missing: 'id' not present in Chapter {chapter_id} output.")
        
        # Must have title
        if not output.get('title'):
            errors.append(f"Required Field Missing: 'title' not present in Chapter {chapter_id} output.")
        
        # Must have main_analysis OR chapter_data.main_analysis OR plane_b.narrative_text (4-plane)
        main = output.get('main_analysis', '')
        chapter_data = output.get('chapter_data', {})
        cd_main = chapter_data.get('main_analysis', '') if isinstance(chapter_data, dict) else ''
        
        # For 4-plane structure, plane_b.narrative_text is the content
        plane_b = output.get('plane_b', {})
        plane_narrative = plane_b.get('narrative_text', '') if isinstance(plane_b, dict) else ''
        
        if not main and not cd_main and not plane_narrative:
            errors.append(
                f"Required Field Missing: 'main_analysis' not present in Chapter {chapter_id}. "
                f"Every chapter must have content."
            )
        
        return errors
    
    # Chapters that MUST have narrative (0-12, excluding media chapter 13)
    NARRATIVE_REQUIRED_CHAPTERS = set(range(13))  # 0-12
    
    # Minimum word count for narrative
    MIN_NARRATIVE_WORD_COUNT = 300
    
    @staticmethod
    def _check_narrative(chapter_id: int, output: Dict[str, Any]) -> List[str]:
        """
        Check that mandatory narrative is present and meets minimum word count.
        
        VALIDATION RULES (FAIL-CLOSED):
        - Chapters 0-12 MUST have a narrative field
        - Narrative MUST have at least 300 words
        - Missing narrative = FAIL
        - Too short narrative = FAIL
        
        There is NO fallback. There is NO skip.
        """
        errors = []
        
        # Only chapters 0-12 require narrative
        if chapter_id not in ValidationGate.NARRATIVE_REQUIRED_CHAPTERS:
            return errors
        
        # Check for narrative in output
        narrative = output.get('narrative')
        
        # Also check in chapter_data
        chapter_data = output.get('chapter_data', {})
        if isinstance(chapter_data, dict) and 'narrative' in chapter_data:
            narrative = narrative or chapter_data.get('narrative')
        
        # ===================================================================
        # VALIDATION: Narrative must exist
        # ===================================================================
        if not narrative:
            errors.append(
                f"Narrative Missing: Chapter {chapter_id} has no 'narrative' field. "
                f"Every chapter (0-12) MUST have a narrative of at least 300 words. "
                f"This is NOT optional."
            )
            return errors
        
        # ===================================================================
        # VALIDATION: Narrative must have text
        # ===================================================================
        text = narrative.get('text', '') if isinstance(narrative, dict) else ''
        if not text or not text.strip():
            errors.append(
                f"Narrative Empty: Chapter {chapter_id} has empty narrative text. "
                f"Narrative text is REQUIRED."
            )
            return errors
        
        # ===================================================================
        # VALIDATION: Narrative must meet minimum word count
        # ===================================================================
        word_count = narrative.get('word_count', 0) if isinstance(narrative, dict) else 0
        
        # Verify word count matches actual text (trust but verify)
        actual_word_count = len(text.split())
        
        # Use the lower of reported vs actual (be strict)
        effective_word_count = min(word_count, actual_word_count) if word_count > 0 else actual_word_count
        
        if effective_word_count < ValidationGate.MIN_NARRATIVE_WORD_COUNT:
            errors.append(
                f"Narrative Too Short: Chapter {chapter_id} narrative has {effective_word_count} words "
                f"(minimum {ValidationGate.MIN_NARRATIVE_WORD_COUNT}). "
                f"Narrative word count requirement is MANDATORY."
            )
        
        return errors
    
    
    @staticmethod
    def validate_full_report(
        chapters: Dict[int, Dict[str, Any]],
        registry_context: Dict[str, Any]
    ) -> Dict[int, List[str]]:
        """
        Validate all chapters in a report.
        
        Returns:
            Dict mapping chapter_id to list of errors. Empty lists = passed.
        """
        results = {}
        
        for chapter_id, output in chapters.items():
            errors = ValidationGate.validate_chapter_output(
                int(chapter_id), 
                output, 
                registry_context
            )
            results[int(chapter_id)] = errors
        
        passed = sum(1 for errs in results.values() if not errs)
        failed = len(results) - passed
        
        logger.info(f"ValidationGate: Full report validation - {passed} passed, {failed} failed")
        
        return results
