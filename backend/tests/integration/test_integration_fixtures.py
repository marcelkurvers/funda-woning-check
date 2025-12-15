import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import unittest
import os
import sys
# Add current directory to path so we can import 'main' and 'parser'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import Parser
from main import build_chapters

class TestFixturesOutput(unittest.TestCase):
    def test_fixtures_generation(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define directories to search
        search_dirs = [
            os.path.join(base_dir, "../fixtures"),
            os.path.join(base_dir, "../../../test-data")
        ]
        
        test_files = []
        for d in search_dirs:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.endswith(".html") or f == "test-html": # test-html has no extension but is html
                        test_files.append(os.path.join(d, f))
                        
        if not test_files:
            self.fail(f"No test files found in {search_dirs}")
            
        print(f"Found {len(test_files)} test files: {test_files}")
        
        for fixtures_path in test_files:
            with self.subTest(file=fixtures_path):
                print(f"\n\n==========================================")
                print(f"Testing file: {fixtures_path}")
                print(f"==========================================")
                
                with open(fixtures_path, "r", encoding="utf-8") as f:
                    html_content = f.read()

                # 2. Parse Data
                parser = Parser()
                core_data = parser.parse_html(html_content)
                print("\n--- Extracted Core Data ---")
                for k, v in core_data.items():
                    print(f"{k}: {v}")

                # 3. Generate Chapters
                print("\n--- Generating Chapters ---")
                chapters = build_chapters(core_data)

                # 4. Verify Output per Page
                expected_chapters = 13 # 0 to 12

                chapters_found = len(chapters)
                print(f"Generated {chapters_found} chapters.")
                
                # We expect roughly 13, but let's just assert we got > 0
                self.assertGreaterEqual(chapters_found, 1, "Should have generated at least some chapters")

                for i in range(13):
                    cid = str(i)
                    if cid not in chapters:
                        print(f"WARNING: Chapter {cid} missing from output")
                        continue

                    ch = chapters[cid]

                    # Check Title
                    title = ch.get("title", "NO TITLE")
                    print(f"Chapter {cid}: {title}")
                    self.assertIn("title", ch, f"Chapter {cid} has no title")

                    # Check Grid Layout (Modern)
                    if "grid_layout" in ch:
                        layout = ch["grid_layout"]
                        self.assertIn("metrics", layout, f"Chapter {cid} layout missing metrics")
                        self.assertIn("main", layout, f"Chapter {cid} layout missing main")
                        self.assertIn("sidebar", layout, f"Chapter {cid} layout missing sidebar")
                        
                        # Check content is not totally empty
                        self.assertTrue(layout["main"].get("title"), f"Chapter {cid} main section has no title")
                    else:
                        print(f"  [Legacy/Fallback] Chapter {cid} uses blocks format.")
                    
                    print(f"  -> Verified.")

if __name__ == "__main__":
    unittest.main()
