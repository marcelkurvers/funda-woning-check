"""
CoreSummary - Mandatory Backbone Contract

=============================================================================
ARCHITECTURAL LAW: CoreSummary is the MANDATORY backbone of every report.
=============================================================================

INVARIANTS (NON-NEGOTIABLE):
1. CoreSummary is ALWAYS present in every report
2. CoreSummary is built DIRECTLY from CanonicalRegistry (after enrichment)
3. CoreSummary is NEVER derived from AI, chapters, or planes
4. CoreSummary is constructed BEFORE any AI/chapter generation
5. If CoreSummary cannot be built → the report is INVALID

If any invariant is violated, the report MUST be rejected.

WHAT CoreSummary CONTAINS:
- Required: asking_price, living_area, location (always present, may be "unknown")
- Required: match_score (always present, may be "unknown")  
- Optional: property_type, build_year, energy_label (if available from registry)
- Provenance: source for each field (registry key used)

WHAT CoreSummary DOES NOT CONTAIN:
- NO interpretation
- NO narrative
- NO AI enrichment
- ONLY factual, normalized data with provenance
"""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class DataStatus(str, Enum):
    """Status of a core summary field."""
    PRESENT = "present"       # Value is known and available
    UNKNOWN = "unknown"       # Value could not be extracted
    NOT_APPLICABLE = "n/a"    # Value does not apply to this property


class CoreField(BaseModel):
    """
    A single field in CoreSummary with mandatory provenance.
    
    Every field has:
    - value: The actual value (always present, may be formatted)
    - raw_value: The raw value from registry (for programmatic use)
    - status: Whether value is present, unknown, or n/a
    - source: The registry key this was derived from
    - unit: Optional unit for display
    """
    value: str = Field(..., description="Human-readable formatted value")
    raw_value: Any = Field(None, description="Raw value from registry")
    status: DataStatus = Field(..., description="Data availability status")
    source: str = Field(..., description="Registry key or source identifier")
    unit: Optional[str] = Field(None, description="Unit for display (e.g., m², €)")
    
    @field_validator('value', mode='before')
    @classmethod
    def ensure_string(cls, v):
        if v is None:
            return "onbekend"
        return str(v)


class CoreSummary(BaseModel):
    """
    MANDATORY Backbone Contract for every report.
    
    This object is the SINGLE SOURCE OF TRUTH for dashboard KPIs.
    It is built directly from the CanonicalRegistry after enrichment.
    It is NEVER derived from AI, chapters, or planes.
    
    FAIL-CLOSED: If this object cannot be constructed, the report is invalid.
    """
    
    # === REQUIRED FIELDS (always present) ===
    asking_price: CoreField = Field(..., description="Vraagprijs - always present")
    living_area: CoreField = Field(..., description="Woonoppervlak - always present")
    location: CoreField = Field(..., description="Locatie (samenvatting) - always present")
    match_score: CoreField = Field(..., description="Match score - always present")
    
    # === OPTIONAL FIELDS (present if available) ===
    property_type: Optional[CoreField] = Field(None, description="Woningtype")
    build_year: Optional[CoreField] = Field(None, description="Bouwjaar")
    energy_label: Optional[CoreField] = Field(None, description="Energielabel")
    plot_area: Optional[CoreField] = Field(None, description="Perceeloppervlak")
    bedrooms: Optional[CoreField] = Field(None, description="Aantal slaapkamers")
    
    # === METADATA ===
    completeness_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Fraction of core fields that have known values (0.0-1.0)"
    )
    registry_entry_count: int = Field(
        ...,
        ge=0,
        description="Total number of entries in the registry when this was built"
    )
    provenance: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of field names to their source registry keys"
    )
    
    def has_valid_price(self) -> bool:
        """Check if asking price has a valid known value."""
        return self.asking_price.status == DataStatus.PRESENT
    
    def has_valid_area(self) -> bool:
        """Check if living area has a valid known value."""
        return self.living_area.status == DataStatus.PRESENT
    
    def get_display_values(self) -> Dict[str, str]:
        """Get all display values for dashboard rendering."""
        values = {
            "asking_price": self.asking_price.value,
            "living_area": self.living_area.value,
            "location": self.location.value,
            "match_score": self.match_score.value,
        }
        if self.property_type:
            values["property_type"] = self.property_type.value
        if self.build_year:
            values["build_year"] = self.build_year.value
        if self.energy_label:
            values["energy_label"] = self.energy_label.value
        if self.plot_area:
            values["plot_area"] = self.plot_area.value
        if self.bedrooms:
            values["bedrooms"] = self.bedrooms.value
        return values


class CoreSummaryMissing(Exception):
    """
    Raised when CoreSummary cannot be constructed.
    
    This is a FATAL error - the report is INVALID.
    """
    pass


class CoreSummaryBuilder:
    """
    Builder for CoreSummary from CanonicalRegistry.
    
    FAIL-CLOSED: This builder NEVER fails silently.
    - Missing required data → field status = UNKNOWN (not error)
    - Builder always produces a valid CoreSummary
    - Caller can check completeness_score to assess data quality
    """
    
    @staticmethod
    def build_from_registry(registry: Any) -> CoreSummary:
        """
        Build CoreSummary directly from a CanonicalRegistry.
        
        Args:
            registry: A CanonicalRegistry instance (must be locked)
            
        Returns:
            CoreSummary: Always returns a valid CoreSummary
            
        Note:
            This method NEVER raises exceptions.
            Missing data is represented as status=UNKNOWN.
        """
        from backend.domain.registry import CanonicalRegistry, RegistryEntry
        
        provenance = {}
        
        def get_field(
            key: str, 
            display_name: str,
            unit: Optional[str] = None,
            format_func=None
        ) -> CoreField:
            """Extract a field from registry with proper status tracking."""
            entry: Optional[RegistryEntry] = registry.get(key)
            
            if entry is None or entry.value is None:
                provenance[display_name] = key
                return CoreField(
                    value="onbekend",
                    raw_value=None,
                    status=DataStatus.UNKNOWN,
                    source=key,
                    unit=unit
                )
            
            raw_value = entry.value
            
            # Format value for display
            if format_func:
                display_value = format_func(raw_value)
            elif unit:
                display_value = f"{raw_value} {unit}"
            else:
                display_value = str(raw_value)
            
            provenance[display_name] = key
            
            return CoreField(
                value=display_value,
                raw_value=raw_value,
                status=DataStatus.PRESENT,
                source=key,
                unit=unit
            )
        
        def format_price(value) -> str:
            """Format price in European notation."""
            try:
                if isinstance(value, str):
                    # Already formatted
                    if '€' in value:
                        return value
                    # Try to parse
                    clean = value.replace('€', '').replace('.', '').replace(',', '').strip()
                    value = int(clean)
                if isinstance(value, (int, float)):
                    return f"€ {int(value):,}".replace(',', '.')
                return str(value)
            except:
                return str(value) if value else "onbekend"
        
        def format_area(value) -> str:
            """Format area in m²."""
            try:
                if isinstance(value, str):
                    if 'm²' in value or 'm2' in value:
                        return value
                    clean = value.replace('m²', '').replace('m2', '').strip()
                    value = int(clean)
                if isinstance(value, (int, float)):
                    return f"{int(value)} m²"
                return str(value)
            except:
                return str(value) if value else "onbekend"
        
        def format_percentage(value) -> str:
            """Format match score as percentage."""
            try:
                if isinstance(value, str):
                    if '%' in value:
                        return value
                    value = float(value)
                if isinstance(value, (int, float)):
                    return f"{int(value)}%"
                return str(value)
            except:
                return str(value) if value else "onbekend"
        
        # === BUILD REQUIRED FIELDS ===
        
        asking_price = get_field(
            "asking_price_eur", 
            "asking_price",
            unit="€",
            format_func=format_price
        )
        
        living_area = get_field(
            "living_area_m2",
            "living_area", 
            unit="m²",
            format_func=format_area
        )
        
        # Location: try address first, then city/municipality
        address_entry = registry.get("address")
        if address_entry and address_entry.value:
            location_value = str(address_entry.value)
            # Extract just city/neighborhood if full address
            parts = location_value.split(',')
            if len(parts) > 1:
                location_display = parts[-1].strip()  # Last part usually city
            else:
                location_display = location_value
            location = CoreField(
                value=location_display,
                raw_value=address_entry.value,
                status=DataStatus.PRESENT,
                source="address",
                unit=None
            )
            provenance["location"] = "address"
        else:
            location = CoreField(
                value="onbekend",
                raw_value=None,
                status=DataStatus.UNKNOWN,
                source="address",
                unit=None
            )
            provenance["location"] = "address"
        
        match_score = get_field(
            "total_match_score",
            "match_score",
            format_func=format_percentage
        )
        
        # === BUILD OPTIONAL FIELDS ===
        
        property_type = None
        type_entry = registry.get("property_type")
        if type_entry and type_entry.value:
            property_type = CoreField(
                value=str(type_entry.value),
                raw_value=type_entry.value,
                status=DataStatus.PRESENT,
                source="property_type",
                unit=None
            )
            provenance["property_type"] = "property_type"
        
        build_year = None
        year_entry = registry.get("build_year")
        if year_entry and year_entry.value:
            build_year = CoreField(
                value=str(year_entry.value),
                raw_value=year_entry.value,
                status=DataStatus.PRESENT,
                source="build_year",
                unit=None
            )
            provenance["build_year"] = "build_year"
        
        energy_label = None
        label_entry = registry.get("energy_label")
        if label_entry and label_entry.value:
            energy_label = CoreField(
                value=str(label_entry.value).upper(),
                raw_value=label_entry.value,
                status=DataStatus.PRESENT,
                source="energy_label",
                unit=None
            )
            provenance["energy_label"] = "energy_label"
        
        plot_area = None
        plot_entry = registry.get("plot_area_m2")
        if plot_entry and plot_entry.value:
            plot_area = CoreField(
                value=format_area(plot_entry.value),
                raw_value=plot_entry.value,
                status=DataStatus.PRESENT,
                source="plot_area_m2",
                unit="m²"
            )
            provenance["plot_area"] = "plot_area_m2"
        
        bedrooms = None
        bed_entry = registry.get("bedrooms")
        if bed_entry and bed_entry.value:
            bedrooms = CoreField(
                value=str(bed_entry.value),
                raw_value=bed_entry.value,
                status=DataStatus.PRESENT,
                source="bedrooms",
                unit=None
            )
            provenance["bedrooms"] = "bedrooms"
        
        # === CALCULATE COMPLETENESS ===
        
        required_fields = [asking_price, living_area, location, match_score]
        optional_fields = [property_type, build_year, energy_label, plot_area, bedrooms]
        
        all_fields = required_fields + [f for f in optional_fields if f is not None]
        present_count = sum(1 for f in all_fields if f.status == DataStatus.PRESENT)
        total_count = len(all_fields)
        
        completeness = present_count / total_count if total_count > 0 else 0.0
        
        # === BUILD CORE SUMMARY ===
        
        return CoreSummary(
            asking_price=asking_price,
            living_area=living_area,
            location=location,
            match_score=match_score,
            property_type=property_type,
            build_year=build_year,
            energy_label=energy_label,
            plot_area=plot_area,
            bedrooms=bedrooms,
            completeness_score=round(completeness, 2),
            registry_entry_count=len(registry.get_all()),
            provenance=provenance
        )
    
    @staticmethod
    def create_empty() -> CoreSummary:
        """
        Create a CoreSummary with all fields set to UNKNOWN.
        
        This is used when no valid registry is available.
        It does NOT attempt to reconstruct data from raw dicts.
        
        Returns:
            CoreSummary: Valid object but with all fields statuses=UNKNOWN
        """
        provenance = {"note": "created_empty"}
        
        def unknown_field(name: str) -> CoreField:
            return CoreField(
                value="onbekend",
                raw_value=None,
                status=DataStatus.UNKNOWN,
                source="missing_registry",
                unit=None
            )
            
        return CoreSummary(
            asking_price=unknown_field("asking_price"),
            living_area=unknown_field("living_area"),
            location=unknown_field("location"),
            match_score=unknown_field("match_score"),
            property_type=None,
            build_year=None,
            energy_label=None,
            plot_area=None,
            bedrooms=None,
            completeness_score=0.0,
            registry_entry_count=0,
            provenance=provenance
        )
