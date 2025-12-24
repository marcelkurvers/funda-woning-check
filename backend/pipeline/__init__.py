"""
Pipeline Package - FAIL-CLOSED Execution Spine

This package contains all components for the enforced execution pipeline.

CRITICAL ENFORCEMENT:
- All report generation MUST flow through PipelineSpine
- There are NO alternative paths
- Bypass attempts will raise exceptions
- Validation is MANDATORY and BLOCKING

Usage:
    from backend.pipeline import execute_report_pipeline
    
    chapters, kpis, enriched = execute_report_pipeline(
        run_id="abc123",
        raw_data={"asking_price_eur": 500000, ...},
        preferences={"marcel": {...}, "petra": {...}}
    )

DEPRECATED (will throw):
    - build_chapters() - BLOCKED
    - execute_pipeline() - Use execute_report_pipeline() instead
"""

from backend.pipeline.spine import (
    PipelineSpine,
    execute_report_pipeline,
    execute_pipeline,  # Deprecated but exported for backward compat errors
    is_production_mode
)
from backend.pipeline.bridge import (
    execute_report_pipeline as bridge_execute_report_pipeline
)
from backend.domain.pipeline_context import (
    PipelineContext,
    PipelineViolation,
    ValidationFailure,
    create_pipeline_context
)
from backend.domain.registry import (
    RegistryConflict,
    RegistryLocked
)

__all__ = [
    # Primary API
    "PipelineSpine",
    "execute_report_pipeline",
    
    # Context
    "PipelineContext",
    "create_pipeline_context",
    
    # Exceptions (FAIL-CLOSED)
    "PipelineViolation",
    "ValidationFailure",
    "RegistryConflict",
    "RegistryLocked",
    
    # Utilities
    "is_production_mode",
    
    # Deprecated (kept for error messages)
    "execute_pipeline"
]
