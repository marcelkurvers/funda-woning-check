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
        system_prompt, user_prompt = self._build_extraction_prompts(text)
        
        try:
            # We use a lower temperature for extraction to improve reliability and enable json_mode
            response = await self.provider.generate(
                user_prompt, 
                system=system_prompt,
                temperature=0.2, 
                json_mode=True
            )
            
            # 2. Pipeline Stage: Parse LLM output
            if not response:
                logger.warning("DynamicExtractor: Empty response from LLM.")
                return []

            # Clean the response in case there's markdown or extra text
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                # Handle markdown code blocks
                lines = cleaned_response.splitlines()
                if lines[0].startswith("```json"):
                    cleaned_response = "\n".join(lines[1:-1])
                elif lines[0].startswith("```"):
                    cleaned_response = "\n".join(lines[1:-1])
            
            # Look for JSON array in the response if it's not a pure array
            if not (cleaned_response.startswith("[") and cleaned_response.endswith("]")):
                json_match = re.search(r'\[\s*\{.*\}\s*\]', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(0)
                else:
                    logger.warning("DynamicExtractor: No JSON array found in LLM response.")
                    return []

            extracted_data = json.loads(cleaned_response)
            
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

    def _build_extraction_prompts(self, text: str) -> tuple[str, str]:
        """
        Constructs structured prompts (system and user) for the LLM.
        """
        system_prompt = """
        You are a 'Property Data Extraction Agent' specialized in the Dutch housing market (Funda).
        Your task is to analyze the provided 'paste' data and extract all structured information.
        
        FORMAT: Return EVERY attribute as an object in a JSON array.
        {
          "key": "Internal name (e.g. woonoppervlakte, vve_kosten, bouwjaar)",
          "name_nl": "Label as shown in Dutch (e.g. Woonoppervlakte, VvE bijdrage per maand)",
          "value": "The extracted value including units (e.g. 145 m2, € 150)",
          "namespace": "Category (financial, energy, physical, technical, legal, location, features, narrative)",
          "confidence": 0.0 - 1.0 (score how sure you are),
          "source_snippet": "The exact text fragment (max 50 chars) where this came from"
        }

        RULES:
        1. Be exhaustive. Extract everything: from insulation to garden orientation.
        2. Normalize the 'key' to snake_case (e.g. 'soort_woning').
        3. Maintain original units in the 'value'.
        4. Use 'narrative' for qualitative descriptions ('Bright living room').
        5. Output MUST be a valid JSON array of objects.
        """

        user_prompt = f"INPUT DATA:\n---\n{text[:4000]}\n---"
        
        return system_prompt, user_prompt

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
