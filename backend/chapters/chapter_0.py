from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent

class ExecutiveSummary(BaseChapter):
    def get_title(self) -> str:
        return "Executive Summary"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        
        # --- 1. INTELLIGENCE ENGINE ---
        # Parse inputs
        try:
            import re
            # Regex to find the first valid number sequence, ignoring dots but keeping the structure
            # e.g. "€ 1.400.000" -> "1400000"
            price_raw = ctx.get('prijs', '0')
            size_raw = ctx.get('oppervlakte', '0')

            # Extract digits from price (handle 1.250.000 -> 1250000)
            price_digits = re.sub(r'[^\d]', '', price_raw)
            price_val = int(price_digits) if price_digits else 0
            
            # Extract digits from size (handle 120 m2 -> 120)
            # We take the first group of digits found
            size_match = re.search(r'(\d+)', size_raw)
            size_val = int(size_match.group(1)) if size_match else 1
            
            if size_val == 0: size_val = 1
            
            price_m2 = round(price_val / size_val)
        except Exception as e:
            import logging
            logging.error(f"Parsing Error: {e}")
            price_val = 0
            size_val = 0
            price_m2 = 0

        year = ctx.get('bouwjaar', '2000')
        label = ctx.get('label', '?').upper()
        
        # Logic: Valuation
        market_avg_m2 = ctx.get('avg_m2_price', 4800) # National average fallback if local unavailable
        valuation_status = "Marktconform"
        trend = "neutral"
        if price_m2 > market_avg_m2 * 1.2:
            valuation_status = "Premium Segment"
            trend = "up"
        elif price_m2 < market_avg_m2 * 0.8:
            valuation_status = "Potentiële Kans"
            trend = "down"

        # Logic: Renovation Risk
        reno_cost = 0
        if "F" in label or "G" in label:
            reno_cost = 45000
            sustain_advice = "Ingrijpende verduurzaming nodig."
        elif "D" in label or "E" in label:
            reno_cost = 25000
            sustain_advice = "Isolatie-update aanbevolen."
        else:
            sustain_advice = "Voldoet aan moderne standaarden."

        # Logic: Construction
        try:
            year_val = int(re.sub(r'[^\d]', '', str(year)) or 2000)
            if year_val < 1990:
                construction_alert = "Aandacht nodig: Dak, Leidingwerk & Asbest."
            else:
                construction_alert = "Relatief jonge bouw; beperkt risico."
        except:
            construction_alert = "Bouwjaar verificatie vereist."

        # Logic: AI Score
        base_score = 70
        if price_m2 < market_avg_m2: base_score += 10
        if "A" in label or "B" in label: base_score += 10
        if "G" in label: base_score -= 15
        
        ai_score = min(max(base_score, 0), 100)

        # --- 2. BUILD PRO REPORT ---
        
        # Hero
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": ctx.get('prijs', 'Prijs op aanvraag'),
            "status": "Te Koop" if price_val > 0 else "Analyse Mode",
            "labels": ["Woonhuis", f"{ctx.get('oppervlakte', '?').replace('m2','')} m² Wonen", f"{ctx.get('perceel', '?').replace('m2','')} m² Perceel"] 
        }

        # Metrics
        market_delta = round(((price_m2 - market_avg_m2) / market_avg_m2) * 100)
        delta_str = f"{'+' if market_delta > 0 else ''}{market_delta}% vs markt"
        
        metrics = [
            {"id": "price_m2", "label": "Vraagprijs per m²", "value": f"€ {price_m2:,}", "icon": "pricetag", "trend": trend, "trend_text": delta_str},
            {"id": "energy", "label": "Duurzaamheid", "value": f"Label {label}", "icon": "leaf", "color": "green" if label in ["A","B","C"] else "orange"},
            {"id": "investment", "label": "Verw. Investering", "value": f"€ {reno_cost:,}" if reno_cost > 0 else "Geen direct", "icon": "hammer", "trend": "neutral" if reno_cost == 0 else "down"},
            {"id": "return", "label": "Verhuurpotentie", "value": f"€ {int(size_val * 22.5):,}", "icon": "trending-up", "trend": "up"}
        ]

        # Strategic Main Content
        summary_html = f"""
        <p class="lead-text">
            <strong>Strategische Analyse:</strong> Het object aan de {ctx.get('adres')} positioneert zich als een 
            <strong>{valuation_status}</strong> in de huidige markt. Met een vierkantemeterprijs van € {price_m2} ligt het 
            {abs(market_delta)}% { "boven" if market_delta > 0 else "onder" } het gemiddelde.
        </p>

        <div class="analysis-grid">
            <div class="analysis-item">
                <div class="analysis-icon {'warning' if reno_cost > 0 else 'valid'}"><ion-icon name="construct"></ion-icon></div>
                <div class="analysis-text">
                    <strong>Bouwtechnische Staat & Risico's</strong><br>
                    {construction_alert} Gezien het energielabel {label} moet rekening gehouden worden met een investering van circa € {reno_cost:,} om het comfort naar niveau 2025 te tillen.
                </div>
            </div>
            <div class="analysis-item">
                <div class="analysis-icon valid"><ion-icon name="cash"></ion-icon></div>
                <div class="analysis-text">
                    <strong>Waardering & Loopopties</strong><br>
                    Gezien de marktdruk en de staat van onderhoud is de {valuation_status.lower()} een belangrijk onderhandelpunt. {sustain_advice}
                </div>
            </div>
        </div>
        """

        # Expert Sidebar
        sidebar = [
             {
                "type": "advisor_score", 
                "title": "AI Aankoop Score", 
                "score": ai_score, 
                "content": f"Score bepaald o.b.v. {valuation_status}, Label {label} en marktcourantheid."
            },
            {
                "type": "advisor_card", 
                "title": "Strategisch Advies", 
                "style": "gradient",
                "content": f"Op basis van de analyse: <strong>{'Koopwaardig' if ai_score > 70 else 'Risicovol'}</strong>. { 'Focus op de prijs-kwaliteit.' if ai_score > 70 else 'Verdere inspectie is cruciaal.' }"
            },
            {
                "type": "action_list",
                "title": "Noodzakelijke Acties",
                "items": [
                    "Bouwkundige keuring inplannen" if reno_cost > 0 else "Onderhoudshistorie opvragen",
                    "Energielabel checken in register",
                    "Juridische erfdienstbaarheden controleren"
                ]
            }
        ]

        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "World Class Investigation", "content": summary_html},
            "sidebar": sidebar
        }
        
        return ChapterOutput(
            title="0. Executive Summary",
            grid_layout=layout, 
            blocks=[] 
        )
