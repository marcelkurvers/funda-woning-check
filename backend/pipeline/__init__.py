"""
Pipeline Package - The Execution Spine

This package contains all components for the enforced execution pipeline.

IMPORTANT: All report generation MUST flow through PipelineSpine.
Direct use of IntelligenceEngine, DataEnricher, or chapter classes
is prohibited for production report generation.

Usage:
    from backend.pipeline import execute_pipeline
    
    output = execute_pipeline(
        run_id="abc123",
        raw_data={"asking_price_eur": 500000, ...},
        preferences={"marcel": {...}, "petra": {...}}
    )
"""

from backend.pipeline.spine import (
    PipelineSpine,
    execute_pipeline
)
from backend.domain.pipeline_context import (
    PipelineContext,
    PipelineViolation,
    ValidationFailure,
    create_pipeline_context
)

__all__ = [
    "PipelineSpine",
    "execute_pipeline",
    "PipelineContext",
    "PipelineViolation",
    "ValidationFailure",
    "create_pipeline_context"
]
