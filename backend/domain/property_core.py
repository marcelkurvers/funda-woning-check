"""
Property Core Data Model

This module defines the centralized property data structure that is parsed once
and shared across all chapters. This prevents repetition and ensures consistency.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class PropertyCoreData:
    """
    Core property information that is parsed once and shared across all chapters.
    This data appears ONLY in Chapter 0 (Executive Summary) with full AI interpretation.
    
    Other chapters should show ONLY their domain-specific variables.
    """
    
    # Identity
    address: str = "Onbekend Adres"
    postal_code: Optional[str] = None
    city: Optional[str] = None
    
    # Pricing
    asking_price_eur: int = 0
    price_per_m2: int = 0
    woz_value: Optional[int] = None
    
    # Physical
    living_area_m2: int = 0
    plot_area_m2: int = 0
    volume_m3: Optional[int] = None
    property_type: str = "Woning"
    build_year: int = 2000
    
    # Rooms
    num_rooms: int = 0
    num_bedrooms: int = 0
    num_bathrooms: int = 0
    
    # Energy & Sustainability
    energy_label: str = "?"
    insulation: Optional[str] = None
    heating: Optional[str] = None
    
    # Legal & Financial
    ownership: Optional[str] = None
    service_costs: Optional[int] = None
    listed_since: Optional[str] = None
    acceptance: Optional[str] = None
    
    # Outdoor
    garden: Optional[str] = None
    garage: Optional[str] = None
    parking: Optional[str] = None
    
    # Marcel & Petra Preference Match Scores
    marcel_match_score: float = 0.0
    petra_match_score: float = 0.0
    combined_match_score: float = 0.0
    
    # Preference-specific matches
    marcel_matches: List[str] = field(default_factory=list)
    marcel_misses: List[str] = field(default_factory=list)
    petra_matches: List[str] = field(default_factory=list)
    petra_misses: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "address": self.address,
            "postal_code": self.postal_code,
            "city": self.city,
            "asking_price_eur": self.asking_price_eur,
            "price_per_m2": self.price_per_m2,
            "woz_value": self.woz_value,
            "living_area_m2": self.living_area_m2,
            "plot_area_m2": self.plot_area_m2,
            "volume_m3": self.volume_m3,
            "property_type": self.property_type,
            "build_year": self.build_year,
            "num_rooms": self.num_rooms,
            "num_bedrooms": self.num_bedrooms,
            "num_bathrooms": self.num_bathrooms,
            "energy_label": self.energy_label,
            "insulation": self.insulation,
            "heating": self.heating,
            "ownership": self.ownership,
            "service_costs": self.service_costs,
            "listed_since": self.listed_since,
            "acceptance": self.acceptance,
            "garden": self.garden,
            "garage": self.garage,
            "parking": self.parking,
            "marcel_match_score": self.marcel_match_score,
            "petra_match_score": self.petra_match_score,
            "combined_match_score": self.combined_match_score,
            "marcel_matches": self.marcel_matches,
            "marcel_misses": self.marcel_misses,
            "petra_matches": self.petra_matches,
            "petra_misses": self.petra_misses,
        }
    
    @classmethod
    def from_context(cls, ctx: Dict[str, Any], preferences: Dict[str, Any]) -> 'PropertyCoreData':
        """
        Create PropertyCoreData from parser context and calculate preference matches.
        
        This is called ONCE during the analysis pipeline and the result is stored.
        """
        import re
        
        # Parse price
        price_raw = str(ctx.get('prijs', '0'))
        price_digits = re.sub(r'[^\d]', '', price_raw)
        price_val = int(price_digits) if price_digits else 0
        
        # Parse area
        size_raw = str(ctx.get('oppervlakte', '0'))
        base_size = size_raw.split(',')[0]
        size_digits = re.sub(r'[^\d]', '', base_size)
        size_val = int(size_digits) if size_digits else 1
        if size_val == 0:
            size_val = 1
        
        # Calculate price per m2
        price_m2 = round(price_val / size_val) if size_val > 0 else 0
        
        # Parse plot area
        plot_raw = str(ctx.get('perceel', '0'))
        plot_digits = re.sub(r'[^\d]', '', plot_raw)
        plot_val = int(plot_digits) if plot_digits else 0
        
        # Parse build year
        year_raw = str(ctx.get('bouwjaar', '2000'))
        year_digits = re.sub(r'[^\d]', '', year_raw)
        year_val = int(year_digits) if year_digits else 2000
        
        # Calculate preference matches
        marcel_matches, marcel_misses, marcel_score = cls._calculate_preference_match(
            ctx, preferences.get('marcel', {})
        )
        
        petra_matches, petra_misses, petra_score = cls._calculate_preference_match(
            ctx, preferences.get('petra', {})
        )
        
        combined_score = (marcel_score + petra_score) / 2
        
        return cls(
            address=ctx.get('adres', 'Onbekend Adres'),
            postal_code=ctx.get('postcode'),
            city=ctx.get('plaats'),
            asking_price_eur=price_val,
            price_per_m2=price_m2,
            woz_value=ctx.get('woz_waarde'),
            living_area_m2=size_val,
            plot_area_m2=plot_val,
            volume_m3=ctx.get('inhoud'),
            property_type=ctx.get('soort_woning', 'Woning'),
            build_year=year_val,
            num_rooms=ctx.get('aantal_kamers', 0),
            num_bedrooms=ctx.get('aantal_slaapkamers', 0),
            num_bathrooms=ctx.get('aantal_badkamers', 0),
            energy_label=ctx.get('label', '?').upper(),
            insulation=ctx.get('isolatie'),
            heating=ctx.get('verwarming'),
            ownership=ctx.get('eigendom'),
            service_costs=ctx.get('servicekosten'),
            listed_since=ctx.get('aangeboden_sinds'),
            acceptance=ctx.get('aanvaarding'),
            garden=ctx.get('tuin'),
            garage=ctx.get('garage'),
            parking=ctx.get('parkeerfaciliteiten'),
            marcel_match_score=marcel_score,
            petra_match_score=petra_score,
            combined_match_score=combined_score,
            marcel_matches=marcel_matches,
            marcel_misses=marcel_misses,
            petra_matches=petra_matches,
            petra_misses=petra_misses,
        )
    
    @staticmethod
    def _calculate_preference_match(ctx: Dict[str, Any], person_prefs: Dict[str, Any]) -> tuple[List[str], List[str], float]:
        """
        Calculate how well the property matches a person's preferences.
        
        Returns:
            (matches, misses, score_percentage)
        """
        priorities = person_prefs.get('priorities', [])
        hidden_priorities = person_prefs.get('hidden_priorities', [])
        all_priorities = priorities + hidden_priorities
        
        if not all_priorities:
            return [], [], 50.0  # Default neutral score
        
        # Combine source text for searching
        description = ctx.get('description', '') or ""
        features = str(ctx.get('features', []))
        source_blob = f"{description} {features}".lower()
        
        matches = []
        misses = []
        
        for priority in all_priorities:
            p_lower = priority.lower()
            
            # Handle compound tags like "CAT6 / Ethernet"
            sub_tokens = [t.strip() for t in p_lower.split('/') if len(t.strip()) > 2]
            if not sub_tokens:
                sub_tokens = [p_lower]
            
            is_match = False
            for token in sub_tokens:
                # Specialized mappings
                if token == "solar":
                    token = "zonnepanelen"
                if token == "accu":
                    token = "batterij"
                if token == "jaren 30":
                    token = "193"  # rudimentary year check
                
                if token in source_blob:
                    is_match = True
                    break
            
            if is_match:
                matches.append(priority)
            else:
                misses.append(priority)
        
        score = (len(matches) / len(all_priorities)) * 100 if all_priorities else 50.0
        return matches, misses, round(score, 1)
    
    def get_preference_indicator(self, variable_name: str) -> Dict[str, Any]:
        """
        Get preference match indicator for a specific variable.
        
        Returns dict with:
        - marcel_relevant: bool
        - petra_relevant: bool
        - marcel_match: bool (if relevant)
        - petra_match: bool (if relevant)
        - interpretation: str (AI interpretation of the match)
        """
        # Map variable names to preference keywords
        variable_preference_map = {
            'energy_label': ['duurzaamheid', 'energie', 'label'],
            'build_year': ['bouwjaar', 'jaren 30', 'karakteristiek'],
            'heating': ['warmtepomp', 'verwarming'],
            'insulation': ['isolatie', 'dakisolatie'],
            'garden': ['tuin', 'buiten'],
            'garage': ['garage', 'parkeren'],
            'living_area_m2': ['ruimte', 'woonoppervlakte'],
        }
        
        keywords = variable_preference_map.get(variable_name, [])
        
        marcel_relevant = any(k in ' '.join(self.marcel_matches + self.marcel_misses).lower() for k in keywords)
        petra_relevant = any(k in ' '.join(self.petra_matches + self.petra_misses).lower() for k in keywords)
        
        marcel_match = marcel_relevant and any(k in ' '.join(self.marcel_matches).lower() for k in keywords)
        petra_match = petra_relevant and any(k in ' '.join(self.petra_matches).lower() for k in keywords)
        
        # Generate interpretation
        interpretation = ""
        if marcel_match and petra_match:
            interpretation = "✓ Voldoet aan wensen van zowel Marcel als Petra"
        elif marcel_match:
            interpretation = "✓ Voldoet aan Marcel's tech-eisen"
        elif petra_match:
            interpretation = "✓ Voldoet aan Petra's sfeer-wensen"
        elif marcel_relevant or petra_relevant:
            interpretation = "⚠ Aandachtspunt voor bezichtiging"
        
        return {
            'marcel_relevant': marcel_relevant,
            'petra_relevant': petra_relevant,
            'marcel_match': marcel_match,
            'petra_match': petra_match,
            'interpretation': interpretation
        }
