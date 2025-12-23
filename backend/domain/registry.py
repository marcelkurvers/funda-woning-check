from enum import Enum
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

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
    name: str # Human readable name
    source: str # e.g. "funda_parse", "kadaster", "ai_inference"
    confidence: float = 1.0 # 0.0 to 1.0
    unit: Optional[str] = None
    completeness: bool = True
    derived_from: List[str] = field(default_factory=list) # IDs of parent facts
    
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
    """
    def __init__(self):
        self._entries: Dict[str, RegistryEntry] = {}
        self._locked = False
        
    def register(self, entry: RegistryEntry):
        if self._locked:
            raise RuntimeError("Registry is locked. Cannot add new entries.")
        
        if entry.id in self._entries:
             # Idempotency check: if exactly same, ignore. If different, error.
             existing = self._entries[entry.id]
             if existing.value != entry.value:
                 logger.warning(f"CONFLICT: Registry ID {entry.id} redefined. Old: {existing.value}, New: {entry.value}. Keeping Old.")
                 return
        
        self._entries[entry.id] = entry
        
    def get(self, id: str) -> Optional[RegistryEntry]:
        return self._entries.get(id)
        
    def get_all(self) -> Dict[str, RegistryEntry]:
        return self._entries.copy()
    
    def lock(self):
        """Prevent further modifications."""
        self._locked = True
        
    def to_legacy_dict(self) -> Dict[str, Any]:
        """Backward compatibility for existing code expecting a flat dict."""
        return {k: v.value for k, v in self._entries.items()}

    def validate_completeness(self) -> List[str]:
        """Returns list of IDs that are marked as uncertain/incomplete."""
        return [e.id for e in self._entries.values() if not e.completeness or e.type == RegistryType.UNCERTAINTY]
