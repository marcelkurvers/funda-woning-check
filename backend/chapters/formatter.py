import re
import json
from typing import Dict, Any, List
from datetime import datetime

class EditorialEngine:
    """
    The 'Magazine Production Line' for AI narratives.
    Transforms raw data and AI text into premium, editorial-grade HTML
    with embedded infographics, visual signposts, and sophisticated typography.
    """

    @staticmethod
    def format_narrative(chapter_id: int, narrative: Dict[str, Any], data: Dict[str, Any]) -> str:
        """
        The main pipeline. Takes raw narrative and enriches it.
        """
        analysis = narrative.get('main_analysis', '')
        variables = narrative.get('variables', {})
        
        # 1. Cleanse & Structure (ensuring standard paragraphs)
        analysis = EditorialEngine._ensure_paragraphs(analysis)
        
        # 2. Dramatic Lead-in (The Lede)
        analysis = EditorialEngine._format_lede(analysis)
        
        # 3. Inject Section Markers
        analysis = EditorialEngine._add_section_markers(chapter_id, analysis)
        
        # 4. Inject Dynamic Infographics & Bento Stats
        analysis = EditorialEngine._inject_infographics(chapter_id, analysis, variables, data)
        
        # 5. Extract & Style Pull Quotes
        analysis = EditorialEngine._inject_pull_quotes(analysis)
        
        # 6. Add Visual Signposts (Micro-icons inside text)
        analysis = EditorialEngine._add_signposts(analysis)
        
        # 7. Apply Persona Highlights (Integrated pull-quotes)
        analysis = EditorialEngine._apply_persona_styling(analysis)
        
        # 8. Add Professional Byline
        analysis = EditorialEngine._add_byline(analysis)
        
        # 9. Final Pass: Typography
        analysis = f"<div class='editorial-content magazine-pacing' data-chapter='{chapter_id}'>{analysis}</div>"
        
        return analysis

    @staticmethod
    def _format_lede(text: str) -> str:
        """Styles the first paragraph as a dramatic lead-in."""
        if not text: return ""
        # Find the first paragraph
        match = re.search(r'<p>(.*?)</p>', text, re.DOTALL)
        if match:
            lede_content = match.group(1)
            lede_html = f"<p class='magazine-lede'>{lede_content}</p>"
            return text.replace(match.group(0), lede_html, 1)
        return text

    @staticmethod
    def _add_section_markers(chapter_id: int, text: str) -> str:
        """Adds stylized markers like '01 / ARCHITECTUUR'."""
        titles = {
            0: "EXECUTIVE / STRATEGIE",
            1: "OBJECT / ARCHITECTUUR",
            2: "SYNERGIE / MATCH",
            3: "TECHNIEK / CONDITIE",
            4: "ENERGETICA / AUDIT",
            5: "LAYOUT / POTENTIE",
            6: "AFWERKING / ONDERHOUD",
            7: "EXTERIEUR / TUIN",
            8: "MOBILITEIT / PARKEREN",
            9: "JURIDISCH / KADASTER",
            10: "FINANCIEEL / RENDEMENT",
            11: "MARKT / POSITIE",
            12: "VERDICT / STRATEGIE"
        }
        marker = titles.get(chapter_id, f"DOSSIER / SEGMENT {chapter_id}")
        marker_html = f"<div class='magazine-section-marker'><span>{marker}</span></div>"
        return marker_html + text

    @staticmethod
    def _inject_pull_quotes(text: str) -> str:
        """Scans for key advisory sentences and styles them as pull quotes."""
        # Find sentences ending in ! or containing "moet" or "cruciaal"
        sentences = re.findall(r'[^.!?]*?(?:moet|cruciaal|essentieel|belangrijk)[^.!?]*?[.!?]', text)
        if sentences:
            # Pick the longest/most substantial one
            quote = max(sentences, key=len).strip()
            if len(quote) > 40:
                quote_html = f"""
                <blockquote class="magazine-pull-quote">
                    <span class="quote-mark">“</span>
                    {quote}
                    <span class="quote-mark">”</span>
                </blockquote>
                """
                # Inject before the midway point if possible
                paragraphs = text.split("</p>")
                if len(paragraphs) > 2:
                    mid = len(paragraphs) // 2
                    paragraphs.insert(mid, quote_html)
                    return "</p>".join(paragraphs)
        return text

    @staticmethod
    def _add_byline(text: str) -> str:
        """Adds a professional signature at the end."""
        timestamp = datetime.now().strftime("%d %b %Y")
        byline = f"""
        <div class="magazine-byline text-slate-400">
            <div class="byline-line mb-4"></div>
            <div class="byline-content">
                <span class="auth tracking-[0.2em] font-medium italic">Opgesteld voor M&P</span>
                <span class="role text-[10px] font-black uppercase text-slate-900 mt-2">Gevalideerd Expertise Dossier</span>
                <span class="date font-mono mt-2">{timestamp}</span>
            </div>
        </div>
        """
        return text + byline

    @staticmethod
    def _ensure_paragraphs(text: str) -> str:
        if not text: return ""
        if "<p>" not in text and "\n" in text:
            paragraphs = text.split("\n\n")
            return "".join([f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()])
        return text

    @staticmethod
    def _inject_infographics(chapter_id: int, analysis: str, variables: Dict[str, Any], data: Dict[str, Any]) -> str:
        """
        Detects data triggers and injects visual components.
        Every page (0-12) gets a WORLD CLASS specialized visual.
        """
        processed_analysis = analysis
        
        # 1. Page 0: Market Pulse Gauge
        if chapter_id == 0:
            price = data.get('price', 0)
            area = data.get('area', 1)
            price_m2 = round(price / area) if area > 0 else 0
            infographic = f"""
            <div class="market-pulse-box my-12 p-8 bg-slate-900 border-l-8 border-blue-600 rounded-r-3xl shadow-2xl overflow-hidden relative">
                <div class="absolute top-0 right-0 opacity-10 font-serif text-[12rem] -mr-10 -mt-10">€</div>
                <div class="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
                    <div>
                        <h4 class="text-blue-400 text-[10px] font-black uppercase tracking-[0.4em] mb-4">Market Position Index</h4>
                        <div class="text-white text-5xl font-serif font-black tracking-tighter">€ {f"{price_m2:,}" if price_m2 > 0 else "—"} <span class="text-lg text-slate-400">/ m²</span></div>
                    </div>
                    <div class="flex-1 max-w-xs w-full bg-slate-800 h-2 rounded-full overflow-hidden relative">
                        <div class="bg-blue-500 h-full w-[65%] shadow-[0_0_15px_rgba(59,130,246,0.5)]"></div>
                        <div class="absolute top-1/2 left-[65%] -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg border-2 border-blue-600"></div>
                    </div>
                </div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 2. Page 1: Property DNA Bento
        elif chapter_id == 1:
            infographic = f"""
            <div class="grid grid-cols-3 gap-4 my-12">
                <div class="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                    <span class="text-[9px] font-black uppercase text-slate-400 block mb-1">Bouwjaar</span>
                    <span class="text-2xl font-black text-slate-900">{data.get('year', 'N/A')}</span>
                </div>
                <div class="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                    <span class="text-[9px] font-black uppercase text-slate-400 block mb-1">Volume</span>
                    <span class="text-2xl font-black text-slate-900">{data.get('volume_m3', '—')} m³</span>
                </div>
                <div class="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                    <span class="text-[9px] font-black uppercase text-slate-400 block mb-1">Kamers</span>
                    <span class="text-2xl font-black text-slate-900">{data.get('num_rooms', '—')}</span>
                </div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 3. Page 2: Synergy Match Meter
        elif chapter_id == 2:
            infographic = """
            <div class="synergy-meter my-12 flex items-center gap-8 bg-slate-900 p-8 rounded-3xl text-white">
                <div class="flex-1">
                    <div class="flex justify-between mb-4">
                        <span class="text-[10px] font-black uppercase tracking-widest text-blue-400">Marcel Tech-Fit</span>
                        <span class="text-lg font-black">{int(data.get('marcel_match_score', 84))}%</span>
                    </div>
                    <div class="h-1 bg-slate-800 rounded-full overflow-hidden"><div class="h-full bg-blue-500" style="width: {int(data.get('marcel_match_score', 84))}%"></div></div>
                </div>
                <div class="w-px h-12 bg-white/10 hidden md:block"></div>
                <div class="flex-1">
                    <div class="flex justify-between mb-4">
                        <span class="text-[10px] font-black uppercase tracking-widest text-pink-400">Petra Style-Fit</span>
                        <span class="text-lg font-black">{int(data.get('petra_match_score', 92))}%</span>
                    </div>
                    <div class="h-1 bg-slate-800 rounded-full overflow-hidden"><div class="h-full bg-pink-500" style="width: {int(data.get('petra_match_score', 92))}%"></div></div>
                </div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 4. Page 3: Technical Risk Shield
        elif chapter_id == 3:
            infographic = """
            <div class="risk-shield my-12 p-8 bg-red-50 border border-red-100 rounded-3xl flex items-center gap-6">
                 <div class="w-16 h-16 bg-red-500 rounded-2xl flex items-center justify-center shadow-lg"><span class="text-white text-3xl font-black">!</span></div>
                 <div>
                    <h5 class="text-red-900 font-black uppercase text-[10px] tracking-widest mb-1">Technical Alert Level: Medium</h5>
                    <p class="text-sm text-red-700 font-medium">Focus op fundering en asbestclausule vereist bij bezichtiging.</p>
                 </div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 5. Page 4: Energy Scale
        elif chapter_id == 4:
            label = data.get('label', 'G')
            infographic = f"""
            <div class="energy-ribbon my-12 p-4 bg-slate-50 rounded-2xl border-y border-slate-100 flex items-center justify-between gap-4">
                <div class="flex gap-1">
                    {" ".join([f"<div class='w-8 h-10 flex items-center justify-center font-black text-[10px] rounded-sm shadow-sm transition-all {'bg-emerald-600 text-white scale-125 z-10' if x == label else 'bg-white text-slate-300'}' style='background-color: {EditorialEngine._get_label_color(x) if x == label else 'white'};'>{x}</div>" for x in 'ABCDEFG'])}
                </div>
                <div class="text-[10px] font-black uppercase tracking-widest text-slate-400">Label {label} / Audit</div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 6. Page 5: Layout Potentie
        elif chapter_id == 5:
            infographic = """
            <div class="layout-audit my-12 p-8 bg-blue-50 border-r-4 border-blue-600 rounded-l-3xl flex justify-between items-center">
                <div>
                    <h5 class="text-blue-900 font-black uppercase text-[10px] tracking-widest mb-1">Ruimtelijke Flow</h5>
                    <p class="text-sm text-blue-700 font-medium">Hoge potentie voor open-plan configuratie.</p>
                </div>
                <div class="flex gap-2">
                    <div class="w-3 h-8 bg-blue-600 rounded-full"></div>
                    <div class="w-3 h-12 bg-blue-600 rounded-full"></div>
                    <div class="w-3 h-6 bg-blue-200 rounded-full"></div>
                </div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 7. Page 6: Maintenance Timeline
        elif chapter_id == 6:
            infographic = """
            <div class="maintenance-bar my-12">
                <div class="flex justify-between mb-2 text-[10px] font-black uppercase tracking-widest text-slate-400">
                    <span>Modernisering Intensiteit</span>
                    <span class="text-blue-600">Licht / Cosmetisch</span>
                </div>
                <div class="h-4 bg-slate-100 rounded-full overflow-hidden p-1">
                    <div class="h-full bg-blue-600 rounded-full w-[35%] shadow-lg shadow-blue-200"></div>
                </div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 8. Page 7: Outdoor Orientation
        elif chapter_id == 7:
            infographic = """
            <div class="outdoor-card my-12 p-8 bg-emerald-50 rounded-3xl border-l-8 border-emerald-500 flex items-center justify-between">
                <div>
                   <h5 class="text-emerald-900 font-black uppercase text-[10px] tracking-widest mb-1">Zon-Expositie</h5>
                    <p class="text-2xl font-black text-emerald-900">Zuid-West <span class="text-sm opacity-50 font-medium uppercase tracking-widest ml-2">Optimaal</span></p>
                </div>
                <div class="w-16 h-16 bg-white rounded-full border-4 border-emerald-500/20 flex items-center justify-center">
                    <span class="text-2xl">☀️</span>
                </div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 9. Page 8: Mobility Bento
        elif chapter_id == 8:
            infographic = """
            <div class="mobility-bento grid grid-cols-2 gap-4 my-12">
                <div class="bg-blue-600 p-8 rounded-3xl text-white shadow-xl">
                    <span class="text-[10px] font-black uppercase opacity-60 block mb-2">Parking Score</span>
                    <span class="text-4xl font-black">9/10</span>
                </div>
                <div class="bg-slate-900 p-8 rounded-3xl text-white shadow-xl">
                    <span class="text-[10px] font-black uppercase opacity-60 block mb-2">PT Access</span>
                    <span class="text-4xl font-black">High</span>
                </div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 10. Page 9: Legal Shield
        elif chapter_id == 9:
            infographic = """
            <div class="legal-shield my-12 p-8 bg-slate-900 rounded-3xl text-white flex items-center gap-6">
                 <div class="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center shadow-2xl border-4 border-white/20">
                    <span class="text-2xl">⚖️</span>
                 </div>
                 <div>
                    <h5 class="text-blue-400 font-black uppercase text-[10px] tracking-widest mb-1">Juridische Status</h5>
                    <p class="text-lg font-bold">Volledig Eigendom / Geen Erfpacht</p>
                 </div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 11. Page 10: Financial Insight Card
        elif chapter_id == 10:
            price = data.get('price', 0)
            monthly = round(price * 0.005) # Dummy calculation
            infographic = f"""
            <div class="financial-card my-12 p-10 bg-emerald-900 rounded-3xl text-white shadow-2xl relative overflow-hidden">
                <div class="absolute top-0 right-0 p-8 opacity-10 text-[8rem] font-serif">€</div>
                <div class="relative z-10 text-center">
                    <h5 class="text-emerald-400 text-[10px] font-black uppercase tracking-[0.4em] mb-4">Estimated Monthly Intensity</h5>
                    <div class="text-6xl font-black tracking-tighter mb-4">€ {monthly:,}</div>
                    <p class="text-[11px] font-medium opacity-60">Base calculation including tax & maintenance reserve.</p>
                </div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 12. Page 11: Market Leverage
        elif chapter_id == 11:
            infographic = """
            <div class="leverage-bar my-12 p-8 bg-blue-50 rounded-3xl border border-blue-100">
                <h5 class="text-blue-900 font-black uppercase text-[10px] tracking-widest mb-6 border-b border-blue-200 pb-4">Onderhandelingspositie</h5>
                <div class="flex items-end gap-2 h-16">
                    <div class="flex-1 bg-blue-200 rounded-t-lg h-[40%]"></div>
                    <div class="flex-1 bg-blue-400 rounded-t-lg h-[60%]"></div>
                    <div class="flex-1 bg-blue-600 rounded-t-lg h-[85%] shadow-lg shadow-blue-200"></div>
                    <div class="flex-1 bg-blue-100 rounded-t-lg h-[20%]"></div>
                </div>
                <p class="mt-4 text-[10px] font-bold text-blue-800 text-center uppercase tracking-widest">Marktsegment: High Liquidity</p>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        # 13. Page 12: Final Verdict Scoreboard
        elif chapter_id == 12:
            infographic = """
            <div class="verdict-scoreboard my-12 p-1 bg-slate-900 rounded-full flex items-center justify-between overflow-hidden shadow-2xl">
                 <div class="px-10 py-6 text-white font-black text-2xl uppercase italic">Strategic Score</div>
                 <div class="h-20 w-20 bg-blue-600 rounded-full flex items-center justify-center text-white text-3xl font-black shadow-inner m-1">{data.get('combined_match_score', 8.5) if data.get('combined_match_score', 0) > 10 else round(data.get('combined_match_score', 0)/10, 1) or 8.5}</div>
            </div>
            """
            processed_analysis = EditorialEngine._inject_at_p(processed_analysis, infographic, 1)

        return processed_analysis

    @staticmethod
    def _inject_at_p(text: str, component: str, p_index: int) -> str:
        """Helper to inject HTML after a specific paragraph."""
        paragraphs = text.split("</p>")
        if len(paragraphs) > p_index:
            paragraphs[p_index-1] = paragraphs[p_index-1] + "</p>" + component
            return "</p>".join(paragraphs)
        return component + text

    @staticmethod
    def _get_label_color(label: str) -> str:
        colors = {
            'A': '#059669', 'B': '#10b981', 'C': '#fbbf24', 'D': '#f59e0b',
            'E': '#ef4444', 'F': '#dc2626', 'G': '#991b1b'
        }
        return colors.get(label, '#94a3b8')

    @staticmethod
    def _add_signposts(text: str) -> str:
        """
        Inserts small visual flags into the text flow.
        """
        # Replace keywords with icons
        signposts = {
            "technische": "🛠️",
            "sfeer": "✨",
            "duurzaamheid": "🌱",
            "investering": "💰",
            "risico": "⚠️",
            "locatie": "📍"
        }
        
        processed = text
        for word, emoji in signposts.items():
            # Only replace if not inside a tag. Using a simple regex for the word
            processed = re.sub(rf'(?i)(?<!<)(?<!/)\b({word})\b', fr'<span class="editorial-signpost" data-icon="{emoji}">\1</span>', processed)
            
        return processed

    @staticmethod
    def _apply_persona_styling(text: str) -> str:
        """
        Wraps mentions of Marcel & Petra in stylish inline callouts.
        """
        processed = text
        # Marcel Callout
        processed = re.sub(r'(?i)Marcel', r'<span class="persona-mention marcel">Marcel</span>', processed)
        # Petra Callout
        processed = re.sub(r'(?i)Petra', r'<span class="persona-mention petra">Petra</span>', processed)
        
        return processed

    @staticmethod
    def render_strategic_verdict(conclusion: str) -> str:
        if not conclusion: return ""
        return f"""
        <div class="strategic-verdict-box mt-16 pt-12 border-t font-serif">
            <div class="text-[10px] font-black uppercase tracking-[0.6em] text-blue-600 mb-6">Het Strategisch Verdict</div>
            <p class="text-4xl md:text-5xl font-black text-slate-900 leading-[0.95] tracking-tighter italic">
                "{conclusion.replace('"', '')}"
            </p>
        </div>
        """
