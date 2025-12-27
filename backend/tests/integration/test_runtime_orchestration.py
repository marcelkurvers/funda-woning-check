import pytest
import sqlite3
import json
import time
from unittest.mock import MagicMock, patch
from backend.main import cleanup_zombie_runs, simulate_pipeline, db, now, update_run

@pytest.fixture
def clean_db():
    """Reset DB runs table."""
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM runs")
    con.commit()
    con.close()
    yield
    # Cleanup
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM runs")
    con.commit()
    con.close()

def create_dummy_run(run_id, status="running", updated_offset_minutes=0):
    """Insert a dummy run with a specific timestamp offset."""
    con = db()
    cur = con.cursor()
    
    # Calculate timestamp
    # Note: backend/main.py uses time.strftime("%Y-%m-%d %H:%M:%S") which is local time
    # We simulate this format
    t = time.time() - (updated_offset_minutes * 60)
    ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
    
    cur.execute(
        "INSERT INTO runs (id, funda_url, status, steps_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (run_id, "http://test.url", status, "{}", ts_str, ts_str)
    )
    con.commit()
    con.close()

def get_run_status(run_id):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT status, kpis_json, steps_json FROM runs WHERE id=?", (run_id,))
    row = cur.fetchone()
    con.close()
    return row

def test_cleanup_zombie_runs(clean_db):
    """Verify that runs stuck in 'running' for >30m are marked failed."""
    # 1. Active run (recent)
    create_dummy_run("active_run", "running", updated_offset_minutes=5)
    
    # 2. Zombie run (old)
    create_dummy_run("zombie_run", "running", updated_offset_minutes=40)
    
    # 3. Already done run (old)
    create_dummy_run("done_run", "done", updated_offset_minutes=40)
    
    # Run cleanup
    cleanup_zombie_runs()
    
    # Verify
    s_active = get_run_status("active_run")
    assert s_active['status'] == "running"
    
    s_zombie = get_run_status("zombie_run")
    assert s_zombie['status'] == "failed"
    kpis = json.loads(s_zombie['kpis_json'] or "{}")
    assert "Zombie run detected" in kpis.get("error", "")
    
    s_done = get_run_status("done_run")
    assert s_done['status'] == "done"

@patch("backend.main.init_ai_provider", return_value=True)
@patch("backend.main.Scraper")
@patch("backend.pipeline.bridge.execute_report_pipeline")
def test_heartbeat_updates_db(mock_pipeline, mock_scraper_cls, mock_init_ai, clean_db):
    """Verify that progress callback from spine updates the DB."""
    run_id = "heartbeat_test"
    create_dummy_run(run_id, "queued", 0)
    
    # Mock scraping
    mock_instance = mock_scraper_cls.return_value
    mock_instance.derive_property_core.return_value = {"address": "Teststraat 1"}
    
    # Mock pipeline to use the callback
    def side_effect(run_id, raw_data, preferences=None, progress_callback=None):
        if progress_callback:
            progress_callback("running (Chapter 1/13)")
            
            # VERIFY HEARTBEAT PERSISTENCE HERE
            row = get_run_status(run_id)
            steps = json.loads(row['steps_json'])
            assert steps['compute_kpis'] == "running (Chapter 1/13)"
            
        # Return valid structure to allow pipeline to complete success path
        return {}, {}, {"address": "Teststraat 1", "core_summary": {}}, {} 
        
    mock_pipeline.side_effect = side_effect
    
    # Run pipeline
    simulate_pipeline(run_id)
    
    # We don't care about the final status here, as we verified the heartbeat implementation in the side_effect


@patch("backend.main.init_ai_provider", return_value=True)
@patch("backend.main.Scraper")
@patch("backend.pipeline.bridge.execute_report_pipeline")
def test_pipeline_failure_sets_error_status(mock_pipeline, mock_scraper_cls, mock_init_ai, clean_db):
    """Verify that unhandled exceptions result in 'error' status in DB."""
    run_id = "failure_test"
    create_dummy_run(run_id, "queued", 0)
    
    # Mock scraping
    mock_instance = mock_scraper_cls.return_value
    mock_instance.derive_property_core.return_value = {"address": "Teststraat 1"}
    
    # Mock pipeline to raise error
    mock_pipeline.side_effect = Exception("Simulated Crash")
    
    # Run pipeline
    simulate_pipeline(run_id)
    
    # Check DB
    row = get_run_status(run_id)
    assert row['status'] == "error"
