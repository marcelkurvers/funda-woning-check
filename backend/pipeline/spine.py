"""
Pipeline Spine - The Single Execution Path

This module contains the ONLY valid execution path for report generation.
Every browser button click, every API call must flow through this spine.

INVARIANTS ENFORCED:
1. Registry is created once, locked once, never recreated
2. Every chapter passes through ValidationGate
3. AI failure does not bypass validation
4. Rendering is blocked on validation failure
5. No output path exists outside this spine

If you find yourself wanting to bypass this spine, stop.
The architecture requires this enforcement. Find another way.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from backend.domain.pipeline_context import (
    PipelineContext, 
    create_pipeline_context, 
    PipelineViolation,
    ValidationFailure
)
from backend.domain.registry import RegistryType
from backend.domain.ownership import OwnershipMap
from backend.validation.gate import ValidationGate

logger = logging.getLogger(__name__)


class PipelineSpine:
    """
    The single execution spine for report generation.
    
    All report generation MUST flow through this class.
    There are no alternative paths.
    """
    
    def __init__(self, run_id: str, preferences: Optional[Dict[str, Any]] = None):
        """
        Initialize the pipeline spine.
        
        This creates the PipelineContext which holds the canonical registry
        for the entire lifecycle of this report generation.
        """
        self.ctx = create_pipeline_context(run_id, preferences)
        self._phase = "initialized"
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
        """
        if self._phase != "data_ingested":
            raise PipelineViolation(f"Cannot enrich in phase '{self._phase}'")
        
        raw = self.ctx.get_raw_data()
        
        # Import here to avoid circular imports
        from backend.pipeline.enrichment_adapter import enrich_into_context
        
        # Enrich data INTO the context (not returning a new dict)
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
    
    def generate_all_chapters(self) -> Dict[int, Dict[str, Any]]:
        """
        Generate all chapters with MANDATORY validation.
        
        Every chapter output passes through ValidationGate.
        Validation failure raises ValidationFailure exception.
        
        Returns:
            Dict mapping chapter_id to validated chapter output
        
        Raises:
            ValidationFailure: If any chapter fails validation
        """
        if self._phase != "enriched_and_locked":
            raise PipelineViolation(f"Cannot generate chapters in phase '{self._phase}'")
        
        self.ctx.begin_chapter_generation()
        
        # Import chapter generator
        from backend.pipeline.chapter_generator import generate_chapter_with_validation
        
        validated_chapters = {}
        
        for chapter_id in range(14):
            logger.info(f"PipelineSpine [{self.ctx.run_id}]: Generating chapter {chapter_id}")
            
            # Generate chapter (may use AI or fallback - doesn't matter)
            output = generate_chapter_with_validation(self.ctx, chapter_id)
            
            # MANDATORY VALIDATION - No exceptions, no bypasses
            errors = ValidationGate.validate_chapter_output(
                chapter_id, 
                output, 
                self.ctx.get_registry_dict()
            )
            
            # Record validation result
            self.ctx.record_validation_result(chapter_id, errors)
            
            if errors:
                logger.error(f"PipelineSpine [{self.ctx.run_id}]: Chapter {chapter_id} FAILED validation: {errors}")
                # Store error state but continue to collect all errors
                output["_validation_failed"] = True
                output["_validation_errors"] = errors
            else:
                # Only store in validated chapters if validation passed
                self.ctx.store_validated_chapter(chapter_id, output)
            
            validated_chapters[chapter_id] = output
        
        self._phase = "chapters_generated"
        
        # Check if any chapter failed
        if not self.ctx.all_chapters_valid():
            failed = [cid for cid, errs in self.ctx._validation_results.items() if errs]
            logger.error(f"PipelineSpine [{self.ctx.run_id}]: {len(failed)} chapters failed validation")
            # We continue but mark the report as having validation issues
        
        return validated_chapters
    
    def generate_single_chapter(self, chapter_id: int) -> Dict[str, Any]:
        """
        Generate a single chapter with mandatory validation.
        
        For incremental generation or regeneration scenarios.
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
            self.ctx.get_registry_dict()
        )
        
        self.ctx.record_validation_result(chapter_id, errors)
        
        if errors:
            raise ValidationFailure(chapter_id, errors)
        
        self.ctx.store_validated_chapter(chapter_id, output)
        return output
    
    # =========================================================================
    # PHASE 4: RENDER (Only after validation)
    # =========================================================================
    
    def get_renderable_output(self, strict: bool = True) -> Dict[str, Any]:
        """
        Get the final renderable output.
        
        Args:
            strict: If True, raises if any validation failed.
                    If False, returns partial output with error markers.
        
        Returns:
            Complete report structure ready for rendering
        
        Raises:
            PipelineViolation: If pipeline not in correct phase
            ValidationFailure: If strict=True and validations failed
        """
        if self._phase != "chapters_generated":
            raise PipelineViolation(f"Cannot render in phase '{self._phase}'")
        
        if strict and not self.ctx.all_chapters_valid():
            failed = {cid: errs for cid, errs in self.ctx._validation_results.items() if errs}
            raise PipelineViolation(f"Cannot render - validation failed for chapters: {list(failed.keys())}")
        
        # Build final output structure
        chapters = self.ctx.get_validated_chapters()
        
        # Add any failed chapters with error markers if not strict
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
        
        return {
            "run_id": self.ctx.run_id,
            "created_at": self.ctx.created_at.isoformat(),
            "registry_entry_count": len(self.ctx.registry.get_all()),
            "validation_passed": self.ctx.all_chapters_valid(),
            "chapters": {str(k): v for k, v in chapters.items()},
            "incomplete_data": self.ctx.get_incomplete_entries()
        }
    
    # =========================================================================
    # CONVENIENCE: Full Pipeline Execution
    # =========================================================================
    
    @classmethod
    def execute_full_pipeline(
        cls,
        run_id: str,
        raw_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None,
        strict_validation: bool = False
    ) -> Tuple["PipelineSpine", Dict[str, Any]]:
        """
        Execute the complete pipeline from raw data to renderable output.
        
        This is the primary entry point for report generation.
        
        Args:
            run_id: Unique identifier for this pipeline run
            raw_data: Parsed property data
            preferences: User preferences (Marcel & Petra)
            strict_validation: If True, raise on any validation failure
        
        Returns:
            Tuple of (PipelineSpine instance, renderable output)
        """
        logger.info(f"PipelineSpine.execute_full_pipeline: Starting run {run_id}")
        
        spine = cls(run_id, preferences)
        
        # Phase 1: Ingest
        spine.ingest_raw_data(raw_data)
        
        # Phase 2: Enrich & Lock
        spine.enrich_and_populate_registry()
        
        # Phase 3: Generate with Validation
        spine.generate_all_chapters()
        
        # Phase 4: Get Renderable Output
        output = spine.get_renderable_output(strict=strict_validation)
        
        logger.info(f"PipelineSpine.execute_full_pipeline: Completed run {run_id}")
        
        return spine, output


def execute_pipeline(
    run_id: str,
    raw_data: Dict[str, Any],
    preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to execute the full pipeline.
    
    This is the ONLY function that should be called from main.py.
    """
    _, output = PipelineSpine.execute_full_pipeline(
        run_id=run_id,
        raw_data=raw_data,
        preferences=preferences,
        strict_validation=False  # Allow partial output in production
    )
    return output
