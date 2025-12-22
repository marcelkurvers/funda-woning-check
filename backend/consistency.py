import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VerifyResult:
    field: str
    source_value: Optional[str]
    parsed_value: Optional[str]
    status: str # "ok", "mismatch", "missing_source"
    message: str

class ConsistencyChecker:
    """
    Dynamic Verification Layer.
    
    Instead of hardcoding regex extraction for every field (which duplicates the parser),
    this checker acts as a 'Reverse Validator'.
    
    It takes the *Parsed Value* and verifies if it (or a plausible format of it) 
    exists in the *Source Text*, ideally in the correct context.
    """

    # Heuristic mapping of field names to likely Dutch context keywords
    # This helps disambiguate small numbers (e.g. "4" bedrooms vs "4" in postcode).
    CONTEXT_KEYWORDS = {
        "price": ["vraagprijs", "prijs", "koopsom", "kosten", "euro", "€"],
        "area": ["oppervlakte", "wonen", "gebruiks", "m2", "m²", "vierkante"],
        "living": ["wonen", "woonoppervlakte", "leefruimte"],
        "plot": ["perceel", "grond", "kavel"],
        "bedroom": ["slaapkamer", "slp", "bed"],
        "bathroom": ["badkamer", "bad", "sanitair"],
        "room": ["kamer", "vertrek"],
        "year": ["bouwjaar", "jaar", "gebouwd"],
        "label": ["energielabel", "label", "energie"],
        "garden": ["tuin", "buiten"],
        "garage": ["garage", "parkeer"],
        "volume": ["inhoud", "m3", "m³"],
        "service_costs": ["servicekosten", "vve", "bijdrage"],
        "acceptance": ["aanvaarding", "oplevering"],
        "ownership": ["eigendom", "erfpacht", "grond"]
    }

    ignored_fields = [
        "funda_url", "_parsing_warnings", "description", "features", 
        "media_urls", "extra_facts", "id", "_preferences",
        "asking_price_per_m2" # Derivative field, often not explicit in text
    ]

    def check(self, raw_text: str, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        
        # Flatten and Normalize Text for search
        # We keep a version with lines for context, and a flat version for scanning
        text_lines = raw_text.splitlines()
        flat_text_lower = raw_text.lower()

        for key, value in parsed_data.items():
            # 1. Skip irrelevant fields
            if key in self.ignored_fields or value in [None, "", []]:
                continue
            
            # 2. Skip complex objects (lists/dicts) - we only verify scalar extraction
            if isinstance(value, (list, dict)):
                continue

            # 3. Determine Field Type & Search Strategy
            str_val = str(value).strip()
            if not str_val: 
                continue

            # Heuristics to skip "default" values if they look like placeholder (e.g. 0)
            if str_val == "0":
                continue

            status = "unknown"
            msg = ""

            # STRATEGY A: Numeric Value Verification
            # If value looks like a number (digits > 0), we use context-aware search.
            digits_only = re.sub(r'[^\d]', '', str_val)
            is_numeric_field = len(digits_only) > 0 and (len(digits_only) / len(str_val) > 0.5 or len(digits_only) >= 1)
            
            if is_numeric_field:
                match_found, match_context = self._find_number_in_context(key, digits_only, text_lines)
                
                if match_found:
                    status = "ok"
                else:
                    # FAILED context check.
                    # Only fallback to loose string search if it's a complex string (e.g. "3e verdieping")
                    # NOT if it's just "4".
                    if len(str_val) > 4 and str_val.lower() in flat_text_lower:
                         status = "ok"
                    else:
                        status = "mismatch"
                        kw_hint = self.CONTEXT_KEYWORDS.get(key, [])
                        msg = f"Waarde '{str_val}' niet gevonden bij trefwoorden {kw_hint}."

            # STRATEGY B: String/Enum Verification (e.g. Label A, Garage present)
            else:
                # Special case: Boolean values (Ja/Nee)
                if str_val.lower() in ['ja', 'nee', 'yes', 'no']:
                    # For boolean values, check if the field name appears in the text
                    field_keywords = []
                    if 'balcony' in key.lower() or 'balkon' in key.lower():
                        field_keywords = ['balkon', 'balcony']
                    elif 'garden' in key.lower() or 'tuin' in key.lower():
                        field_keywords = ['tuin', 'garden']
                    elif 'garage' in key.lower():
                        field_keywords = ['garage', 'parkeer']
                    elif 'terrace' in key.lower() or 'terras' in key.lower():
                        field_keywords = ['terras', 'terrace']
                    
                    if field_keywords:
                        if any(kw in flat_text_lower for kw in field_keywords):
                            status = "ok"
                        else:
                            status = "mismatch"
                            msg = f"Veld '{key}' niet gevonden in brontekst."
                    else:
                        if str_val.lower() in flat_text_lower:
                            status = "ok"
                        else:
                            status = "mismatch"
                            msg = f"Waarde '{str_val}' niet gevonden als losstaand woord."
                
                # If short string (non-boolean), enforce word boundary
                elif len(str_val) < 4:
                    safe_val = re.escape(str_val.lower())
                    if re.search(rf'\b{safe_val}\b', flat_text_lower):
                        status = "ok"
                    else:
                        status = "mismatch"
                        msg = f"Waarde '{str_val}' niet gevonden als losstaand woord."
                else:
                    # Direct case-insensitive search
                    if str_val.lower() in flat_text_lower:
                        status = "ok"
                    else:
                        status = "mismatch"
                        msg = f"Tekst '{str_val}' niet letterlijk gevonden in brontekst."

            results.append({
                "field": key,
                "status": status,
                "source": "Text Scan",
                "parsed": str_val,
                "message": msg
            })

        # Log mismatches
        issues = [r for r in results if r["status"] == "mismatch"]
        if issues:
            logger.warning(f"Consistency Issues: {len(issues)} fields mismatch.")
            
        return results

    def _find_number_in_context(self, field_key: str, target_digits: str, lines: List[str]) -> Tuple[bool, str]:
        """
        Scans lines. If it finds the target_digits, it checks if
        relevant context keywords are present in that line (or adjacency).
        """
        # 1. Identify Context Keywords for this field
        keywords = []
        for k_part, words in self.CONTEXT_KEYWORDS.items():
            if k_part in field_key.lower():
                keywords.extend(words)
        
        # If no keywords found, fallback to the key itself parts
        if not keywords:
            keywords = field_key.lower().replace('_', ' ').split()

        # 2. Scan Lines
        # We search for the digits. But digits might be formatted: 1.500.000 or 1500000
        # We create a regex that allows dots/commas between digits
        # e.g. 1.*5.*0.*0.*0.*0.*0
        # This is loose, but effective for "1.500.000" matching "1500000"
        
        # However, for small numbers (e.g. 15), "1.*5" matches "105". Too loose.
        if len(target_digits) < 4:
            # Strict exact match for small numbers
            regex_pat = re.compile(rf'\b{target_digits}\b')
        else:
            # Allow thousand separators for big numbers
            pattern_str = r"\D?".join(list(target_digits))
            regex_pat = re.compile(pattern_str)

        for i, line in enumerate(lines):
            for match in regex_pat.finditer(line):
                # Verify boundaries:
                # Check char before match
                start, end = match.span()
                if start > 0 and line[start-1].isdigit():
                    continue # Part of larger number suffix
                
                # Check char after match
                # We need to be careful with decimals. "1.400.000" matched "1.400.00". Next is "0".
                if end < len(line) and line[end].isdigit():
                    continue # Part of larger number prefix
                
                # If "1.400.00" matched inside "1.400.000", the regex \D? might have consumed the last dot?
                # No, \D? matches 0 or 1 non-digit.
                # If target is 140000. pattern is 1\D?4\D?0...
                # It would match 1.400.00
                
                # Found valid number! Now check context.
                window = " ".join(lines[max(0, i-1):min(len(lines), i+2)]).lower()
                
                if any(kw in window for kw in keywords):
                    return True, line.strip()
                
                if "price" in field_key and "€" in window:
                    return True, line.strip()

        # If we found nothing with context, we might accept a "naked" match 
        # only if the number is very unique (> 4 digits), e.g. a price or specific area
        if len(target_digits) >= 4:
             full_text = "\n".join(lines)
             for match in regex_pat.finditer(full_text):
                start, end = match.span()
                # Verify boundaries (same as above):
                if start > 0 and full_text[start-1].isdigit():
                    continue 
                if end < len(full_text) and full_text[end].isdigit():
                    continue
                
                return True, "Found in text (no context)"

        return False, ""
