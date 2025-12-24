"""
Backend Domain Module

This module contains all domain models, validators, and generators for the
4-Plane Enforced Analytical Report System.
"""

# 4-Plane Cognitive Model exports
from backend.domain.plane_models import (
    PlaneAVisualModel,
    PlaneBNarrativeModel,
    PlaneCFactModel,
    PlaneDPreferenceModel,
    ChapterPlaneComposition,
    FourPlaneReport,
    PlaneViolationError,
    PlaneType,
    VisualDataPoint,
    ChartConfig,
    FactualKPI,
    PersonaScore,
    PreferenceComparison,
)

from backend.domain.plane_validator import (
    PlaneValidator,
    ViolationType,
    PlaneViolation,
    create_validated_chapter,
    validate_plane_content,
)

from backend.domain.plane_generator import (
    generate_four_plane_chapter,
    generate_plane_a,
    generate_plane_b,
    generate_plane_c,
    generate_plane_d,
    PLANE_B_SYSTEM_PROMPT,
)

# Core models
from backend.domain.models import (
    ChapterOutput,
    NarrativeContract,
    PropertyCore,
    UIComponent,
    ChapterLayout,
    AIProvenance,
)

# Registry
from backend.domain.registry import (
    CanonicalRegistry,
    RegistryEntry,
    RegistryType,
    RegistryConflict,
    RegistryLocked,
)

__all__ = [
    # 4-Plane Models
    "PlaneAVisualModel",
    "PlaneBNarrativeModel", 
    "PlaneCFactModel",
    "PlaneDPreferenceModel",
    "ChapterPlaneComposition",
    "FourPlaneReport",
    "PlaneViolationError",
    "PlaneType",
    "VisualDataPoint",
    "ChartConfig",
    "FactualKPI",
    "PersonaScore",
    "PreferenceComparison",
    # Validator
    "PlaneValidator",
    "ViolationType",
    "PlaneViolation",
    "create_validated_chapter",
    "validate_plane_content",
    # Generator
    "generate_four_plane_chapter",
    "generate_plane_a",
    "generate_plane_b",
    "generate_plane_c",
    "generate_plane_d",
    "PLANE_B_SYSTEM_PROMPT",
    # Core Models
    "ChapterOutput",
    "NarrativeContract",
    "PropertyCore",
    "UIComponent",
    "ChapterLayout",
    "AIProvenance",
    # Registry
    "CanonicalRegistry",
    "RegistryEntry",
    "RegistryType",
    "RegistryConflict",
    "RegistryLocked",
]
