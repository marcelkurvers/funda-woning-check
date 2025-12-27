# TEST_REGIME: STRUCTURAL
# REQUIRES: offline_structural_mode=True
"""
Tests for async pipeline processing and status polling
"""
import pytest
import json
import time
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys

# Set test mode BEFORE imports
os.environ["PIPELINE_TEST_MODE"] = "true"

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from main import app, simulate_pipeline, executor


@pytest.fixture(autouse=True)
def governance_setup():
    """T4gB-FIX: Apply governance singleton pattern for all tests in this module."""
    from backend.domain.governance_state import GovernanceStateManager
    GovernanceStateManager._instance = None
    
    from backend.domain.governance_state import get_governance_state
    from backend.domain.config import GovernanceConfig, DeploymentEnvironment
    gov_state = get_governance_state()
    gov_state.apply_config(
        GovernanceConfig(
            environment=DeploymentEnvironment.TEST,
            offline_structural_mode=True
        ),
        source="test_async_pipeline"
    )
    
    yield
    
    GovernanceStateManager._instance = None


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_run_id():
    """Generate a mock run ID"""
    return "test-run-123"


class TestAsyncPipeline:
    """Test suite for async pipeline processing"""

    def test_start_run_returns_immediately(self, client, mock_run_id):
        """Test that /runs/{run_id}/start returns immediately without blocking"""
        # First create a run
        create_response = client.post("/api/runs", json={
            "funda_url": "manual-paste",
            "funda_html": "<html><body>Test property</body></html>"
        })
        assert create_response.status_code == 200
        run_id = create_response.json()["run_id"]

        # Start the run
        start_time = time.time()
        start_response = client.post(f"/api/runs/{run_id}/start")
        elapsed_time = time.time() - start_time

        # Should return immediately (< 1 second)
        assert elapsed_time < 1.0
        assert start_response.status_code == 200
        assert start_response.json()["ok"] is True
        assert start_response.json()["status"] == "processing"

    def test_status_polling_endpoint_exists(self, client, mock_run_id):
        """Test that status polling endpoint is accessible"""
        # Create a run first
        create_response = client.post("/api/runs", json={
            "funda_url": "manual-paste",
            "funda_html": "<html><body>Test property</body></html>"
        })
        run_id = create_response.json()["run_id"]

        # Check status endpoint
        status_response = client.get(f"/api/runs/{run_id}/status")
        assert status_response.status_code == 200

        data = status_response.json()
        assert "run_id" in data
        assert "status" in data
        assert "steps" in data
        assert "progress" in data

    def test_status_polling_progress_calculation(self, client):
        """Test that progress is calculated correctly"""
        # Create a run
        create_response = client.post("/api/runs", json={
            "funda_url": "manual-paste",
            "funda_html": "<html><body>Test property</body></html>"
        })
        run_id = create_response.json()["run_id"]

        # Get status
        status_response = client.get(f"/api/runs/{run_id}/status")
        data = status_response.json()

        progress = data["progress"]
        assert "current" in progress
        assert "total" in progress
        assert "percent" in progress
        assert progress["total"] > 0
        assert 0 <= progress["percent"] <= 100

    def test_status_endpoint_404_for_nonexistent_run(self, client):
        """Test that status endpoint returns 404 for non-existent run"""
        response = client.get("/api/runs/nonexistent-id/status")
        assert response.status_code == 404

    def test_pipeline_runs_in_background(self, client):
        """
        Test that pipeline executes in background thread.
        Uses real pipeline with minimal data to test actual async behavior.
        """
        # Create run with minimal but valid HTML
        create_response = client.post("/api/runs", json={
            "funda_url": "manual-paste",
            "funda_html": """
                <html><body>
                <h1>Test Property</h1>
                <div>Prijs: €500.000</div>
                <div>Woonoppervlakte: 100 m²</div>
                </body></html>
            """
        })
        run_id = create_response.json()["run_id"]

        # Start pipeline - should return immediately (async)
        start_time = time.time()
        start_response = client.post(f"/api/runs/{run_id}/start")
        response_time = time.time() - start_time

        assert start_response.status_code == 200
        assert response_time < 1.0, "Start endpoint should return immediately (async)"

        # Check initial status - should be queued or running
        status_response = client.get(f"/api/runs/{run_id}/status")
        initial_status = status_response.json()["status"]
        assert initial_status in ["queued", "running", "processing"], \
            f"Expected async status, got: {initial_status}"

        # Wait for completion with reasonable timeout
        # Note: May fail or validate_failed due to missing AI provider - both are acceptable
        max_wait = 10
        start_wait = time.time()

        final_status = None
        while (time.time() - start_wait) < max_wait:
            status_response = client.get(f"/api/runs/{run_id}/status")
            status_data = status_response.json()
            status = status_data["status"]

            if status in ["done", "error", "validation_failed"]:
                final_status = status
                break

            time.sleep(0.2)

        # Verify pipeline reached a terminal state (success or expected failure)
        assert final_status is not None, \
            f"Pipeline did not complete within {max_wait}s"
        assert final_status in ["done", "error", "validation_failed"], \
            f"Unexpected terminal status: {final_status}"


    def test_multiple_concurrent_pipelines(self, client):
        """Test that multiple pipelines can run concurrently"""
        run_ids = []

        # Create multiple runs
        for i in range(3):
            response = client.post("/api/runs", json={
                "funda_url": "manual-paste",
                "funda_html": f"<html><body>Property {i}</body></html>"
            })
            run_ids.append(response.json()["run_id"])

        # Start all pipelines
        for run_id in run_ids:
            response = client.post(f"/api/runs/{run_id}/start")
            assert response.status_code == 200

        # All should be processing or queued
        for run_id in run_ids:
            status = client.get(f"/api/runs/{run_id}/status")
            assert status.json()["status"] in ["queued", "running", "done"]


class TestThreadExecutor:
    """Test suite for thread executor configuration"""

    def test_executor_exists(self):
        """Test that thread executor is initialized"""
        from concurrent.futures import ThreadPoolExecutor
        assert executor is not None
        assert isinstance(executor, ThreadPoolExecutor)

    def test_simulate_pipeline_callable(self):
        """Test that simulate_pipeline function is callable"""
        assert callable(simulate_pipeline)


class TestBackwardCompatibility:
    """Test that new features don't break existing functionality"""

    # TODO(T4gE): Determine if this test should be STRUCTURAL with mocking or AI regime
    # EVIDENCE: T4gC execution shows this test triggers full pipeline → AI narrative generation → fail
    def test_report_endpoint_still_works(self, client):
        """Test that /runs/{run_id}/report endpoint still functions"""
        # Create and process a run
        create_response = client.post("/api/runs", json={
            "funda_url": "manual-paste",
            "funda_html": "<html><body>Test property</body></html>"
        })
        run_id = create_response.json()["run_id"]

        # Start and wait for completion
        client.post(f"/api/runs/{run_id}/start")
        # Poll for completion
        max_wait = 10
        start_wait = time.time()
        while (time.time() - start_wait) < max_wait:
            status = client.get(f"/api/runs/{run_id}/status").json()["status"]
            if status in ["done", "error", "validation_failed"]:
                break
            time.sleep(0.1)

        # Report endpoint should still work
        report_response = client.get(f"/api/runs/{run_id}/report")
        assert report_response.status_code == 200

        data = report_response.json()
        assert "property_core" in data
        assert "chapters" in data

    def test_create_run_endpoint_unchanged(self, client):
        """Test that creating runs still works as before"""
        response = client.post("/api/runs", json={
            "funda_url": "manual-paste",
            "funda_html": "<html><body>Test</body></html>"
        })

        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert "status" in data
        assert data["status"] == "queued"
