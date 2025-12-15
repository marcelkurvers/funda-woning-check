import sys
import os
import json

# Add backend to path so we can import chapters
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from chapters.chapter_0 import ExecutiveSummary

# Mock Context Data
mock_context = {
    "adres": "Teststraat 123, Amsterdam",
    "prijs": "€ 450.000 k.k.",
    "prijs_m2": "€ 4.500",
    "oppervlakte": "100",
    "bouwjaar": "1990",
    "label": "A"
}

def test_chapter_0_generation():
    print("--- Testing Chapter 0 Generation ---")
    
    try:
        # Instantiate
        chapter = ExecutiveSummary(mock_context)
        
        # Generate
        output = chapter.generate()
        
        # Verify
        layout = output.grid_layout
        
        print(f"Title: {output.title}")
        print(f"Layout Type: {layout.get('layout_type')}")
        
        if layout.get('layout_type') != 'modern_dashboard':
            print("FAIL: Layout type mismatch!")
            return

        print("\n[Hero Section]")
        print(json.dumps(layout.get('hero'), indent=2))
        
        print("\n[Metrics Section]")
        # Just print count
        print(f"Metrics count: {len(layout.get('metrics', []))}")
        
        print("\n[Main Section]")
        print(f"Title: {layout.get('main', {}).get('title')}")
        print(f"Content length: {len(layout.get('main', {}).get('content', ''))} chars")
        
        print("\n[Sidebar Section]")
        print(f"Sidebar items: {len(layout.get('sidebar', []))}")

        print("\nSUCCESS: Chapter 0 generated valid 'modern_dashboard' structure.")
        
    except Exception as e:
        print(f"ERROR: Generation failed - {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chapter_0_generation()
