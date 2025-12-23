from typing import Dict, Set, List, Optional, Any
from backend.domain.chapter_variables import get_chapter_variables, should_show_core_data

class OwnershipMap:
    """
    Layer 2: Ownership & Scope Resolution.
    Determines which page/chapter owns which data points.
    """
    
    def __init__(self):
        # We use the existing definition in chapter_variables.py as the source of truth
        pass

    @staticmethod
    def get_owned_variables(chapter_id: int) -> Set[str]:
        """Returns the set of variables that this chapter explicitly owns/defines."""
        return get_chapter_variables(chapter_id)
    
    @staticmethod
    def is_referencing_allowed(chapter_id: int, variable_id: str) -> bool:
        """
        Determines if a chapter is allowed to REFERENCE a variable it doesn't own.
        Rules:
        - Chapter 0 can reference everything (Executive Summary).
        - Other chapters can reference only if explicitly needed (can be refined).
        Currently, we assume strict ownership for *displaying* the variable as a primary item.
        Referencing in text is allowed if it doesn't restate the fact as a new revelation.
        """
        # For now, we lean on the strict 'owned variables' list for the Variables Grid.
        # References in text are harder to police statically without AI parsing, 
        # but Layer 4 will check for duplicate raw facts.
        return True 

    @staticmethod
    def get_chapter_context(chapter_id: int, registry_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns the data context filtered by ownership rules.
        """
        owned_vars = OwnershipMap.get_owned_variables(chapter_id)
        show_core = should_show_core_data(chapter_id)
        
        # If showing core data (Chapter 0), we permit core fields.
        # Otherwise, strict filtering.
        
        filtered = {}
        for k, v in registry_dict.items():
            # If it's an owned variable, include it
            if k in owned_vars:
                filtered[k] = v
            # Always include narrative source text (AI needs this to reason!)
            elif k in ['description', 'features', 'media_captions', 'media_urls']:
                filtered[k] = v
            # If it's core data and we are in Chapter 0, include it
            elif show_core and k in [
                'asking_price_eur', 'living_area_m2', 'plot_area_m2', 'build_year', 
                'energy_label', 'address', 'postal_code', 'city',
            ]:
                filtered[k] = v
            # Always pass preferences for context (AI needs it to reason)
            elif k == '_preferences':
                filtered[k] = v
            # Always pass basic identity for context
            elif k in ['address', 'id', 'funda_url']:
                filtered[k] = v
                
        return filtered
