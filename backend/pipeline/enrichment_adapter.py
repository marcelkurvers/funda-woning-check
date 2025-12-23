"""
Enrichment Adapter - Populates Registry from Raw Data

This adapter transforms raw parsed data into canonical registry entries.
It adapts the existing enrichment logic to work with PipelineContext.

KEY DIFFERENCE FROM OLD APPROACH:
- Old: Creates local CanonicalRegistry, flattens to dict, discards registry
- New: Populates the existing registry in PipelineContext directly

The registry in PipelineContext becomes the ONLY source of truth.
"""

import re
import math
from typing import Dict, Any, List, Optional

from backend.domain.pipeline_context import PipelineContext
from backend.domain.registry import RegistryType


def enrich_into_context(ctx: PipelineContext, raw_data: Dict[str, Any]) -> None:
    """
    Enrich raw data and populate the canonical registry in the context.
    
    This function MUTATES the context by registering facts into its registry.
    It does NOT return a dict. All truth lives in ctx.registry.
    
    Args:
        ctx: The PipelineContext to populate
        raw_data: Raw parsed property data
    """
    # Helper to register facts
    def reg(key: str, val: Any, name: str, 
            rtype: RegistryType = RegistryType.FACT,
            unit: Optional[str] = None,
            source: str = "enricher") -> None:
        ctx.register_fact(
            key=key,
            value=val,
            name=name,
            rtype=rtype,
            unit=unit,
            source=source
        )
    
    # Parse Integers safely
    def parse_int(val) -> int:
        if not val:
            return 0
        s = str(val).replace('.', '').replace(',', '')
        match = re.search(r'\d+', s)
        return int(match.group()) if match else 0
    
    # =========================================================================
    # 1. PARSE & CLEAN CORE DATA
    # =========================================================================
    
    price = parse_int(raw_data.get('asking_price_eur') or raw_data.get('prijs'))
    living_area = parse_int(raw_data.get('living_area_m2') or raw_data.get('oppervlakte'))
    plot_area = parse_int(raw_data.get('plot_area_m2') or raw_data.get('perceel'))
    year = parse_int(raw_data.get('build_year') or raw_data.get('bouwjaar'))
    
    # Energy label parsing
    label = (raw_data.get('energy_label') or raw_data.get('label') or "G").upper()
    if len(label) > 3:
        label = label[0]
    label_clean = label.split(' ')[0].strip()
    
    # =========================================================================
    # 2. REGISTER CORE FACTS
    # =========================================================================
    
    reg("asking_price_eur", price, "Vraagprijs", unit="EUR")
    reg("living_area_m2", living_area, "Woonoppervlakte", unit="m2")
    reg("plot_area_m2", plot_area, "Perceeloppervlakte", unit="m2")
    reg("build_year", year, "Bouwjaar")
    reg("energy_label", label_clean, "Energielabel")
    
    # Address info
    reg("address", raw_data.get('address', ''), "Adres", source="parse")
    reg("postal_code", raw_data.get('postal_code', ''), "Postcode", source="parse")
    reg("city", raw_data.get('city', ''), "Plaats", source="parse")
    
    # =========================================================================
    # 3. DERIVE METRICS
    # =========================================================================
    
    price_m2 = round(price / living_area) if living_area and living_area > 0 else 0
    reg("price_per_m2", price_m2, "Vierkantemeterprijs", rtype=RegistryType.VARIABLE, unit="EUR/m2")
    
    # Volume (estimate if missing)
    volume = parse_int(raw_data.get('volume_m3') or raw_data.get('inhoud'))
    if not volume and living_area:
        volume = int(living_area * 3)
    reg("volume_m3", volume, "Inhoud", rtype=RegistryType.VARIABLE, unit="m3")
    
    # Rooms
    bedrooms = parse_int(raw_data.get('bedrooms'))
    rooms = parse_int(raw_data.get('rooms'))
    if not rooms and living_area:
        rooms = max(2, int(living_area / 25))
    reg("rooms", rooms, "Aantal kamers")
    reg("bedrooms", bedrooms or 0, "Aantal slaapkamers")
    
    # =========================================================================
    # 4. MARKET ANALYSIS
    # =========================================================================
    
    market_avg_m2 = int(raw_data.get('avg_m2_price', 4800) or 4800)
    
    valuation_status = "Marktconform"
    trend = "neutral"
    
    if price_m2 > 0:
        if price_m2 > market_avg_m2 * 1.2:
            valuation_status = "Premium Segment"
            trend = "up"
        elif price_m2 < market_avg_m2 * 0.8:
            valuation_status = "Potentiële Kans"
            trend = "down"
        elif price_m2 < market_avg_m2 * 0.95:
            valuation_status = "Scherp Geprijsd"
    
    reg("valuation_status", valuation_status, "Marktwaardering", rtype=RegistryType.VARIABLE)
    reg("market_trend", trend, "Markttrend", rtype=RegistryType.VARIABLE)
    reg("avg_m2_price", market_avg_m2, "Gemiddelde m² prijs markt", rtype=RegistryType.VARIABLE, unit="EUR/m2")
    
    # =========================================================================
    # 5. INVESTMENT / RENOVATION LOGIC
    # =========================================================================
    
    energy_reno_cost = 0
    sustain_advice = "Voldoet aan moderne standaarden."
    
    if any(x in label_clean for x in ["F", "G"]):
        energy_reno_cost = 45000
        sustain_advice = "Ingrijpende verduurzaming nodig."
    elif any(x in label_clean for x in ["D", "E"]):
        energy_reno_cost = 25000
        sustain_advice = "Isolatie-update aanbevolen."
    elif "C" in label_clean:
        energy_reno_cost = 10000
        sustain_advice = "Optimalisatie mogelijk (zonnepanelen/warmtepomp)."
    
    construction_risk_cost = 0
    construction_alert = "Relatief jonge bouw."
    
    if year and year < 1930:
        construction_risk_cost = 25000
        construction_alert = "Risico: Fundering & Loodgieterswerk."
    elif year and year < 1990:
        construction_risk_cost = 15000
        construction_alert = "Risico: Asbest & Isolatie."
    
    total_investment = energy_reno_cost + construction_risk_cost
    
    reg("sustainability_advice", sustain_advice, "Duurzaamheidsadvies", rtype=RegistryType.VARIABLE)
    reg("construction_alert", construction_alert, "Bouwkundige Notitie", rtype=RegistryType.VARIABLE)
    reg("estimated_reno_cost", total_investment, "Geschatte Renovatiekosten", rtype=RegistryType.VARIABLE, unit="EUR")
    reg("energy_invest", energy_reno_cost, "Energie Investering", rtype=RegistryType.VARIABLE, unit="EUR")
    reg("construction_invest", construction_risk_cost, "Bouw Investering", rtype=RegistryType.VARIABLE, unit="EUR")
    
    # =========================================================================
    # 6. AI / MATCH SCORES
    # =========================================================================
    
    base_score = 70
    if price_m2 < market_avg_m2:
        base_score += 10
    if "A" in label_clean or "B" in label_clean:
        base_score += 10
    if "F" in label_clean or "G" in label_clean:
        base_score -= 15
    if total_investment > 30000:
        base_score -= 10
    
    ai_score = min(max(base_score, 0), 100)
    reg("ai_score", ai_score, "AI Woning Score", rtype=RegistryType.KPI)
    
    # Preference Matching
    prefs = ctx.preferences
    marcel_score, marcel_reasons = _calculate_persona_match(raw_data, prefs.get('marcel', {}))
    petra_score, petra_reasons = _calculate_persona_match(raw_data, prefs.get('petra', {}))
    total_match_score = int((marcel_score + petra_score) / 2)
    
    reg("marcel_match_score", marcel_score, "Marcel Match", rtype=RegistryType.KPI)
    reg("petra_match_score", petra_score, "Petra Match", rtype=RegistryType.KPI)
    reg("total_match_score", total_match_score, "Totaal Match", rtype=RegistryType.KPI)
    
    # Store match reasons (as VARIABLE since they're derived)
    reg("marcel_reasons", marcel_reasons, "Marcel Match Redenen", rtype=RegistryType.VARIABLE, source="matcher")
    reg("petra_reasons", petra_reasons, "Petra Match Redenen", rtype=RegistryType.VARIABLE, source="matcher")
    
    # =========================================================================
    # 7. PRESERVE NON-SCALAR DATA
    # =========================================================================
    
    # Description and features for AI reasoning
    reg("description", raw_data.get('description', ''), "Omschrijving", source="parse")
    reg("features", raw_data.get('features', []), "Kenmerken", source="parse")
    
    # Media URLs
    media_urls = raw_data.get('media_urls', [])
    reg("media_urls", media_urls, "Foto URLs", source="parse")
    
    # Funda URL
    reg("funda_url", raw_data.get('funda_url', ''), "Funda Link", source="parse")


def _calculate_persona_match(data: Dict[str, Any], prefs: Dict[str, Any]) -> tuple[int, List[str]]:
    """Calculate match score for a persona based on their preferences."""
    if not prefs:
        return 50, []
    
    priorities = prefs.get('priorities', []) + prefs.get('hidden_priorities', [])
    if not priorities:
        return 50, []
    
    # Build search blob
    blob = (
        str(data.get('description', '')) + " " +
        str(data.get('features', '')) + " " +
        str(data.get('energy_label', ''))
    ).lower()
    
    hits = []
    for p in priorities:
        tokens = [t.strip().lower() for t in p.split('/') if t.strip()]
        
        match = False
        for token in tokens:
            # Specialized mappings
            if token == "solar":
                token = "zonnepanelen"
            if token == "jaren 30":
                token = "193"
            if token == "warmtepomp":
                token = "warmtepomp"
            if token == "visgraat":
                token = "visgraat"
            
            if token in blob:
                match = True
                break
        
        if match:
            hits.append(p)
    
    score = int((len(hits) / len(priorities)) * 100)
    return max(min(score, 100), 10), hits
