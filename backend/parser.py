from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class Parser:
    """
    Enhanced parser for Funda property listings with comprehensive field extraction
    and data validation to prevent illogical values.
    """
    
    # Validation thresholds
    MAX_BEDROOMS = 15  # Unlikely to have more than 15 bedrooms in residential property
    MAX_BATHROOMS = 10  # Unlikely to have more than 10 bathrooms
    MAX_TOTAL_ROOMS = 30  # Unlikely to have more than 30 total rooms
    MIN_LIVING_AREA = 10  # Minimum 10 m² for a living space
    MAX_LIVING_AREA = 2000  # Maximum 2000 m² for residential
    MIN_BUILD_YEAR = 1500  # Oldest reasonable build year
    MAX_BUILD_YEAR = 2030  # Future construction
    
    def parse_html(self, html: str) -> Dict[str, Any]:
        """
        Parses Funda HTML and returns a validated dictionary with property details.
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract all fields
        raw_data = {
            "asking_price_eur": self._extract_price(soup),
            "asking_price_per_m2": self._extract_price_per_m2(soup),
            "address": self._extract_address(soup),
            "living_area_m2": self._extract_spec(soup, "living_area_m2"),
            "plot_area_m2": self._extract_spec(soup, "plot_area_m2"),
            "build_year": self._extract_spec(soup, "build_year"),
            "energy_label": self._extract_label(soup),
            "rooms": self._extract_spec(soup, "rooms"),
            "bedrooms": self._extract_bedrooms(soup),
            "bathrooms": self._extract_bathrooms(soup),
            "property_type": self._extract_property_type(soup),
            "construction_type": self._extract_construction_type(soup),
            "garage": self._extract_garage(soup),
            "garden": self._extract_garden(soup),
            "balcony": self._extract_balcony(soup),
            "roof_type": self._extract_roof_type(soup),
            "heating": self._extract_heating(soup),
            "insulation": self._extract_insulation(soup),
            "volume_m3": self._extract_spec(soup, "volume_m3"),
            "service_costs": self._extract_service_costs(soup),
            "acceptance": self._extract_acceptance(soup),
            "ownership": self._extract_ownership(soup),
            "listed_since": self._extract_spec(soup, "listed_since"),
        }
        
        # Validate and clean the data
        validated_data = self._validate_data(raw_data)
        
        return validated_data

    def _extract_price(self, soup) -> Optional[str]:
        # 1. Structured CSS Selector (Most reliable if HTML is intact)
        price_el = soup.select_one(".object-header__price")
        if price_el:
            text = price_el.get_text(strip=True)
            match = re.search(r"€\s*[\d\.]+", text)
            if match:
                return match.group(0)

        # 2. Robust Full Text Scan (Primary for Pasted/Unstructured Content)
        # This is moved UP because it handles commas (1,400,000) better than the simple text node search below.
        full_text = soup.get_text(separator="\n")
        
        # Regex: Matches € followed by digits, supporting both . and , as separators.
        # e.g. € 1.400.000 or € 1,400,000
        match = re.search(r"€\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)", full_text)
        if match:
             val = match.group(0).rstrip('.,')
             # Filter out tiny partial matches like "€1" only if they seem incomplete
             if len(val) > 4 or re.search(r'\d{3}', val):
                 return val

        # 3. Simple Text Node Search (Legacy/Backup)
        price_el = soup.find(string=re.compile(r"€\s*\d"))
        if price_el:
            text = price_el.get_text(strip=True)
            # This legacy regex only supported dots, which is why it failed for 1,400,000
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
        # BLOCKLIST for common navigation/UI elements to ignore
        BLOCKLIST = [
            "ga naar", "menu", "zoeken", "inloggen", "funda", 
            "te koop", "te huur", "favorieten", "foto's", 
            "video's", "360-graden", "kenmerken", "kaart",
            "verkoper", "contact"
        ]
        
        lines = [line.strip() for line in soup.get_text().splitlines() if line.strip()]
        for line in lines:
            line_lower = line.lower()
            # Skip if explicitly in blocklist or starts with (e.g. "Ga naar content")
            if any(line_lower.startswith(b) for b in BLOCKLIST):
                continue
            
            # Additional heuristic: Addresses usually have a number
            if not any(c.isdigit() for c in line):
                # If it's a very short word like "Photos", skip it
                if len(line.split()) < 2:
                    continue
            
            # Heuristic: address usually < 100 chars
            if len(line) < 100:
                return line
                
        return "Adres onbekend"
        
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

        # 3. Aggressive Regex Search for Address Patterns (Postcode + City)
        # e.g. "1012 AB Amsterdam"
        text = soup.get_text(separator="\n")
        # Regex for Dutch Postcode: 4 digits, space, 2 letters
        postcode_regex = re.compile(r'(\b\d{4}\s?[A-Z]{2}\b)', re.IGNORECASE)
        
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for i, line in enumerate(lines):
             match = postcode_regex.search(line)
             if match:
                 # Found a postcode. The address is likely this line or previous one.
                 # If this line starts with postcode, previous line might be street.
                 if line.startswith(match.group(0)) and i > 0:
                     potential_street = lines[i-1]
                     # Heuristic: Street address often ends with a number
                     if any(c.isdigit() for c in potential_street):
                         return f"{potential_street}, {line}"
                 
                 # If postcode is at end, return whole line
                 return line

        # 4. Fallback to existing heuristic
        # BLOCKLIST for common navigation/UI elements to ignore
        BLOCKLIST = [
            "ga naar", "menu", "zoeken", "inloggen", "funda", 
            "te koop", "te huur", "favorieten", "foto's", 
            "video's", "360-graden", "kenmerken", "kaart",
            "verkoper", "contact"
        ]
        
        for line in lines:
            line_lower = line.lower()
            if any(line_lower.startswith(b) for b in BLOCKLIST): continue
            
            # Heuristic: Addresses usually have a number
            if not any(c.isdigit() for c in line):
                if len(line.split()) < 2: continue
            
            if len(line) < 100:
                return line
                
        return "Adres onbekend"

    def _extract_spec(self, soup, keyword):
        # Map logical keys to multiple Dutch keywords
        kw_map = {
            "living_area_m2": ["Woonoppervlakte", "Wonen", "Gebruiksoppervlakte wonen"],
            "plot_area_m2": ["Perceel", "Perceeloppervlakte"],
            "build_year": ["Bouwjaar"],
            "energy_label": ["Energielabel"],
            "rooms": ["Aantal kamers", "kamers"],
            "volume_m3": ["Inhoud", "Bruto inhoud"],
            "listed_since": ["Aangeboden sinds"]
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
                # 1. Strict Colon Match first "Label: Value"
                match_colon = re.search(f"{keyword_long}:\s*(.*)", text, flags)
                if match_colon:
                    val = match_colon.group(1).strip()
                    if self._validate_value(keyword_long, val): return val
                    
                # 2. Loose match (no colon) - ONLY if line is short (likely a list item)
                # This prevents matching "Garage" in "Mooie woning met garage en tuin..."
                if len(text) < 50:
                    match_loose = re.search(f"{keyword_long}\s+(.*)", text, flags)
                    if match_loose:
                        val = match_loose.group(1).strip()
                        if self._validate_value(keyword_long, val): return val

                # 3. Value in next sibling (remains same)
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

        return None

        return None

    def _scan_raw_text(self, soup, keyword):
        """
        Scans the full text content using robust regex patterns.
        """
        text = soup.get_text(separator="\n")
        
        # KEYWORD MAPPING for "Paste Mode"
        # Map internal keys back to their Dutch display labels found in raw text
        
        # Construct a flexible regex for the keyword
        # allow optional colon, allow spaces
        # Pattern: (Keyword)[:\s]+(Value)
        
        # Improved Regex: Prefer a colon, otherwise strict. 
        # Stop at newline.
        # Anchor to start of line to avoid matching words in sentences (e.g. "met garage")
        pattern = re.compile(f"(?:^|\\n)\\s*({keyword})[:\\s]+(.*?)(?=\\n|$)", re.IGNORECASE)
        
        match = pattern.search(text)
        if match:
             val = match.group(2).strip()
             # Cleanup value (stop at first newline or unreasonable length)
             if len(val) < 100 and self._validate_value(keyword, val):
                 return val
                 
        # Fallback: Look for "Value keyword" pattern (e.g. "124 m² wonen" or "400 m³ inhoud")
        # specialized for areas/volumes
        if "m2" in keyword.lower() or "wonen" in keyword.lower() or "m3" in keyword.lower() or "inhoud" in keyword.lower():
             # Look for digits followed by m², m2, m³ or m3
             # Adjust regex based on keyword
             unit = "m[²2]"
             if "m3" in keyword.lower() or "inhoud" in keyword.lower():
                 unit = "m[³3]"
                 
             p2 = re.compile(r'(\d+(?:[\.,]\d+)?)\s*' + unit, re.IGNORECASE)
             match = p2.search(text)
             
             if match and ("wonen" in keyword.lower() or "inhoud" in keyword.lower()):
                 return match.group(0)
                 
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

    def _extract_price_per_m2(self, soup) -> Optional[str]:
        """Extract price per square meter"""
        keywords = ["Vraagprijs per m²", "prijs per m²", "per m²"]
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val:
                return val
        return None

    def _extract_bedrooms(self, soup) -> Optional[str]:
        """Extract number of bedrooms separately from total rooms"""
        keywords = ["slaapkamers", "slaapkamer"]
        
        # First try to find in the structured data
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val:
                # Extract just the number
                match = re.search(r'(\d+)', val)
                if match:
                    num = int(match.group(1))
                    if num <= self.MAX_BEDROOMS:
                        return str(num)
                    else:
                        logger.warning(f"Suspicious bedroom count: {num} (max expected: {self.MAX_BEDROOMS})")
                        return str(num)  # Return raw for validation to handle
        
        # Fallback: check if it's in the rooms field
        rooms_text = self._extract_spec(soup, "rooms")
        if rooms_text:
            match = re.search(r'(\d+)\s*slaapkamers?', rooms_text, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                if num <= self.MAX_BEDROOMS:
                    return str(num)
                else:
                    logger.warning(f"Suspicious bedroom count in rooms field: {num} (max expected: {self.MAX_BEDROOMS})")
                    return str(num)
        
        return None

    def _extract_bathrooms(self, soup) -> Optional[str]:
        """Extract number of bathrooms"""
        keywords = ["Aantal badkamers"]
        # First try to find in the structured data
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val:
                # Extract just the number
                match = re.search(r'(\d+)', val)
                if match:
                    num = int(match.group(1))
                    if num <= self.MAX_BATHROOMS:
                        return str(num)
                    else:
                        logger.warning(f"Suspicious bathroom count: {num} (max expected: {self.MAX_BATHROOMS})")
                        return str(num)  # Return raw for validation to handle
        
        # Alternative: look for pattern like "2 badkamers"
        text = soup.get_text()
        match = re.search(r'(\d+)\s+badkamers?(?:\s+en)?', text, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if num <= self.MAX_BATHROOMS:
                return str(num)
            else:
                logger.warning(f"Suspicious bathroom count in text: {num} (max expected: {self.MAX_BATHROOMS})")
                return str(num)
        
        return None

    def _extract_property_type(self, soup) -> Optional[str]:
        """Extract property type (villa, apartment, etc.)"""
        keywords = ["Soort woonhuis", "Type woning", "Woningtype"]
        
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val:
                return val
        
        return None

    def _extract_construction_type(self, soup) -> Optional[str]:
        """Extract construction type (new/existing)"""
        keywords = ["Soort bouw", "Bouwtype"]
        
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val:
                return val
        
        return None

    def _extract_garage(self, soup) -> Optional[str]:
        """Extract garage information"""
        keywords = ["Soort garage", "Garage", "Parkeren"]
        
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val:
                return val
        
        return None

    def _extract_garden(self, soup) -> Optional[str]:
        """Extract garden information"""
        keywords = ["Tuin", "Achtertuin", "Ligging tuin"]
        
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val:
                return val
        
        return None

    def _extract_balcony(self, soup) -> Optional[str]:
        """Extract balcony/terrace information"""
        keywords = ["Balkon", "dakterras", "Balkon/dakterras"]
        
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val:
                return val
        
        return None

    def _extract_roof_type(self, soup) -> Optional[str]:
        """Extract roof type"""
        keywords = ["Soort dak", "Dak"]
        
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val:
                return val
        
        return None

    def _extract_heating(self, soup) -> Optional[str]:
        """Extract heating information"""
        keywords = ["Verwarming", "Cv-ketel"]
        
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val:
                return val
        
        return None

    def _extract_insulation(self, soup) -> Optional[str]:
        """Extract insulation information"""
        keywords = ["Isolatie"]
        
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val:
                return val
        
        return None

    def _extract_service_costs(self, soup) -> Optional[str]:
        """Extract service costs"""
        keywords = ["Servicekosten", "Bijdrage VvE"]
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val: return val
        return None

    def _extract_acceptance(self, soup) -> Optional[str]:
        """Extract acceptance (e.g. In overleg)"""
        keywords = ["Aanvaarding"]
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val: return val
        return None

    def _extract_ownership(self, soup) -> Optional[str]:
        """Extract ownership situation"""
        keywords = ["Eigendomssituatie"]
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val: return val
        return None

    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted data and flag suspicious values.
        Returns validated data with quality warnings.
        """
        validated = data.copy()
        warnings = []
        
        # Validate bedrooms
        if data.get("bedrooms"):
            try:
                num = int(re.search(r'\d+', str(data["bedrooms"])) .group())
                if num > self.MAX_BEDROOMS:
                    warnings.append(f"Suspicious bedroom count: {num} (max expected: {self.MAX_BEDROOMS})")
                    validated["bedrooms"] = str(self.MAX_BEDROOMS)  # Cap it
                elif num == 0:
                    warnings.append("Zero bedrooms detected, likely parsing error")
                    validated["bedrooms"] = None
                # If exactly max, keep as is (could be legitimate)
            except (AttributeError, ValueError):
                pass
        
        # Validate bathrooms
        if data.get("bathrooms"):
            try:
                num = int(re.search(r'\d+', str(data["bathrooms"])).group())
                if num > self.MAX_BATHROOMS:
                    warnings.append(f"Suspicious bathroom count: {num} (max expected: {self.MAX_BATHROOMS})")
                    validated["bathrooms"] = str(self.MAX_BATHROOMS) # Cap it
            except (AttributeError, ValueError):
                pass
        
        # Validate total rooms
        if data.get("rooms"):
            try:
                num = int(re.search(r'\d+', str(data["rooms"])).group())
                if num > self.MAX_TOTAL_ROOMS:
                    warnings.append(f"Suspicious total room count: {num} (max expected: {self.MAX_TOTAL_ROOMS})")
                    # INVALIDATE it. Better to estimate from m2 than to show "54 rooms".
                    validated["rooms"] = None
            except (AttributeError, ValueError):
                pass
        
        # Validate living area
        if data.get("living_area_m2"):
            try:
                # Extract digits including dots/commas
                match = re.search(r'[\d\.,]+', str(data["living_area_m2"]))
                if match:
                    raw_num = match.group().replace('.', '').replace(',', '')
                    num = int(raw_num)
                    if num < self.MIN_LIVING_AREA:
                        warnings.append(f"Suspicious living area: {num} m² (min expected: {self.MIN_LIVING_AREA} m²)")
                    elif num > self.MAX_LIVING_AREA:
                        warnings.append(f"Suspicious living area: {num} m² (max expected: {self.MAX_LIVING_AREA} m²)")
            except (AttributeError, ValueError):
                pass
        
        # Validate build year
        if data.get("build_year"):
            try:
                # Basic check for YYYY
                match = re.search(r'(\d{4})', str(data["build_year"]))
                if match:
                    year = int(match.group(1))
                    if year < self.MIN_BUILD_YEAR or year > self.MAX_BUILD_YEAR:
                        warnings.append(f"Suspicious build year: {year} (expected between {self.MIN_BUILD_YEAR}-{self.MAX_BUILD_YEAR})")
                        validated["build_year"] = None
                else:
                    validated["build_year"] = None
            except (AttributeError, ValueError):
                pass
        
        # Cross-validation: bedrooms should be less than total rooms
        if validated.get("bedrooms") and validated.get("rooms"):
            try:
                bedrooms = int(re.search(r'\d+', str(validated["bedrooms"])).group())
                total_rooms = int(re.search(r'\d+', str(validated["rooms"])).group())
                
                if bedrooms > total_rooms:
                    warnings.append(f"Bedrooms ({bedrooms}) exceeds total rooms ({total_rooms})")
                    # Trust bedrooms more if rooms is suspiciously small, or rooms more if bedrooms is huge?
                    # For now just warn.
            except (AttributeError, ValueError):
                pass
        
        # Add warnings to validated data if any
        if warnings:
            validated["_parsing_warnings"] = warnings
            logger.warning(f"Data validation warnings: {warnings}")
        
        return validated
