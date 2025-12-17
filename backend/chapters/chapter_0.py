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
        # Strip m² and m2 from values to avoid duplication
        oppervlakte_clean = ctx.get('oppervlakte', '?').replace('m²', '').replace('m2', '').strip()
        perceel_clean = ctx.get('perceel', '?').replace('m²', '').replace('m2', '').strip()
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": ctx.get('prijs', 'Prijs op aanvraag'),
            "status": "Te Koop" if price_val > 0 else "Analyse Mode",
            "labels": ["Woonhuis", f"{oppervlakte_clean} m² Wonen", f"{perceel_clean} m² Perceel"] 
        }

        
        # Determine colors and explanations for metrics
        energy_color = "green" if label in ["A","B"] else "orange" if label in ["C","D"] else "red"
        energy_explanation = "Uitstekende energie-efficiëntie" if label in ["A","B"] else "Gemiddeld, verbetering aanbevolen" if label in ["C","D"] else "Slecht, renovatie dringend nodig"
        
        investment_color = "green" if reno_cost == 0 else "orange" if reno_cost <= 30000 else "red"
        investment_explanation = "Geen directe renovatie nodig" if reno_cost == 0 else f"Gemiddelde renovatiekosten (€{reno_cost:,})" if reno_cost <= 30000 else f"Hoge renovatiekosten (€{reno_cost:,})"
        
        price_m2_color = "green" if price_m2 < market_avg_m2 * 0.95 else "orange" if price_m2 <= market_avg_m2 * 1.05 else "red"
        price_m2_explanation = "Onder marktprijs" if price_m2 < market_avg_m2 * 0.95 else "Rond marktprijs" if price_m2 <= market_avg_m2 * 1.05 else "Boven marktprijs"
        
        # Calculate market deviation for metrics
        market_delta = 0
        delta_str = "0% vs markt"
        if market_avg_m2:
            market_delta = round(((price_m2 - market_avg_m2) / market_avg_m2) * 100)
            delta_str = f"{market_delta:+}% vs markt"

        metrics = [
            {"id": "price_m2", "label": "Vraagprijs per m²", "value": f"€ {price_m2:,}", "icon": "pricetag", "trend": trend, "trend_text": delta_str, "color": price_m2_color, "explanation": price_m2_explanation},
            {"id": "energy", "label": "Duurzaamheid", "value": f"Label {label}", "icon": "leaf", "color": energy_color, "explanation": energy_explanation},
            {"id": "investment", "label": "Verw. Investering", "value": f"€ {reno_cost:,}" if reno_cost > 0 else "Geen direct", "icon": "hammer", "trend": "neutral" if reno_cost == 0 else "down", "color": investment_color, "explanation": investment_explanation},
            {"id": "return", "label": "Verhuurpotentie", "value": f"€ {int(size_val * 22.5):,}", "icon": "trending-up", "trend": "up"}
        ]
        
        # Logic: Pros & Cons
        pros = []
        cons = []
        if "A" in label or "B" in label: pros.append("Uitstekend energielabel (Toekomstbestendig)")
        else: cons.append(f"Matig energielabel ({label}), verduurzaming nodig")
        
        if price_m2 < market_avg_m2: pros.append("Scherpe m² prijs t.o.v. gemiddelde")
        elif price_m2 > market_avg_m2 * 1.2: cons.append("Hoge m² prijs (Premium segment)")
        
        if year_val > 2000: pros.append("Recent bouwjaar, lage onderhoudsverwachting")
        elif year_val < 1990: cons.append("Ouder object, mogelijk bouwkundige risico's")

        if size_val > 150: pros.append("Royaal woonoppervlak")

        pros_html = "".join([f"<li class='pro'><ion-icon name='checkmark-circle' style='color:#10b981'></ion-icon> {p}</li>" for p in pros])
        cons_html = "".join([f"<li class='con'><ion-icon name='alert-circle' style='color:#ef4444'></ion-icon> {c}</li>" for c in cons])

        # New additive metrics (added after pros/cons to avoid reference errors)
        if market_avg_m2:
            price_dev_pct = market_delta
            price_dev_color = "green" if price_dev_pct < -5 else "orange" if price_dev_pct <= 5 else "red"
            price_dev_explanation = "Onder marktprijs" if price_dev_pct < -5 else "Rond marktprijs" if price_dev_pct <= 5 else "Boven marktprijs"
            metrics.append({"id": "price_deviation", "label": "Prijsafwijking %", "value": f"{price_dev_pct:+}%" if price_dev_pct != 0 else "0%", "icon": "analytics", "trend": "up" if price_dev_pct > 0 else "down" if price_dev_pct < 0 else "neutral", "trend_text": f"{price_dev_pct:+}% vs markt", "color": price_dev_color, "explanation": price_dev_explanation})
        
        future_score = 80 if label in ["A", "A+", "A++", "B"] else 60 if label in ["C", "D"] else 40
        future_score_color = "green" if future_score >= 70 else "orange" if future_score >= 50 else "red"
        future_score_explanation = "Uitstekende toekomstbestendigheid" if future_score >= 70 else "Gemiddelde toekomstbestendigheid" if future_score >= 50 else "Lage toekomstbestendigheid"
        metrics.append({"id": "energy_future", "label": "Energie Toekomstscore", "value": f"{future_score}/100", "icon": "leaf", "color": future_score_color, "explanation": future_score_explanation, "trend": "neutral"})
        
        maintenance = "Hoog" if reno_cost > 30000 else "Middelmatig" if reno_cost > 0 else "Laag"
        maintenance_color = "red" if reno_cost > 30000 else "orange" if reno_cost > 0 else "green"
        maintenance_explanation = f"Hoge onderhoudskosten (€{reno_cost:,})" if reno_cost > 30000 else f"Gemiddelde onderhoudskosten (€{reno_cost:,})" if reno_cost > 0 else "Lage onderhoudskosten"
        metrics.append({"id": "maintenance_intensity", "label": "Onderhoudsintensiteit", "value": maintenance, "icon": "hammer", "trend": "neutral", "color": maintenance_color, "explanation": maintenance_explanation})
        
        family = "Geschikt" if size_val >= 120 else "Beperkt geschikt"
        family_color = "green" if size_val >= 120 else "orange"
        family_explanation = "Voldoende ruimte voor gezin" if size_val >= 120 else "Beperkte ruimte voor groot gezin"
        metrics.append({"id": "family_suitability", "label": "Gezinsgeschiktheid", "value": family, "icon": "people", "trend": "neutral", "color": family_color, "explanation": family_explanation})
        
        lt_quality = "Hoog" if year_val >= 1990 else "Middelmatig" if year_val >= 1970 else "Laag"
        lt_quality_color = "green" if year_val >= 1990 else "orange" if year_val >= 1970 else "red"
        lt_quality_explanation = "Moderne bouw" if year_val >= 1990 else "Oudere bouw, aandacht nodig" if year_val >= 1970 else "Oude bouw, renovatie nodig"
        metrics.append({"id": "long_term_quality", "label": "Lange-termijn kwaliteit", "value": lt_quality, "icon": "shield", "trend": "neutral", "color": lt_quality_color, "explanation": lt_quality_explanation})





        # Strategic Main Content with Color Legend
        summary_html = f"""
        <p class="lead-text">
            <strong>Strategische Analyse:</strong> Het object aan de {ctx.get('adres')} positioneert zich als een 
            <strong>{valuation_status}</strong> in de huidige markt. Met een vierkantemeterprijs van € {price_m2} ligt het 
            {abs(market_delta)}% { "boven" if market_delta > 0 else "onder" } het gemiddelde.
        </p>

        <div class="analysis-grid" style="margin-bottom: 2rem;">
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

        <div style="background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 1.5rem; margin-top: 2rem;">
            <h4 style="margin-top:0; color:#334155; margin-bottom: 1rem;">Sterke & Zwakke Punten</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                <div>
                    <h5 style="color:#10b981; margin:0 0 0.5rem 0;">Voordelen</h5>
                    <ul style="list-style:none; padding:0; margin:0; font-size: 0.95rem; color:#475569;">{pros_html}</ul>
                </div>
                <div>
                    <h5 style="color:#ef4444; margin:0 0 0.5rem 0;">Aandachtspunten</h5>
                    <ul style="list-style:none; padding:0; margin:0; font-size: 0.95rem; color:#475569;">{cons_html}</ul>
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

        # Left sidebar: Key property highlights
        left_sidebar = [
             {
                "type": "highlight_card",
                "icon": "analytics",
                "title": "AI Score",
                "content": f"{ai_score}/100 - {valuation_status}"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Executive Property Assessment", "content": summary_html},
            "left_sidebar": left_sidebar,
            "sidebar": sidebar
        }
        
        chapter_data = {
            "title": "Executive Summary",
            "intro": f"Strategische Analyse: Het object aan de {ctx.get('adres')} positioneert zich als een {valuation_status} in de huidige markt.",
            "main_analysis": summary_html,
            "conclusion": f"AI Score: {ai_score}/100 - {valuation_status}. {'Koopwaardig' if ai_score > 70 else 'Risicovol'}.",
            "strengths": pros,
            "advice": cons,
            "interpretation": f"Waardering: {valuation_status} (Label {label})",
            "sidebar_items": sidebar
        }

        return ChapterOutput(
            title="0. Executive Summary",
            grid_layout=layout, 
            blocks=[],
            chapter_data=chapter_data
        )
