"""
Chapter Variable Strategy

This module defines which variables should be displayed on which chapters,
preventing repetition and ensuring each chapter shows only relevant data.

RULE: Core property data (address, price, area, etc.) appears ONLY in Chapter 0.
      All other chapters show ONLY their domain-specific variables with AI interpretation.
"""

from typing import Dict, List, Set, Any

# Chapter 0: Executive Summary - Shows ALL core property data
CHAPTER_0_VARIABLES = {
    'address', 'postal_code', 'city',
    'asking_price_eur', 'price_per_m2', 'woz_value',
    'living_area_m2', 'plot_area_m2', 'volume_m3',
    'property_type', 'build_year',
    'num_rooms', 'num_bedrooms', 'num_bathrooms',
    'energy_label', 'insulation', 'heating',
    'ownership', 'service_costs', 'listed_since', 'acceptance',
    'garden', 'garage', 'parking'
}

# Chapter 1: General Features - NO CORE DATA, only derived insights
CHAPTER_1_VARIABLES = {
    'type_woning_classificatie',  # Not just "type" but classification
    'bebouwingsratio',  # Derived: area/plot ratio
    'inhoud_indicatie',  # Derived: volume estimation
    'kamerverdeling',  # Derived: room distribution analysis
    'bouwperiode_karakteristiek'  # Derived: architectural period characteristics
}

# Chapter 2: Preference Match - Marcel & Petra specific
CHAPTER_2_VARIABLES = {
    'marcel_match_percentage',
    'petra_match_percentage',
    'combined_match_score',
    'marcel_tech_hits',  # Count of tech preferences matched
    'petra_sfeer_hits',  # Count of atmosphere preferences matched
    'critical_misses',  # Important preferences not met
    'bezichtiging_focus'  # What to check during viewing
}

# Chapter 3: Technical State - Building condition
CHAPTER_3_VARIABLES = {
    'technische_staat_score',
    'dak_gevel_conditie',
    'fundering_risico',
    'leidingwerk_leeftijd',
    'asbest_risico',
    'onderhoudsbuffer_advies'  # Recommended maintenance budget
}

# Chapter 4: Energy & Sustainability - Energy specific
CHAPTER_4_VARIABLES = {
    'energie_index_score',
    'isolatie_niveau',
    'verwarming_type',
    'zonnepanelen_aanwezig',
    'verduurzaming_potentie',
    'energiekosten_schatting',
    'subsidie_mogelijkheden'
}

# Chapter 5: Layout Analysis - Space usage
CHAPTER_5_VARIABLES = {
    'indeling_type',
    'ruimte_efficientie',
    'verbouwingsmogelijkheden',
    'lichtinval_score',
    'verkeersruimte_ratio',
    'flexibiliteit_score'
}

# Chapter 6: Maintenance & Finish - Quality level
CHAPTER_6_VARIABLES = {
    'afwerking_niveau',
    'keuken_leeftijd',
    'badkamer_leeftijd',
    'vloeren_conditie',
    'schilderwerk_staat',
    'modernisering_kosten'
}

# Chapter 7: Garden & Outdoor - Outdoor spaces
CHAPTER_7_VARIABLES = {
    'tuin_grootte',
    'tuin_ligging',  # North/South/East/West
    'privacy_score',
    'onderhoud_intensiteit',
    'uitbreidingsmogelijkheden',
    'buitenberging'
}

# Chapter 8: Parking & Accessibility - Mobility
CHAPTER_8_VARIABLES = {
    'parkeer_situatie',
    'ov_afstand',
    'snelweg_afstand',
    'bewonersvergunning',
    'fiets_faciliteiten',
    'laadpaal_aanwezig'
}

# Chapter 9: Legal Aspects - Juridical
CHAPTER_9_VARIABLES = {
    'eigendom_type',
    'erfpacht_details',
    'vve_kosten',
    'kwalitatieve_verplichting',
    'erfdienstbaarheden',
    'bestemmingsplan'
}

# Chapter 10: Financial Analysis - Money matters
CHAPTER_10_VARIABLES = {
    'aankoopkosten_totaal',
    'maandlasten_schatting',
    'energiekosten_maand',
    'onderhoudskosten_jaar',
    'tco_10_jaar',  # Total Cost of Ownership
    'roi_verhuur'
}

# Chapter 11: Market Position - Market analysis
CHAPTER_11_VARIABLES = {
    'markt_positie',
    'dagen_op_funda',
    'prijswijzigingen',
    'vergelijkbare_objecten',
    'vraag_aanbod_ratio',
    'verkoopkans_score'
}

# Chapter 12: Advice & Conclusion - Final verdict
CHAPTER_12_VARIABLES = {
    'koopadvies',
    'openingsbod_advies',
    'doelbod_advies',
    'maximaal_bod_advies',
    'voorbehouden_advies',
    'onderhandelings_strategie'
}

# Chapter 13: Media Library - No variables, just gallery
CHAPTER_13_VARIABLES = set()


def get_chapter_variables(chapter_id: int) -> Set[str]:
    """
    Get the set of variables that should be displayed for a specific chapter.
    
    Args:
        chapter_id: Chapter number (0-13)
        
    Returns:
        Set of variable names that are relevant for this chapter
    """
    chapter_map = {
        0: CHAPTER_0_VARIABLES,
        1: CHAPTER_1_VARIABLES,
        2: CHAPTER_2_VARIABLES,
        3: CHAPTER_3_VARIABLES,
        4: CHAPTER_4_VARIABLES,
        5: CHAPTER_5_VARIABLES,
        6: CHAPTER_6_VARIABLES,
        7: CHAPTER_7_VARIABLES,
        8: CHAPTER_8_VARIABLES,
        9: CHAPTER_9_VARIABLES,
        10: CHAPTER_10_VARIABLES,
        11: CHAPTER_11_VARIABLES,
        12: CHAPTER_12_VARIABLES,
        13: CHAPTER_13_VARIABLES,
    }
    
    return chapter_map.get(chapter_id, set())


def should_show_core_data(chapter_id: int) -> bool:
    """
    Determine if core property data should be shown on this chapter.
    
    RULE: Only Chapter 0 shows core data.
    
    Args:
        chapter_id: Chapter number
        
    Returns:
        True if core data should be displayed, False otherwise
    """
    return chapter_id == 0


def filter_variables_for_chapter(chapter_id: int, all_variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter variables to show only those relevant for the current chapter.
    
    This prevents the same boring info from appearing on every page.
    
    Args:
        chapter_id: Current chapter number
        all_variables: All available variables
        
    Returns:
        Filtered dict containing only chapter-relevant variables
    """
    allowed_vars = get_chapter_variables(chapter_id)
    
    if not allowed_vars:
        return {}
    
    return {
        key: value
        for key, value in all_variables.items()
        if key in allowed_vars
    }


def enrich_variable_with_preferences(
    variable_name: str,
    variable_value: Any,
    property_core: 'PropertyCoreData'
) -> Dict[str, Any]:
    """
    Enrich a variable with Marcel & Petra preference matching information.
    
    This adds AI interpretation showing how the variable relates to their preferences.
    
    Args:
        variable_name: Name of the variable
        variable_value: Current value
        property_core: PropertyCoreData instance with preference match info
        
    Returns:
        Enriched variable dict with preference indicators
    """
    from typing import Any
    
    pref_indicator = property_core.get_preference_indicator(variable_name)
    
    # Base structure
    enriched = {
        'value': variable_value,
        'status': 'fact',  # Will be overridden by AI if inferred
        'reasoning': '',
        'preference_match': pref_indicator
    }
    
    return enriched


# AI Prompt templates for each chapter to ensure relevant variable extraction
CHAPTER_AI_PROMPTS = {
    0: """
    Extract and interpret ALL core property data for the Executive Summary.
    Focus on: Identity, Pricing, Physical specs, Energy, Legal basics.
    Provide Marcel & Petra match scores and interpretation.
    """,
    
    1: """
    Analyze ONLY derived general features. Do NOT repeat core data.
    Focus on: Building classification, space efficiency, architectural characteristics.
    Interpret how the building period and type affect livability.
    """,
    
    2: """
    Deep-dive into Marcel & Petra preference matching.
    For EACH preference, explicitly state: matched/partial/missing/unknown.
    Provide specific recommendations for the viewing.
    Marcel focuses on: Tech infrastructure, ROI, future-proofing.
    Petra focuses on: Atmosphere, light, flow, finish quality.
    """,
    
    3: """
    Analyze ONLY technical building state. Do NOT repeat energy label.
    Focus on: Roof, foundation, plumbing age, asbestos risk, structural issues.
    Provide maintenance budget recommendation.
    """,
    
    4: """
    Analyze ONLY energy and sustainability aspects.
    Focus on: Insulation level, heating type, solar potential, renovation costs.
    Calculate estimated monthly energy costs.
    """,
    
    5: """
    Analyze ONLY layout and space usage.
    Focus on: Room distribution, light penetration, renovation possibilities.
    Do NOT repeat room counts - interpret the QUALITY of the layout.
    """,
    
    6: """
    Analyze ONLY maintenance and finish quality.
    Focus on: Kitchen age, bathroom age, flooring, paintwork.
    Estimate modernization costs if needed.
    """,
    
    7: """
    Analyze ONLY garden and outdoor spaces.
    Focus on: Garden size, orientation, privacy, maintenance intensity.
    Do NOT repeat plot area - interpret the USABILITY.
    """,
    
    8: """
    Analyze ONLY parking and accessibility.
    Focus on: Parking situation, public transport, highway access.
    Provide mobility score.
    """,
    
    9: """
    Analyze ONLY legal aspects.
    Focus on: Ownership type, ground lease, VvE costs, easements.
    Highlight any legal risks or obligations.
    """,
    
    10: """
    Analyze ONLY financial aspects and TCO.
    Focus on: Purchase costs, monthly costs, energy costs, maintenance, 10-year TCO.
    Provide rental ROI if applicable.
    """,
    
    11: """
    Analyze ONLY market position.
    Focus on: Days on market, price changes, comparable properties, market sentiment.
    Provide negotiation leverage assessment.
    """,
    
    12: """
    Provide ONLY final advice and bidding strategy.
    Focus on: Buy recommendation, opening bid, target bid, max bid, contingencies.
    Synthesize all previous chapters into actionable strategy.
    """,
}


def get_chapter_ai_prompt(chapter_id: int) -> str:
    """Get the AI prompt template for a specific chapter"""
    return CHAPTER_AI_PROMPTS.get(chapter_id, "Analyze this chapter's specific domain.")
