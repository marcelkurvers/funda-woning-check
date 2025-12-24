"""
Fact-Safe Renderer - Registry-Only Fact Rendering

CORE INVARIANT (ABSOLUTE):
    If a factual value appears in a report, it MUST come from the CanonicalRegistry.
    AI-generated text is rendered AROUND facts, never containing them.

RENDERING RULE:
    - Facts are pulled from CanonicalRegistry ONLY
    - Facts are formatted by the SYSTEM
    - AI text is inserted as interpretation/context
    - AI text may NEVER contain factual values

EXAMPLE:
    ❌ "The asking price is €500.000, which is high."
    ✅ System renders: "Vraagprijs: €500.000" + AI renders: "This is considered high relative to comparable properties."

If a fact needs to appear in the report, the system MUST:
    1. Look it up in the registry
    2. Format it using system formatters
    3. Render it in a designated fact slot
    4. Render AI interpretation in a separate slot
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

from backend.domain.registry import CanonicalRegistry, RegistryEntry, RegistryType
from backend.domain.ai_interpretation_schema import (
    AIInterpretationOutput, 
    Interpretation, 
    Assessment,
    Risk,
    PreferenceMatch
)

logger = logging.getLogger(__name__)


# =============================================================================
# FACT FORMATTING - SYSTEM-ONLY
# =============================================================================

def format_currency(value: Any, currency: str = "EUR") -> str:
    """Format a currency value. SYSTEM FUNCTION - NOT AI."""
    if value is None:
        return "Niet beschikbaar"
    try:
        num = int(float(value))
        formatted = f"{num:,}".replace(",", ".")
        return f"€ {formatted}"
    except (ValueError, TypeError):
        return str(value)


def format_area(value: Any, unit: str = "m²") -> str:
    """Format an area value. SYSTEM FUNCTION - NOT AI."""
    if value is None or value == 0:
        return "Niet beschikbaar"
    return f"{value} {unit}"


def format_year(value: Any) -> str:
    """Format a year value. SYSTEM FUNCTION - NOT AI."""
    if value is None or value == 0:
        return "Niet beschikbaar"
    return str(int(value))


def format_percentage(value: Any) -> str:
    """Format a percentage value. SYSTEM FUNCTION - NOT AI."""
    if value is None:
        return "Niet beschikbaar"
    return f"{value}%"


def format_energy_label(value: Any) -> str:
    """Format an energy label. SYSTEM FUNCTION - NOT AI."""
    if value is None or value == "":
        return "?"
    return str(value).upper()


# Registry key to formatter mapping
FORMATTERS = {
    "asking_price_eur": format_currency,
    "price_per_m2": format_currency,
    "estimated_reno_cost": format_currency,
    "energy_invest": format_currency,
    "construction_invest": format_currency,
    "living_area_m2": format_area,
    "plot_area_m2": format_area,
    "volume_m3": lambda v: format_area(v, "m³"),
    "build_year": format_year,
    "energy_label": format_energy_label,
    "marcel_match_score": format_percentage,
    "petra_match_score": format_percentage,
    "total_match_score": format_percentage,
    "ai_score": lambda v: f"{v}/100" if v is not None else "Niet beschikbaar",
}


def format_registry_value(key: str, value: Any) -> str:
    """
    Format a registry value using the appropriate system formatter.
    
    SYSTEM FUNCTION - AI may not call this to create facts.
    """
    formatter = FORMATTERS.get(key, str)
    return formatter(value)


# =============================================================================
# RENDERED FACT - THE ATOMIC UNIT OF SYSTEM-OWNED DISPLAY
# =============================================================================

@dataclass
class RenderedFact:
    """
    A single rendered fact from the registry.
    
    This is the ATOMIC unit of factual display.
    It contains:
        - The registry ID (for auditability)
        - The formatted value (SYSTEM-generated)
        - Optional AI interpretation (AI-generated, no facts)
    
    INVARIANT: The 'formatted_value' comes from the registry + system formatter.
               The 'interpretation' comes from AI and contains NO facts.
    """
    registry_id: str
    label: str  # Human-readable label (from registry name)
    formatted_value: str  # SYSTEM-FORMATTED value
    unit: Optional[str] = None
    interpretation: Optional[str] = None  # AI interpretation (NO FACTS)
    assessment: Optional[str] = None  # AI assessment (high/average/low)
    source: str = "registry"  # Always "registry" for auditing
    
    def to_html(self, include_interpretation: bool = True) -> str:
        """Render as HTML. Fact and interpretation are SEPARATE."""
        html = f"""
        <div class="rendered-fact" data-registry-id="{self.registry_id}">
            <span class="fact-label">{self.label}:</span>
            <span class="fact-value">{self.formatted_value}</span>
        """
        
        if include_interpretation and self.interpretation:
            html += f"""
            <span class="fact-interpretation">{self.interpretation}</span>
            """
        
        if self.assessment:
            html += f"""
            <span class="fact-assessment assessment-{self.assessment}">{self.assessment}</span>
            """
        
        html += "</div>"
        return html
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "registry_id": self.registry_id,
            "label": self.label,
            "value": self.formatted_value,
            "unit": self.unit,
            "interpretation": self.interpretation,
            "assessment": self.assessment,
            "source": self.source
        }


# =============================================================================
# FACT-SAFE RENDERER - THE CORE CLASS
# =============================================================================

class FactSafeRenderer:
    """
    Renders reports with strict fact/interpretation separation.
    
    INVARIANTS:
        1. All facts come from the locked CanonicalRegistry
        2. Facts are formatted by system formatters
        3. AI interpretations are inserted around facts, never containing them
        4. Every rendered fact is traceable to a registry_id
    
    If these invariants are violated, audit will fail.
    """
    
    def __init__(self, registry: CanonicalRegistry):
        """
        Initialize with a LOCKED registry.
        
        Args:
            registry: The canonical registry (MUST be locked)
            
        Raises:
            ValueError: If registry is not locked
        """
        if not registry.is_locked():
            raise ValueError(
                "FATAL: FactSafeRenderer requires a LOCKED registry. "
                "This prevents facts from changing during rendering."
            )
        
        self._registry = registry
        self._rendered_facts: Dict[str, RenderedFact] = {}
    
    def render_fact(
        self, 
        registry_id: str, 
        interpretation: Optional[AIInterpretationOutput] = None
    ) -> Optional[RenderedFact]:
        """
        Render a single fact from the registry.
        
        Args:
            registry_id: The registry ID to render
            interpretation: Optional AI interpretation output
            
        Returns:
            RenderedFact or None if not in registry
        """
        entry = self._registry.get(registry_id)
        if entry is None:
            logger.warning(f"FactSafeRenderer: Registry ID '{registry_id}' not found")
            return None
        
        # Format value using SYSTEM formatter
        formatted = format_registry_value(registry_id, entry.value)
        
        # Find AI interpretation if provided
        ai_interpretation = None
        ai_assessment = None
        
        if interpretation:
            for interp in interpretation.interpretations:
                if interp.registry_id == registry_id:
                    ai_interpretation = interp.reasoning
                    ai_assessment = interp.assessment.value if hasattr(interp.assessment, 'value') else str(interp.assessment)
                    break
        
        rendered = RenderedFact(
            registry_id=registry_id,
            label=entry.name,
            formatted_value=formatted,
            unit=entry.unit,
            interpretation=ai_interpretation,
            assessment=ai_assessment,
            source="registry"
        )
        
        self._rendered_facts[registry_id] = rendered
        return rendered
    
    def render_facts_for_chapter(
        self,
        chapter_id: int,
        owned_keys: List[str],
        interpretation: Optional[AIInterpretationOutput] = None
    ) -> List[RenderedFact]:
        """
        Render all facts owned by a chapter.
        
        Args:
            chapter_id: The chapter number
            owned_keys: List of registry keys this chapter owns
            interpretation: Optional AI interpretation output
            
        Returns:
            List of RenderedFact objects
        """
        facts = []
        
        for key in owned_keys:
            rendered = self.render_fact(key, interpretation)
            if rendered:
                facts.append(rendered)
        
        logger.info(
            f"FactSafeRenderer: Rendered {len(facts)} facts for Chapter {chapter_id}"
        )
        
        return facts
    
    def render_chapter_content(
        self,
        chapter_id: int,
        owned_keys: List[str],
        interpretation: Optional[AIInterpretationOutput] = None
    ) -> Dict[str, Any]:
        """
        Render complete chapter content with strict fact/interpretation separation.
        
        Returns a structure where:
            - 'facts' contains ONLY system-rendered values
            - 'interpretations' contains ONLY AI analysis (no facts)
            - Both are separate and traceable
        
        Args:
            chapter_id: The chapter number
            owned_keys: List of registry keys this chapter owns
            interpretation: Optional AI interpretation output
            
        Returns:
            Chapter content dict with separated facts and interpretations
        """
        facts = self.render_facts_for_chapter(chapter_id, owned_keys, interpretation)
        
        # Build content structure
        content = {
            "chapter_id": chapter_id,
            "facts": [f.to_dict() for f in facts],
            "facts_html": "\n".join(f.to_html() for f in facts),
            
            # AI interpretations (NO FACTS)
            "title": "",
            "summary": "",
            "detailed_analysis": "",
            "risks": [],
            "preference_matches": [],
            "uncertainties": [],
            
            # Metadata
            "fact_count": len(facts),
            "interpretation_provided": interpretation is not None,
            "_source": "FactSafeRenderer",
            "_registry_locked": True
        }
        
        # Add AI interpretations if provided
        if interpretation:
            content["title"] = interpretation.title
            content["summary"] = interpretation.summary
            content["detailed_analysis"] = interpretation.detailed_analysis
            content["risks"] = [
                {
                    "registry_id": r.registry_id,
                    "impact": r.impact.value if hasattr(r.impact, 'value') else str(r.impact),
                    "explanation": r.explanation
                }
                for r in interpretation.risks
            ]
            content["preference_matches"] = [
                {
                    "preference_id": pm.preference_id,
                    "registry_id": pm.registry_id,
                    "fit": pm.fit.value if hasattr(pm.fit, 'value') else str(pm.fit),
                    "explanation": pm.explanation
                }
                for pm in interpretation.preference_matches
            ]
            content["uncertainties"] = [
                {
                    "registry_id": u.registry_id,
                    "reason": u.reason.value if hasattr(u.reason, 'value') else str(u.reason)
                }
                for u in interpretation.uncertainties
            ]
            content["ai_confidence"] = interpretation.confidence
            content["ai_provider"] = interpretation.provider
            content["ai_model"] = interpretation.model
        
        return content
    
    def get_all_rendered_facts(self) -> Dict[str, RenderedFact]:
        """Get all facts that have been rendered. For audit purposes."""
        return self._rendered_facts.copy()
    
    def audit_fact_origins(self) -> Dict[str, str]:
        """
        Audit that all rendered facts originated from the registry.
        
        Returns:
            Dict mapping registry_id to source (always "registry")
        """
        return {k: v.source for k, v in self._rendered_facts.items()}


# =============================================================================
# SAFE NARRATIVE GENERATOR - AI TEXT WITHOUT FACTS
# =============================================================================

def generate_safe_narrative_prompt(
    chapter_id: int,
    registry_facts: List[RenderedFact],
    chapter_focus: str
) -> str:
    """
    Generate a prompt that instructs AI to interpret, not restate.
    
    The prompt explicitly lists facts and instructs AI to NOT include them.
    
    Args:
        chapter_id: The chapter number
        registry_facts: Facts from the registry (AI sees these but must not restate)
        chapter_focus: Description of what this chapter analyzes
        
    Returns:
        AI prompt string
    """
    facts_list = "\n".join([
        f"- {f.label}: {f.formatted_value}"
        for f in registry_facts
    ])
    
    prompt = f"""
You are analyzing a property for Chapter {chapter_id}: {chapter_focus}.

CRITICAL RULES (VIOLATION = PIPELINE FAILURE):
1. You MAY NOT output any numbers, prices, percentages, or measurements
2. You MAY NOT restate any of the facts listed below
3. You can ONLY output interpretations, assessments, and reasoning
4. Your text must be meaningful WITHOUT including specific values

FACTS (for context - DO NOT INCLUDE THESE IN YOUR OUTPUT):
{facts_list}

YOUR OUTPUT MUST BE:
{{
    "interpretations": [
        {{
            "registry_id": "key_name",
            "assessment": "high|average|low",
            "reasoning": "Interpretive text WITHOUT numbers"
        }}
    ],
    "risks": [
        {{
            "registry_id": "key_name",
            "impact": "low|medium|high",
            "explanation": "Risk explanation WITHOUT numbers"
        }}
    ],
    "preference_matches": [
        {{
            "preference_id": "marcel_tech" or "petra_comfort",
            "registry_id": "key_name",
            "fit": "good|neutral|poor"
        }}
    ],
    "uncertainties": [
        {{
            "registry_id": "key_name",
            "reason": "missing|uncertain"
        }}
    ],
    "title": "Chapter title",
    "summary": "Brief interpretive summary WITHOUT any numbers",
    "detailed_analysis": "Extended analysis WITHOUT any specific values"
}}

FORBIDDEN IN YOUR OUTPUT:
❌ €, $, or any currency symbol
❌ m², m2, m³, or any unit with numbers
❌ Percentages like "85%"
❌ Years like "1920" or "built in 1930"
❌ Any numeric values

EXAMPLES:
❌ BAD: "The property costs €500.000 which is high"
✅ GOOD: "The asking price is considered high for this market segment"

❌ BAD: "With 120m² of living space"
✅ GOOD: "The living space is generous compared to similar properties"

Generate your interpretation now.
"""
    return prompt
