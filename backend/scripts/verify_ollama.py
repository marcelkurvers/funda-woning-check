import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from ollama_client import OllamaClient
from intelligence import IntelligenceEngine

def test_ollama():
    print("Testing Ollama Client...")
    client = OllamaClient()
    
    if not client.check_health():
        print("❌ Ollama server not reachable at http://localhost:11434")
        return

    print("✅ Ollama server reachable.")
    
    models = client.list_models()
    print(f"✅ Available Models: {models}")
    
    if not models:
        print("⚠️ No models found. Please run `ollama pull llama3` or similar.")
        return

    print("Testing Generation...")
    # Inject client
    IntelligenceEngine.set_client(client)
    
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
