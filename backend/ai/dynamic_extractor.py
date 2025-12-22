import json
import logging
from typing import List, Dict, Any, Optional
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class DynamicExtractor:
    """
    Implements the 'Dynamic Interpretation Pipeline' for schema-agnostic
    attribute discovery from raw text/HTML pastes.
    
    This component turns unstructured property data into typed, namespaced attributes
    with confidence scores and provenance.
    """

    def __init__(self, provider):
        """
        Initialize with an AIProvider instance (e.g. OpenAIProvider, OllamaProvider).
        """
        self.provider = provider

    async def extract_attributes(self, text: str) -> List[Dict[str, Any]]:
        """
        Performs the full segmentation -> extraction -> classification pipeline.
        
        Returns a list of attribute dictionaries matching the database schema.
        """
        if not text or len(text.strip()) < 10:
            return []

        # 1. Pipeline Stage: Request extraction from LLM
        prompt = self._build_extraction_prompt(text)
        
        try:
            # We use a lower temperature for extraction to improve reliability
            response = await self.provider.generate(prompt)
            
            # 2. Pipeline Stage: Parse LLM output
            # Look for JSON array in the response
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if not json_match:
                logger.warning("DynamicExtractor: No JSON array found in LLM response.")
                # Fallback: simple regex for common fields if LLM fails? 
                # (Skipped for now to maintain LLM-first strategy)
                return []

            extracted_data = json.loads(json_match.group(0))
            
            # 3. Pipeline Stage: Validation and Post-processing
            valid_attributes = []
            for item in extracted_data:
                processed = self._process_item(item, text)
                if processed:
                    valid_attributes.append(processed)
            
            logger.info(f"Successfully extracted {len(valid_attributes)} dynamic attributes.")
            return valid_attributes

        except json.JSONDecodeError as e:
            logger.error(f"DynamicExtractor: Failed to decode JSON from LLM: {e}")
            return []
        except Exception as e:
            logger.error(f"DynamicExtractor: Extraction pipeline error: {e}")
            return []

    def _build_extraction_prompt(self, text: str) -> str:
        """
        Constructs a structured prompt for the LLM to perform NER and attribute creation.
        """
        return f"""
        SYSTEM: Je bent een 'Property Data Extraction Agent' gespecialiseerd in de Nederlandse woningmarkt (Funda).
        TAAK: Analyseer de onderstaande 'paste' data en extraheer alle gestructureerde informatie.
        
        FORMAAT: Retourneer ELK kenmerk als een object in een JSON array.
        {{
          "key": "Interne naam (bijv. woonoppervlakte, vve_kosten, bouwjaar)",
          "name_nl": "Label zoals getoond (bijv. Woonoppervlakte, VvE bijdrage per maand)",
          "value": "De geëxtraheerde waarde inclusief eenheden (bijv. 145 m2, € 150)",
          "namespace": "Categorie (financial, energy, physical, technical, legal, location, features, narrative)",
          "confidence": 0.0 - 1.0 (score hoe zeker je bent),
          "source_snippet": "Het exacte tekstfragment (max 50 chars) waar dit vandaan komt"
        }}

        REGELS:
        1. Wees uitputtend. Extraheer alles: van isolatie tot tuinligging.
        2. Normaliseer de 'key' naar snake_case (bijv. 'soort_woning').
        3. Behoud de oorspronkelijke eenheden in de 'value'.
        4. Gebruik 'narrative' voor kwalitatieve beschrijvingen ('Lichte woonkamer').
        5. Geef GEEN tekst buiten de JSON array.

        INPUT DATA:
        ---
        {text[:4000]} 
        ---
        """

    def _process_item(self, item: Dict[str, Any], full_text: str) -> Optional[Dict[str, Any]]:
        """
        Validates, types, and cleans an individual extracted attribute.
        """
        required = ["key", "value", "namespace"]
        if not all(k in item for k in required):
            return None

        # Ensure confidence exists
        confidence = item.get("confidence", 0.5)
        try:
            confidence = float(confidence)
        except (ValueError, TypeError):
            confidence = 0.5

        # Basic type inference or unit recognition could happen here
        # (e.g., using quantulum3 in the future)
        
        return {
            "key": str(item["key"]).lower().replace(" ", "_"),
            "display_name": item.get("name_nl", item["key"]),
            "value": str(item["value"]),
            "namespace": item["namespace"],
            "confidence": confidence,
            "source_snippet": item.get("source_snippet", ""),
            "timestamp": datetime.now().isoformat()
        }
