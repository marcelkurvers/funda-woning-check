"""
Pytest configuration and fixtures for backend tests
"""
import pytest
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before running tests"""
    # Ensure we're using the correct backend directory
    os.environ["APP_DB"] = ":memory:"  # Use in-memory database for tests
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"  # Default for local tests
    yield
    # Cleanup after all tests


@pytest.fixture
def test_db_path(tmp_path):
    """Provide a temporary database path for tests"""
    return tmp_path / "test.db"


@pytest.fixture
def sample_html():
    """Provide sample Funda HTML for testing"""
    return """
    <html>
        <body>
            <div class="object-header__price">€ 500.000 k.k.</div>
            <div class="object-header__title">Teststraat 123, 1234 AB Amsterdam</div>
            <div class="kenmerken-highlighted__value">120 m²</div>
            <div class="kenmerken-highlighted__value">5</div>
        </body>
    </html>
    """


@pytest.fixture
def sample_property_core():
    """Provide sample property core data for testing"""
    return {
        "address": "Teststraat 123, 1234 AB Amsterdam",
        "asking_price_eur": 500000,
        "living_area_m2": 120,
        "plot_area_m2": 200,
        "bedrooms": 3,
        "build_year": 2010,
        "energy_label": "B",
        "property_type": "Eengezinswoning",
        "media_urls": [],
        "extra_facts": ""
    }
