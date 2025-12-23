from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine
import re
import logging

class ExecutiveSummary(BaseChapter):
    def get_title(self) -> str:
        return "Executive Summary"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        
        # Smart Address Display - MOVED UP to affect AI Narrative
        raw_address = str(ctx.get('adres', 'Adres Onbekend'))
        generic_titles = ['mijn huis', 'te koop', 'woning', 'object', 'huis', 'appartement']
        is_generic = raw_address.lower().strip() in generic_titles
        display_address = raw_address if not is_generic else "dit object"
        intro_address_text = f"aan de {raw_address}" if not is_generic else "op deze locatie"
        
        # Ensure AI uses the cleaned address
        if is_generic:
            ctx['address'] = display_address
            # Also update the key AI might look for if different
            ctx['adres'] = display_address
        
        # --- 1. INTELLIGENCE ENGINE ---
        # Generate Narrative (This triggers the AI Backend if available)
        narrative = IntelligenceEngine.generate_chapter_narrative(0, ctx)
        
        # Polish intro grammar if generic replacement occurred
        if is_generic and narrative.get('intro'):
             narrative['intro'] = narrative['intro'].replace("van de dit object", "van dit object")

        # Use Enriched Data (Single Source of Truth)
        price_val = ctx.get('price_parsed', 0)
        size_val = ctx.get('living_area_parsed', 1)
        price_m2 = ctx.get('price_per_m2', 0)
        
        year = ctx.get('construction_year', 2000)
        label = (ctx.get('energy_label') or "?").upper()
        
        # Logic: Valuation
        valuation_status = ctx.get('valuation_status', 'Marktconform')
        market_avg_m2 = int(ctx.get('avg_m2_price', 4800) or 4800) 
        trend = "neutral"
        if price_m2 > market_avg_m2 * 1.2:
            valuation_status = "Premium Segment"
            trend = "up"
        elif price_m2 < market_avg_m2 * 0.8:
            valuation_status = "Potentiële Kans"
            trend = "down"


        # Logic: Renovation Risk & Costs
        energy_reno_cost = ctx.get('energy_invest', 0)
        sustain_advice = ctx.get('sustainability_advice', 'Standaard')
        
        # Logic: Construction & Age Risk
        construction_risk_cost = ctx.get('construction_invest', 0)
        construction_alert = ctx.get('construction_alert', 'Check constructie.')
        year_val = year
        
        total_expected_invest = ctx.get('estimated_reno_cost', energy_reno_cost + construction_risk_cost)

        # Logic: AI Score
        ai_score = ctx.get('ai_score', 70)
        


        # --- 2. BUILD PRO REPORT ---
        
        # Hero
        # Strip m² and m2 from values to avoid duplication
        oppervlakte_clean = str(ctx.get('oppervlakte', '?')).replace('m²', '').replace('m2', '').strip()
        perceel_clean = str(ctx.get('perceel', '?')).replace('m²', '').replace('m2', '').strip()
        
        # Smart Address Display
        raw_address = str(ctx.get('adres', 'Adres Onbekend'))
        generic_titles = ['mijn huis', 'te koop', 'woning', 'object', 'huis', 'appartement']
        is_generic = raw_address.lower().strip() in generic_titles
        display_address = raw_address if not is_generic else "dit object"
        intro_address_text = f"aan de {raw_address}" if not is_generic else "op deze locatie"
        
        # Ensure AI uses the cleaned address
        if is_generic:
            ctx['address'] = display_address
            ctx['adres'] = display_address

        hero = {
            "address": raw_address,
            "price": f"€ {price_val:,}".replace(',', '.') if price_val > 0 else "Prijs op aanvraag",
            "status": "Te Koop" if price_val > 0 else "Analyse Mode",
            "labels": ["Woonhuis", f"{oppervlakte_clean} m² Wonen", f"{perceel_clean} m² Perceel"] 
        }

        
        # Determine colors and explanations for metrics
        energy_color = "green" if label in ["A","B"] else "orange" if label in ["C","D"] else "red"
        energy_explanation = "Uitstekende energie-efficiëntie" if label in ["A","B"] else "Gemiddeld, verbetering aanbevolen" if label in ["C","D"] else "Slecht, renovatie dringend nodig"
        
        investment_color = "green" if total_expected_invest == 0 else "orange" if total_expected_invest <= 30000 else "red"
        
        if total_expected_invest == 0:
            inv_text = "Geen directe investering"
            inv_exp = "Instapklaar"
        else:
            inv_text = f"€ {total_expected_invest:,}"
            inv_exp = f"{'Hoge' if total_expected_invest > 30000 else 'Gemiddelde'} verwachte kosten"
        
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
            {"id": "investment", "label": "Verw. Investering", "value": inv_text, "icon": "hammer", "trend": "neutral" if total_expected_invest == 0 else "down", "color": investment_color, "explanation": inv_exp},
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
        
        # Maintenance Intensity Logic - Fixed Consistency
        # Now uses total_expected_invest which includes construction risks
        maintenance = "Hoog" if total_expected_invest > 30000 else "Middelmatig" if total_expected_invest > 0 else "Laag"
        maintenance_color = "red" if total_expected_invest > 30000 else "orange" if total_expected_invest > 0 else "green"
        maintenance_explanation = f"Hoge kosten (€{total_expected_invest:,})" if total_expected_invest > 30000 else f"Gemiddelde kosten (€{total_expected_invest:,})" if total_expected_invest > 0 else "Lage onderhoudskosten"
        metrics.append({"id": "maintenance_intensity", "label": "Onderhoudsintensiteit", "value": maintenance, "icon": "hammer", "trend": "neutral", "color": maintenance_color, "explanation": maintenance_explanation})
        
        family = "Geschikt" if size_val >= 120 else "Beperkt geschikt"
        family_color = "green" if size_val >= 120 else "orange"
        family_explanation = "Voldoende ruimte voor gezin" if size_val >= 120 else "Beperkte ruimte voor groot gezin"
        metrics.append({"id": "family_suitability", "label": "Gezinsgeschiktheid", "value": family, "icon": "people", "trend": "neutral", "color": family_color, "explanation": family_explanation})
        
        lt_quality = "Hoog" if year_val >= 1990 else "Middelmatig" if year_val >= 1970 else "Laag"
        lt_quality_color = "green" if year_val >= 1990 else "orange" if year_val >= 1970 else "red"
        lt_quality_explanation = "Moderne bouw" if year_val >= 1990 else "Oudere bouw, aandacht nodig" if year_val >= 1970 else "Oude bouw, renovatie nodig"
        metrics.append({"id": "long_term_quality", "label": "Lange-termijn kwaliteit", "value": lt_quality, "icon": "shield", "trend": "neutral", "color": lt_quality_color, "explanation": lt_quality_explanation})


        # Strategic Main Content
        # We use the base class renderer to ensure consistency.
        # dashboard_extra_html is removed as it's now handled by the React Data Matrix.
        
        # Merge hardcoded pros/cons with AI narrative results
        final_strengths = list(dict.fromkeys(pros + (narrative.get('strengths') or [])))
        
        # Ensure advice is a list before merging
        raw_advice = narrative.get('advice') or []
        if isinstance(raw_advice, str):
            raw_advice = [raw_advice]
        final_advice = list(dict.fromkeys(cons + raw_advice))
        
        narrative['strengths'] = final_strengths
        narrative['advice'] = final_advice

        # Render the rich narrative which now includes the comparison section
        final_content = self._render_rich_narrative(narrative)

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
                "content": narrative.get('conclusion', f"Op basis van de analyse: <strong>{'Koopwaardig' if ai_score > 70 else 'Risicovol'}</strong>.")
            },
            {
                "type": "action_list",
                "title": "Noodzakelijke Acties",
                "items": [
                    "Bouwkundige keuring inplannen" if total_expected_invest > 0 else "Onderhoudshistorie opvragen",
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
            "main": {"title": "Executive Property Assessment", "content": final_content},
            "left_sidebar": left_sidebar,
            "sidebar": sidebar
        }
        
        chapter_data = {
            "title": "Executive Summary",
            "intro": narrative.get('intro', ''),
            "main_analysis": final_content,
            "conclusion": narrative.get('conclusion', ''),
            "strengths": final_strengths,
            "advice": final_advice,
            "interpretation": narrative.get('interpretation', ''),
            "variables": narrative.get('variables', {}),
            "sidebar_items": sidebar,
            "comparison": narrative.get('comparison', {}),
            "marcel_match_score": self.data.get('marcel_match_score', 0),
            "petra_match_score": self.data.get('petra_match_score', 0)
        }

        # Provenance mapping
        prov_dict = narrative.get('_provenance')
        from domain.models import AIProvenance
        prov = AIProvenance(**prov_dict) if prov_dict else None

        return ChapterOutput(
            id="0",
            title="0. Executive Summary",
            grid_layout=layout, 
            blocks=[],
            chapter_data=chapter_data,
            provenance=prov,
            missing_critical_data=narrative.get('metadata', {}).get('missing_vars', [])
        )
