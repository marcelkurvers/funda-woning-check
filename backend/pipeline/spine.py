"""
Pipeline Spine - The Single Execution Path (FAIL-CLOSED)

This module contains the ONLY valid execution path for report generation.
Every browser button click, every API call must flow through this spine.

INVARIANTS ENFORCED (NON-NEGOTIABLE):
1. Registry is created once, locked once, never recreated
2. Every chapter passes through ValidationGate
3. AI failure does not bypass validation
4. Rendering is BLOCKED on validation failure (no graceful degradation)
5. No output path exists outside this spine

FAIL-CLOSED PRINCIPLE:
- Invalid reports cannot be produced
- Violations cause hard failures, not warnings
- If you find yourself wanting to bypass this spine, STOP - the architecture forbids it

If any of these invariants are violated, the system is incorrect.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple, Callable
import gc
from datetime import datetime

from backend.domain.pipeline_context import (
    PipelineContext, 
    create_pipeline_context, 
    PipelineViolation,
    ValidationFailure
)
from backend.domain.registry import RegistryType, RegistryConflict, RegistryLocked
from backend.domain.ownership import OwnershipMap
from backend.validation.gate import ValidationGate
from backend.domain.guardrails import PolicyLevel

logger = logging.getLogger(__name__)


# =============================================================================
# PRODUCTION MODE DETECTION (LAW E ENFORCEMENT)
# =============================================================================
# In production, strict validation is ALWAYS enabled. 
# Only tests may disable it, and only with explicit flag.
#
# LAW E: No "Test Mode" That Leaks to Real Output
# If PIPELINE_TEST_MODE=true, outputs MUST be isolated and never served
# through the same endpoint a user uses.
# =============================================================================

def is_production_mode() -> bool:
    """
    Detect if we're in production mode.
    Production = strict validation MANDATORY.
    
    LAW E ENFORCEMENT:
    - Default is ALWAYS production mode (fail-closed)
    - Test mode requires explicit environment variable
    - Test mode outputs must be marked as test-only
    """
    # FAIL-CLOSED: Default to production (strict) unless explicitly in test mode
    test_mode = os.environ.get("PIPELINE_TEST_MODE", "").lower() == "true"
    return not test_mode


def is_test_mode() -> bool:
    """Check if running in test mode (inverse of production)."""
    return not is_production_mode()


# Test mode isolation marker - added to all outputs in test mode
TEST_MODE_ISOLATION_MARKER = "__TEST_MODE_ONLY__"


def mark_test_output(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mark output as test-only if running in test mode.
    
    LAW E: Test outputs must be distinguishable from production outputs.
    """
    if is_test_mode():
        # NOTE: We can't easily access PipelineContext here as this is a helper function.
        # But we can assume the Global Policy for this static helper.
        from backend.domain.governance_state import get_governance_state
        from backend.domain.guardrails import PolicyLevel
        
        policy = get_governance_state().get_effective_policy()
        
        if policy.prevent_test_mode_leakage == PolicyLevel.STRICT:
             # Enforce marking
             pass

        output[TEST_MODE_ISOLATION_MARKER] = True
        output["_test_mode_warning"] = (
            "This output was generated in PIPELINE_TEST_MODE=true. "
            "It may contain invalid data that bypassed strict validation. "
            "Do NOT serve to end users. (Policy: prevent_test_mode_leakage)"
        )
    return output


class PipelineSpine:
    """
    The single execution spine for report generation.
    
    All report generation MUST flow through this class.
    There are no alternative paths.
    
    FAIL-CLOSED: Any invalid state causes immediate failure.
    """
    
    def __init__(self, run_id: str, preferences: Optional[Dict[str, Any]] = None):
        """
        Initialize the pipeline spine.
        
        This creates the PipelineContext which holds the canonical registry
        for the entire lifecycle of this report generation.
        """
        self.ctx = create_pipeline_context(run_id, preferences)
        self._phase = "initialized"
        self._validation_failed = False
        self._failed_chapters: List[int] = []
        logger.info(f"PipelineSpine [{run_id}]: Initialized")
    
    # =========================================================================
    # PHASE 1: DATA INGESTION
    # =========================================================================
    
    def ingest_raw_data(self, raw_data: Dict[str, Any]) -> None:
        """
        Ingest raw parsed data into the pipeline.
        
        This is the ONLY entry point for external data.
        After this, data can only be enriched, not replaced.
        """
        if self._phase != "initialized":
            raise PipelineViolation(f"Cannot ingest data in phase '{self._phase}'")
        
        self.ctx.set_raw_data(raw_data)
        self._phase = "data_ingested"
        logger.info(f"PipelineSpine [{self.ctx.run_id}]: Raw data ingested ({len(raw_data)} keys)")
    
    # =========================================================================
    # PHASE 2: ENRICHMENT & REGISTRY POPULATION
    # =========================================================================
    
    def enrich_and_populate_registry(self) -> None:
        """
        Enrich data and populate the canonical registry.
        
        This is where all facts, variables, and KPIs are registered.
        After this phase, the registry is LOCKED and immutable.
        
        FAIL-CLOSED: RegistryConflict during enrichment aborts the pipeline.
        """
        if self._phase != "data_ingested":
            raise PipelineViolation(f"Cannot enrich in phase '{self._phase}'")
        
        raw = self.ctx.get_raw_data()
        
        # Import here to avoid circular imports
        from backend.pipeline.enrichment_adapter import enrich_into_context
        
        # Enrich data INTO the context (not returning a new dict)
        # This may raise RegistryConflict - which is FATAL
        enrich_into_context(self.ctx, raw)
        
        # Mark enrichment complete
        self.ctx.complete_enrichment()
        
        # LOCK THE REGISTRY - No more modifications after this
        self.ctx.lock_registry()
        
        self._phase = "enriched_and_locked"
        logger.info(f"PipelineSpine [{self.ctx.run_id}]: Enrichment complete, registry LOCKED")
    
    # =========================================================================
    # PHASE 3: CHAPTER GENERATION WITH MANDATORY VALIDATION
    # =========================================================================
    
    def generate_all_chapters(self, progress_callback: Optional[Callable[[str], None]] = None) -> Dict[int, Dict[str, Any]]:
        """
        Generate all chapters with MANDATORY validation.
        
        Every chapter output passes through ValidationGate.
        
        FAIL-CLOSED BEHAVIOR:
        - Validation is always run
        - Failed chapters are tracked
        - In production, validation failure means pipeline failure
        
        Args:
            progress_callback: Optional function to report progress (e.g. for DB heartbeats)
        
        Returns:
            Dict mapping chapter_id to chapter output (may include failed chapters)
        """
        if self._phase != "enriched_and_locked":
            raise PipelineViolation(f"Cannot generate chapters in phase '{self._phase}'")
        
        self.ctx.begin_chapter_generation()
        
        # Import chapter generator
        from backend.pipeline.chapter_generator import generate_chapter_with_validation
        
        all_chapters = {}
        
        for chapter_id in range(1, 14): # Skip 0, it is generated as Dashboard
            # Heartbeat update via callback
            if progress_callback:
                try:
                    progress_callback(f"running (Chapter {chapter_id}/13)")
                except Exception as e:
                    logger.warning(f"PipelineSpine: Progress callback failed: {e}")

            logger.info(f"PipelineSpine [{self.ctx.run_id}]: Generating chapter {chapter_id}")
            
            # Generate chapter (may use AI or fallback - doesn't matter)
            output = generate_chapter_with_validation(self.ctx, chapter_id)
            
            # MANDATORY VALIDATION - No exceptions, no bypasses
            errors = ValidationGate.validate_chapter_output(
                chapter_id, 
                output, 
                self.ctx.get_registry_dict(),
                policy=self.ctx.truth_policy
            )
            
            # Record validation result
            self.ctx.record_validation_result(chapter_id, errors)
            
            if errors:
                logger.error(f"PipelineSpine [{self.ctx.run_id}]: Chapter {chapter_id} FAILED validation: {errors}")
                self._validation_failed = True
                self._failed_chapters.append(chapter_id)
                output["_validation_failed"] = True
                output["_validation_errors"] = errors
            else:
                # Only store in validated chapters if validation passed
                self.ctx.store_validated_chapter(chapter_id, output)
            
            all_chapters[chapter_id] = output
            
            # MEMORY RELIEF (Fix 4)
            # Explicitly collect garbage after each heavy chapter generation to reduce OOM risk
            gc.collect()
        
        self._phase = "chapters_generated"
        
        if self._validation_failed:
            # We continue to generate dashboard even if chapters failed? 
            # Spec says "If ANY narrative fails -> stop execution".
            # So we should probably raise here or ensure get_renderable_output fails.
             logger.error(
                f"PipelineSpine [{self.ctx.run_id}]: VALIDATION FAILED for chapters: {self._failed_chapters}. "
                f"Report generation is INVALID."
            )
        
        return all_chapters
    
    def generate_single_chapter(self, chapter_id: int) -> Dict[str, Any]:
        """
        Generate a single chapter with mandatory validation.
        
        FAIL-CLOSED: Raises ValidationFailure if validation fails.
        """
        if self._phase not in ["enriched_and_locked", "chapters_generated"]:
            raise PipelineViolation(f"Cannot generate chapter in phase '{self._phase}'")
        
        if self._phase == "enriched_and_locked":
            self.ctx.begin_chapter_generation()
        
        from backend.pipeline.chapter_generator import generate_chapter_with_validation
        
        output = generate_chapter_with_validation(self.ctx, chapter_id)
        
        # MANDATORY VALIDATION
        errors = ValidationGate.validate_chapter_output(
            chapter_id,
            output,
            self.ctx.get_registry_dict(),
            policy=self.ctx.truth_policy
        )
        
        self.ctx.record_validation_result(chapter_id, errors)
        
        if errors:
            raise ValidationFailure(chapter_id, errors)
        
        self.ctx.store_validated_chapter(chapter_id, output)
        return output
    
    # =========================================================================
    # PHASE 3.5: DASHBOARD GENERATION (First-Class Output)
    # =========================================================================
    
    def generate_dashboard(self) -> Dict[str, Any]:
        """
        Generate decision dashboard (LAT 2).
        
        This MUST happen after chapter generation.
        """
        if self._phase != "chapters_generated":
            raise PipelineViolation(f"Cannot generate dashboard in phase '{self._phase}'")
            
        from backend.pipeline.dashboard_generator import generate_dashboard_with_validation
        
        logger.info(f"PipelineSpine [{self.ctx.run_id}]: Generating Dashboard")
        
        # FAIL-CLOSED: Dashboard failure kills the pipeline
        try:
            output = generate_dashboard_with_validation(self.ctx)
            # Store as dict
            self.ctx.store_dashboard(output.model_dump())
        except Exception as e:
            self._validation_failed = True
            logger.error(f"PipelineSpine [{self.ctx.run_id}]: Dashboard generation FAILED: {e}")
            if is_production_mode():
                raise e
        
        return self.ctx.get_dashboard()

    
    # =========================================================================
    # PHASE 4: RENDER (Only after validation)
    # =========================================================================
    
    def get_renderable_output(self, strict: bool = True) -> Dict[str, Any]:
        """
        Get the final renderable output.
        
        Args:
            strict: PRODUCTION MODE - must be True in production.
                    If True, raises if any validation failed.
                    If False (ONLY for tests), returns output with error markers.
        
        Returns:
            Complete report structure ready for rendering
        
        Raises:
            PipelineViolation: If pipeline not in correct phase
            PipelineViolation: If strict=True and validations failed
        """
        if self._phase != "chapters_generated":
            raise PipelineViolation(f"Cannot render in phase '{self._phase}'")
        
        # FAIL-CLOSED: In production, always strict
        if is_production_mode():
            if self.ctx.truth_policy.enforce_production_strictness == PolicyLevel.STRICT:
                strict = True
            elif strict is False:
                 # Should never happen in prod if policy is STRICT
                 logger.warning("PipelineSpine: Production strictness policy is NOT strict (Legacy behavior)")
        
        if strict and not self.ctx.all_chapters_valid():
            failed = {cid: errs for cid, errs in self.ctx._validation_results.items() if errs}
            raise PipelineViolation(
                f"FATAL: Cannot render invalid report. Validation failed for chapters: {list(failed.keys())}. "
                f"Errors: {failed} (Policy: enforce_production_strictness)"
            )
        
        # Build final output structure
        chapters = self.ctx.get_validated_chapters()
        
        # Add any failed chapters with error markers if not strict (test mode only)
        if not strict:
            for chapter_id in range(14):
                if chapter_id not in chapters:
                    errors = self.ctx.get_validation_errors(chapter_id)
                    chapters[chapter_id] = {
                        "id": str(chapter_id),
                        "title": f"Chapter {chapter_id} - Validation Failed",
                        "_validation_failed": True,
                        "_validation_errors": errors,
                        "grid_layout": {},
                        "blocks": [],
                        "chapter_data": {}
                    }
        
        # === MANDATORY: Get CoreSummary ===
        # CoreSummary is the BACKBONE CONTRACT - MUST be present in every output
        core_summary = self.ctx.get_core_summary()
        
        output = {
            "run_id": self.ctx.run_id,
            "created_at": self.ctx.created_at.isoformat(),
            "registry_entry_count": len(self.ctx.registry.get_all()),
            "validation_passed": self.ctx.all_chapters_valid(),
            "chapters": {str(k): v for k, v in chapters.items()},
            "dashboard": self.ctx.get_dashboard(),
            "incomplete_data": self.ctx.get_incomplete_entries(),
            # === BACKBONE CONTRACT: CoreSummary is MANDATORY ===
            "core_summary": core_summary.model_dump()
        }
        
        # LAW E: Mark test mode outputs for isolation
        return mark_test_output(output)
    
    # =========================================================================
    # CONVENIENCE: Full Pipeline Execution
    # =========================================================================
    
    @classmethod
    def execute_full_pipeline(
        cls,
        run_id: str,
        raw_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None,
        strict_validation: Optional[bool] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple["PipelineSpine", Dict[str, Any]]:
        """
        Execute the complete pipeline from raw data to renderable output.
        
        This is the primary entry point for report generation.
        
        Args:
            run_id: Unique identifier for this pipeline run
            raw_data: Parsed property data
            preferences: User preferences (Marcel & Petra)
            strict_validation: If None, uses production mode detection.
                               Only tests should set this to False.
        
        Returns:
            Tuple of (PipelineSpine instance, renderable output)
            
        Raises:
            PipelineViolation: If any validation fails (in production mode)
            RegistryConflict: If registry conflicts occur during enrichment
        """
        logger.info(f"PipelineSpine.execute_full_pipeline: Starting run {run_id}")
        
        # FAIL-CLOSED: Default to strict in production
        if strict_validation is None:
            strict_validation = is_production_mode()
        
        spine = cls(run_id, preferences)
        
        # Phase 1: Ingest
        spine.ingest_raw_data(raw_data)
        
        # Phase 2: Enrich & Lock (may raise RegistryConflict)
        spine.enrich_and_populate_registry()
        
        # Phase 3: Generate with Validation
        spine.generate_all_chapters(progress_callback=progress_callback)
        
        # Phase 3.5: Dashboard
        spine.generate_dashboard()
        
        # Phase 4: Get Renderable Output (may raise PipelineViolation if strict)
        output = spine.get_renderable_output(strict=strict_validation)
        
        logger.info(f"PipelineSpine.execute_full_pipeline: Completed run {run_id}")
        
        return spine, output


# =============================================================================
# PUBLIC API - THESE ARE THE ONLY VALID ENTRY POINTS
# =============================================================================

def execute_report_pipeline(
    run_id: str,
    raw_data: Dict[str, Any],
    preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute the full pipeline - PUBLIC API.
    
    This is the ONLY function that should be called from main.py.
    All other paths are deprecated and will throw.
    
    FAIL-CLOSED: In production, validation failure raises PipelineViolation.
    """
    _, output = PipelineSpine.execute_full_pipeline(
        run_id=run_id,
        raw_data=raw_data,
        preferences=preferences,
        strict_validation=None  # Uses production mode detection
    )
    return output


# Backward compatibility alias - but marked for removal
def execute_pipeline(
    run_id: str,
    raw_data: Dict[str, Any],
    preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    DEPRECATED: Use execute_report_pipeline instead.
    
    This function exists only for backward compatibility.
    It forwards to execute_report_pipeline.
    """
    logger.warning(
        "execute_pipeline is DEPRECATED. Use execute_report_pipeline. "
        "This function will be removed in a future version."
    )
    return execute_report_pipeline(run_id, raw_data, preferences)
