
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class GeneralFeatures(BaseChapter):
    def get_title(self) -> str:
        ctx = self.context
        p_type = ctx.get('property_type', '').lower()
        if 'appartement' in p_type:
            return "Kenmerken Appartement"
        elif 'vrijstaand' in p_type or 'villa' in p_type:
            return "Kenmerken Vrijstaande Woning"
        return "Algemene Woningkenmerken"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        
        # 1. Ask Intelligence Engine for Dynamic Narrative
        narrative = IntelligenceEngine.generate_chapter_narrative(1, ctx)
        
        # 2. Key Metrics - Use new fields with fallback to old names
        living_area = IntelligenceEngine._parse_int(
            ctx.get('living_area_m2') or ctx.get('oppervlakte', '0')
        )
        plot_area = IntelligenceEngine._parse_int(
            ctx.get('plot_area_m2') or ctx.get('perceel', '0')
        )
        # Volume Calculation (Use actual value or estimate carefully)
        # Use abs() to ensure positive volume if bad math occurs
        volume = abs(living_area * 3)
        
        # Use actual parsed bedrooms if available, otherwise estimate
        bedrooms = ctx.get('bedrooms')
        if bedrooms:
            rooms_count = IntelligenceEngine._parse_int(bedrooms)
        else:
            rooms_count = max(3, int(living_area / 25))
        
        bathrooms = ctx.get('bathrooms', '?')
        property_type = ctx.get('property_type', 'Woonhuis')
        
        # Additional calculations for new metrics
        price_val = IntelligenceEngine._parse_int(
            ctx.get('asking_price_eur') or ctx.get('prijs') or '0'
        )
        price_m2 = round(price_val / living_area) if living_area else 0
        market_avg_m2 = ctx.get('avg_m2_price', 4800)
        label = ctx.get('energy_label') or ctx.get('label') or '?'
        reno_cost = 45000 if "F" in label or "G" in label else 25000 if "D" in label or "E" in label else 0
        construction_year = IntelligenceEngine._parse_int(
            ctx.get('build_year') or ctx.get('bouwjaar') or '0'
        )
        construction_alert = "Aandacht nodig" if construction_year < 1990 else "Relatief jong"
        
        # 3. Layout Construction (Modern Dashboard)
        hero = {
            "address": ctx.get('address') or ctx.get('adres', 'Adres Onbekend'),
            "price": ctx.get('asking_price_eur') or ctx.get('prijs', 'Prijs op aanvraag'),
            "status": "Woninginformatie",
            "labels": [property_type, f"{construction_year} Bouwjaar"]
        }


        # Determine semantic colors based on values
        living_area_color = "green" if living_area >= 120 else "orange" if living_area >= 80 else "red"
        living_area_explanation = "Ruim woonoppervlak" if living_area >= 120 else "Gemiddeld woonoppervlak" if living_area >= 80 else "Beperkt woonoppervlak"
        
        plot_area_color = "green" if plot_area >= 200 else "orange" if plot_area >= 100 else "blue"
        plot_area_explanation = "Ruim perceel" if plot_area >= 200 else "Gemiddeld perceel" if plot_area >= 100 else None
        
        bedrooms_color = "green" if rooms_count >= 4 else "orange" if rooms_count >= 3 else "red"
        bedrooms_explanation = "Voldoende slaapkamers" if rooms_count >= 4 else "Gemiddeld aantal kamers" if rooms_count >= 3 else "Beperkt aantal kamers"
        
        metrics = [
            {"id": "living", "label": "Woonoppervlakte", "value": f"{living_area} m²", "icon": "expand", "color": living_area_color, "explanation": living_area_explanation},
        ]
        
        # STRUCTURAL DYNAMISM: Only show plot if it's significant (house) or non-zero
        if plot_area > 10:
             metrics.append({"id": "plot", "label": "Perceeloppervlakte", "value": f"{plot_area} m²", "icon": "image", "color": plot_area_color, "explanation": plot_area_explanation})
        
        metrics.extend([
            {"id": "bedrooms", "label": "Slaapkamers", "value": f"{bedrooms or rooms_count}", "icon": "bed", "color": bedrooms_color, "explanation": bedrooms_explanation},
            {"id": "bathrooms", "label": "Badkamers", "value": f"{bathrooms}", "icon": "droplet", "color": "blue", "explanation": "Extra comfort" if str(bathrooms) > "1" else "Basisvoorziening"},
            {"id": "volume", "label": "Inhoud (est.)", "value": f"ca. {volume} m³", "icon": "cube", "trend": "neutral"},
        ])
        # New metrics (additive)
        if market_avg_m2:
            price_dev_pct = round(((price_m2 - market_avg_m2) / market_avg_m2) * 100)
            price_dev_color = "green" if price_dev_pct < -5 else "orange" if price_dev_pct <= 5 else "red"
            price_dev_explanation = "Onder marktprijs" if price_dev_pct < -5 else "Rond marktprijs" if price_dev_pct <= 5 else "Boven marktprijs"
            metrics.append({"id": "price_deviation", "label": "Prijsafwijking %", "value": f"{price_dev_pct:+,}%" if price_dev_pct != 0 else "0%", "icon": "trending-down" if price_dev_pct < 0 else "trending-up", "color": price_dev_color, "explanation": price_dev_explanation, "trend": "up" if price_dev_pct > 0 else "down" if price_dev_pct < 0 else "neutral", "trend_text": f"{price_dev_pct:+}% vs markt"})
        
        future_score = 80 if label in ["A","A+","A++","B"] else 60 if label in ["C","D"] else 40
        future_score_color = "green" if future_score >= 70 else "orange" if future_score >= 50 else "red"
        future_score_explanation = "Uitstekende energie-efficiëntie" if future_score >= 70 else "Gemiddelde energie-efficiëntie" if future_score >= 50 else "Lage energie-efficiëntie, renovatie nodig"
        metrics.append({"id": "energy_future", "label": "Energie Toekomstscore", "value": f"{future_score}", "icon": "leaf", "color": future_score_color, "explanation": future_score_explanation, "trend": "neutral"})
        
        maintenance = "Hoog" if reno_cost > 30000 else "Middelmatig" if reno_cost > 0 else "Laag"
        maintenance_color = "red" if reno_cost > 30000 else "orange" if reno_cost > 0 else "green"
        maintenance_explanation = f"Hoge onderhoudskosten verwacht (€{reno_cost:,})" if reno_cost > 30000 else f"Gemiddelde onderhoudskosten (€{reno_cost:,})" if reno_cost > 0 else "Lage onderhoudskosten verwacht"
        metrics.append({"id": "maintenance_intensity", "label": "Onderhoudsintensiteit", "value": maintenance, "icon": "hammer", "color": maintenance_color, "explanation": maintenance_explanation, "trend": "neutral"})
        
        family = "Geschikt" if living_area >= 120 and rooms_count >= 3 else "Beperkt geschikt"
        family_color = "green" if living_area >= 120 and rooms_count >= 3 else "orange"
        family_explanation = "Voldoende ruimte voor gezin" if living_area >= 120 and rooms_count >= 3 else "Beperkte ruimte voor groot gezin"
        metrics.append({"id": "family_suitability", "label": "Gezinsgeschiktheid", "value": family, "icon": "people", "color": family_color, "explanation": family_explanation, "trend": "neutral"})
        
        lt_quality = "Hoog" if construction_year >= 1990 else "Middelmatig" if construction_year >= 1970 else "Laag"
        lt_quality_color = "green" if construction_year >= 1990 else "orange" if construction_year >= 1970 else "red"
        lt_quality_explanation = "Moderne bouw, goede kwaliteit" if construction_year >= 1990 else "Oudere bouw, aandacht nodig" if construction_year >= 1970 else "Oude bouw, mogelijk grote renovatie nodig"
        metrics.append({"id": "long_term_quality", "label": "Lange-termijn kwaliteit", "value": lt_quality, "icon": "shield", "color": lt_quality_color, "explanation": lt_quality_explanation, "trend": "neutral"})
        
        
        main_content = self._render_rich_narrative(narrative)
        
        specs_card = {
            "type": "advisor_card", 
            "title": "Object Paspoort",
            "content": f"""
            <ul class="specs-list">
            <li><strong>Soort:</strong> {property_type}</li>
            <li><strong>Bouwtype:</strong> {ctx.get('construction_type', 'Onbekend')}</li>
            <li><strong>Bouwjaar:</strong> {construction_year}</li>
            <li><strong>Energielabel:</strong> {label}</li>
            <li><strong>Verwarming:</strong> {ctx.get('heating', 'Onbekend')[:50]}...</li>
            <li><strong>Isolatie:</strong> {ctx.get('insulation', 'Onbekend')}</li>
            <li><strong>Garage:</strong> {ctx.get('garage', 'Onbekend')}</li>
            </ul>
            """
        }
        
        # CONTEXTUAL WIDGETS
        advisor_title = "Makelaars Blik"
        advisor_content = "Een ruime woning met veel mogelijkheden. Controleer altijd de NEN2580 meetrapporten."
        
        if construction_year < 1980:
            advisor_title = "Renovatie Advies"
            advisor_content = "Gezien de leeftijd is een bouwkundige keuring sterk aanbevolen. Let op isolatie en leidingwerk."
        elif property_type.lower() == "appartement":
            advisor_title = "VvE Check"
            advisor_content = "Controleer de VvE-stukken: notulen, meerjarenonderhoudsplan (MJOP) en reservefonds."

        sidebar_advisor = {
            "type": "advisor",
            "title": advisor_title,
            "content": advisor_content,
        }

        # Left sidebar: Space-focused metrics
        left_sidebar = [
            {
                "type": "highlight_card",
                "icon": "home",
                "title": "Woningtype",
                "content": f"{property_type} uit {construction_year}"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Algemene Kenmerken", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [specs_card, sidebar_advisor]
        }

        return ChapterOutput(
            title="1. Algemene Woningkenmerken",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative # Populate chapter data for tests and reuse
        )
