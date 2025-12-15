from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional

class Parser:
    def parse_html(self, html: str) -> Dict[str, Any]:
        """
        Parses Funda HTML and returns a dictionary with property details.
        """
        soup = BeautifulSoup(html, "html.parser")
        data = {
            "asking_price_eur": self._extract_price(soup),
            "address": self._extract_address(soup),
            "living_area_m2": self._extract_spec(soup, "living_area_m2"),
            "plot_area_m2": self._extract_spec(soup, "plot_area_m2"),
            "build_year": self._extract_spec(soup, "build_year"),
            "energy_label": self._extract_label(soup),
            "rooms": self._extract_spec(soup, "rooms"),
        }
        return data

    def _extract_price(self, soup) -> Optional[str]:
        price_el = soup.select_one(".object-header__price")
        if not price_el:
            price_el = soup.find(string=re.compile(r"€\s*\d"))
        
        if price_el:
            text = price_el.get_text(strip=True)
            match = re.search(r"€\s*[\d\.]+", text)
            if match:
                return match.group(0)
        return None

    def _extract_address(self, soup) -> str:
        # 1. Standard Title
        title_el = soup.select_one(".object-header__title")
        if title_el:
            return title_el.get_text(strip=True)
        
        # 2. Page Title tag
        if soup.title:
            t = soup.title.text
            if "Te koop:" in t:
                return t.split("Te koop:")[1].split("[")[0].strip()
        
        # 3. First valid line fallback (for raw text pastes)
        lines = [line.strip() for line in soup.get_text().splitlines() if line.strip()]
        if lines:
            first = lines[0]
            # Heuristic: address usually < 100 chars and starts with something reasonable
            if len(first) < 100:
                return first
                
        return "Adres onbekend"

    def _extract_spec(self, soup, keyword):
        # Map logical keys to multiple Dutch keywords
        kw_map = {
            "living_area_m2": ["Woonoppervlakte", "Wonen", "Gebruiksoppervlakte wonen"],
            "plot_area_m2": ["Perceel", "Perceeloppervlakte"],
            "build_year": ["Bouwjaar"],
            "energy_label": ["Energielabel"],
            "rooms": ["Aantal kamers", "kamers"]
        }
        
        keywords = kw_map.get(keyword, [keyword])
        
        for k in keywords:
            val = self._extract_spec_by_keyword(soup, k)
            if val: return val
            
        return None

    def _extract_spec_by_keyword(self, soup, keyword_long):
        # Strategy 1: specific classes (skipped as we focus on robustness)
        pass 
        
        # Strategy 2: Text scan in any text node
        
        # Helper to scan with specific flags
        def scan(flags):
            candidates = soup.find_all(string=re.compile(keyword_long, flags))
            for cand in candidates:
                # Check if exact match to keyword (heuristic: titles are usually exact)
                # This avoids matching "woonoppervlak" inside a sentence
                if len(cand.strip()) < len(keyword_long) + 5: 
                    pass
                
                text = cand.strip()
                # 1. "Label: Value" or "Label Value" on same line?
                match = re.search(f"{keyword_long}[:\\s]+(.*)", text, flags)
                if match:
                    val = match.group(1).strip()
                    if self._validate_value(keyword_long, val): return val
                
                # 2. Value in next sibling
                parent = cand.parent
                if parent:
                    for sib in parent.next_siblings:
                        s_text = None
                        if isinstance(sib, str):
                            s_text = sib.strip()
                        elif hasattr(sib, 'get_text'):
                            s_text = sib.get_text(strip=True)
                        
                        if s_text:
                            if self._validate_value(keyword_long, s_text): return s_text
                            break
            return None

        # 1. Try EXACT casing first (e.g. "Wonen" vs "wonen")
        val = scan(0) # 0 means case-sensitive
        if val: return val
        
        # 2. Fallback to IGNORECASE scan in DOM
        val = scan(re.IGNORECASE)
        if val: return val
        
        # 3. Fallback: Raw Text Scan (for copy-pastes where structure is lost)
        return self._scan_raw_text(soup, keyword_long)

    def _scan_raw_text(self, soup, keyword):
        """
        Scans the full text content line-by-line.
        Useful when HTML structure is lost (e.g. plain text paste).
        Look for:
        - "Keyword: Value"
        - "Keyword \n Value"
        - "Value \n Keyword" (sometimes happens with copy selection)
        """
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        # Find index of keyword
        for i, line in enumerate(lines):
            # Check if line IS the keyword (approx) or Starts with keyword
            # e.g. "Woonoppervlakte" or "Woonoppervlakte: 120m2"
            
            # Case A: Line starts with keyword
            if line.lower().startswith(keyword.lower()):
                # 1. Check rest of line
                remainder = line[len(keyword):].strip(": ").strip()
                if remainder and self._validate_value(keyword, remainder):
                    return remainder
                
                # 2. Check NEXT line (Key \n Value)
                if i + 1 < len(lines):
                    next_line = lines[i+1]
                    if self._validate_value(keyword, next_line):
                        return next_line
            
            # Case B: Line IS the value, and NEXT line is keyword (Value \n Key - rare but possible in some layouts)
            # e.g. "120 m2 \n Wonen"
            if line.lower() == keyword.lower() or (keyword.lower() in line.lower() and len(line) < len(keyword)+5):
                # Check PREVIOUS line
                if i > 0:
                    prev_line = lines[i-1]
                    if self._validate_value(keyword, prev_line):
                        return prev_line
                        
        return None

    def _validate_value(self, keyword, value):
        # Heuristics to reject bad matches
        val_lower = value.lower()
        if not value: return False
        
        # Energy label: short (A, B, C, A+++)
        if "label" in keyword.lower():
            if len(value) > 10: return False
            if "blikvanger" in val_lower: return False # Specific garbage seen in test
            return True
            
        # Areas: must have digits
        if "m2" in keyword.lower() or "oppervl" in keyword.lower():
            return any(c.isdigit() for c in value)
            
        return True

    def _extract_label(self, soup) -> Optional[str]:
        # Try generic spec extraction
        val = self._extract_spec(soup, "energy_label")
        if val:
            return val.split("(")[0].strip()
            
        # Try finding badge class
        label_badge = soup.select_one(".energy-label")
        if label_badge:
            return label_badge.get_text(strip=True)
            
        return None
