
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import pytest
from fastapi.testclient import TestClient
from main import app, init_db
from ai.provider_factory import ProviderFactory
from ai.providers.openai_provider import OpenAIProvider
from ai.providers.anthropic_provider import AnthropicProvider
from ai.providers.gemini_provider import GeminiProvider
from ai.providers.ollama_provider import OllamaProvider

@pytest.fixture
def client():
    # Use a fixed test DB for consistency between connections in tests
    test_db = "data/test_app.db"
    os.environ["APP_DB"] = test_db
    if os.path.exists(test_db):
        os.remove(test_db)
    
    from config.settings import reset_settings
    reset_settings()
    init_db()
    
    return TestClient(app)

def test_provider_factory_listing():
    providers = ProviderFactory.list_providers()
    assert "openai" in providers
    assert "anthropic" in providers
    assert "gemini" in providers
    assert "ollama" in providers
    
    assert "gpt-4o" in providers["openai"]["models"]
    assert "claude-3-5-sonnet-20240620" in providers["anthropic"]["models"]
    assert "gemini-1.5-flash" in providers["gemini"]["models"]

def test_provider_factory_creation_with_model():
    # OpenAI
    # Using dummy key and model
    p = ProviderFactory.create_provider("openai", api_key="sk-test", model="gpt-4o-mini")
    assert isinstance(p, OpenAIProvider)
    assert p.default_model == "gpt-4o-mini"
    
    # Anthropic
    p = ProviderFactory.create_provider("anthropic", api_key="sk-ant-test", model="claude-3-haiku-20240307")
    assert isinstance(p, AnthropicProvider)
    assert p.default_model == "claude-3-haiku-20240307"
    
    # Gemini
    p = ProviderFactory.create_provider("gemini", api_key="test_key", model="gemini-1.5-pro")
    assert isinstance(p, GeminiProvider)
    assert p.default_model == "gemini-1.5-pro"
    
    # Ollama
    p = ProviderFactory.create_provider("ollama", base_url="http://localhost:11434", model="mistral")
    assert isinstance(p, OllamaProvider)
    assert p.default_model == "mistral"

def test_api_ai_models_endpoint(client):
    # Test current provider
    response = client.get("/api/ai/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0
    
    # Test explicit provider
    response = client.get("/api/ai/models?provider=anthropic")
    assert response.status_code == 200
    data = response.json()
    assert "claude-3-5-sonnet-20240620" in data["models"]

    # Test 'all'
    response = client.get("/api/ai/models?provider=all")
    assert response.status_code == 200
    data = response.json()
    assert "gpt-4o" in data["models"]
    assert "llama3" in data["models"]

def test_preferences_sync_with_ai_settings(client):
    # Set preferences with AI settings
    payload = {
        "marcel": {"priorities": ["Test"]},
        "petra": {"priorities": ["Test"]},
        "ai_provider": "gemini",
        "ai_model": "gemini-3-fast"
    }
    resp = client.post("/api/preferences", json=payload)
    assert resp.status_code == 200
    
    # Verify via config API that it synced to systems settings
    config_resp = client.get("/api/config/ai")
    assert config_resp.status_code == 200
    ai_config = config_resp.json()
    assert ai_config["provider"] == "gemini"
    assert ai_config["model"] == "gemini-3-fast"
