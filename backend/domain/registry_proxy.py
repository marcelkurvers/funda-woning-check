"""
Read-Only Registry Proxy - Presentation Layer Protection

This module provides a read-only proxy to the CanonicalRegistry that:
1. Allows reading values from the registry
2. BLOCKS any attempt to compute, derive, or create new values
3. Enforces the PRESENTATION-ONLY guarantee

INVARIANTS:
- No arithmetic operations allowed on proxied values
- No new fact creation possible
- All access is read-only after lock
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class PresentationViolation(Exception):
    """
    Raised when presentation code attempts to create or compute facts.
    
    This is a FATAL error - the pipeline must abort.
    """
    pass


@dataclass(frozen=True)
class RegistryValue:
    """
    An immutable wrapper around a registry value.
    
    This prevents arithmetic operations on registry values in presentation code.
    Attempts to use +, -, *, / will raise PresentationViolation.
    """
    value: Any
    key: str
    source: str = "registry"
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return f"RegistryValue({self.key}={self.value})"
    
    # =========================================================================
    # BANNED OPERATIONS - Raise PresentationViolation
    # =========================================================================
    
    def __add__(self, other):
        raise PresentationViolation(
            f"FATAL: Attempted arithmetic (+) on registry value '{self.key}' = {self.value}. "
            f"Presentation code may NOT compute new values. "
            f"Move this calculation to the enrichment layer."
        )
    
    def __radd__(self, other):
        raise PresentationViolation(
            f"FATAL: Attempted arithmetic (+) on registry value '{self.key}' = {self.value}. "
            f"Presentation code may NOT compute new values."
        )
    
    def __sub__(self, other):
        raise PresentationViolation(
            f"FATAL: Attempted arithmetic (-) on registry value '{self.key}' = {self.value}. "
            f"Presentation code may NOT compute new values."
        )
    
    def __rsub__(self, other):
        raise PresentationViolation(
            f"FATAL: Attempted arithmetic (-) on registry value '{self.key}' = {self.value}. "
            f"Presentation code may NOT compute new values."
        )
    
    def __mul__(self, other):
        raise PresentationViolation(
            f"FATAL: Attempted arithmetic (*) on registry value '{self.key}' = {self.value}. "
            f"Presentation code may NOT compute new values."
        )
    
    def __rmul__(self, other):
        raise PresentationViolation(
            f"FATAL: Attempted arithmetic (*) on registry value '{self.key}' = {self.value}. "
            f"Presentation code may NOT compute new values."
        )
    
    def __truediv__(self, other):
        raise PresentationViolation(
            f"FATAL: Attempted arithmetic (/) on registry value '{self.key}' = {self.value}. "
            f"Presentation code may NOT compute new values."
        )
    
    def __rtruediv__(self, other):
        raise PresentationViolation(
            f"FATAL: Attempted arithmetic (/) on registry value '{self.key}' = {self.value}. "
            f"Presentation code may NOT compute new values."
        )
    
    def __floordiv__(self, other):
        raise PresentationViolation(
            f"FATAL: Attempted arithmetic (//) on registry value '{self.key}' = {self.value}. "
            f"Presentation code may NOT compute new values."
        )
    
    def __mod__(self, other):
        raise PresentationViolation(
            f"FATAL: Attempted arithmetic (%) on registry value '{self.key}' = {self.value}. "
            f"Presentation code may NOT compute new values."
        )
    
    def __pow__(self, other):
        raise PresentationViolation(
            f"FATAL: Attempted arithmetic (**) on registry value '{self.key}' = {self.value}. "
            f"Presentation code may NOT compute new values."
        )
    
    # =========================================================================
    # SAFE READ OPERATIONS
    # =========================================================================
    
    def raw(self) -> Any:
        """Get the raw underlying value for display purposes only."""
        return self.value
    
    def __eq__(self, other):
        """Equality comparison is safe for display logic."""
        if isinstance(other, RegistryValue):
            return self.value == other.value
        return self.value == other
    
    def __hash__(self):
        return hash((self.key, self.value))
    
    def __bool__(self):
        """Boolean conversion is safe."""
        return bool(self.value)
    
    def __lt__(self, other):
        """Comparison for sorting/display is safe."""
        if isinstance(other, RegistryValue):
            return self.value < other.value
        return self.value < other
    
    def __le__(self, other):
        if isinstance(other, RegistryValue):
            return self.value <= other.value
        return self.value <= other
    
    def __gt__(self, other):
        if isinstance(other, RegistryValue):
            return self.value > other.value
        return self.value > other
    
    def __ge__(self, other):
        if isinstance(other, RegistryValue):
            return self.value >= other.value
        return self.value >= other


class ReadOnlyRegistryProxy:
    """
    A read-only proxy to the CanonicalRegistry for presentation code.
    
    This proxy:
    1. Wraps all values in RegistryValue to block arithmetic
    2. Prevents any modification to the underlying registry
    3. Provides safe read access for templates and display
    
    Usage:
        proxy = ReadOnlyRegistryProxy(registry)
        price = proxy.get("asking_price_eur")  # Returns RegistryValue
        # price + 1000  # RAISES PresentationViolation
        str(price)  # SAFE - returns "500000"
    """
    
    def __init__(self, registry_dict: Dict[str, Any]):
        """
        Create a proxy from a registry dict.
        
        Args:
            registry_dict: The legacy dict from registry.to_legacy_dict()
        """
        self._data = registry_dict.copy()
        self._frozen = True
        logger.debug(f"ReadOnlyRegistryProxy created with {len(self._data)} entries")
    
    def get(self, key: str, default: Any = None) -> Optional[RegistryValue]:
        """
        Get a value from the registry.
        
        Returns a RegistryValue wrapper that blocks arithmetic operations.
        """
        if key in self._data:
            return RegistryValue(value=self._data[key], key=key)
        if default is not None:
            return RegistryValue(value=default, key=key, source="default")
        return None
    
    def get_raw(self, key: str, default: Any = None) -> Any:
        """
        Get the raw value from the registry.
        
        WARNING: This bypasses protection. Only use for display formatting
        where arithmetic is not possible (e.g., direct template interpolation).
        """
        return self._data.get(key, default)
    
    def __getitem__(self, key: str) -> RegistryValue:
        """Dict-like access, returns RegistryValue."""
        if key not in self._data:
            raise KeyError(f"Registry key '{key}' not found")
        return RegistryValue(value=self._data[key], key=key)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._data
    
    def keys(self):
        """Get all keys."""
        return self._data.keys()
    
    def items(self):
        """Get all items as (key, RegistryValue) pairs."""
        return [(k, RegistryValue(value=v, key=k)) for k, v in self._data.items()]
    
    def to_display_dict(self) -> Dict[str, Any]:
        """
        Get a dict suitable for display/templates.
        
        Returns raw values, but this dict should ONLY be used
        for direct template interpolation, not computation.
        """
        return self._data.copy()
    
    def __setitem__(self, key: str, value: Any):
        raise PresentationViolation(
            f"FATAL: Attempted to set registry value '{key}' in presentation layer. "
            f"Registry is READ-ONLY after lock. "
            f"Facts can only be created in the enrichment layer."
        )
    
    def __delitem__(self, key: str):
        raise PresentationViolation(
            f"FATAL: Attempted to delete registry value '{key}' in presentation layer. "
            f"Registry is READ-ONLY after lock."
        )


def create_presentation_context(registry_dict: Dict[str, Any]) -> ReadOnlyRegistryProxy:
    """
    Factory function to create a presentation-safe registry proxy.
    
    This is the ONLY way presentation code should access registry data.
    """
    return ReadOnlyRegistryProxy(registry_dict)
