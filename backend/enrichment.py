import re
import math
from typing import Dict, Any, List

class DataEnricher:
    """
    Centralized service for data cleaning, metric calculation, and enrichment.
    Ensures 'Single Source of Truth' for all derived data.
    """

    @staticmethod
    def enrich(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes raw scraped data and returns a fully enriched context.
        """
        # 1. Clean Core Data
        ctx = raw_data.copy()
        
        # Parse Integers
        price = DataEnricher._parse_int(ctx.get('asking_price_eur') or ctx.get('prijs'))
        living_area = DataEnricher._parse_int(ctx.get('living_area_m2') or ctx.get('oppervlakte'))
        plot_area = DataEnricher._parse_int(ctx.get('plot_area_m2') or ctx.get('perceel'))
        year = DataEnricher._parse_int(ctx.get('build_year') or ctx.get('bouwjaar'))
        
        # Parse & Clean Strings
        label = (ctx.get('energy_label') or ctx.get('label') or "G").upper()
        if len(label) > 3: label = label[0] # "A++++" -> "A" (simplified for logic, keep original for display?)
        # Let's keep original for display, but cleaned for logic
        label_clean = label.split(' ')[0].strip()

        # 2. Derive Metrics
        price_m2 = round(price / living_area) if living_area and living_area > 0 else 0
        
        # Volume (Estimate if missing)
        volume = DataEnricher._parse_int(ctx.get('volume_m3') or ctx.get('inhoud'))
        if not volume and living_area:
            volume = int(living_area * 3) # Standard height 3m assumption
            
        # Rooms
        bedrooms = DataEnricher._parse_int(ctx.get('bedrooms'))
        rooms = DataEnricher._parse_int(ctx.get('rooms'))
        if not rooms and living_area:
             rooms = max(2, int(living_area / 25)) # Fallback estimation
        
        # 3. Market Analysis Logic
        market_avg_m2 = int(ctx.get('avg_m2_price', 4800) or 4800)
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
        
        # 4. Investment / Renovation Logic
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
        
        # 5. AI / Match Score Logic (Heuristic Baseline)
        base_score = 70
        if price_m2 < market_avg_m2: base_score += 10
        if "A" in label_clean or "B" in label_clean: base_score += 10
        if "F" in label_clean or "G" in label_clean: base_score -= 15
        if total_investment > 30000: base_score -= 10
        
        ai_score = min(max(base_score, 0), 100)

        # 6. Preferences Matching (Marcel & Petra)
        prefs = ctx.get('_preferences', {})
        marcel_score, marcel_reasons = DataEnricher._calculate_persona_match(ctx, prefs.get('marcel', {}))
        petra_score, petra_reasons = DataEnricher._calculate_persona_match(ctx, prefs.get('petra', {}))
        
        total_match_score = int((marcel_score + petra_score) / 2)

        # 7. Populate Context with Canonical Data
        # We overwrite keys to ensure consistency, but keep originals if needed for debug
        
        # --- LAYER 1: CANONICAL REGISTRY INTEGRATION ---
        from backend.domain.registry import CanonicalRegistry, RegistryEntry, RegistryType
        
        registry = CanonicalRegistry()
        
        # Helper to register facts
        def reg(key, val, name, rtype=RegistryType.FACT, unit=None, source="enricher"):
            registry.register(RegistryEntry(
                id=key, 
                type=rtype, 
                value=val, 
                name=name, 
                unit=unit, 
                source=source,
                completeness=val is not None
            ))

        # Register Facts
        reg("asking_price_eur", price, "Vraagprijs", unit="EUR")
        reg("living_area_m2", living_area, "Woonoppervlakte", unit="m2")
        reg("plot_area_m2", plot_area, "Perceeloppervlakte", unit="m2")
        reg("volume_m3", volume, "Inhoud", unit="m3", rtype=RegistryType.VARIABLE) # Inferred often
        reg("rooms", rooms, "Aantal kamers", unit=None)
        reg("bedrooms", bedrooms or 0, "Aantal slaapkamers", unit=None)
        reg("build_year", year, "Bouwjaar", unit=None)
        reg("energy_label", label_clean, "Energielabel", unit=None)
        
        # Register Enriched/Derived Variables
        reg("price_per_m2", price_m2, "Vierkantemeterprijs", rtype=RegistryType.VARIABLE, unit="EUR/m2")
        reg("valuation_status", valuation_status, "Marktwaardering", rtype=RegistryType.VARIABLE)
        reg("market_trend", trend, "Markttrend", rtype=RegistryType.VARIABLE)
        reg("sustainability_advice", sustain_advice, "Duurzaamheidsadvies", rtype=RegistryType.VARIABLE)
        reg("construction_alert", construction_alert, "Bouwkundige Notitie", rtype=RegistryType.VARIABLE)
        
        # Register Financials
        reg("estimated_reno_cost", total_investment, "Geschatte Renovatiekosten", rtype=RegistryType.VARIABLE, unit="EUR")
        reg("energy_invest", energy_reno_cost, "Energie Investering", rtype=RegistryType.VARIABLE, unit="EUR")
        reg("construction_invest", construction_risk_cost, "Bouw Investering", rtype=RegistryType.VARIABLE, unit="EUR")
        
        # Register Matches & Scores (KPIs)
        reg("ai_score", ai_score, "AI Woning Score", rtype=RegistryType.KPI)
        reg("marcel_match_score", marcel_score, "Marcel Match", rtype=RegistryType.KPI)
        reg("petra_match_score", petra_score, "Petra Match", rtype=RegistryType.KPI)
        reg("total_match_score", total_match_score, "Totaal Match", rtype=RegistryType.KPI)
        
        # We also need to preserve the lists/dicts derived
        # For legacy compatibility, we merge the registry values back into ctx
        # But we ALSO optionally store the registry map if the caller supports it.
        
        enriched_data = registry.to_legacy_dict()
        ctx.update(enriched_data)
        
        # Add complex non-scalar objects that Registry might not handle gracefully yet (lists)
        ctx["marcel_reasons"] = marcel_reasons
        ctx["petra_reasons"] = petra_reasons
        
        # Store a flag that Layer 1 is complete
        ctx["_layer1_complete"] = True
        
        return ctx

    @staticmethod
    def _parse_int(val):
        if not val: return 0
        # Handle "1.500.000" -> "1500000"
        s = str(val).replace('.', '').replace(',', '')
        match = re.search(r'\d+', s)
        return int(match.group()) if match else 0

    @staticmethod
    def _calculate_persona_match(data: Dict[str, Any], prefs: Dict[str, Any]) -> tuple[int, List[str]]:
        if not prefs: return 50, []
        
        priorities = prefs.get('priorities', []) + prefs.get('hidden_priorities', [])
        if not priorities: return 50, []
        
        # Search blob
        blob = (
            str(data.get('description', '')) + " " + 
            str(data.get('features', '')) + " " +
            str(data.get('energy_label', ''))
        ).lower()
        
        hits = []
        for p in priorities:
            # Tokenize "zon / solar" logic
            tokens = [t.strip().lower() for t in p.split('/') if t.strip()]
            
            match = False
            for token in tokens:
                # Specific mappings
                if token == "solar": token = "zonnepanelen"
                if token == "jaren 30": token = "193"
                if token == "warmtepomp": token = "warmtepomp"
                if token == "visgraat": token = "visgraat"
                
                if token in blob:
                    match = True
                    break
            
            if match:
                hits.append(p)
                
        score = int((len(hits) / len(priorities)) * 100)
        return max(min(score, 100), 10), hits
