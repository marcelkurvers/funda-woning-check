import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from ai.provider_factory import ProviderFactory
from intelligence import IntelligenceEngine

def test_ollama():
    print("Testing Ollama Provider...")
    try:
        provider = ProviderFactory.create_provider("ollama")
    except Exception as e:
        print(f"❌ Failed to create Ollama provider: {e}")
        return

    # Check health using asyncio
    import asyncio
    try:
        health = asyncio.run(provider.check_health())
        if not health:
            print("❌ Ollama server not reachable")
            return
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return

    print("✅ Ollama server reachable.")

    models = provider.list_models()
    print(f"✅ Available Models: {models}")
    
    if not models:
        print("⚠️ No models found. Please run `ollama pull llama3` or similar.")
        return

    print("Testing Generation...")
    # Inject provider
    IntelligenceEngine.set_provider(provider)
    
    # Mock Data
    data = {
        "address": "Teststraat 1",
        "price": 500000,
        "area": 120,
        "plot": 200,
        "year": 1990,
        "label": "B",
        "_preferences": {
            "marcel": {"priorities": ["Garage", "Glasvezel"]},
            "petra": {"priorities": ["Tuin", "Sfeer"]}
        }
    }
    
    # Mock fallback
    fallback = {"title": "Test", "intro": "Fallback intro", "main_analysis": "Fallback analysis", "conclusion": "Fallback conclusion"}
    
    # Test Generation
    result = IntelligenceEngine._generate_ai_narrative(1, data, fallback)
    
    if result:
        print("✅ AI Generation Successful!")
        print("--- Result ---")
        print(result)
    else:
        print("❌ AI Generation Failed or returned None.")

if __name__ == "__main__":
    test_ollama()
