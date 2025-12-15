
import json
import os
from main import build_chapters

def test_chapter_generation():
    print("Testing Chapter Generation...")
    
    # Mock Core Data
    core_data = {
        "address": "Teststraat 42",
        "asking_price_eur": "€ 450.000",
        "living_area_m2": "100 m²",
        "plot_area_m2": "200 m²",
        "build_year": "1995",
        "energy_label": "A"
    }
    
    # Build
    chapters = build_chapters(core_data)
    
    # Verify Keys
    print(f"Generated Chapter Keys: {list(chapters.keys())}")
    
    # Assertions
    if "0" not in chapters:
        print("FAIL: Chapter 0 (Executive Summary) is MISSING!")
        exit(1)
    else:
        print("SUCCESS: Chapter 0 is present.")
        print("Title:", chapters["0"]["title"])
        print("Grid Keys:", list(chapters["0"]["grid_layout"].keys()))

if __name__ == "__main__":
    test_chapter_generation()
