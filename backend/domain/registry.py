"""
Canonical Registry - FAIL-CLOSED Single Source of Truth

INVARIANTS (NON-NEGOTIABLE):
1. Once locked, no modifications allowed - raises RegistryLocked
2. Conflicts (same key, different value) raise RegistryConflict  
3. No fallback logic - missing keys stay missing
4. No variable can be synthesized outside registration

If any invariant is violated, execution MUST abort.
"""

from enum import Enum
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class RegistryConflict(Exception):
    """Raised when attempting to redefine a registry entry with a different value.
    
    This is a FATAL error - the pipeline must abort.
    """
    pass


class RegistryLocked(Exception):
    """Raised when attempting to modify a locked registry.
    
    This is a FATAL error - the pipeline must abort.
    """
    pass


class RegistryType(Enum):
    FACT = "FACT"           # Hard data (e.g. "120 m2")
    VARIABLE = "VARIABLE"   # Derived/Interpreted (e.g. "Ruime woonkamer")
    KPI = "KPI"            # Calculated Metric (e.g. "Match Score: 80%")
    UNCERTAINTY = "UNCERTAINTY" # Information explicitly missing


@dataclass
class RegistryEntry:
    id: str
    type: RegistryType
    value: Any
    name: str  # Human readable name
    source: str  # e.g. "funda_parse", "kadaster", "ai_inference"
    confidence: float = 1.0  # 0.0 to 1.0
    unit: Optional[str] = None
    completeness: bool = True
    derived_from: List[str] = field(default_factory=list)  # IDs of parent facts
    
    def dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "source": self.source,
            "confidence": self.confidence,
            "completeness": self.completeness
        }


class CanonicalRegistry:
    """
    Layer 1: Canonical Knowledge Registry.
    Single source of truth before any AI reasoning.
    
    FAIL-CLOSED ENFORCEMENT:
    - Locked registry cannot be modified (raises RegistryLocked)
    - Conflicting registrations raise RegistryConflict
    - No silent failures, warnings converted to errors
    """
    
    def __init__(self):
        self._entries: Dict[str, RegistryEntry] = {}
        self._locked = False
        
    def register(self, entry: RegistryEntry):
        """
        Register an entry. FAIL-CLOSED behavior:
        - Raises RegistryLocked if registry is locked
        - Raises RegistryConflict if redefining with different value
        - Idempotent for exact same value (no-op)
        """
        if self._locked:
            raise RegistryLocked(
                f"FATAL: Registry is locked. Cannot add entry: '{entry.id}'. "
                f"This indicates a pipeline phase violation."
            )
        
        if entry.id in self._entries:
            existing = self._entries[entry.id]
            # Idempotency: exact same value is allowed (no-op)
            if existing.value == entry.value:
                return
            # FAIL-CLOSED: Different value is a conflict - THROW
            raise RegistryConflict(
                f"FATAL CONFLICT: Registry ID '{entry.id}' redefined. "
                f"Old: {existing.value} (source: {existing.source}), "
                f"New: {entry.value} (source: {entry.source}). "
                f"This is a structural violation - the pipeline must abort."
            )
        
        self._entries[entry.id] = entry
        
    def get(self, id: str) -> Optional[RegistryEntry]:
        """Get an entry by ID. Returns None if not found - no fallbacks."""
        return self._entries.get(id)
        
    def get_all(self) -> Dict[str, RegistryEntry]:
        """Get a copy of all entries."""
        return self._entries.copy()
    
    def lock(self):
        """
        Permanently lock the registry. No further modifications allowed.
        This is called after enrichment, before chapter generation.
        """
        self._locked = True
        logger.info(f"Registry LOCKED with {len(self._entries)} entries. No further modifications allowed.")
    
    def is_locked(self) -> bool:
        """Check if registry is locked."""
        return self._locked
        
    def to_legacy_dict(self) -> Dict[str, Any]:
        """Backward compatibility for existing code expecting a flat dict."""
        return {k: v.value for k, v in self._entries.items()}

    def validate_completeness(self) -> List[str]:
        """Returns list of IDs that are marked as uncertain/incomplete."""
        return [e.id for e in self._entries.values() if not e.completeness or e.type == RegistryType.UNCERTAINTY]
