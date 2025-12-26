# filename: backend/pipeline/four_plane_max_contract.py
"""
4-PLANE MAXIMALIZATION CONTRACT

This module defines the SINGLE SOURCE OF TRUTH for per-chapter maximalization requirements.
Every chapter must attempt to produce the defined minimum component counts.

CONTRACT PRINCIPLES:
1. If data is available in registry → MUST be extracted
2. If data is not available → MUST be documented in diagnostics
3. No silent emptiness — every gap must be explained
4. Fail-closed: missing required componentsdiagnostics, not silent failure

VALIDATION FLOW:
1. Extractor attempts to extract based on this contract
2. Backbone receives extracted data
3. Diagnostics report what was found vs what was expected
"""

from typing import Dict, List, Any, Optional, NamedTuple
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# PLANE A — VISUAL INTELLIGENCE CONTRACT
# =============================================================================

class ChartType(Enum):
    """Allowed chart types for Plane A."""
    BAR = "bar"
    GAUGE = "gauge"
    RADAR = "radar"
    COMPARISON = "comparison"
    DISTRIBUTION = "distribution"
    TREND = "trend"
    SCORE = "score"


@dataclass
class ChartSpec:
    """Specification for a chart that should be attempted."""
    chart_id: str
    chart_type: ChartType
    title: str
    required_registry_keys: List[str]
    description: str
    fallback_if_missing: str  # What to say in diagnostics if can't generate


# Chapter-specific chart catalogs
PLANE_A_CHART_CATALOG: Dict[int, List[ChartSpec]] = {
    1: [
        ChartSpec(
            chart_id="ch1_area_scale",
            chart_type=ChartType.COMPARISON,
            title="Woonoppervlak vs Gemiddelde",
            required_registry_keys=["living_area_m2"],
            description="Relatieve schaal t.o.v. gemiddelde vrijstaande woning (125m²)",
            fallback_if_missing="Woonoppervlak onbekend - schaal niet bepaalbaar"
        ),
        ChartSpec(
            chart_id="ch1_plot_ratio",
            chart_type=ChartType.BAR,
            title="Bebouwingsratio",
            required_registry_keys=["living_area_m2", "plot_area_m2"],
            description="Verhouding woonoppervlak / perceel",
            fallback_if_missing="Perceel of woonoppervlak onbekend"
        ),
        ChartSpec(
            chart_id="ch1_rooms_distribution",
            chart_type=ChartType.BAR,
            title="Kamerverdeling",
            required_registry_keys=["rooms", "bedrooms"],
            description="Verdeling kamers en slaapkamers",
            fallback_if_missing="Kamerindeling onbekend"
        ),
        ChartSpec(
            chart_id="ch1_build_period",
            chart_type=ChartType.GAUGE,
            title="Bouwperiode Score",
            required_registry_keys=["build_year"],
            description="Bouwjaar in historische context",
            fallback_if_missing="Bouwjaar onbekend"
        ),
    ],
    2: [
        ChartSpec(
            chart_id="ch2_match_radar",
            chart_type=ChartType.RADAR,
            title="Marcel & Petra Match Profiel",
            required_registry_keys=["marcel_match_score", "petra_match_score"],
            description="Match scores per dimensie",
            fallback_if_missing="Match scores niet berekend"
        ),
        ChartSpec(
            chart_id="ch2_score_comparison",
            chart_type=ChartType.COMPARISON,
            title="Score Vergelijking",
            required_registry_keys=["marcel_match_score", "petra_match_score", "total_match_score"],
            description="Marcel vs Petra vs Totaal",
            fallback_if_missing="Scores ontbreken"
        ),
    ],
    3: [
        # CHAPTER 3: BOUWKUNDIGE STAAT — MAXIMALIZED CHART CATALOG
        # These charts visualize structural and technical condition
        ChartSpec(
            chart_id="ch3_condition_breakdown",
            chart_type=ChartType.RADAR,
            title="Conditie Overzicht",
            required_registry_keys=["build_year"],
            description="Multi-dimensionele conditiescore: fundering, dak, gevel, installaties, interieur structuur",
            fallback_if_missing="Onvoldoende bouwgegevens voor conditieprofiel"
        ),
        ChartSpec(
            chart_id="ch3_age_risk",
            chart_type=ChartType.GAUGE,
            title="Leeftijds-Risico Score",
            required_registry_keys=["build_year"],
            description="Risicoprofiel o.b.v. bouwjaar en verwachte onderhoudscurve",
            fallback_if_missing="Bouwjaar onbekend - risicoprofiel niet bepaalbaar"
        ),
        ChartSpec(
            chart_id="ch3_maintenance_load",
            chart_type=ChartType.GAUGE,
            title="Onderhoudsbelasting",
            required_registry_keys=["build_year"],
            description="Laag/Gemiddeld/Hoog o.b.v. bouwjaar en constructietype",
            fallback_if_missing="Onvoldoende data voor onderhoudsindicator"
        ),
        ChartSpec(
            chart_id="ch3_longevity_projection",
            chart_type=ChartType.BAR,
            title="Levensduur Componenten",
            required_registry_keys=["build_year"],
            description="Geschatte resterende levensduur per bouwcomponent",
            fallback_if_missing="Bouwjaar nodig voor levensduurprojectie"
        ),
        ChartSpec(
            chart_id="ch3_renovation_urgency",
            chart_type=ChartType.SCORE,
            title="Renovatie Urgentie",
            required_registry_keys=["build_year"],
            description="Urgentiescore voor grootschalige renovatie",
            fallback_if_missing="Renovatie-urgentie niet te bepalen"
        ),
    ],
    4: [
        # CHAPTER 4: ENERGIE & DUURZAAMHEID — MAXIMALIZED CHART CATALOG
        # Energieprestatie-overzicht (RADAR)
        ChartSpec(
            chart_id="ch4_energy_performance",
            chart_type=ChartType.RADAR,
            title="Energieprestatie Overzicht",
            required_registry_keys=["energy_label"],
            description="Multi-dimensioneel: label, isolatie, installaties, verbruik",
            fallback_if_missing="Energielabel onbekend - overzicht niet mogelijk"
        ),
        # Warmteverliesprofiel (BAR)
        ChartSpec(
            chart_id="ch4_heat_loss",
            chart_type=ChartType.BAR,
            title="Warmteverliesprofiel",
            required_registry_keys=["build_year"],
            description="Warmteverlies per component: dak, gevel, vloer, glas",
            fallback_if_missing="Bouwjaar nodig voor warmteverliesschatting"
        ),
        # Installatie-efficiëntie (GAUGE)
        ChartSpec(
            chart_id="ch4_installation_efficiency",
            chart_type=ChartType.GAUGE,
            title="Installatie-efficiëntie",
            required_registry_keys=["energy_label"],
            description="CV/warmtepomp/hybride efficiëntiescore",
            fallback_if_missing="Installatietype onbekend"
        ),
        # Verduurzamingspotentieel (SCORE)
        ChartSpec(
            chart_id="ch4_sustainability_potential",
            chart_type=ChartType.SCORE,
            title="Verduurzamingspotentieel",
            required_registry_keys=["energy_label", "build_year"],
            description="Huidige staat vs potentieel na verduurzaming",
            fallback_if_missing="Onvoldoende data voor potentieelberekening"
        ),
        # Energie-onzekerheid (INDICATOR)
        ChartSpec(
            chart_id="ch4_energy_uncertainty",
            chart_type=ChartType.GAUGE,
            title="Data-zekerheid Energie",
            required_registry_keys=["energy_label"],
            description="Datakwaliteit, aannames, ontbrekende info",
            fallback_if_missing="Geen energiedata beschikbaar"
        ),
        # Geschatte jaarkosten (BAR)
        ChartSpec(
            chart_id="ch4_annual_cost",
            chart_type=ChartType.BAR,
            title="Geschatte Energiekosten",
            required_registry_keys=["energy_label", "living_area_m2"],
            description="Jaarlijkse energiekosten indicatie o.b.v. label en oppervlak",
            fallback_if_missing="Label/oppervlak nodig voor kostenberekening"
        ),
    ],
    5: [
        # CHAPTER 5: INDELING, RUIMTELIJKHEID & DAGELIJKS GEBRUIK — MAXIMALIZED CHART CATALOG
        # Ruimteverdeling (BAR / STACKED BAR)
        ChartSpec(
            chart_id="ch5_space_distribution",
            chart_type=ChartType.BAR,
            title="Ruimteverdeling",
            required_registry_keys=["living_area_m2", "rooms"],
            description="Woonoppervlak vs functies: wonen, slapen, werken, opslag",
            fallback_if_missing="Ruimteverdeling niet te bepalen"
        ),
        # Functionele Dichtheid (SCORE / GAUGE)
        ChartSpec(
            chart_id="ch5_functional_density",
            chart_type=ChartType.GAUGE,
            title="Functionele Dichtheid",
            required_registry_keys=["living_area_m2", "rooms"],
            description="m² per functie / per persoon",
            fallback_if_missing="Dichtheid niet te berekenen"
        ),
        # Circulatie & Flow (RADAR)
        ChartSpec(
            chart_id="ch5_circulation_flow",
            chart_type=ChartType.RADAR,
            title="Circulatie & Flow",
            required_registry_keys=["rooms", "living_area_m2"],
            description="Logische routing, doorloopbaarheid, overlap zones",
            fallback_if_missing="Flow niet in te schatten zonder plattegrond"
        ),
        # Flexibiliteitsscore (GAUGE)
        ChartSpec(
            chart_id="ch5_flexibility",
            chart_type=ChartType.GAUGE,
            title="Flexibiliteitsscore",
            required_registry_keys=["living_area_m2", "build_year"],
            description="Mogelijkheid tot herindeling / meegroeiend gebruik",
            fallback_if_missing="Flexibiliteit niet te bepalen"
        ),
        # Daglicht & Openheid (BAR)
        ChartSpec(
            chart_id="ch5_daylight_openness",
            chart_type=ChartType.BAR,
            title="Daglicht & Openheid",
            required_registry_keys=["living_area_m2", "rooms"],
            description="Indicatief o.b.v. ruimteverdeling & geveldata",
            fallback_if_missing="Daglichtindicatie niet beschikbaar"
        ),
        # Opslagdruk (SCORE)
        ChartSpec(
            chart_id="ch5_storage_pressure",
            chart_type=ChartType.SCORE,
            title="Opslagdruk",
            required_registry_keys=["living_area_m2"],
            description="Berging vs woonfunctie balans",
            fallback_if_missing="Opslagcapaciteit onbekend"
        ),
    ],
    6: [
        # CHAPTER 6: AFWERKING & KWALITEIT — MAXIMALIZED CHART CATALOG
        # Kwaliteitsscore (GAUGE)
        ChartSpec(
            chart_id="ch6_quality_score",
            chart_type=ChartType.GAUGE,
            title="Overall Kwaliteitsscore",
            required_registry_keys=["build_year"],
            description="Totaalscore afwerking o.b.v. bouwjaar en context",
            fallback_if_missing="Kwaliteit niet in te schatten"
        ),
        # Afwerkingsniveau per ruimte (RADAR)
        ChartSpec(
            chart_id="ch6_finish_level",
            chart_type=ChartType.RADAR,
            title="Afwerkingsniveau",
            required_registry_keys=["build_year"],
            description="Keuken, badkamer, woonruimtes, slaapkamers, buiten",
            fallback_if_missing="Afwerking niet te beoordelen"
        ),
        # Materiaalstaat (BAR)
        ChartSpec(
            chart_id="ch6_material_condition",
            chart_type=ChartType.BAR,
            title="Materiaalstaat",
            required_registry_keys=["build_year"],
            description="Conditie per materiaaltype: hout, steen, metaal, glas",
            fallback_if_missing="Materiaalstaat onbekend"
        ),
        # Renovatiebehoefte (SCORE)
        ChartSpec(
            chart_id="ch6_renovation_need",
            chart_type=ChartType.SCORE,
            title="Renovatiebehoefte",
            required_registry_keys=["build_year"],
            description="Urgentie van verfraaiing of vernieuwing",
            fallback_if_missing="Renovatiebehoefte niet te bepalen"
        ),
        # Onderhoudsintensiteit (GAUGE)
        ChartSpec(
            chart_id="ch6_maintenance_intensity",
            chart_type=ChartType.GAUGE,
            title="Onderhoudsintensiteit",
            required_registry_keys=["build_year", "property_type"],
            description="Verwachte onderhoudsinspanning voor kwaliteitsbehoud",
            fallback_if_missing="Onderhoudsbehoefte niet in te schatten"
        ),
        # Modernisatiegraad (GAUGE)
        ChartSpec(
            chart_id="ch6_modernization",
            chart_type=ChartType.GAUGE,
            title="Modernisatiegraad",
            required_registry_keys=["build_year"],
            description="Mate van actuele afwerking t.o.v. hedendaagse standaard",
            fallback_if_missing="Modernisering niet te beoordelen"
        ),
    ],
    7: [
        # CHAPTER 7: BUITENRUIMTE, TUIN & OMGEVINGSGEBRUIK — MAXIMALIZED CHART CATALOG
        # Tuinoppervlak & perceelverhouding (BAR)
        ChartSpec(
            chart_id="ch7_plot_ratio",
            chart_type=ChartType.BAR,
            title="Perceel & Tuinverhouding",
            required_registry_keys=["plot_area_m2", "living_area_m2"],
            description="Verhouding tuin/perceel vs woonoppervlak",
            fallback_if_missing="Perceelgegevens onbekend"
        ),
        # Buitenruimte-bruikbaarheid (RADAR)
        ChartSpec(
            chart_id="ch7_usability",
            chart_type=ChartType.RADAR,
            title="Buitenruimte Bruikbaarheid",
            required_registry_keys=["plot_area_m2"],
            description="Actief vs passief gebruik: terras, gazon, moestuin, spelen",
            fallback_if_missing="Tuindetails onbekend"
        ),
        # Onderhoudsdruk buitenruimte (GAUGE)
        ChartSpec(
            chart_id="ch7_maintenance",
            chart_type=ChartType.GAUGE,
            title="Onderhoudsdruk Buiten",
            required_registry_keys=["plot_area_m2"],
            description="Verwachte onderhoudsinspanning voor tuin en buitenruimte",
            fallback_if_missing="Onderhoudsinschatting niet mogelijk"
        ),
        # Privacy & beschutting indicatie (GAUGE)
        ChartSpec(
            chart_id="ch7_privacy",
            chart_type=ChartType.GAUGE,
            title="Privacy & Beschutting",
            required_registry_keys=["property_type"],
            description="Indicatie privacy o.b.v. woningtype en ligging",
            fallback_if_missing="Privacy niet in te schatten"
        ),
        # Zon-/lichtpotentieel indicatie (SCORE)
        ChartSpec(
            chart_id="ch7_sun_potential",
            chart_type=ChartType.SCORE,
            title="Zonpotentieel",
            required_registry_keys=["plot_area_m2"],
            description="Zon- en lichtpotentieel o.b.v. oriëntatie (indien bekend)",
            fallback_if_missing="Oriëntatie onbekend"
        ),
        # Data-zekerheid buitenruimte (GAUGE)
        ChartSpec(
            chart_id="ch7_data_certainty",
            chart_type=ChartType.GAUGE,
            title="Data-zekerheid Buiten",
            required_registry_keys=["plot_area_m2"],
            description="Betrouwbaarheid beschikbare tuindata",
            fallback_if_missing="Geen buitenruimtedata beschikbaar"
        ),
    ],
    8: [
        # CHAPTER 8: LOCATIE & BEREIKBAARHEID — MAXIMALIZED CHART CATALOG
        # Bereikbaarheidsscore (GAUGE)
        ChartSpec(
            chart_id="ch8_accessibility",
            chart_type=ChartType.GAUGE,
            title="Bereikbaarheidsscore",
            required_registry_keys=["address"],
            description="Algemene mobiliteits- en toegankelijkheidsscore",
            fallback_if_missing="Locatiegegevens ontbreken"
        ),
        # Voorzieningen Radar (RADAR)
        ChartSpec(
            chart_id="ch8_amenities",
            chart_type=ChartType.RADAR,
            title="Voorzieningen Nabijheid",
            required_registry_keys=["address"],
            description="Scholen, winkels, zorg, sport, horeca in de buurt",
            fallback_if_missing="Voorzieningendata onbekend"
        ),
        # OV-Toegang (SCORE)
        ChartSpec(
            chart_id="ch8_public_transport",
            chart_type=ChartType.SCORE,
            title="OV-Toegankelijkheid",
            required_registry_keys=["address"],
            description="Afstand tot stations, haltes, frequentie",
            fallback_if_missing="OV-gegevens onbekend"
        ),
        # Auto-Bereikbaarheid (BAR)
        ChartSpec(
            chart_id="ch8_car_access",
            chart_type=ChartType.BAR,
            title="Auto-Bereikbaarheid",
            required_registry_keys=["address"],
            description="Snelweg, parkeren, drukte",
            fallback_if_missing="Wegdata onbekend"
        ),
        # Buurtprofiel (RADAR)
        ChartSpec(
            chart_id="ch8_neighborhood",
            chart_type=ChartType.RADAR,
            title="Buurtprofiel",
            required_registry_keys=["address"],
            description="Veiligheid, sfeer, demografie indicaties",
            fallback_if_missing="Buurtdata onbekend"
        ),
        # Data-zekerheid Locatie (GAUGE)
        ChartSpec(
            chart_id="ch8_data_certainty",
            chart_type=ChartType.GAUGE,
            title="Data-zekerheid Locatie",
            required_registry_keys=["address"],
            description="Betrouwbaarheid beschikbare locatiedata",
            fallback_if_missing="Locatiedata niet verifieerbaar"
        ),
    ],
    9: [
        # CHAPTER 9: JURIDISCH & EIGENDOM — MAXIMALIZED CHART CATALOG
        # Eigendomstype (BAR)
        ChartSpec(
            chart_id="ch9_ownership_type",
            chart_type=ChartType.BAR,
            title="Eigendomstype",
            required_registry_keys=[],
            description="Volledig eigendom, erfpacht, of appartementsrecht",
            fallback_if_missing="Eigendomstype onbekend"
        ),
        # VvE-Risico (GAUGE)
        ChartSpec(
            chart_id="ch9_vve_risk",
            chart_type=ChartType.GAUGE,
            title="VvE-Risico Indicatie",
            required_registry_keys=["property_type"],
            description="Risico-indicatie voor VvE-verplichtingen",
            fallback_if_missing="VvE-status onbekend"
        ),
        # Erfpacht Status (SCORE)
        ChartSpec(
            chart_id="ch9_leasehold",
            chart_type=ChartType.SCORE,
            title="Erfpacht Status",
            required_registry_keys=[],
            description="Erfpacht looptijd, canon, afkoopstatus",
            fallback_if_missing="Erfpachtgegevens onbekend"
        ),
        # Juridische Zekerheid (GAUGE)
        ChartSpec(
            chart_id="ch9_legal_certainty",
            chart_type=ChartType.GAUGE,
            title="Juridische Zekerheid",
            required_registry_keys=[],
            description="Mate van beschikbare juridische documentatie",
            fallback_if_missing="Juridische status onduidelijk"
        ),
        # Documentatie Compleetheid (RADAR)
        ChartSpec(
            chart_id="ch9_documentation",
            chart_type=ChartType.RADAR,
            title="Documentatie Status",
            required_registry_keys=[],
            description="Kadaster, splitsingsakte, VvE-notulen, vergunningen",
            fallback_if_missing="Documentatie niet geverifieerd"
        ),
        # Verplichtingen Overzicht (BAR)
        ChartSpec(
            chart_id="ch9_obligations",
            chart_type=ChartType.BAR,
            title="Verplichtingen Overzicht",
            required_registry_keys=[],
            description="VvE-bijdrage, erfpachtcanon, overige lasten",
            fallback_if_missing="Verplichtingen onbekend"
        ),
    ],
    10: [
        # CHAPTER 10: FINANCIËLE ANALYSE — MAXIMALIZED CHART CATALOG
        # Prijs per m² (COMPARISON)
        ChartSpec(
            chart_id="ch10_price_per_m2",
            chart_type=ChartType.COMPARISON,
            title="Prijs per m² vs Gemiddeld",
            required_registry_keys=["asking_price_eur", "living_area_m2"],
            description="Prijs/m² vergelijking met regionaal gemiddelde",
            fallback_if_missing="Prijs of oppervlak onbekend"
        ),
        # Maandlasten Breakdown (BAR)
        ChartSpec(
            chart_id="ch10_monthly_costs",
            chart_type=ChartType.BAR,
            title="Maandlasten Breakdown",
            required_registry_keys=["asking_price_eur"],
            description="Hypotheek + energie + onderhoud + VvE",
            fallback_if_missing="Prijs onbekend"
        ),
        # WOZ vs Vraagprijs (BAR)
        ChartSpec(
            chart_id="ch10_woz_comparison",
            chart_type=ChartType.BAR,
            title="WOZ vs Vraagprijs",
            required_registry_keys=["asking_price_eur", "woz_value"],
            description="Vergelijking WOZ-waarde met vraagprijs",
            fallback_if_missing="WOZ of vraagprijs onbekend"
        ),
        # Financieringsdruk (GAUGE)
        ChartSpec(
            chart_id="ch10_financing_pressure",
            chart_type=ChartType.GAUGE,
            title="Financieringsdruk",
            required_registry_keys=["asking_price_eur"],
            description="Indicatie maandlast t.o.v. inkomen",
            fallback_if_missing="Financieringsdata onbekend"
        ),
        # Kosten Koper (BAR)
        ChartSpec(
            chart_id="ch10_buyer_costs",
            chart_type=ChartType.BAR,
            title="Kosten Koper Overzicht",
            required_registry_keys=["asking_price_eur"],
            description="Overdrachtsbelasting, notaris, taxatie, advies",
            fallback_if_missing="Prijsdata onbekend"
        ),
        # Data-zekerheid Financieel (GAUGE)
        ChartSpec(
            chart_id="ch10_data_certainty",
            chart_type=ChartType.GAUGE,
            title="Data-zekerheid Financieel",
            required_registry_keys=["asking_price_eur"],
            description="Betrouwbaarheid beschikbare financiële data",
            fallback_if_missing="Financiële data onvolledig"
        ),
    ],
    11: [
        # CHAPTER 11: MARKTPOSITIE & ONDERHANDELINGSRUIMTE — MAXIMALIZED CHART CATALOG
        # Marktpositie Score (GAUGE)
        ChartSpec(
            chart_id="ch11_market_position",
            chart_type=ChartType.GAUGE,
            title="Marktpositie Score",
            required_registry_keys=["asking_price_eur", "living_area_m2"],
            description="Relatieve marktwaarde in de regio",
            fallback_if_missing="Marktdata onvoldoende"
        ),
        # Onderhandelingsruimte (BAR)
        ChartSpec(
            chart_id="ch11_negotiation_range",
            chart_type=ChartType.BAR,
            title="Onderhandelingsruimte",
            required_registry_keys=["asking_price_eur"],
            description="Indicatie biedingsruimte onder vraagprijs",
            fallback_if_missing="Vraagprijs onbekend"
        ),
        # Marktdynamiek (RADAR)
        ChartSpec(
            chart_id="ch11_market_dynamics",
            chart_type=ChartType.RADAR,
            title="Marktdynamiek",
            required_registry_keys=["asking_price_eur"],
            description="Kopersdominantie, looptijd, concurrentie",
            fallback_if_missing="Marktdata onbekend"
        ),
        # Vergelijkingsprijzen (BAR)
        ChartSpec(
            chart_id="ch11_comparison_prices",
            chart_type=ChartType.BAR,
            title="Vergelijkingsprijzen",
            required_registry_keys=["asking_price_eur", "living_area_m2"],
            description="Prijzen vergelijkbare woningen in de buurt",
            fallback_if_missing="Vergelijkingsdata onbekend"
        ),
        # Timing Indicator (GAUGE)
        ChartSpec(
            chart_id="ch11_timing",
            chart_type=ChartType.GAUGE,
            title="Timing Indicator",
            required_registry_keys=["asking_price_eur"],
            description="Gunstigheid huidig koopmoment",
            fallback_if_missing="Timingdata onbekend"
        ),
        # Data-zekerheid Markt (GAUGE)
        ChartSpec(
            chart_id="ch11_data_certainty",
            chart_type=ChartType.GAUGE,
            title="Data-zekerheid Markt",
            required_registry_keys=["asking_price_eur"],
            description="Betrouwbaarheid beschikbare marktdata",
            fallback_if_missing="Marktdata onvolledig"
        ),
    ],
    12: [
        # CHAPTER 12: EINDCONCLUSIE & AANBEVELING — MAXIMALIZED CHART CATALOG
        # Eindoordeel Score (GAUGE)
        ChartSpec(
            chart_id="ch12_final_score",
            chart_type=ChartType.GAUGE,
            title="Eindoordeel Score",
            required_registry_keys=["total_match_score"],
            description="Totaal advies score voor deze woning",
            fallback_if_missing="Match scores ontbreken"
        ),
        # Biedingsadvies Range (BAR)
        ChartSpec(
            chart_id="ch12_bid_range",
            chart_type=ChartType.BAR,
            title="Biedingsadvies Range",
            required_registry_keys=["asking_price_eur"],
            description="Minimaal → Doelbod → Maximum",
            fallback_if_missing="Vraagprijs onbekend"
        ),
        # Sterkte/Zwakte Overzicht (RADAR)
        ChartSpec(
            chart_id="ch12_swot_summary",
            chart_type=ChartType.RADAR,
            title="Sterkte/Zwakte Overzicht",
            required_registry_keys=[],
            description="Samenvatting pluspunten en aandachtspunten",
            fallback_if_missing="Analyse onvolledig"
        ),
        # Marcel vs Petra Match (BAR)
        ChartSpec(
            chart_id="ch12_persona_match",
            chart_type=ChartType.BAR,
            title="Marcel vs Petra Match",
            required_registry_keys=["total_match_score"],
            description="Vergelijking persona-scores",
            fallback_if_missing="Persona-data onvolledig"
        ),
        # Beslissingsindicator (GAUGE)
        ChartSpec(
            chart_id="ch12_decision_gauge",
            chart_type=ChartType.GAUGE,
            title="Beslissingsindicator",
            required_registry_keys=[],
            description="Gecombineerd advies: aanbevolen / twijfel / afraden",
            fallback_if_missing="Beslisdata onvoldoende"
        ),
        # Actielijst Prioriteit (SCORE)
        ChartSpec(
            chart_id="ch12_action_priority",
            chart_type=ChartType.SCORE,
            title="Actielijst Prioriteit",
            required_registry_keys=[],
            description="Topprioriteit vervolgacties",
            fallback_if_missing="Actielijst niet samengesteld"
        ),
    ],
}


# =============================================================================
# PLANE B — NARRATIVE REASONING CONTRACT
# =============================================================================

@dataclass
class NarrativeRequirement:
    """Requirements for Plane B narrative."""
    min_words: int
    required_sections: List[str]
    required_references: Dict[str, int]  # e.g., {"plane_c_kpi": 2, "plane_d_persona": 1}


PLANE_B_NARRATIVE_CONTRACT: Dict[int, NarrativeRequirement] = {
    0: NarrativeRequirement(
        min_words=500,
        required_sections=[
            "Wat we zeker weten (feitelijk)",
            "Wat dit betekent (interpretatie)",
            "Risico's & onbekenden",
            "Aanbevelingen"
        ],
        required_references={"plane_c_kpi": 3, "plane_d_persona": 2, "plane_a_visual": 1}
    ),
}

# Default for chapters 1-12
DEFAULT_NARRATIVE_CONTRACT = NarrativeRequirement(
    min_words=300,
    required_sections=[
        "Wat we zeker weten (feitelijk)",
        "Wat dit betekent (interpretatie)",
        "Risico's & onbekenden",
        "Acties / Vervolgvragen"
    ],
    required_references={"plane_c_kpi": 2, "plane_d_persona": 1, "plane_a_visual": 1}
)

def get_narrative_contract(chapter_id: int) -> NarrativeRequirement:
    """Get narrative requirements for a chapter."""
    return PLANE_B_NARRATIVE_CONTRACT.get(chapter_id, DEFAULT_NARRATIVE_CONTRACT)


# =============================================================================
# PLANE C — FACTUAL ANCHOR CONTRACT
# =============================================================================

@dataclass
class KPISpec:
    """Specification for a KPI that should be extracted."""
    kpi_id: str
    label: str
    registry_key: str
    unit: Optional[str] = None
    derived_from: Optional[List[str]] = None  # If computed from multiple keys
    format_hint: Optional[str] = None  # e.g., "currency", "percentage"


PLANE_C_KPI_CATALOG: Dict[int, List[KPISpec]] = {
    1: [
        # Core KPIs from registry
        KPISpec("ch1_price", "Vraagprijs", "asking_price_eur", "€", format_hint="currency"),
        KPISpec("ch1_area", "Woonoppervlak", "living_area_m2", "m²"),
        KPISpec("ch1_plot", "Perceeloppervlak", "plot_area_m2", "m²"),
        KPISpec("ch1_rooms", "Kamers", "rooms"),
        KPISpec("ch1_beds", "Slaapkamers", "bedrooms"),
        KPISpec("ch1_year", "Bouwjaar", "build_year"),
        KPISpec("ch1_energy", "Energielabel", "energy_label"),
        KPISpec("ch1_volume", "Inhoud", "volume_m3", "m³"),
        KPISpec("ch1_type", "Woningtype", "property_type"),
        KPISpec("ch1_address", "Adres", "address"),
        # Derived KPIs for maximalization
        KPISpec("ch1_price_m2", "Prijs/m²", None, "€/m²", derived_from=["asking_price_eur", "living_area_m2"]),
        KPISpec("ch1_age", "Leeftijd", None, "jaar", derived_from=["build_year"]),
        KPISpec("ch1_coverage", "Bebouwingsgraad", None, "%", derived_from=["living_area_m2", "plot_area_m2"]),
        KPISpec("ch1_garden_est", "Geschatte Tuin", None, "m²", derived_from=["living_area_m2", "plot_area_m2"]),
        KPISpec("ch1_avg_room", "Gem. Kamergrootte", None, "m²", derived_from=["living_area_m2", "rooms"]),
    ],
    2: [
        KPISpec("ch2_marcel", "Marcel Match", "marcel_match_score", "%"),
        KPISpec("ch2_petra", "Petra Match", "petra_match_score", "%"),
        KPISpec("ch2_total", "Totaal Match", "total_match_score", "%"),
    ],
    3: [
        # CHAPTER 3: BOUWKUNDIGE STAAT — MAXIMALIZED KPI CATALOG
        # Structural age indicators
        KPISpec("ch3_year", "Bouwjaar", "build_year"),
        KPISpec("ch3_age", "Woningouderdom", None, "jaar", derived_from=["build_year"]),
        KPISpec("ch3_construction_period", "Bouwperiode", "build_year"),
        
        # Foundation and structural indicators (derived from build_year)
        KPISpec("ch3_foundation_type", "Funderingstype", "foundation_type"),
        KPISpec("ch3_foundation_risk", "Funderingsrisico", None, None, derived_from=["build_year"]),
        
        # Roof condition indicators
        KPISpec("ch3_roof_age", "Dakleeftijd", None, "jaar", derived_from=["build_year"]),
        KPISpec("ch3_roof_replacement", "Dakrenovatie Indicatie", None, None, derived_from=["build_year"]),
        
        # Installation age indicators
        KPISpec("ch3_cv_age", "CV-ketel Leeftijd", None, "jaar", derived_from=["build_year"]),
        KPISpec("ch3_electrical_risk", "Elektra Risico", None, None, derived_from=["build_year"]),
        
        # Maintenance backlog indicators
        KPISpec("ch3_maintenance_score", "Onderhoudsscore", None, None, derived_from=["build_year"]),
        KPISpec("ch3_renovation_cost_class", "Renovatieklasse", None, None, derived_from=["build_year"]),
        
        # Construction type risk factors
        KPISpec("ch3_building_type", "Woningtype", "property_type"),
        KPISpec("ch3_living_area", "Woonoppervlak", "living_area_m2", "m²"),
        
        # Explicit uncertainty markers (MANDATORY per contract)
        KPISpec("ch3_uncertainty_foundation", "Fundering Status", None),
        KPISpec("ch3_uncertainty_installations", "Installaties Status", None),
        KPISpec("ch3_uncertainty_hidden", "Verborgen Gebreken Risico", None),
    ],
    4: [
        # CHAPTER 4: ENERGIE & DUURZAAMHEID — MAXIMALIZED KPI CATALOG (14+ KPIs required)
        
        # Core energy indicators
        KPISpec("ch4_energy_label", "Energielabel", "energy_label"),
        KPISpec("ch4_label_score", "Label Score", None, None, derived_from=["energy_label"]),
        KPISpec("ch4_living_area", "Woonoppervlak", "living_area_m2", "m²"),
        KPISpec("ch4_build_year", "Bouwjaar", "build_year"),
        
        # Isolation status per component (derived from build_year)
        KPISpec("ch4_isolation_roof", "Dakisolatie", None, None, derived_from=["build_year"]),
        KPISpec("ch4_isolation_wall", "Gevelisolatie", None, None, derived_from=["build_year"]),
        KPISpec("ch4_isolation_floor", "Vloerisolatie", None, None, derived_from=["build_year"]),
        KPISpec("ch4_isolation_glass", "Glasisolatie", None, None, derived_from=["build_year"]),
        
        # Heating system
        KPISpec("ch4_heating_type", "Verwarmingssysteem", "heating_type"),
        KPISpec("ch4_heating_efficiency", "Verwarmingsefficiëntie", None, None, derived_from=["energy_label", "build_year"]),
        
        # Consumption and costs
        KPISpec("ch4_est_gas_m3", "Geschat Gasverbruik", None, "m³/jaar", derived_from=["energy_label", "living_area_m2"]),
        KPISpec("ch4_est_elec_kwh", "Geschat Elektraverbruik", None, "kWh/jaar", derived_from=["living_area_m2"]),
        KPISpec("ch4_est_annual_cost", "Geschatte Jaarkosten", None, "€/jaar", derived_from=["energy_label", "living_area_m2"]),
        
        # Environmental impact
        KPISpec("ch4_co2_indication", "CO₂ Indicatie", None, "kg/jaar", derived_from=["energy_label", "living_area_m2"]),
        
        # Sustainability investment
        KPISpec("ch4_sustainability_cost_low", "Verduurzaming Min", None, "€", derived_from=["energy_label", "living_area_m2"]),
        KPISpec("ch4_sustainability_cost_high", "Verduurzaming Max", None, "€", derived_from=["energy_label", "living_area_m2"]),
        KPISpec("ch4_savings_potential", "Besparingspotentieel", None, "€/jaar", derived_from=["energy_label"]),
        KPISpec("ch4_payback_years", "Terugverdientijd", None, "jaar", derived_from=["energy_label", "living_area_m2"]),
        
        # Explicit uncertainty markers (MANDATORY per contract)
        KPISpec("ch4_uncertainty_label", "Label Betrouwbaarheid", None),
        KPISpec("ch4_uncertainty_consumption", "Verbruik Onzekerheid", None),
        KPISpec("ch4_uncertainty_costs", "Kosten Bandbreedte", None),
    ],
    5: [
        # CHAPTER 5: INDELING, RUIMTELIJKHEID & DAGELIJKS GEBRUIK — MAXIMALIZED KPI CATALOG (16+ required)
        
        # Ruimte metrics
        KPISpec("ch5_living_area", "Woonoppervlak", "living_area_m2", "m²"),
        KPISpec("ch5_total_rooms", "Totaal Kamers", "rooms"),
        KPISpec("ch5_avg_room_size", "Gemiddelde Kamermaat", None, "m²", derived_from=["living_area_m2", "rooms"]),
        KPISpec("ch5_plot_area", "Perceeloppervlak", "plot_area_m2", "m²"),
        
        # Functionality metrics
        KPISpec("ch5_bedrooms", "Slaapkamers", "bedrooms"),
        KPISpec("ch5_bathrooms", "Badkamers", "bathrooms"),
        KPISpec("ch5_workspace_potential", "Werkruimte-indicatie", None, None, derived_from=["rooms", "bedrooms"]),
        KPISpec("ch5_storage_indication", "Opslagruimte", None, None, derived_from=["living_area_m2"]),
        
        # Usage metrics
        KPISpec("ch5_m2_per_person", "m² per Persoon", None, "m²", derived_from=["living_area_m2"]),
        KPISpec("ch5_living_ratio", "Woon-Slaap Ratio", None, None, derived_from=["rooms", "bedrooms"]),
        KPISpec("ch5_multifunctionality", "Multifunctionaliteitsscore", None, None, derived_from=["living_area_m2", "rooms"]),
        
        # Flexibility metrics
        KPISpec("ch5_reconfig_potential", "Herindelingspotentieel", None, None, derived_from=["build_year", "rooms"]),
        KPISpec("ch5_future_proof", "Toekomstbestendigheid", None, None, derived_from=["living_area_m2", "bedrooms"]),
        KPISpec("ch5_expansion_potential", "Uitbreidingspotentieel", None, None, derived_from=["plot_area_m2", "living_area_m2"]),
        
        # Property type context
        KPISpec("ch5_property_type", "Woningtype", "property_type"),
        KPISpec("ch5_build_year", "Bouwjaar", "build_year"),
        
        # Explicit uncertainty markers (MANDATORY per contract)
        KPISpec("ch5_uncertainty_floorplan", "Plattegrond Status", None),
        KPISpec("ch5_uncertainty_daylight", "Daglicht Onbekend", None),
        KPISpec("ch5_uncertainty_layout", "Indeling Subjectief", None),
    ],
    6: [
        # CHAPTER 6: AFWERKING & KWALITEIT — MAXIMALIZED KPI CATALOG (14+ required)
        
        # Context indicators
        KPISpec("ch6_build_year", "Bouwjaar", "build_year"),
        KPISpec("ch6_property_type", "Woningtype", "property_type"),
        KPISpec("ch6_living_area", "Woonoppervlak", "living_area_m2", "m²"),
        
        # Quality age indicators
        KPISpec("ch6_age", "Woningouderdom", None, "jaar", derived_from=["build_year"]),
        KPISpec("ch6_construction_period", "Bouwperiode", None, None, derived_from=["build_year"]),
        
        # Finish level estimates (derived from build_year)
        KPISpec("ch6_kitchen_age", "Keuken Leeftijd", None, "jaar", derived_from=["build_year"]),
        KPISpec("ch6_bathroom_age", "Badkamer Leeftijd", None, "jaar", derived_from=["build_year"]),
        KPISpec("ch6_floor_condition", "Vloer Conditie", None, None, derived_from=["build_year"]),
        KPISpec("ch6_wall_finish", "Wand Afwerking", None, None, derived_from=["build_year"]),
        
        # Material and maintenance
        KPISpec("ch6_material_quality", "Materiaalkwaliteit", None, None, derived_from=["build_year", "property_type"]),
        KPISpec("ch6_maintenance_state", "Onderhoudsconditie", None, None, derived_from=["build_year"]),
        KPISpec("ch6_paint_refresh", "Schilderwerk Nodig", None, None, derived_from=["build_year"]),
        
        # Renovation cost estimates
        KPISpec("ch6_reno_cost_low", "Renovatie Min", None, "€", derived_from=["living_area_m2", "build_year"]),
        KPISpec("ch6_reno_cost_high", "Renovatie Max", None, "€", derived_from=["living_area_m2", "build_year"]),
        KPISpec("ch6_modernization_score", "Modernisatiescore", None, None, derived_from=["build_year"]),
        
        # Explicit uncertainty markers (MANDATORY)
        KPISpec("ch6_uncertainty_interior", "Interieur Onbekend", None),
        KPISpec("ch6_uncertainty_finish", "Afwerking Subjectief", None),
        KPISpec("ch6_uncertainty_hidden", "Verborgen Gebreken", None),
    ],
    7: [
        # CHAPTER 7: BUITENRUIMTE, TUIN & OMGEVINGSGEBRUIK — MAXIMALIZED KPI CATALOG (16+ required)
        
        # Perceel & tuinoppervlak
        KPISpec("ch7_plot_area", "Perceeloppervlak", "plot_area_m2", "m²"),
        KPISpec("ch7_living_area", "Woonoppervlak", "living_area_m2", "m²"),
        KPISpec("ch7_garden_area", "Tuinoppervlak", None, "m²", derived_from=["plot_area_m2", "living_area_m2"]),
        KPISpec("ch7_outdoor_ratio", "Tuin/Woning Ratio", None, None, derived_from=["plot_area_m2", "living_area_m2"]),
        
        # Tuinligging & oriëntatie
        KPISpec("ch7_orientation", "Tuinoriëntatie", None),  # Often unknown
        KPISpec("ch7_garden_type", "Tuintype", None, None, derived_from=["property_type"]),
        KPISpec("ch7_terrace_potential", "Terraspotentieel", None, None, derived_from=["plot_area_m2"]),
        
        # Privacy-indicatoren
        KPISpec("ch7_property_type", "Woningtype", "property_type"),
        KPISpec("ch7_privacy_level", "Privacy-indicatie", None, None, derived_from=["property_type"]),
        KPISpec("ch7_neighbor_exposure", "Inkijk Risico", None, None, derived_from=["property_type"]),
        
        # Onderhoudsintensiteit
        KPISpec("ch7_maintenance_level", "Onderhoudsniveau", None, None, derived_from=["plot_area_m2"]),
        KPISpec("ch7_garden_work_hours", "Tuinwerk Uren/Week", None, "uur", derived_from=["plot_area_m2"]),
        
        # Buitenvoorzieningen (indien bekend)
        KPISpec("ch7_parking", "Parkeerplaats", None),
        KPISpec("ch7_shed", "Schuur/Berging", None),
        KPISpec("ch7_outdoor_features", "Buitenvoorzieningen", None),
        
        # Uitbreidings-/herinrichtingspotentieel
        KPISpec("ch7_expansion_potential", "Uitbreidingspotentieel", None, None, derived_from=["plot_area_m2", "living_area_m2"]),
        KPISpec("ch7_value_contribution", "Waardebijdrage Tuin", None, None, derived_from=["plot_area_m2"]),
        
        # Explicit uncertainty markers (MANDATORY)
        KPISpec("ch7_uncertainty_orientation", "Oriëntatie Onbekend", None),
        KPISpec("ch7_uncertainty_layout", "Tuinindeling Onbekend", None),
        KPISpec("ch7_uncertainty_condition", "Tuinconditie Subjectief", None),
    ],
    8: [
        # CHAPTER 8: LOCATIE & BEREIKBAARHEID — MAXIMALIZED KPI CATALOG (14+ required)
        
        # Address & location context
        KPISpec("ch8_address", "Adres", "address"),
        KPISpec("ch8_city", "Plaats", None, None, derived_from=["address"]),
        KPISpec("ch8_postal_code", "Postcode", None),
        KPISpec("ch8_province", "Provincie", None, None, derived_from=["address"]),
        
        # Transport accessibility
        KPISpec("ch8_ov_score", "OV-Score", None, None, derived_from=["address"]),
        KPISpec("ch8_station_distance", "Afstand Station", None, "km", derived_from=["address"]),
        KPISpec("ch8_highway_access", "Snelweg Afstand", None, "km", derived_from=["address"]),
        KPISpec("ch8_parking", "Parkeermogelijkheden", None),
        
        # Amenities proximity
        KPISpec("ch8_schools_nearby", "Scholen Nabij", None),
        KPISpec("ch8_shops_nearby", "Winkels Nabij", None),
        KPISpec("ch8_healthcare", "Zorg Nabij", None),
        KPISpec("ch8_recreation", "Recreatie Nabij", None),
        
        # Neighborhood profile
        KPISpec("ch8_neighborhood_type", "Buurttype", None, None, derived_from=["address"]),
        KPISpec("ch8_safety_indication", "Veiligheid Indicatie", None),
        KPISpec("ch8_noise_level", "Geluidsbelasting", None),
        
        # Commute indicators
        KPISpec("ch8_commute_potential", "Woon-Werk Geschiktheid", None, None, derived_from=["address"]),
        
        # Explicit uncertainty markers (MANDATORY)
        KPISpec("ch8_uncertainty_transport", "OV-Data Onzeker", None),
        KPISpec("ch8_uncertainty_safety", "Veiligheid Subjectief", None),
        KPISpec("ch8_uncertainty_neighborhood", "Buurt Beoordeling Nodig", None),
    ],
    9: [
        # CHAPTER 9: JURIDISCH & EIGENDOM — MAXIMALIZED KPI CATALOG (12+ required)
        
        # Ownership type
        KPISpec("ch9_ownership_type", "Eigendomstype", None),
        KPISpec("ch9_property_type", "Woningtype", "property_type"),
        
        # VvE-related (for apartments)
        KPISpec("ch9_vve_contribution", "VvE-Bijdrage", "vve_contribution", "€/mnd"),
        KPISpec("ch9_vve_reserve", "VvE-Reserve", None, "€"),
        KPISpec("ch9_vve_status", "VvE-Status", None),
        KPISpec("ch9_mjop_present", "MJOP Aanwezig", None),
        
        # Leasehold
        KPISpec("ch9_leasehold_status", "Erfpacht Status", None),
        KPISpec("ch9_leasehold_duration", "Erfpacht Looptijd", None, "jaar"),
        KPISpec("ch9_leasehold_canon", "Erfpacht Canon", None, "€/jr"),
        
        # Legal documentation
        KPISpec("ch9_kadaster_checked", "Kadaster Gecontroleerd", None),
        KPISpec("ch9_encumbrances", "Bezwaringen/Erfdienstbaarheden", None),
        KPISpec("ch9_permits_status", "Vergunningen Status", None),
        
        # Financial obligations
        KPISpec("ch9_monthly_obligations", "Maandelijkse Verplichtingen", None, "€"),
        KPISpec("ch9_ozb_indication", "OZB Indicatie", None, "€/jr"),
        
        # Explicit uncertainty markers (MANDATORY)
        KPISpec("ch9_uncertainty_ownership", "Eigendom Vraagt Verificatie", None),
        KPISpec("ch9_uncertainty_vve", "VvE-Info Onvolledig", None),
        KPISpec("ch9_uncertainty_legal", "Juridische Review Nodig", None),
    ],
    10: [
        # CHAPTER 10: FINANCIËLE ANALYSE — MAXIMALIZED KPI CATALOG (14+ required)
        
        # Core pricing
        KPISpec("ch10_price", "Vraagprijs", "asking_price_eur", "€", format_hint="currency"),
        KPISpec("ch10_price_m2", "Prijs/m²", "price_per_m2", "€/m²"),
        KPISpec("ch10_woz", "WOZ-waarde", "woz_value", "€", format_hint="currency"),
        KPISpec("ch10_living_area", "Woonoppervlak", "living_area_m2", "m²"),
        
        # Financing calculations
        KPISpec("ch10_mortgage_monthly", "Hypotheek/mnd (indicatief)", None, "€", derived_from=["asking_price_eur"]),
        KPISpec("ch10_buyer_costs", "Kosten Koper", None, "€", derived_from=["asking_price_eur"]),
        KPISpec("ch10_transfer_tax", "Overdrachtsbelasting", None, "€", derived_from=["asking_price_eur"]),
        KPISpec("ch10_notary_costs", "Notariskosten", None, "€", derived_from=["asking_price_eur"]),
        
        # Monthly costs
        KPISpec("ch10_energy_monthly", "Energielasten/mnd", None, "€", derived_from=["energy_label", "living_area_m2"]),
        KPISpec("ch10_vve_monthly", "VvE-Bijdrage/mnd", "vve_contribution", "€"),
        KPISpec("ch10_maintenance_reserve", "Onderhoudsreserve/mnd", None, "€", derived_from=["living_area_m2"]),
        KPISpec("ch10_total_monthly", "Totale Maandlasten", None, "€", derived_from=["asking_price_eur"]),
        
        # Value indicators
        KPISpec("ch10_price_vs_woz", "Prijs vs WOZ Ratio", None, None, derived_from=["asking_price_eur", "woz_value"]),
        KPISpec("ch10_affordability", "Betaalbaarheidsindicator", None, None, derived_from=["asking_price_eur"]),
        
        # Explicit uncertainty markers (MANDATORY)
        KPISpec("ch10_uncertainty_rates", "Rentestand Veranderlijk", None),
        KPISpec("ch10_uncertainty_income", "Inkomen Niet Ingevoerd", None),
        KPISpec("ch10_uncertainty_costs", "Bijkosten Indicatief", None),
    ],
    11: [
        # CHAPTER 11: MARKTPOSITIE & ONDERHANDELINGSRUIMTE — MAXIMALIZED KPI CATALOG (12+ required)
        
        # Core market data
        KPISpec("ch11_price", "Vraagprijs", "asking_price_eur", "€", format_hint="currency"),
        KPISpec("ch11_price_m2", "Prijs/m²", "price_per_m2", "€/m²"),
        KPISpec("ch11_woz", "WOZ-waarde", "woz_value", "€", format_hint="currency"),
        
        # Market position indicators
        KPISpec("ch11_market_position", "Marktpositie Score", None, None, derived_from=["asking_price_eur", "living_area_m2"]),
        KPISpec("ch11_regional_avg_m2", "Regionaal Gem. /m²", None, "€/m²"),
        KPISpec("ch11_price_deviation", "Afwijking van Gemiddeld", None, "%", derived_from=["asking_price_eur"]),
        
        # Negotiation insights
        KPISpec("ch11_negotiation_room", "Onderhandelingsruimte", None, "%", derived_from=["asking_price_eur"]),
        KPISpec("ch11_suggested_bid", "Indicatief Doelbod", None, "€", derived_from=["asking_price_eur"]),
        
        # Market dynamics
        KPISpec("ch11_days_on_market", "Dagen op Markt", None, "dagen"),
        KPISpec("ch11_market_trend", "Markttrend", None),
        KPISpec("ch11_seller_motivation", "Verkoper Motivatie", None),
        
        # Explicit uncertainty markers (MANDATORY)
        KPISpec("ch11_uncertainty_market", "Marktdata Beperkt", None),
        KPISpec("ch11_uncertainty_comps", "Vergelijkingen Indicatief", None),
        KPISpec("ch11_uncertainty_timing", "Timing Onzeker", None),
    ],
    12: [
        # CHAPTER 12: EINDCONCLUSIE & AANBEVELING — MAXIMALIZED KPI CATALOG (12+ required)
        
        # Core summary
        KPISpec("ch12_price", "Vraagprijs", "asking_price_eur", "€", format_hint="currency"),
        KPISpec("ch12_match", "Match Score", "total_match_score", "%"),
        KPISpec("ch12_marcel_score", "Marcel Score", None, "%", derived_from=["total_match_score"]),
        KPISpec("ch12_petra_score", "Petra Score", None, "%", derived_from=["total_match_score"]),
        
        # Decision support
        KPISpec("ch12_combined_score", "Gecombineerde Score", None, "%", derived_from=["total_match_score"]),
        KPISpec("ch12_recommendation", "Aanbeveling", None),
        KPISpec("ch12_confidence_level", "Betrouwbaarheidsniveau", None, "%"),
        
        # Bid guidance
        KPISpec("ch12_suggested_bid_low", "Minimumbod", None, "€", derived_from=["asking_price_eur"]),
        KPISpec("ch12_suggested_bid_target", "Doelbod", None, "€", derived_from=["asking_price_eur"]),
        KPISpec("ch12_suggested_bid_max", "Maximumbod", None, "€", derived_from=["asking_price_eur"]),
        
        # Action items
        KPISpec("ch12_priority_actions", "Prioriteitsacties", None),
        KPISpec("ch12_next_steps", "Volgende Stappen", None),
        
        # Explicit uncertainty markers (MANDATORY)
        KPISpec("ch12_uncertainty_data", "Data Compleetheid", None),
        KPISpec("ch12_uncertainty_visit", "Bezichtiging Vereist", None),
        KPISpec("ch12_uncertainty_advice", "Advies Indicatief", None),
    ],
}

# Minimum KPI thresholds per chapter (for diagnostics, not hard failure)
PLANE_C_MIN_KPIS: Dict[int, int] = {
    1: 5,   # Core chapter needs many facts
    2: 3,   # Match needs the 3 scores
    3: 6,   # Bouwkundige staat needs comprehensive structural KPIs
    4: 14,  # Energie & Duurzaamheid needs comprehensive energy KPIs
    5: 16,  # Indeling & Ruimtelijkheid needs comprehensive layout KPIs
    6: 14,  # Afwerking & Kwaliteit needs comprehensive quality KPIs
    7: 16,  # Buitenruimte & Tuin needs comprehensive outdoor KPIs
    8: 14,  # Locatie & Bereikbaarheid needs comprehensive location KPIs
    9: 12,  # Juridisch & Eigendom needs comprehensive legal KPIs
    10: 14, # Financiële Analyse needs comprehensive financial KPIs
    11: 12, # Marktpositie needs comprehensive market KPIs
    12: 12, # Eindconclusie needs comprehensive summary KPIs
}


# =============================================================================
# PLANE D — HUMAN PREFERENCE CONTRACT
# =============================================================================

@dataclass
class PersonaRequirement:
    """Requirements for a persona in Plane D."""
    min_positives: int = 3
    min_concerns: int = 3
    require_tradeoff_text: bool = True


@dataclass
class PlaneDContract:
    """Contract for Plane D."""
    marcel: PersonaRequirement
    petra: PersonaRequirement
    require_tensions: bool = True
    require_overlap: bool = True
    min_tension_count: int = 1
    min_overlap_count: int = 1


DEFAULT_PLANE_D_CONTRACT = PlaneDContract(
    marcel=PersonaRequirement(min_positives=3, min_concerns=3, require_tradeoff_text=True),
    petra=PersonaRequirement(min_positives=3, min_concerns=3, require_tradeoff_text=True),
    require_tensions=True,
    require_overlap=True,
    min_tension_count=1,
    min_overlap_count=1
)


# =============================================================================
# MAXIMALIZATION SUMMARY DIAGNOSTICS
# =============================================================================

@dataclass
class MaximalizationDiagnostic:
    """Diagnostic summary for maximalization compliance."""
    chapter_id: int
    
    # Plane A
    charts_expected: int
    charts_generated: int
    charts_missing_reasons: List[str]
    
    # Plane B
    word_count: int
    word_target: int
    sections_found: List[str]
    sections_missing: List[str]
    cross_refs_found: Dict[str, int]
    
    # Plane C
    kpis_expected: int
    kpis_generated: int
    kpis_missing: List[str]
    
    # Plane D
    marcel_positives: int
    marcel_concerns: int
    petra_positives: int
    petra_concerns: int
    tensions_count: int
    overlap_count: int
    
    @property
    def is_maximized(self) -> bool:
        """Check if chapter meets maximalization contract."""
        return (
            self.charts_generated >= 1 and
            self.word_count >= self.word_target and
            self.kpis_generated >= 2 and
            self.marcel_positives >= 1 and
            self.petra_positives >= 1
        )
    
    def to_log_block(self) -> str:
        """Generate log-friendly diagnostic block."""
        return f"""
=== 4PLANE DIAGNOSTICS: CHAPTER {self.chapter_id} ===
PLANE A (Visuals):
  Expected: {self.charts_expected} | Generated: {self.charts_generated}
  Missing: {', '.join(self.charts_missing_reasons) if self.charts_missing_reasons else 'None'}

PLANE B (Narrative):
  Words: {self.word_count}/{self.word_target}
  Sections: {', '.join(self.sections_found) if self.sections_found else 'None'}
  Missing Sections: {', '.join(self.sections_missing) if self.sections_missing else 'None'}
  Cross-refs: {self.cross_refs_found}

PLANE C (Facts):
  Expected: {self.kpis_expected} | Generated: {self.kpis_generated}
  Missing: {', '.join(self.kpis_missing) if self.kpis_missing else 'None'}

PLANE D (Preferences):
  Marcel: +{self.marcel_positives} / -{self.marcel_concerns}
  Petra: +{self.petra_positives} / -{self.petra_concerns}
  Tensions: {self.tensions_count} | Overlap: {self.overlap_count}

MAXIMIZED: {'✓ YES' if self.is_maximized else '✗ NO'}
=== END DIAGNOSTICS ===
"""


def get_chart_catalog(chapter_id: int) -> List[ChartSpec]:
    """Get chart specifications for a chapter."""
    return PLANE_A_CHART_CATALOG.get(chapter_id, [])


def get_kpi_catalog(chapter_id: int) -> List[KPISpec]:
    """Get KPI specifications for a chapter."""
    return PLANE_C_KPI_CATALOG.get(chapter_id, [])


def get_min_kpis(chapter_id: int) -> int:
    """Get minimum KPI threshold for diagnostics."""
    return PLANE_C_MIN_KPIS.get(chapter_id, 2)


def get_plane_d_contract() -> PlaneDContract:
    """Get Plane D contract (same for all chapters)."""
    return DEFAULT_PLANE_D_CONTRACT
