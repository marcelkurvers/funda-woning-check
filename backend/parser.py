from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional, List
import logging
from config.settings import get_settings

logger = logging.getLogger(__name__)

class Parser:
    """
    Enhanced parser for Funda property listings with comprehensive field extraction
    and data validation to prevent illogical values.
    """

    # Get settings singleton for validation thresholds
    settings = get_settings()

    # Validation thresholds from settings
    MAX_BEDROOMS = settings.validation.max_bedrooms
    MAX_BATHROOMS = settings.validation.max_bathrooms
    MAX_TOTAL_ROOMS = settings.validation.max_total_rooms
    MIN_LIVING_AREA = settings.validation.min_living_area
    MAX_LIVING_AREA = settings.validation.max_living_area
    MIN_BUILD_YEAR = settings.validation.min_build_year
    MAX_BUILD_YEAR = settings.validation.max_build_year
    
    def parse_html(self, html: str) -> Dict[str, Any]:
        """
        Parses Funda HTML and returns a validated dictionary with property details.
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract all fields
        raw_data = {
            "asking_price_eur": self._extract_price(soup),
            "address": self._extract_address(soup),
            "living_area_m2": self._extract_spec(soup, "living_area_m2"),
            "plot_area_m2": self._extract_spec(soup, "plot_area_m2"),
            "build_year": self._extract_spec(soup, "build_year"),
            "energy_label": self._extract_label(soup),
            "rooms": self._extract_spec(soup, "rooms"),
            "bedrooms": self._extract_bedrooms(soup),
            "bathrooms": self._extract_bathrooms(soup),
            "property_type": self._extract_spec(soup, "property_type"),
            "construction_type": self._extract_spec(soup, "construction_type"),
            "garage": self._extract_garage(soup),
            "garden": self._extract_garden(soup),
            "balcony": self._extract_balcony(soup),
            "roof_type": self._extract_roof_type(soup),
            "heating": self._extract_spec(soup, "heating"),
            "insulation": self._extract_spec(soup, "insulation"),
            "volume_m3": self._extract_spec(soup, "volume_m3"),
            "service_costs": self._extract_service_costs(soup),
            "acceptance": self._extract_acceptance(soup),
            "ownership": self._extract_ownership(soup),
            "listed_since": self._extract_spec(soup, "listed_since"),
            "media_urls": self._extract_media_urls(soup),
        }
        
        # Calculate price per m2
        price = self._parse_num(raw_data["asking_price_eur"])
        area = self._parse_num(raw_data["living_area_m2"])
        if price and area:
            raw_data["asking_price_per_m2"] = f"€ {int(price/area)}"
        else:
            raw_data["asking_price_per_m2"] = None
        
        # Validate and clean the data
        validated_data = self._validate_data(raw_data)
        
        return validated_data

    def _extract_price(self, soup) -> Optional[str]:
        # 1. Structured CSS Selector
        price_el = soup.select_one(".object-header__price")
        if price_el:
            text = price_el.get_text(strip=True)
            match = re.search(r"€\s*[\d\.,]+", text)
            if match:
                return match.group(0).rstrip('.,')

        # 2. Robust Full Text Scan
        full_text = soup.get_text(separator="\n")
        match = re.search(r"€\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)", full_text)
        if match:
             val = match.group(0).rstrip('.,')
             if len(val) > 4 or re.search(r'\d{3}', val):
                 return val
            
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
                # Clean up "Te koop: Adres | Funda"
                addr = t.split("Te koop:")[1].split("|")[0].split("[")[0].strip()
                if addr: return addr
        
        # 3. Postcode search with line cleaning
        text = soup.get_text(separator="\n")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        blocklist = ["menu", "navigation", "ga naar", "funda", "kaart", "lijst", "foto's"]
        
        postcode_match = re.search(r'(\d{4}\s?[A-Z]{2})', text)
        if postcode_match:
            for i, line in enumerate(lines):
                if postcode_match.group(1) in line:
                    # Check if line is just the postcode (e.g. "1234 AB Stad")
                    # If so, the address might be in the previous line
                    if i > 0 and not any(b in lines[i-1].lower() for b in blocklist) and len(lines[i-1]) < 80:
                         return f"{lines[i-1]} {line}"
                    return line
        
        # 4. Filter blocklist from raw lines if we have something that looks like an address
        for line in lines:
            if any(char.isdigit() for char in line) and len(line) < 100:
                if not any(b in line.lower() for b in blocklist):
                     return line

        return "Adres onbekend"

    def _extract_spec(self, soup, keyword):
        kw_map = {
            "living_area_m2": ["Woonoppervlakte", "Wonen", "Gebruiksoppervlakte wonen", "Gebruiksoppervlakte"],
            "plot_area_m2": ["Perceel", "Perceeloppervlakte"],
            "build_year": ["Bouwjaar"],
            "energy_label": ["Energielabel"],
            "rooms": ["Aantal kamers"],
            "volume_m3": ["Inhoud", "Bruto inhoud"],
            "listed_since": ["Aangeboden sinds"],
            "property_type": ["Soort woonhuis", "Soort appartement", "Woningtype"],
            "construction_type": ["Soort bouw", "Bouwvorm"],
            "heating": ["Verwarming"],
            "insulation": ["Isolatie"]
        }
        
        keywords = kw_map.get(keyword, [keyword])
        
        # 1. Try DT/DD structure first (very reliable for Funda)
        for kw in keywords:
            for dt in soup.find_all("dt"):
                if kw.lower() in dt.get_text().lower():
                    dd = dt.find_next_sibling("dd")
                    if dd:
                        val = dd.get_text(strip=True)
                        if val: return val

        # 2. Fallback to line-based search
        for kw in keywords:
            val = self._extract_spec_by_keyword(soup, kw)
            if val: return val
            
        return None

    def _extract_spec_by_keyword(self, soup, keyword):
        text = soup.get_text(separator="\n")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        for i, line in enumerate(lines):
            # Check if line IS the keyword or CONTAINS it at the end (e.g. "453 m2 wonen")
            if re.search(f"\\b{keyword}\\b", line, re.IGNORECASE):
                # Case 1: "Keyword: Value"
                match_colon = re.search(f"{keyword}:?\\s*(.*)", line, re.IGNORECASE)
                if match_colon and match_colon.group(1).strip():
                    val = match_colon.group(1).strip()
                    if self._is_mostly_digits(val): return val
                
                # Case 2: "Value Keyword" (e.g. "453 m² wonen" or "2 badkamers")
                # Value must be at the end of the line with the keyword, and relatively short
                match_before = re.search(f"(^|\\s)(.{1,15})\\s+{keyword}$", line, re.IGNORECASE)
                if match_before and match_before.group(2).strip():
                    val = match_before.group(2).strip()
                    if self._is_mostly_digits(val): return val

                # Case 3: Value is in next line
                if i < len(lines) - 1:
                    nxt = lines[i+1]
                    if self._is_mostly_digits(nxt): return nxt

                # Case 4: Value is in previous line (Use strict check to avoid crossing)
                if i > 0:
                    prev = lines[i-1]
                    if self._is_mostly_digits(prev, strict=True): return prev
        
        return None

    def _is_mostly_digits(self, text, strict=False):
        if not text: return False
        
        # Original density check
        clean = re.sub(r'[\d\.,\s]|m[²23]', '', text, flags=re.IGNORECASE)
        is_dense = len(clean) < len(text) * 0.4
        if is_dense: return True
        
        if strict: return False

        # Relaxed check for Case 1, 2, 3 (Same line or Next line)
        # Allow short descriptive strings even without digits (e.g. "Villa", "Gas", "Bestaande bouw")
        if len(text) < 80:
            # Avoid picking up long narrative lines
            if len(text) > 40 and any(c in text for c in [",", ".", "!"]):
                 # Sounds like a sentence
                 return False
            return True
        
        return False

    def _extract_label(self, soup) -> str:
        # Search for "Energielabel" then find letter A-G
        text = soup.get_text(separator="\n")
        # Handle "Energielabel: C" or "Energielabel C" or "Energielabel: A++"
        match = re.search(r"Energielabel[:\s]*([A-G][\+]*)\b", text, re.IGNORECASE)
        if match: return match.group(1).upper()
        
        # Simple letter search in short lines
        for line in text.splitlines():
            if len(line.strip()) < 15 and re.match(r"^[A-G][\+]*$", line.strip()):
                return line.strip().upper()
        
        return "?"

    def _extract_media_urls(self, soup) -> List[str]:
        # Extract images from meta tags and standard img tags
        urls = []
        # Meta og:image is usually the main photo
        meta_img = soup.find("meta", property="og:image")
        if meta_img: urls.append(meta_img.get("content"))
        
        # First few large images
        imgs = soup.find_all("img", src=True)
        for img in imgs:
            src = img["src"]
            if "media.funda.nl" in src and "p2" in src: # p2 is usually high res
                urls.append(src)
            if len(urls) >= 10: break
            
        return [u for u in urls if u]

    def _extract_bedrooms(self, soup):
        text = soup.get_text()
        m = re.search(r"(\d+)\s*slaapkamer", text, re.IGNORECASE)
        if m: return m.group(1)
        val = self._extract_spec(soup, "slaapkamers")
        num = self._parse_num(val)
        return str(num) if num is not None else None

    def _extract_bathrooms(self, soup):
        val = self._extract_spec(soup, "badkamers")
        num = self._parse_num(val)
        return str(num) if num is not None else None

    def _extract_property_type(self, soup):
        return self._extract_spec(soup, "Soort woonhuis")

    def _extract_construction_type(self, soup):
        return self._extract_spec(soup, "Soort bouw")

    def _extract_garage(self, soup):
        return self._extract_spec(soup, "Soort garage")

    def _extract_garden(self, soup):
        return self._extract_spec(soup, "Tuin")

    def _extract_balcony(self, soup):
        return "Ja" if self._extract_spec(soup, "Balkon") else "Nee"

    def _extract_roof_type(self, soup):
        return self._extract_spec(soup, "Soort dak")

    def _extract_heating(self, soup):
        return self._extract_spec(soup, "Verwarming")

    def _extract_insulation(self, soup):
        return self._extract_spec(soup, "Isolatie")

    def _extract_service_costs(self, soup):
        return self._extract_spec(soup, "Servicekosten")

    def _extract_acceptance(self, soup):
        return self._extract_spec(soup, "Aanvaarding")

    def _extract_ownership(self, soup):
        return self._extract_spec(soup, "Eigendomssituatie")

    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure we don't have crazy values
        validated = data.copy()
        warnings = []
        
        # Room logic
        try:
            rooms_val = self._parse_num(data.get("rooms"))
            bed_val = self._parse_num(data.get("bedrooms"))
            bath_val = self._parse_num(data.get("bathrooms"))
            if bed_val and bed_val > self.MAX_BEDROOMS:
                validated["bedrooms"] = str(self.MAX_BEDROOMS)
                warnings.append(f"Suspicious bedroom count: {bed_val}. Capping at {self.MAX_BEDROOMS}.")
            if rooms_val and rooms_val > self.MAX_TOTAL_ROOMS:
                validated["rooms"] = str(self.MAX_TOTAL_ROOMS)
                warnings.append(f"Suspiciously high room count: {rooms_val}. Capping at {self.MAX_TOTAL_ROOMS}.")
            if bath_val and bath_val > self.MAX_BATHROOMS:
                validated["bathrooms"] = str(self.MAX_BATHROOMS)
                warnings.append(f"Suspicious bathroom count: {bath_val}.")
        except: pass

        if data.get("living_area_m2"):
            area = self._parse_num(data["living_area_m2"])
            if area and (area < self.MIN_LIVING_AREA or area > self.MAX_LIVING_AREA):
                validated["living_area_m2"] = None
                warnings.append(f"Living area out of logical range: {area}")
        
        if data.get("build_year"):
            year = self._parse_num(data["build_year"])
            if year and (year < self.MIN_BUILD_YEAR or year > self.MAX_BUILD_YEAR):
                validated["build_year"] = None
                warnings.append(f"Build year out of range: {year}")
        
        if warnings:
            validated["_parsing_warnings"] = warnings
                
        return validated

    def _parse_num(self, val):
        if not val: return None
        # Dutch format uses dots for thousands. Remove them before extracting numbers.
        # But be careful: if there's a comma, it might be a decimal. 
        # For our purposes (area, rooms, price), we'll strip dots and treat comma as a separator.
        s = str(val).replace('.', '')
        match = re.search(r'(\d+)', s)
        return int(match.group(1)) if match else None
