import sys
import os
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import build_chapters

core_data = {
    "address": "Teststraat 1",
    "asking_price_eur": "€ 500.000",
    "living_area_m2": "100",
    "plot_area_m2": "200",
    "build_year": "2000",
    "energy_label": "A"
}

chapters = build_chapters(core_data)
print("Generated Chapter Keys:", list(chapters.keys()))

if "0" in chapters:
    print("Chapter 0 content preview:", json.dumps(chapters["0"], indent=2))
else:
    print("FATAL: Chapter 0 is missing!")
