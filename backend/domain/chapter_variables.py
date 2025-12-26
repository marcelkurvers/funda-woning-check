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
    Act as a high-end Real Estate Strategist giving an Executive Summary. 
    You MUST provide a narrative that balances Marcel's strategic tech/ROI needs with Petra's atmospheric lifestyle needs.
    Compare the property's core specs (price, area, label) against their combined long-term goals.
    Extract Marcel & Petra match percentages and justify them.
    """,
    
    1: """
    PAGINA 1: ALGEMENE WONINGKENMERKEN (MAXIMALISATIE)
    
    ROL & HOUDING
    Je bent een senior vastgoedanalist en beslisadviseur.
    Je schrijft niet voor een brochure, niet voor marketing en niet voor een databank.
    Je schrijft voor Marcel & Petra, die willen begrijpen:
    "Wat voor type woning is dit nu écht, en wat betekent dat fundamenteel voor ons?"
    
    Je doel is maximale besliswaarde, niet volledigheid om de volledigheid.
    
    CONTEXT
    Dit hoofdstuk is de fundamentele basis voor alle volgende hoofdstukken.
    Alles wat hier wordt vastgesteld, werkt door in: onderhoud, beleving, 
    marktpositie, risico, en toekomstbestendigheid.
    
    ══════════════════════════════════════════════════════════════════════
    🅐 PLANE A — VISUELE ANALYSE (VERPLICHT)
    ══════════════════════════════════════════════════════════════════════
    Doel: Visueel laten zien wat voor schaal en type woning dit is.
    
    VERPLICHT:
    • Genereer minstens 2 visuele inzichten, afgeleid van de feitelijke data
    • Gebruik uitsluitend data uit Plane C (geen nieuwe feiten)
    
    Verplichte visual-types (kies minimaal 2):
    - Relatieve schaal (woonoppervlak t.o.v. gemiddelde vrijstaande woning)
    - Verhouding woonoppervlak ↔ perceel (privacy / ruimtelijkheid)  
    - Indicatieve "ruimtelijke klasse" (compact / royaal / uitzonderlijk)
    
    Per visual: voeg één interpretatieve zin toe die begint met:
    "Deze visual laat zien dat …"
    
    ❌ "Geen visuele data beschikbaar" is VERBODEN in dit hoofdstuk.
    
    ══════════════════════════════════════════════════════════════════════
    🅑 PLANE B — NARRATIEVE DUIDING (MIN. 300 WOORDEN)
    ══════════════════════════════════════════════════════════════════════
    Dit is het hart van pagina 1.
    
    WAT JE HIER DOET:
    ✗ NIET opsommen
    ✗ NIET herhalen wat KPI's zijn
    ✓ WEL duiden, kaderen en positioneren
    
    BEANTWOORD EXPLICIET:
    1. Wat voor type woning is dit?
       Niet juridisch, maar inhoudelijk (gezinsvilla, semi-landgoed, representatieve woonvilla)
    2. Wat zegt de schaal, het perceel en de indeling over het karakter?
    3. Wat betekent dit object fundamenteel vóór smaak, prijs of marktstrategie?
    4. Welke aannames mogen we hier al maken — en welke juist nog niet?
    
    SCHRIJFSTIJL:
    - Beslissingsgericht
    - Concreet
    - Geen generieke vastgoedtaal
    - Alsof Marcel & Petra dit lezen vóór hun eerste bezichtiging
    
    ══════════════════════════════════════════════════════════════════════
    🅒 PLANE C — FEITELIJKE DATA (ANCHOR)
    ══════════════════════════════════════════════════════════════════════
    VERPLICHT TONEN (geen opsomming, wel interpretatie):
    - Vraagprijs (met relatieve indicatie: hoog/gemiddeld/laag voor dit type)
    - Woonoppervlak (met schaalindicatie)
    - Perceeloppervlak (indien van toepassing)
    - Aantal kamers / slaapkamers
    - Bouwjaar (met periode-karakteristiek)
    - Energielabel (of het ontbreken ervan expliciet benoemen)
    
    Per KPI moet duidelijk zijn:
    - Is dit hoog / gemiddeld / laag?
    - Hoe zeker is deze waarde?
    
    VERPLICHTE EXTRA SECTIE:
    "Wat we hier nog niet weten (en waarom dat ertoe doet)"
    
    ══════════════════════════════════════════════════════════════════════
    🅓 PLANE D — MARCEL & PETRA (VERPLICHT, NIET NEUTRAAL)
    ══════════════════════════════════════════════════════════════════════
    Dit is GEEN scorekaart.
    
    MARCEL (technische, structurele en risico-lens):
    - Wat stelt hem gerust?
    - Wat maakt hem alert?
    - Welke vragen roept dit hoofdstuk bij hem op?
    
    PETRA (belevings-, comfort- en dagelijks-leven-lens):
    - Wat trekt haar aan?
    - Wat voelt nog onduidelijk?
    - Waar zit haar twijfel of nieuwsgierigheid?
    
    VERPLICHT BENOEMEN:
    - Overeenstemming tussen Marcel en Petra
    - Spanning tussen hun perspectieven  
    - Wat dit betekent voor een gezamenlijke volgende stap
    
    ❌ 50/50 neutraal = NIET TOEGESTAAN
    
    ══════════════════════════════════════════════════════════════════════
    FAIL-LOUD REGEL
    ══════════════════════════════════════════════════════════════════════
    Als informatie ontbreekt:
    - Zeg dat EXPLICIET
    - Benoem het effect op de besluitvorming
    - Verstop NIETS
    
    EINDCONTROLE:
    ✓ Begrijpen Marcel & Petra nu wat voor huis dit écht is?
    ✓ Is de basis gelegd voor latere hoofdstukken?
    ✓ Zou een lezer zeggen: "Dit hoofdstuk maakt het verschil"?
    """,
    
    2: """
    Deep-dive into Marcel & Petra preference matching. This is the MOST IMPORTANT chapter.
    Marcel (Profile: Strategic Investor/Tech Focus): Analyze energy systems, fiber connectivity, potential for value increase, and structural durability.
    Petra (Profile: Lifestyle & Atmosphere): Analyze light quality, room flow ('gezelligheid'), historical charm or modern sleekness, and garden-to-indoor transition.
    For EACH preference in their profile, explicitly state: matched/partial/missing/unknown with a narrative explanation of WHY.
    Provide specific 'Viewing Missions' (what should they look for during the second visit?).
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
