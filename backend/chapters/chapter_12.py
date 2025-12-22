
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine

class AdviceConclusion(BaseChapter):
    def get_title(self) -> str:
        return "Advies & Conclusie"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(12, ctx)
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": "Eindoordeel",
            "status": "Samenvatting",
            "labels": ["Koopadvies", "Strategie"]
        }
        
        main_content = self._render_rich_narrative(narrative)
        
        # Calculate dynamic final score and risk
        fit_score = IntelligenceEngine.calculate_fit_score(ctx)
        
        # Energy label based risk
        label = ctx.get('label', 'G').upper()
        energy_risk = "Hoog" if label in ["F", "G"] else "Middel" if label in ["D", "E"] else "Laag"
        risk_color = "red" if energy_risk == "Hoog" else "orange" if energy_risk == "Middel" else "green"
        
        # Action recommendation
        action = "Bezichtig" if fit_score > 0.6 else "Heroverweeg"
        
        metrics = [
            {"id": "final", "label": "Totaalscore", "value": f"{int(fit_score*10 + 2)}/10", "icon": "trophy", "color": "blue", "explanation": "Goede investering" if fit_score > 0.6 else "Gemiddeld"},
            {"id": "risk", "label": "Risico (Energie)", "value": energy_risk, "icon": "shield-checkmark", "color": risk_color, "explanation": "Impact op waarde"},
            {"id": "action", "label": "Actie", "value": action, "icon": "walk", "color": "blue", "explanation": "Volgende stap"},
            {"id": "bid", "label": "Bieding", "value": "Individueel", "icon": "cash", "color": "orange", "explanation": "Zie strategie"}
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
        maintenance = "Hoog" if reno_cost>30000 else "Middelmatig" if reno_cost>0 else "Laag"
        metrics.append({"id":"maintenance_intensity","label":"Onderhoud","value":maintenance,"icon":"hammer","trend":"neutral", "color": "red" if reno_cost > 30000 else "green"})
        family = "Geschikt voor gezin" if (IntelligenceEngine._parse_int(ctx.get('oppervlakte','0')) or 0) >= 120 else "Minder geschikt voor groot gezin"
        metrics.append({"id":"family_suitability","label":"Gezinsgeschiktheid","value":family,"icon":"people","trend":"neutral"})
        lt_quality = "Hoog" if "jong" in construction_alert.lower() else "Middelmatig" if "aandacht" in construction_alert.lower() else "Laag"
        metrics.append({"id":"long_term_quality","label":"Lange-termijn kwaliteit","value":lt_quality,"icon":"shield","trend":"neutral"})
        
        # Left sidebar: Final recommendation
        left_sidebar = [
             {
                "type": "highlight_card",
                "icon": "checkmark-circle",
                "title": "Aanbeveling",
                "content": "Deze woning verdient nadere inspectie"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Eindconclusie", "content": main_content},
            "left_sidebar": left_sidebar,
            "sidebar": [{"type": "advisor_card", "title": "Vervolgstappen", "style": "gradient", "content": "1. Bezichtigen 2. Documenten 3. Bieden"}]
        }

        return ChapterOutput(
            title="12. Advies & Conclusie",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative
        )
