"""
Run Status API - Real-time Pipeline Telemetry

This module provides real-time status information during report generation.
It tracks:
- Current pipeline step
- Which plane is being generated
- Elapsed time per step
- Warnings and errors (especially timeouts)
- Provider and model in use
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field, asdict
from threading import Lock

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/runs", tags=["run-status"])


# === In-Memory Run Status Store ===
# This is a simple in-memory store for real-time status tracking.
# It's cleared after runs complete and is not persisted.

@dataclass
class PipelineStep:
    """Status of a single pipeline step."""
    name: str
    status: str = "pending"  # pending, running, done, error, skipped
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    elapsed_ms: Optional[int] = None
    message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class PlaneStatus:
    """Status of a 4-plane generation."""
    plane: str  # A, B, C, D
    status: str = "pending"
    chapter_id: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    word_count: Optional[int] = None


@dataclass 
class RunStatus:
    """Complete real-time status of a run."""
    run_id: str
    status: str = "initializing"  # initializing, running, done, error, validation_failed
    
    # Configuration
    provider: str = "unknown"
    model: str = "unknown"
    mode: str = "unknown"
    
    # Steps
    steps: Dict[str, PipelineStep] = field(default_factory=dict)
    current_step: Optional[str] = None
    
    # Plane generation (for 4-plane backbone)
    planes: Dict[str, PlaneStatus] = field(default_factory=dict)
    current_plane: Optional[str] = None
    current_chapter: Optional[str] = None
    
    # Timing
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    total_elapsed_ms: Optional[int] = None
    
    # Messages
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Progress
    progress_percent: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        result = asdict(self)
        # Convert steps and planes to dict format
        result["steps"] = {k: asdict(v) for k, v in self.steps.items()}
        result["planes"] = {k: asdict(v) for k, v in self.planes.items()}
        return result


class RunStatusStore:
    """Thread-safe store for run status."""
    
    def __init__(self):
        self._store: Dict[str, RunStatus] = {}
        self._lock = Lock()
    
    def create(self, run_id: str, provider: str = "unknown", model: str = "unknown", mode: str = "unknown") -> RunStatus:
        """Create a new run status entry."""
        with self._lock:
            status = RunStatus(
                run_id=run_id,
                provider=provider,
                model=model,
                mode=mode,
                started_at=time.time(),
                steps={
                    "scrape_funda": PipelineStep(name="Scrape & Parse"),
                    "dynamic_extraction": PipelineStep(name="Dynamic Extraction"),
                    "registry_build": PipelineStep(name="Registry Build"),
                    "plane_generation": PipelineStep(name="4-Plane Generation"),
                    "validation": PipelineStep(name="Validation Gate"),
                    "render": PipelineStep(name="Render Output"),
                }
            )
            self._store[run_id] = status
            return status
    
    def get(self, run_id: str) -> Optional[RunStatus]:
        """Get run status."""
        with self._lock:
            return self._store.get(run_id)
    
    def update_step(self, run_id: str, step: str, status: str, message: Optional[str] = None):
        """Update a step's status."""
        with self._lock:
            run_status = self._store.get(run_id)
            if not run_status:
                return
            
            if step not in run_status.steps:
                run_status.steps[step] = PipelineStep(name=step)
            
            step_obj = run_status.steps[step]
            
            if status == "running" and step_obj.started_at is None:
                step_obj.started_at = time.time()
            elif status in ("done", "error", "skipped"):
                step_obj.completed_at = time.time()
                if step_obj.started_at:
                    step_obj.elapsed_ms = int((step_obj.completed_at - step_obj.started_at) * 1000)
            
            step_obj.status = status
            if message:
                step_obj.message = message
            
            run_status.current_step = step if status == "running" else run_status.current_step
            
            # Calculate progress
            total_steps = len(run_status.steps)
            done_steps = sum(1 for s in run_status.steps.values() if s.status in ("done", "skipped"))
            run_status.progress_percent = int((done_steps / total_steps) * 100) if total_steps > 0 else 0
    
    def update_plane(self, run_id: str, plane: str, chapter_id: str, status: str, word_count: Optional[int] = None):
        """Update plane generation status."""
        with self._lock:
            run_status = self._store.get(run_id)
            if not run_status:
                return
            
            plane_key = f"{chapter_id}_{plane}"
            if plane_key not in run_status.planes:
                run_status.planes[plane_key] = PlaneStatus(plane=plane, chapter_id=chapter_id)
            
            plane_obj = run_status.planes[plane_key]
            
            if status == "running" and plane_obj.started_at is None:
                plane_obj.started_at = time.time()
            elif status in ("done", "error"):
                plane_obj.completed_at = time.time()
            
            plane_obj.status = status
            if word_count:
                plane_obj.word_count = word_count
            
            run_status.current_plane = plane if status == "running" else run_status.current_plane
            run_status.current_chapter = chapter_id if status == "running" else run_status.current_chapter
    
    def add_warning(self, run_id: str, warning: str):
        """Add a warning message."""
        with self._lock:
            run_status = self._store.get(run_id)
            if run_status:
                run_status.warnings.append(f"[{datetime.now().strftime('%H:%M:%S')}] {warning}")
    
    def add_error(self, run_id: str, error: str):
        """Add an error message."""
        with self._lock:
            run_status = self._store.get(run_id)
            if run_status:
                run_status.errors.append(f"[{datetime.now().strftime('%H:%M:%S')}] {error}")
    
    def complete(self, run_id: str, status: str = "done"):
        """Mark a run as complete."""
        with self._lock:
            run_status = self._store.get(run_id)
            if run_status:
                run_status.status = status
                run_status.completed_at = time.time()
                if run_status.started_at:
                    run_status.total_elapsed_ms = int((run_status.completed_at - run_status.started_at) * 1000)
                run_status.progress_percent = 100 if status == "done" else run_status.progress_percent
    
    def cleanup_old(self, max_age_seconds: int = 3600):
        """Remove old run statuses."""
        with self._lock:
            now = time.time()
            to_remove = []
            for run_id, status in self._store.items():
                if status.completed_at and (now - status.completed_at) > max_age_seconds:
                    to_remove.append(run_id)
            for run_id in to_remove:
                del self._store[run_id]


# Global store instance
run_status_store = RunStatusStore()


# === API Endpoints ===

class RunStatusResponse(BaseModel):
    """API response model for run status."""
    run_id: str
    status: str
    provider: str
    model: str
    mode: str
    current_step: Optional[str]
    current_chapter: Optional[str]
    current_plane: Optional[str]
    progress_percent: int
    total_elapsed_ms: Optional[int]
    steps: Dict[str, Dict[str, Any]]
    planes: Dict[str, Dict[str, Any]]
    warnings: List[str]
    errors: List[str]


@router.get("/{run_id}/live-status")
async def get_live_status(run_id: str):
    """
    Get real-time status of a running pipeline.
    
    Use this endpoint for live updates during report generation.
    Poll every 500ms-1000ms for smooth UI updates.
    
    Returns:
        - Current step and progress
        - Which plane is being generated
        - Elapsed time per step
        - Warnings and errors
        - Provider/model/mode in use
    """
    status = run_status_store.get(run_id)
    
    if not status:
        # Fall back to database status
        from backend.main import get_run_row
        row = get_run_row(run_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Run not found")
        
        # Build basic status from database
        steps = json.loads(row["steps_json"]) if row["steps_json"] else {}
        
        return {
            "run_id": run_id,
            "status": row["status"],
            "provider": "unknown",
            "model": "unknown",
            "mode": "unknown",
            "current_step": None,
            "current_chapter": None,
            "current_plane": None,
            "progress_percent": sum(1 for s in steps.values() if s == "done") * 20,
            "total_elapsed_ms": None,
            "steps": {k: {"name": k, "status": v} for k, v in steps.items()},
            "planes": {},
            "warnings": [],
            "errors": [],
            "source": "database"
        }
    
    return {
        **status.to_dict(),
        "source": "realtime"
    }


@router.get("/{run_id}/step-timing")
async def get_step_timing(run_id: str):
    """Get detailed timing breakdown for each step."""
    status = run_status_store.get(run_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Run status not found")
    
    timings = []
    for step_name, step in status.steps.items():
        timings.append({
            "step": step_name,
            "name": step.name,
            "status": step.status,
            "elapsed_ms": step.elapsed_ms,
            "started_at": datetime.fromtimestamp(step.started_at).isoformat() if step.started_at else None,
            "completed_at": datetime.fromtimestamp(step.completed_at).isoformat() if step.completed_at else None,
        })
    
    return {
        "run_id": run_id,
        "total_elapsed_ms": status.total_elapsed_ms,
        "timings": timings
    }


@router.get("/{run_id}/plane-status")
async def get_plane_status(run_id: str):
    """Get detailed status of 4-plane generation."""
    status = run_status_store.get(run_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Run status not found")
    
    planes_by_chapter = {}
    for key, plane in status.planes.items():
        chapter_id = plane.chapter_id
        if chapter_id not in planes_by_chapter:
            planes_by_chapter[chapter_id] = {}
        planes_by_chapter[chapter_id][plane.plane] = {
            "status": plane.status,
            "word_count": plane.word_count,
            "elapsed_ms": int((plane.completed_at - plane.started_at) * 1000) if plane.started_at and plane.completed_at else None
        }
    
    return {
        "run_id": run_id,
        "current_chapter": status.current_chapter,
        "current_plane": status.current_plane,
        "chapters": planes_by_chapter
    }


# === Integration Functions (called from pipeline) ===

def start_run_tracking(run_id: str, provider: str, model: str, mode: str):
    """Initialize run tracking. Call at pipeline start."""
    return run_status_store.create(run_id, provider, model, mode)


def track_step(run_id: str, step: str, status: str, message: Optional[str] = None):
    """Update step status. Call from pipeline."""
    run_status_store.update_step(run_id, step, status, message)


def track_plane(run_id: str, plane: str, chapter_id: str, status: str, word_count: Optional[int] = None):
    """Update plane generation status. Call from 4-plane backbone."""
    run_status_store.update_plane(run_id, plane, chapter_id, status, word_count)


def track_warning(run_id: str, warning: str):
    """Add warning. Call when timeout or degradation occurs."""
    run_status_store.add_warning(run_id, warning)


def track_error(run_id: str, error: str):
    """Add error. Call on failures."""
    run_status_store.add_error(run_id, error)


def complete_run_tracking(run_id: str, status: str = "done"):
    """Complete run tracking. Call at pipeline end."""
    run_status_store.complete(run_id, status)
