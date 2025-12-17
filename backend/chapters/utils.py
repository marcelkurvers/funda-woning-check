import re
from typing import Any, Optional


def parse_int(value: Any, default: int = 0) -> int:
    """Parse an integer from various input types, returning default on failure."""
    if value is None:
        return default
    try:
        # Handle string inputs with formatting
        if isinstance(value, str):
            # Remove common formatting: spaces, commas, dots (European number format)
            cleaned = re.sub(r'[^\d-]', '', value)
            if not cleaned or cleaned == '-':
                return default
            return int(cleaned)
        # Handle numeric types
        return int(value)
    except (ValueError, TypeError):
        return default


def parse_float(value: Any, default: float = 0.0) -> float:
    """Parse a float from various input types, returning default on failure."""
    if value is None:
        return default
    try:
        if isinstance(value, str):
            cleaned = value.replace(',', '.').strip()
            return float(cleaned)
        return float(value)
    except (ValueError, TypeError):
        return default


def validate_bedrooms(rooms: int, bedrooms: Optional[int] = None) -> int:
    """
    Validate bedroom count with sensible upper bounds.
    
    Args:
        rooms: Total number of rooms
        bedrooms: Explicit bedroom count (if available)
    
    Returns:
        Validated bedroom count (capped at 10)
    """
    if bedrooms is not None:
        # Use explicit bedroom count if provided
        calculated = min(max(1, bedrooms), 10)
    else:
        # Derive from rooms: max(1, rooms - 1) but cap at 10
        calculated = min(max(1, rooms - 1), 10)
    
    return calculated


def validate_living_area(area_m2: int) -> int:
    """
    Validate living area is within reasonable bounds.
    
    Args:
        area_m2: Living area in square meters
    
    Returns:
        Validated area (must be > 0 and < 2000)
    """
    if area_m2 <= 0:
        return 1  # Fallback to prevent division by zero
    if area_m2 > 2000:
        # Log warning for extremely large values
        import logging
        logging.warning(f"Unusually large living area: {area_m2} m²")
    return min(max(1, area_m2), 2000)


def safe_get(context: dict, key: str, default: str = "") -> str:
    """Safely retrieve a value from the context dict, returning default if missing or None."""
    val = context.get(key, default)
    return default if val is None else str(val)


def ensure_grid_layout(chapter_dict: dict) -> dict:
    """
    Ensure a chapter output dictionary has a grid_layout key.
    
    Args:
        chapter_dict: Chapter output dictionary
    
    Returns:
        Dictionary with guaranteed grid_layout key
    """
    if 'grid_layout' not in chapter_dict:
        # Provide fallback structure
        chapter_dict['grid_layout'] = {
            "layout_type": "fallback",
            "hero": {
                "address": "Onbekend",
                "price": "N/A",
                "status": "Geen data",
                "labels": []
            },
            "metrics": [],
            "main": {"title": "Geen content", "content": "<p>Data niet beschikbaar</p>"},
            "sidebar": []
        }
    return chapter_dict

