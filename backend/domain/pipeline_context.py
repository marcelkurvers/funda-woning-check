"""
Pipeline Context - The Execution Spine

This module provides the single source of truth for the entire report generation pipeline.
Every stage of the pipeline receives this context, and no output can be produced without it.

INVARIANTS:
1. Registry is created exactly once per pipeline execution
2. Registry is locked before chapter generation begins
3. No chapter can render without access to this context
4. Validation is mandatory for every chapter output
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from backend.domain.registry import (
    CanonicalRegistry, 
    RegistryEntry, 
    RegistryType,
    RegistryConflict,
    RegistryLocked
)

logger = logging.getLogger(__name__)


class PipelineViolation(Exception):
    """Raised when pipeline invariants are violated."""
    pass


class ValidationFailure(Exception):
    """Raised when validation gate rejects chapter output."""
    def __init__(self, chapter_id: int, errors: List[str]):
        self.chapter_id = chapter_id
        self.errors = errors
        super().__init__(f"Chapter {chapter_id} validation failed: {'; '.join(errors)}")


@dataclass
class PipelineContext:
    """
    The execution spine for report generation.
    
    This object is created ONCE at pipeline start, passed to EVERY stage,
    and ensures all invariants are enforced structurally.
    """
    
    # The canonical registry - single source of truth
    registry: CanonicalRegistry = field(default_factory=CanonicalRegistry)
    
    # Pipeline state
    run_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    # Lifecycle flags
    _enrichment_complete: bool = field(default=False, repr=False)
    _registry_locked: bool = field(default=False, repr=False)
    _chapters_started: bool = field(default=False, repr=False)
    
    # Raw source data (immutable after enrichment)
    _raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)
    
    # Validation results per chapter
    _validation_results: Dict[int, List[str]] = field(default_factory=dict, repr=False)
    
    # Generated chapter outputs (only populated after validation passes)
    _validated_chapters: Dict[int, Dict[str, Any]] = field(default_factory=dict, repr=False)
    
    # Preferences (user-defined, not from registry)
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def set_raw_data(self, data: Dict[str, Any]) -> None:
        """Set raw data. Can only be called before enrichment."""
        if self._enrichment_complete:
            raise PipelineViolation("Cannot modify raw data after enrichment is complete")
        self._raw_data = data.copy()
    
    def get_raw_data(self) -> Dict[str, Any]:
        """Get a copy of raw data."""
        return self._raw_data.copy()
    
    def register_fact(self, 
                      key: str, 
                      value: Any, 
                      name: str, 
                      rtype: RegistryType = RegistryType.FACT,
                      unit: Optional[str] = None,
                      source: str = "enricher",
                      confidence: float = 1.0) -> None:
        """Register a fact in the canonical registry."""
        if self._registry_locked:
            raise PipelineViolation(f"Cannot register fact '{key}' - registry is locked")
        
        entry = RegistryEntry(
            id=key,
            type=rtype,
            value=value,
            name=name,
            unit=unit,
            source=source,
            confidence=confidence,
            completeness=value is not None
        )
        self.registry.register(entry)
    
    def complete_enrichment(self) -> None:
        """Mark enrichment as complete. No more raw data modifications allowed."""
        if self._enrichment_complete:
            raise PipelineViolation("Enrichment already marked as complete")
        self._enrichment_complete = True
        logger.info(f"Pipeline [{self.run_id}]: Enrichment complete. {len(self.registry.get_all())} entries registered.")
    
    def lock_registry(self) -> None:
        """Lock the registry. No more fact registration allowed."""
        if not self._enrichment_complete:
            raise PipelineViolation("Cannot lock registry before enrichment is complete")
        if self._registry_locked:
            raise PipelineViolation("Registry already locked")
        
        self.registry.lock()
        self._registry_locked = True
        logger.info(f"Pipeline [{self.run_id}]: Registry LOCKED. {len(self.registry.get_all())} canonical entries.")
    
    def begin_chapter_generation(self) -> None:
        """Mark the start of chapter generation. Registry must be locked."""
        if not self._registry_locked:
            raise PipelineViolation("Cannot begin chapter generation - registry is not locked")
        if self._chapters_started:
            raise PipelineViolation("Chapter generation already started")
        
        self._chapters_started = True
        logger.info(f"Pipeline [{self.run_id}]: Chapter generation started.")
    
    def is_registry_locked(self) -> bool:
        """Check if registry is locked."""
        return self._registry_locked
    
    def get_registry_value(self, key: str) -> Any:
        """Get a value from the registry. Returns None if not found."""
        entry = self.registry.get(key)
        return entry.value if entry else None
    
    def get_registry_entry(self, key: str) -> Optional[RegistryEntry]:
        """Get a full registry entry."""
        return self.registry.get(key)
    
    def get_registry_dict(self) -> Dict[str, Any]:
        """
        Get all registry values as a dict.
        
        NOTE: This is for read-only access. The registry itself remains
        the source of truth and cannot be modified through this dict.
        """
        return self.registry.to_legacy_dict()
    
    def record_validation_result(self, chapter_id: int, errors: List[str]) -> None:
        """Record validation result for a chapter."""
        self._validation_results[chapter_id] = errors
    
    def get_validation_errors(self, chapter_id: int) -> List[str]:
        """Get validation errors for a chapter."""
        return self._validation_results.get(chapter_id, [])
    
    def all_chapters_valid(self) -> bool:
        """Check if all generated chapters passed validation."""
        return all(len(errors) == 0 for errors in self._validation_results.values())
    
    def store_validated_chapter(self, chapter_id: int, output: Dict[str, Any]) -> None:
        """
        Store a validated chapter output.
        
        This can ONLY be called after validation passes for this chapter.
        """
        if chapter_id not in self._validation_results:
            raise PipelineViolation(f"Cannot store chapter {chapter_id} - validation not recorded")
        if self._validation_results[chapter_id]:
            raise PipelineViolation(f"Cannot store chapter {chapter_id} - validation failed")
        
        self._validated_chapters[chapter_id] = output
    
    def get_validated_chapters(self) -> Dict[int, Dict[str, Any]]:
        """Get all validated chapter outputs."""
        return self._validated_chapters.copy()
    
    def get_incomplete_entries(self) -> List[str]:
        """Get list of registry entries marked as incomplete or uncertain."""
        return self.registry.validate_completeness()


def create_pipeline_context(run_id: str, preferences: Optional[Dict[str, Any]] = None) -> PipelineContext:
    """
    Factory function to create a new pipeline context.
    
    This is the ONLY way to create a PipelineContext.
    """
    ctx = PipelineContext(
        run_id=run_id,
        preferences=preferences or {}
    )
    logger.info(f"Pipeline [{run_id}]: Context created.")
    return ctx
