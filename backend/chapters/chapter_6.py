
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class MaintenanceFinish(BaseChapter):
    def get_title(self) -> str:
        return "Onderhoud & Afwerking"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(6, ctx)
        year = IntelligenceEngine._parse_int(ctx.get('bouwjaar', '2000')) or 2000
        state_score = "Voldoende"
        if year > 2010: state_score = "Uitstekend"
        elif year < 1980: state_score = "Aandacht nodig"
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": "Onderhoudsstaat",
            "status": state_score,
            "labels": ["Materialen", "Afwerking"]
        }
        
        metrics = [
            {"id": "paint", "label": "Schilderwerk", "value": "Check", "icon": "brush"},
            {"id": "floor", "label": "Vloeren", "value": "Staat?", "icon": "albums"},
            {"id": "kitchen", "label": "Keuken", "value": "Functioneel", "icon": "restaurant"},
            {"id": "bath", "label": "Sanitair", "value": "Basis", "icon": "water"}
        ]
        # New metrics (additive)
        price_val = IntelligenceEngine._parse_int(ctx.get('prijs') or ctx.get('asking_price_eur'))
        price_m2 = round(price_val / (IntelligenceEngine._parse_int(ctx.get('oppervlakte','0')) or 1))
        market_avg_m2 = ctx.get('avg_m2_price', 4800)
        label = ctx.get('label','?')
        reno_cost = 45000 if "F" in label or "G" in label else 25000 if "D" in label or "E" in label else 0
        construction_year = IntelligenceEngine._parse_int(ctx.get('bouwjaar') or ctx.get('build_year'))
        construction_alert = "Aandacht nodig" if construction_year < 1990 else "Relatief jong"
        if market_avg_m2:
            price_dev_pct = round(((price_m2 - market_avg_m2) / market_avg_m2) * 100)
            metrics.append({"id":"price_deviation","label":"Prijsafwijking %","value":f"{price_dev_pct:+,}%" if price_dev_pct != 0 else "0%","icon":"trend-up" if price_dev_pct>0 else "trend-down" if price_dev_pct<0 else "neutral","trend":"up" if price_dev_pct>0 else "down" if price_dev_pct<0 else "neutral","trend_text":f"{price_dev_pct:+}% vs markt"})
        future_score = 80 if label in ["A","A+","A++","B"] else 60 if label in ["C","D"] else 40
        metrics.append({"id":"energy_future","label":"Energie Toekomstscore","value":f"{future_score}","icon":"leaf","color":"green" if future_score>=70 else "orange" if future_score>=50 else "red","trend":"neutral"})
        maintenance = "Hoog" if reno_cost>30000 else "Middelmatig" if reno_cost>0 else "Laag"
        metrics.append({"id":"maintenance_intensity","label":"Onderhoudsintensiteit","value":maintenance,"icon":"hammer","trend":"neutral"})
        family = "Geschikt voor gezin" if (IntelligenceEngine._parse_int(ctx.get('oppervlakte','0')) or 0) >= 120 else "Minder geschikt voor groot gezin"
        metrics.append({"id":"family_suitability","label":"Gezinsgeschiktheid","value":family,"icon":"people","trend":"neutral"})
        lt_quality = "Hoog" if "jong" in construction_alert.lower() else "Middelmatig" if "aandacht" in construction_alert.lower() else "Laag"
        metrics.append({"id":"long_term_quality","label":"Lange-termijn kwaliteit","value":lt_quality,"icon":"shield","trend":"neutral"})
        
        main_content = self._render_rich_narrative(narrative, extra_html=f"""
        <table class="simple-table">
            <thead><tr><th>Onderdeel</th><th>Verwachte Staat</th><th>Actie</th></tr></thead>
            <tbody>
                <tr><td>Kozijnen</td><td>{"Kunststof/Alu (goed)" if year > 1990 else "Hout (check houtrot)"}</td><td>Inspectie</td></tr>
                <tr><td>Keukenapparatuur</td><td>Afschrijving 10-15 jr</td><td>Testen</td></tr>
                <tr><td>Wandafwerking</td><td>Esthetisch</td><td>Schilderen</td></tr>
            </tbody>
        </table>
        """)
        
        # Left sidebar: Maintenance state
        left_sidebar = [
            {
                "type": "key_facts",
                "title": "Onderhoudsstaat",
                "facts": [
                    {"label": "Bouwjaar", "value": str(year)},
                    {"label": "Algemene staat", "value": state_score},
                    {"label": "Verwachte kosten", "value": "€ 5.000-15.000"}
                ]
            },
            {
                "type": "highlight_card",
                "icon": "hammer" if state_score == "Aandacht nodig" else "checkmark-circle",
                "title": "Onderhoud Prioriteit",
                "content": f"{'Directe aandacht vereist' if state_score == 'Aandacht nodig' else 'Regulier onderhoud volstaat' if state_score == 'Voldoende' else 'Minimaal onderhoud verwacht'}"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Afwerkingsniveau", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [{"type": "advisor", "title": "Checklist", "content": "Kijk naar vochtplekken en scheurvorming bij bezichtiging."}]
        }

        return ChapterOutput(
            title="6. Onderhoud & Afwerking",
            grid_layout=layout, 
            blocks=[]
        )
