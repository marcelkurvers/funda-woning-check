"""
Presentation-Only Narrative Templates

INVARIANTS (NON-NEGOTIABLE):
1. NO arithmetic operations
2. NO value derivation
3. NO heuristics
4. All values MUST come from registry

If AI is unavailable, these templates render registry data directly.
No estimation, no inference, no computation.

If a value is missing from the registry, it MUST be explicitly marked
as "Niet beschikbaar" - NOT estimated.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# TEMPLATE CONSTANTS
# ============================================================================

UNAVAILABLE = "Niet beschikbaar"
INSUFFICIENT_DATA = "Onvoldoende data voor analyse"
AI_REQUIRED = "AI-analyse vereist voor diepgaande interpretatie"


def _get(data: Dict[str, Any], key: str, default: str = UNAVAILABLE) -> str:
    """Safely get a value from registry data, returning default if not present."""
    val = data.get(key)
    if val is None or val == "" or val == 0:
        return default
    return str(val)


def _format_price(val: Any) -> str:
    """Format a price value without computation."""
    if val is None or val == 0:
        return UNAVAILABLE
    if isinstance(val, (int, float)):
        return f"€ {int(val):,}".replace(",", ".")
    return str(val)


def _format_area(val: Any, unit: str = "m²") -> str:
    """Format an area value without computation."""
    if val is None or val == 0:
        return UNAVAILABLE
    return f"{val} {unit}"


# ============================================================================
# REGISTRY-ONLY NARRATIVE TEMPLATES
# ============================================================================

def narrative_ch0_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chapter 0: Executive Summary - Registry Values Only
    
    NO COMPUTATION. NO INFERENCE. REGISTRY VALUES ONLY.
    """
    address = _get(data, 'address', _get(data, 'adres', 'Object'))
    price = _format_price(data.get('asking_price_eur'))
    area = _format_area(data.get('living_area_m2'))
    plot = _format_area(data.get('plot_area_m2'))
    year = _get(data, 'build_year')
    label = _get(data, 'energy_label', '?')
    
    # Pre-computed values from registry (computed in enrichment layer)
    marcel_score = _get(data, 'marcel_match_score', '0')
    petra_score = _get(data, 'petra_match_score', '0')
    total_score = _get(data, 'total_match_score', '0')
    ai_score = _get(data, 'ai_score', '0')
    price_m2 = _format_price(data.get('price_per_m2'))
    
    return {
        "title": "Executive Summary",
        "intro": f"Woning aan {address}. Vraagprijs: {price}. Woonoppervlak: {area}.",
        "main_analysis": f"""
        <p><strong>Kerngegevens uit Registry</strong></p>
        <ul>
            <li>Adres: {address}</li>
            <li>Vraagprijs: {price}</li>
            <li>Woonoppervlak: {area}</li>
            <li>Perceelgrootte: {plot}</li>
            <li>Bouwjaar: {year}</li>
            <li>Energielabel: {label}</li>
            <li>Prijs per m²: {price_m2}</li>
        </ul>
        <p><strong>Match Scores (vooraf berekend)</strong></p>
        <ul>
            <li>Marcel: {marcel_score}%</li>
            <li>Petra: {petra_score}%</li>
            <li>Totaal: {total_score}%</li>
            <li>AI Score: {ai_score}/100</li>
        </ul>
        <p><em>{AI_REQUIRED}</em></p>
        """,
        "interpretation": AI_REQUIRED,
        "conclusion": f"Woning data geladen. {AI_REQUIRED}",
        "variables": {},  # No variables computed here
        "comparison": {
            "marcel": f"Match score: {marcel_score}%",
            "petra": f"Match score: {petra_score}%",
            "combined_advice": AI_REQUIRED
        },
        "strengths": [],
        "advice": [],
        "_provenance": {
            "provider": "Registry Template",
            "model": "Presentation-Only",
            "confidence": "low",
            "note": "No AI enrichment - registry values only"
        }
    }


def narrative_ch1_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 1: General Features - Registry Values Only"""
    return _create_minimal_narrative(
        chapter_id=1,
        title="Algemene Woningkenmerken",
        data=data,
        specific_keys=['living_area_m2', 'plot_area_m2', 'build_year', 'energy_label', 'rooms', 'volume_m3']
    )


def narrative_ch2_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 2: Match Analysis - Registry Values Only"""
    marcel = _get(data, 'marcel_match_score', '0')
    petra = _get(data, 'petra_match_score', '0')
    total = _get(data, 'total_match_score', '0')
    
    return {
        "title": "Matchanalyse Marcel & Petra",
        "intro": f"Match scores geladen uit registry: Totaal {total}%.",
        "main_analysis": f"""
        <p><strong>Match Scores (vooraf berekend in enrichment layer)</strong></p>
        <ul>
            <li>Marcel: {marcel}%</li>
            <li>Petra: {petra}%</li>
            <li>Totaal: {total}%</li>
        </ul>
        <p><em>{AI_REQUIRED}</em></p>
        """,
        "interpretation": AI_REQUIRED,
        "conclusion": f"Totale match: {total}%",
        "comparison": {
            "marcel": f"Score: {marcel}%",
            "petra": f"Score: {petra}%"
        },
        "strengths": [],
        "advice": [],
        "_provenance": {
            "provider": "Registry Template",
            "model": "Presentation-Only",
            "confidence": "low"
        }
    }


def narrative_ch3_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 3: Technical State - Registry Values Only"""
    return _create_minimal_narrative(
        chapter_id=3,
        title="Bouwkundige Staat",
        data=data,
        specific_keys=['build_year', 'construction_alert', 'construction_invest']
    )


def narrative_ch4_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 4: Energy & Sustainability - Registry Values Only"""
    return _create_minimal_narrative(
        chapter_id=4,
        title="Energie & Duurzaamheid",
        data=data,
        specific_keys=['energy_label', 'sustainability_advice', 'energy_invest']
    )


def narrative_ch5_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 5: Layout - Registry Values Only"""
    return _create_minimal_narrative(
        chapter_id=5,
        title="Indeling & Ruimte",
        data=data,
        specific_keys=['living_area_m2', 'rooms', 'bedrooms', 'volume_m3']
    )


def narrative_ch6_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 6: Maintenance & Finish - Registry Values Only"""
    return _create_minimal_narrative(
        chapter_id=6,
        title="Onderhoud & Afwerking",
        data=data,
        specific_keys=['build_year', 'estimated_reno_cost']
    )


def narrative_ch7_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 7: Garden & Exterior - Registry Values Only"""
    return _create_minimal_narrative(
        chapter_id=7,
        title="Tuin & Buiten",
        data=data,
        specific_keys=['plot_area_m2']
    )


def narrative_ch8_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 8: Mobility - Registry Values Only"""
    return _create_minimal_narrative(
        chapter_id=8,
        title="Mobiliteit",
        data=data,
        specific_keys=['address']
    )


def narrative_ch9_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 9: Legal Aspects - Registry Values Only"""
    return _create_minimal_narrative(
        chapter_id=9,
        title="Juridische Aspecten",
        data=data,
        specific_keys=['build_year', 'address']
    )


def narrative_ch10_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 10: Financial Analysis - Registry Values Only"""
    price = _format_price(data.get('asking_price_eur'))
    price_m2 = _format_price(data.get('price_per_m2'))
    valuation = _get(data, 'valuation_status', UNAVAILABLE)
    
    return {
        "title": "Financiële Analyse",
        "intro": f"Vraagprijs: {price}. Prijs per m²: {price_m2}.",
        "main_analysis": f"""
        <p><strong>Financiële Kerngegevens</strong></p>
        <ul>
            <li>Vraagprijs: {price}</li>
            <li>Prijs per m²: {price_m2}</li>
            <li>Marktwaardering: {valuation}</li>
        </ul>
        <p><em>Kosten koper, notariskosten en overige bijkomende kosten worden berekend op basis van de vraagprijs. {AI_REQUIRED}</em></p>
        """,
        "interpretation": AI_REQUIRED,
        "conclusion": f"Vraagprijs geregistreerd: {price}. {AI_REQUIRED}",
        "variables": {},
        "strengths": [],
        "advice": [],
        "_provenance": {
            "provider": "Registry Template",
            "model": "Presentation-Only",
            "confidence": "low"
        }
    }


def narrative_ch11_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 11: Market Position - Registry Values Only"""
    return _create_minimal_narrative(
        chapter_id=11,
        title="Marktpositie",
        data=data,
        specific_keys=['asking_price_eur', 'valuation_status', 'market_trend']
    )


def narrative_ch12_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 12: Verdict - Registry Values Only"""
    ai_score = _get(data, 'ai_score', '?')
    total_match = _get(data, 'total_match_score', '?')
    
    return {
        "title": "Advies & Conclusie",
        "intro": f"Gebaseerd op de beschikbare registry data.",
        "main_analysis": f"""
        <p><strong>Beschikbare Scores</strong></p>
        <ul>
            <li>AI Score: {ai_score}/100</li>
            <li>Match Score: {total_match}%</li>
        </ul>
        <p><em>Definitieve aanbevelingen vereisen AI-analyse van alle factoren.</em></p>
        <p>{AI_REQUIRED}</p>
        """,
        "interpretation": AI_REQUIRED,
        "conclusion": AI_REQUIRED,
        "variables": {},
        "strengths": [],
        "advice": [],
        "_provenance": {
            "provider": "Registry Template",
            "model": "Presentation-Only",
            "confidence": "low"
        }
    }


def narrative_ch13_registry_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """Chapter 13: Media Library - Registry Values Only"""
    media_count = len(data.get('media_urls', []))
    
    return {
        "title": "Media Bibliotheek",
        "intro": f"Deze sectie bevat {media_count} afbeelding(en) van de woning.",
        "main_analysis": f"""
        <p>Aantal geregistreerde media items: {media_count}</p>
        <p>Gebruik de Media Tab voor interactieve weergave.</p>
        """,
        "interpretation": "",
        "conclusion": f"{media_count} media items beschikbaar.",
        "variables": {},
        "_provenance": {
            "provider": "Registry Template",
            "model": "Presentation-Only",
            "confidence": "high"
        }
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _create_minimal_narrative(
    chapter_id: int,
    title: str,
    data: Dict[str, Any],
    specific_keys: list
) -> Dict[str, Any]:
    """
    Create a minimal, registry-only narrative for a chapter.
    
    NO COMPUTATION. Just displays the relevant registry values.
    """
    items = []
    for key in specific_keys:
        val = data.get(key)
        if val is not None and val != "" and val != 0:
            # Just display, no formatting that involves computation
            items.append(f"<li><strong>{key}</strong>: {val}</li>")
    
    items_html = "\n".join(items) if items else f"<li>{INSUFFICIENT_DATA}</li>"
    
    return {
        "title": title,
        "intro": f"{title} - Registry data geladen.",
        "main_analysis": f"""
        <p><strong>Relevante Registry Waarden</strong></p>
        <ul>
            {items_html}
        </ul>
        <p><em>{AI_REQUIRED}</em></p>
        """,
        "interpretation": AI_REQUIRED,
        "conclusion": f"Data geladen. {AI_REQUIRED}",
        "variables": {},
        "comparison": {},
        "strengths": [],
        "advice": [],
        "_provenance": {
            "provider": "Registry Template",
            "model": "Presentation-Only",
            "confidence": "low"
        }
    }


# ============================================================================
# DISPATCH
# ============================================================================

REGISTRY_NARRATIVE_DISPATCH = {
    0: narrative_ch0_registry_only,
    1: narrative_ch1_registry_only,
    2: narrative_ch2_registry_only,
    3: narrative_ch3_registry_only,
    4: narrative_ch4_registry_only,
    5: narrative_ch5_registry_only,
    6: narrative_ch6_registry_only,
    7: narrative_ch7_registry_only,
    8: narrative_ch8_registry_only,
    9: narrative_ch9_registry_only,
    10: narrative_ch10_registry_only,
    11: narrative_ch11_registry_only,
    12: narrative_ch12_registry_only,
    13: narrative_ch13_registry_only,
}


def get_registry_only_narrative(chapter_id: int, registry_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a registry-only narrative for a chapter.
    
    This is the fallback when AI is unavailable.
    NO COMPUTATION. NO INFERENCE. REGISTRY VALUES ONLY.
    """
    handler = REGISTRY_NARRATIVE_DISPATCH.get(chapter_id)
    if handler:
        return handler(registry_data)
    
    # Unknown chapter - minimal response
    return {
        "title": f"Chapter {chapter_id}",
        "intro": INSUFFICIENT_DATA,
        "main_analysis": f"<p>{INSUFFICIENT_DATA}</p>",
        "interpretation": "",
        "conclusion": INSUFFICIENT_DATA,
        "variables": {},
        "_provenance": {
            "provider": "Registry Template",
            "model": "Presentation-Only",
            "confidence": "none"
        }
    }
