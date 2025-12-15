import os
import re
from typing import Dict, Any

def load_and_enrich_template(chapter_id: int, title: str, context: Dict[str, Any]) -> str:
    # Logic extracted from main.py lines 358-417
    # Assuming rapport dir is relative to backend root or we find it
    # Ideally main.py passes the path, but let's assume standard location relative to this file
    # /backend/chapters/content_loader.py -> /backend/rapport/
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rapport_dir = os.path.join(base_dir, "rapport")
    
    filename = f"hoofdstuk{chapter_id}.txt"
    path = os.path.join(rapport_dir, filename)
    
    raw_content = ""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_content = f.read()
        except Exception as e:
            raw_content = f"Kon sjabloon {filename} niet laden: {e}"
    else:
        # Fallback if file doesn't exist
        raw_content = f"Genereren van {title}..."

    # AI INJECTION (Specific to Ch 12 in original, but could be general)
    if chapter_id == 12:
        raw_content += _get_swot_content(context)

    # Search & Replace
    enhanced_content = raw_content
    for key, value in context.items():
            enhanced_content = enhanced_content.replace(f"[{key}]", str(value))
            enhanced_content = enhanced_content.replace(f"[{key.title()}]", str(value))
            
    # Conditionals
    enhanced_content = parse_conditionals(enhanced_content, context)
    
    return enhanced_content

def _get_swot_content(ctx):
    return f"""
    <h3>AI SWOT Analyse</h3>
    <div class="swot-grid">
        <div class="swot-card strength">
            <strong>Sterkten</strong>
            <ul>
                <li>Energielabel {ctx.get('label')} biedt toekomstbestendigheid.</li>
                <li>Courante oppervlakte van {ctx.get('oppervlakte')}.</li>
            </ul>
        </div>
        <div class="swot-card weakness">
            <strong>Zwakten</strong>
            <ul>
                <li>Mogelijk onderhoud gezien bouwjaar {ctx.get('bouwjaar')}.</li>
            </ul>
        </div>
        <div class="swot-card opportunity">
            <strong>Kansen</strong>
            <ul>
                <li>Verduurzaming kan waarde met 5-10% verhogen.</li>
            </ul>
        </div>
        <div class="swot-card threat">
            <strong>Bedreigingen</strong>
            <ul>
                <li>Marktrente schommelingen.</li>
            </ul>
        </div>
    </div>
    """

def parse_conditionals(text, ctx):
    pattern = r"\[IF (.*?)\](.*?)(\[ELSE\](.*?))?\[ENDIF\]"
    matches = list(re.finditer(pattern, text, re.DOTALL))
    for match in reversed(matches): 
        full_match = match.group(0)
        condition = match.group(1).strip()
        true_block = match.group(2)
        false_block = match.group(4) or ""
        
        is_true = False
        try:
            if "Label matches" in condition:
                target = condition.split("matches")[-1].strip()
                if target in str(ctx["label"]): is_true = True
            elif "Price >" in condition:
                is_true = True 
            elif "exists" in condition:
                fld = condition.split("exists")[0].strip()
                # simplified check
                if fld.lower() in ctx and ctx[fld.lower()] != "onbekend": is_true = True
        except: pass
        
        replacement = true_block if is_true else false_block
        text = text.replace(full_match, replacement)
    return text
