# TEST_REGIME: STRUCTURAL
# REQUIRES: None (API endpoint tests)
"""
Tests for Configuration Management API.
"""
import pytest
from fastapi.testclient import TestClient
import json
import sqlite3
import os
from unittest.mock import patch

from main import app
from config.settings import get_settings, reset_settings

client = None

@pytest.fixture(autouse=True)
def setup_config_test(tmp_path):
    """Set up a temporary database for config tests."""
    global client
    db_path = tmp_path / "test_app.db"
    
    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Force use of this DB via environment variable
    with patch.dict(os.environ, {"APP_DB": str(db_path), "DATABASE_URL": str(db_path)}):
        # Initialize the DB with the required table
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS kv_store (key TEXT PRIMARY KEY, value TEXT)")
        conn.commit()
        conn.close()
        
        # Reset settings and create client within patched environment
        reset_settings()
        from backend.main import app
        client = TestClient(app)
        
        yield
        
        reset_settings()

def test_get_full_config():
    """Test GET /api/config returns full configuration."""
    response = client.get("/api/config/")
    assert response.status_code == 200
    data = response.json()
    assert "ai" in data
    assert "market" in data
    assert "preferences" in data
    assert "database_url" in data

def test_get_config_section():
    """Test GET /api/config/{section} returns section data."""
    response = client.get("/api/config/ai")
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "model" in data

def test_get_config_section_not_found():
    """Test GET /api/config/{invalid} returns 404."""
    response = client.get("/api/config/invalid_section")
    assert response.status_code == 404

def test_get_config_value():
    """Test GET /api/config/{section}/{key} returns single value."""
    response = client.get("/api/config/ai/provider")
    assert response.status_code == 200
    assert response.json() == {"provider": "ollama"}

def test_update_config_bulk():
    """Test POST /api/config/ updates multiple sections and persists."""
    update_data = {
        "ai": {"timeout": 45, "model": "gpt-4"},
        "market": {"avg_price_m2": 6000}
    }
    response = client.post("/api/config/", json=update_data)
    assert response.status_code == 200
    assert "ai" in response.json()["sections"]
    assert "market" in response.json()["sections"]

    # Verify memory update
    settings = get_settings()
    assert settings.ai.timeout == 45
    assert settings.ai.model == "gpt-4"
    assert settings.market.avg_price_m2 == 6000

    # Verify persistence (by resetting settings and reloading)
    reset_settings()
    settings = get_settings()
    assert settings.ai.timeout == 45
    assert settings.market.avg_price_m2 == 6000

def test_update_config_value():
    """Test PUT /api/config/{section}/{key} updates single value."""
    response = client.put("/api/config/ai/timeout?value=50")
    # Note: Value passed as query param or body depending on implementation
    # My implementation uses : value: Any which fastapi interprets as query or body
    # Let's try as query param first.
    
    # Wait, my implementation is: async def update_config_value(section: str, key: str, value: Any):
    # Without Body(), Any is a query param.
    
    response = client.put("/api/config/ai/timeout", json=50)
    assert response.status_code == 200
    assert response.json()["new_value"] == 50

    # Verify persistence
    reset_settings()
    assert get_settings().ai.timeout == 50

def test_update_config_invalid_section():
    """Test updating non-existent section."""
    response = client.put("/api/config/unknown/key", json="val")
    assert response.status_code == 404

def test_update_config_invalid_key():
    """Test updating non-existent key."""
    response = client.put("/api/config/ai/unknown_key", json="val")
    assert response.status_code == 404
