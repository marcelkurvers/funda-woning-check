
from typing import List, Dict, Any
from chapters.base import BaseChapter
from domain.models import ChapterOutput, UIComponent
from intelligence import IntelligenceEngine
import re

class FinancialAnalysis(BaseChapter):
    def get_title(self) -> str:
        return "Financiële Analyse"

    def generate(self) -> ChapterOutput:
        ctx = self.context
        narrative = IntelligenceEngine.generate_chapter_narrative(10, ctx)
        
        price_raw = str(ctx.get('prijs', '0'))
        price_digits = re.sub(r'[^\d]', '', price_raw)
        price_val = int(price_digits) if price_digits else 0
        
        kk_costs = int(price_val * 0.02)
        notary = 1500
        makelaar = int(price_val * 0.015)
        total_acquisition = price_val + kk_costs + notary + makelaar
        
        hero = {
            "address": ctx.get('adres', 'Adres Onbekend'),
            "price": f"€ {price_val:,}",
            "status": "Vraagprijs",
            "labels": ["Kosten Koper", "Financiering"]
        }
        
        metrics = [
            {"id": "price", "label": "Vraagprijs", "value": f"€ {price_val:,}", "icon": "pricetag", "color": "blue", "explanation": "Kosten Koper excl."},
            {"id": "kk", "label": "Kosten Koper", "value": f"€ {(kk_costs+notary+makelaar):,}", "icon": "wallet", "color": "orange", "explanation": "Overdracht, Notaris, etc."},
            {"id": "total", "label": "Totaal Benodigd", "value": f"€ {total_acquisition:,}", "icon": "cash", "color": "blue", "explanation": "Indicatie investering"},
            {"id": "monthly", "label": "Maandlast", "value": f"€ {int(total_acquisition * 0.04 / 12):,}", "icon": "calendar", "color": "green", "explanation": "Bruto/mnd (indicatie)"}
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
        
        breakdown_html = self._render_rich_narrative(narrative, extra_html=f"""
        <div class="grid grid-cols-1 gap-0 bg-slate-50 rounded-xl overflow-hidden border border-slate-200">
            <div class="flex justify-between items-center p-4 border-b border-slate-200">
                <span class="text-slate-600">Overdrachtsbelasting</span>
                <span class="font-medium text-slate-800">€ {kk_costs:,}</span>
            </div>
            <div class="flex justify-between items-center p-4 border-b border-slate-200">
                <span class="text-slate-600">Notaris (geschat)</span>
                <span class="font-medium text-slate-800">€ {notary:,}</span>
            </div>
            <div class="flex justify-between items-center p-4 border-b border-slate-200">
                <span class="text-slate-600">Makelaar / Advies</span>
                <span class="font-medium text-slate-800">€ {makelaar:,}</span>
            </div>
            <div class="flex justify-between items-center p-4 bg-slate-100">
                <span class="font-bold text-slate-800">Totaal K.K.</span>
                <span class="font-bold text-blue-600">€ {(kk_costs+notary+makelaar):,}</span>
            </div>
        </div>
        """)

        # Left sidebar: Cost breakdown
        left_sidebar = [
             {
                "type": "highlight_card",
                "icon": "cash",
                "title": "Totaal Benodigd",
                "content": f"€ {total_acquisition:,}"
            }
        ]
        
        layout = {
            "layout_type": "modern_dashboard",
            "hero": hero,
            "metrics": metrics,
            "main": {"title": "Kostenanalyse", "content": breakdown_html},
            "left_sidebar": left_sidebar,
            "sidebar": [
                {"type": "advisor", "title": "Biedingsadvies", "content": f"Overweeg een bod rond € {int(price_val*0.95):,}.", "style": "gradient"}
            ]
        }
        
        return ChapterOutput(
            title="10. Financiële Analyse",
            grid_layout=layout, 
            blocks=[],
            chapter_data=narrative
        )
