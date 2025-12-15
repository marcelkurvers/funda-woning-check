import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import os
import re
import glob

def refactor_chapter(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # check if already refactored
    if "_render_rich_narrative" in content:
        print(f"Skipping {filepath} (already refactored)")
        return

    # Regex to find the f-string block containing narrative['intro'] and narrative['conclusion']
    # We look for: var_name = f""" ... """
    
    # Pattern: varname = f"""..."""
    # We need to capture the variable name and the content inside.
    # The content usually has specific markers.
    
    pattern = r"(\w+)\s*=\s*f\"\"\"(.*?)\"\"\""
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"Could not find HTML block in {filepath}")
        return

    var_name = match.group(1)
    html_content = match.group(2)
    
    # Verify it's the right block
    if "narrative['intro']" not in html_content:
        # try next match?
        # Find all matches
        matches = list(re.finditer(pattern, content, re.DOTALL))
        target_match = None
        for m in matches:
            if "narrative['intro']" in m.group(2):
                target_match = m
                break
        
        if not target_match:
            print(f"No narrative block found in {filepath}")
            return
        
        match = target_match
        var_name = match.group(1)
        html_content = match.group(2)

    # Now extract the middle content
    # Structure:
    # <div class="chapter-intro">...</div> (implicit or explicit)
    # <div class="analysis-section">...</div>
    # [MIDDLE]
    # <div class="ai-conclusion-box">...</div>
    
    # We split by 'analysis-section' closing div and 'ai-conclusion-box' opening div
    parts = re.split(r"analysis-section['\"]>.*?</div>", html_content, flags=re.DOTALL)
    if len(parts) < 2:
        print(f"Could not split analysis section in {filepath}")
        # Analysis might be structured differently?
        # Fallback: Just look for what's between analysis } and ai-conclusion-box {
        # Check specific markers in code
        return

    # Post-analysis part
    post_analysis = parts[1]
    
    # Split by conclusion box
    pre_conclusion_parts = re.split(r"<div class=[\"']ai-conclusion-box", post_analysis, flags=re.DOTALL)
    if len(pre_conclusion_parts) < 1:
        print(f"Could not find conclusion box in {filepath}")
        return

    middle_content = pre_conclusion_parts[0].strip()
    
    # Construct new assignment
    # If middle content exists, we wrap it in f"""..."""
    
    new_assignment = ""
    if middle_content:
        new_assignment = f'{var_name} = self._render_rich_narrative(narrative, extra_html=f"""\n        {middle_content}\n        """)'
    else:
        new_assignment = f'{var_name} = self._render_rich_narrative(narrative)'
        
    # Replace the entire match
    new_content = content.replace(match.group(0), new_assignment)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    print(f"Refactored {filepath}")

def main():
    # Script is in backend/scripts/
    # We want backend/chapters/
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../chapters"))
    files = glob.glob(os.path.join(root, "chapter_*.py"))
    for f in files:
        refactor_chapter(f)

if __name__ == "__main__":
    main()
