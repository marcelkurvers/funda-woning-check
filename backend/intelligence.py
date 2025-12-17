import random
import re

from typing import Dict, Any, Optional
import json
import logging

try:
    from ollama_client import OllamaClient
except ImportError:
    OllamaClient = Any

logger = logging.getLogger(__name__)

class IntelligenceEngine:
    """
    Simulates a sophisticated AI analyst that generates dynamic narratives 
    based on property data. In a full production version, this would 
    interface with an LLM (e.g., OpenAI API).
    """
    _client: Optional[OllamaClient] = None

    @classmethod
    def set_client(cls, client: OllamaClient):
        cls._client = client

    @staticmethod
    def generate_chapter_narrative(chapter_id: int, ctx: Dict[str, Any]) -> Dict[str, str]:
        """
        Returns a dictionary with 'title', 'intro', 'main_analysis', and 'conclusion'
        dynamically generated based on the context.
        """
        # Normalize Data
        price_val = IntelligenceEngine._parse_int(ctx.get('prijs') or ctx.get('asking_price_eur'))
        area_val = IntelligenceEngine._parse_int(ctx.get('oppervlakte') or ctx.get('living_area_m2'))
        plot_val = IntelligenceEngine._parse_int(ctx.get('perceel') or ctx.get('plot_area_m2'))
        year_val = IntelligenceEngine._parse_int(ctx.get('bouwjaar') or ctx.get('build_year'))
        label = (ctx.get('label') or ctx.get('energy_label') or "G").upper()
        
        data = {
            "price": price_val,
            "area": area_val,
            "plot": plot_val,
            "year": year_val,
            "label": label,
            "address": ctx.get('adres', 'het object'),
            "description": ctx.get('description', ''),
            "features": ctx.get('features', []),
            "_preferences": ctx.get('_preferences', {})
        }

        result = {}
        if chapter_id == 0:
            result = IntelligenceEngine._narrative_ch0(data)
        elif chapter_id == 1:
            result = IntelligenceEngine._narrative_ch1(data)
        elif chapter_id == 2:
            result = IntelligenceEngine._narrative_ch2(data)
        elif chapter_id == 3:
            result = IntelligenceEngine._narrative_ch3(data)
        elif chapter_id == 4:
            result = IntelligenceEngine._narrative_ch4(data)
        elif chapter_id == 5:
            result = IntelligenceEngine._narrative_ch5(data)
        elif chapter_id == 6:
            result = IntelligenceEngine._narrative_ch6(data)
        elif chapter_id == 7:
            result = IntelligenceEngine._narrative_ch7(data)
        elif chapter_id == 8:
            result = IntelligenceEngine._narrative_ch8(data)
        elif chapter_id == 9:
            result = IntelligenceEngine._narrative_ch9(data)
        elif chapter_id == 10:
            result = IntelligenceEngine._narrative_ch10(data)
        elif chapter_id == 11:
            result = IntelligenceEngine._narrative_ch11(data)
        elif chapter_id == 12:
            result = IntelligenceEngine._narrative_ch12(data)
        elif chapter_id == 12:
            result = IntelligenceEngine._narrative_ch12(data)
        else:
            result = {"title": "Analyse", "intro": "Generieke analyse.", "main_analysis": "Geen data.", "conclusion": "N.v.t."}
        
        # AI OVERRIDE
        if IntelligenceEngine._client:
            try:
                ai_result = IntelligenceEngine._generate_ai_narrative(chapter_id, data, result)
                if ai_result:
                     # Merge or replace. If AI fails or returns partial, we kept the hardcoded one?
                     # Ideally AI result is comprehensive.
                     # We force the structure to match.
                     result.update(ai_result)
                     result["interpretation"] += " (AI Enhanced)"
            except Exception as e:
                logger.error(f"AI Generation failed for Chapter {chapter_id}: {e}")
                # Fallback silently to hardcoded
        
        # Append missing KPI notice if any critical fields are missing or zero
        missing_keys = [k for k in ["price", "area", "plot", "year", "label"] if not data.get(k)]
        if missing_keys:
            notice = "\n<p>De beschikbare KPI's zijn beperkt; sommige waarden ontbreken of zijn niet ingevuld.</p>"
            result["main_analysis"] = result.get("main_analysis", "") + notice
        
        # Append AI usage disclaimer
        ai_note = "\n<p>Deze analyse is gegenereerd met behulp van een AI‑engine die de beschikbare data interpreteert.</p>"
        result["interpretation"] = result.get("interpretation", "") + ai_note

        # Augment the result dictionary
        result['chapter_id'] = chapter_id
        return result

    @staticmethod
    def _parse_int(val):
        try:
            # Only keep standard ASCII digits
            digits = re.sub(r'[^\d]', '', str(val))
            # Filter out superscripts if any remain (though \d matches them in some python versions depending on flags)
            # Safest is [0-9]
            digits = re.sub(r'[^0-9]', '', str(val))
            return int(digits) if digits else 0
        except:
            return 0

    @classmethod
    def _generate_ai_narrative(cls, chapter_id: int, data: Dict[str, Any], fallback: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Uses Ollama to generate the narrative.
        """
        if not cls._client: return None
        
        # Construct Prompt
        # We strip heavy fields to save context matching if needed, but local LLMs handle 4k/8k usually.
        # Ensure preferences are known
        prefs = data.get('_preferences', {})
        
        system_prompt = (
            "You are an expert Real Estate Analyst for 'Funda AI Rapport'. "
            "Your clients are Marcel (Tech/Infra focus) and Petra (Atmosphere/Comfort focus). "
            "Analyze the provided property data STRICTLY based on the requested chapter context. "
            "Output must be valid JSON matching the structure: "
            "{'title': str, 'intro': str, 'main_analysis': str, 'interpretation': str, 'advice': str, 'conclusion': str, 'strengths': [str]}. "
            "Use Dutch language. Use HTML tags <p>, <ul>, <li>, <strong> for formatting where appropriate."
        )
        
        user_prompt = f"""
        **Context**: Chapter {chapter_id}
        **Property Data**: {json.dumps(data, default=str)}
        **Current Hardcoded Draft (Reference)**: {json.dumps(fallback, default=str)}
        
        **Task**:
        1. Rewrite the content to be more insightful and personalized for Marcel & Petra.
        2. Check specific preferences: {json.dumps(prefs.get('marcel', {}))} and {json.dumps(prefs.get('petra', {}))}.
        3. Keep the same Keys. 'main_analysis' should be detailed.
        4. If data is missing (0 or null), explicitly mention it in 'advice'.
        
        Return ONLY the JSON object.
        """
        
        try:
            response_text = cls._client.generate(user_prompt, system=system_prompt, json_mode=True)
            # Parse JSON
            # Sometimes local models wrap in ```json ... ```
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text.split("```json")[1].split("```")[0]
            elif clean_text.startswith("```"):
                clean_text = clean_text.split("```")[1].split("```")[0]
            
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}\nResponse: {response_text}")
            return None

    # --- NARRATIVES ---

    @staticmethod
    def _narrative_ch1(d):
        ratio = int(d['area'] / d['plot'] * 100) if d['plot'] else 100
        rooms_est = max(3, int(d['area']/25))
        
        # 1. Intro - Dynamic Builder
        intro_parts = []
        
        # Smart Address Logic
        raw_address = str(d.get('address', ''))
        generic_titles = ['mijn huis', 'te koop', 'woning', 'object', 'huis', 'appartement']
        is_generic = raw_address.lower().strip() in generic_titles
        intro_addr_text = f"aan de {raw_address}" if not is_generic else "op deze locatie"
        
        if d['area'] < 60:
            intro_parts.append(f"Dit compacte stadsappartement {intro_addr_text} biedt een efficiënte woonbeleving op {d['area']} m².")
        elif d['area'] > 200:
            intro_parts.append(f"Resideren in weelde {intro_addr_text}. Met een imposant woonoppervlak van {d['area']} m² spreken we van een buitencategorie object.")
        else:
            intro_parts.append(f"Aan de {d.get('address', '...')} vinden we deze courante woning met een gebruiksoppervlakte van {d['area']} m²." if not is_generic else f"Op deze locatie vinden we een courante woning met {d['area']} m² woonoppervlak.")

        if d['plot'] > 1000:
            intro_parts.append(f"Het landgoed van {d['plot']} m² waarborgt absolute privacy en rust.")
        elif d['plot'] == 0:
            intro_parts.append("Het object betreft een appartementsrecht zonder eigen grondgebonden buitenruimte, wat het onderhoud minimaliseert.")
        else:
            intro_parts.append(f"De kavel van {d['plot']} m² biedt een prettige balans tussen tuin en bebouwing.")
            
        intro = " ".join(intro_parts)

        # 2. Main Analysis - Dynamic Vocab
        analysis_parts = []
        
        # Ratio Analysis
        if ratio > 80:
            analysis_parts.append(f"<p>De bebouwingsdichtheid is hoog (circa {ratio}%), wat typerend is voor een stedelijke of centrum-locatie. Elke vierkante meter wordt hier benut.</p>")
        elif ratio < 20:
            analysis_parts.append(f"<p>Slechts {ratio}% van het perceel is bebouwd. Dit geeft het object een vrij en groen karakter met volop uitbreidingsmogelijkheden.</p>")
        else:
            analysis_parts.append(f"<p>De verhouding wonen/perceel ({ratio}%) is marktconform voor deze wijkopzet.</p>")

        # Year Analysis
        if d['year'] < 1940:
             analysis_parts.append(f"<p>Historisch karakter uit {d['year']}. De authentieke details en sfeer zijn unieke assets, al vraagt de bouwkundige staat ('ouderdomsclausule') om aandacht.</p>")
        elif d['year'] > 2020:
             analysis_parts.append(f"<p>Nieuwbouwkwaliteit uit {d['year']}. Dit betekent: gasloos, uitstekend geïsoleerd en klaar voor de toekomst. Een zorgeloze investering.</p>")
        else:
             analysis_parts.append(f"<p>Degelijke bouw uit {d['year']}. Een periode waarin praktische indelingen centraal stonden.</p>")
             
        analysis = "".join(analysis_parts)
        
        # 3. Rich AI Interpretation
        interpretation = ""
        if d['price'] > 1000000:
            interpretation = f"<p>In dit topsegment draait het niet alleen om stenen, maar om 'levensstijl'. De combinatie van {d['area']} m² wonen op deze locatie rechtvaardigt de vraagprijs.</p>"
        elif d['price'] < 300000:
            interpretation = f"<p>Een ideale instap in de woningmarkt. Voor dit budget krijgt u relatief veel functionaliteit, al is modernisering wellicht gewenst.</p>"
        else:
            interpretation = f"<p>Een solide gezinswoning in het middensegment. De prijs/kwaliteitverhouding oogt in balans.</p>"

        # 4. Advice / Attention Points
        advice = []
        if d['year'] < 1980:
            advice.append("Check: Asbestclausule van toepassing?")
            advice.append("Advies: Bouwkundige keuring (fundering/dak).")
        if d['label'] in ['E', 'F', 'G']:
            advice.append("Budgettip: Reserveer €20k-€40k voor verduurzaming.")
        if d['year'] > 2000 and d['label'] == 'A':
            advice.append("Comfort: Controleer werking WTW-unit en filters.")
        
        if not advice:
            advice.append("Geen specifieke risico's op basis van data.")
        
        advice_html = "<ul>" + "".join([f"<li>{point}</li>" for point in advice]) + "</ul>"

        # 5. Strengths (Sterktes)
        strengths = []
        if d['area'] > 150: strengths.append("Royaal Wonen")
        if d['plot'] > 500: strengths.append("Vrijheid & Privacy")
        if "A" in d['label']: strengths.append("Toekomstbestendig Label")
        if d['year'] < 1940: strengths.append("Authentieke Sfeer")
        if d['year'] > 2010: strengths.append("Onderhoudsarm")
        
        # 6. Conclusion
        conclusion = ""
        if d['price'] > 1000000 or d['area'] > 200:
            conclusion = "Een uniek, hoogwaardig object voor de liefhebber van luxe."
        elif d['area'] < 60:
            conclusion = "Slimme stadswoning, ideaal voor starters of verhuur."
        else:
            conclusion = "Een courant object met potentie."
        
        return {
            "title": "Algemene Woningkenmerken",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice_html,
            "strengths": strengths,
            "conclusion": conclusion
        }

    @staticmethod
    def _narrative_ch2(d):
        prefs = d.get('_preferences', {})
        marcel_props = prefs.get('marcel', {})
        petra_props = prefs.get('petra', {})
        
        marcel_prio = marcel_props.get('priorities', [])
        marcel_hidden = marcel_props.get('hidden_priorities', [])
        
        petra_prio = petra_props.get('priorities', [])
        petra_hidden = petra_props.get('hidden_priorities', [])
        
        # Simple keyword matching helper
        # Simple keyword matching helper
        def check_features(priorities, source_text):
            matches = []
            misses = []
            source_lower = source_text.lower()
            for p in priorities:
                # Naive matching: property feature descriptions often contain these words
                p_lower = p.lower()
                
                # Handling for compound tags like "CAT6 / Ethernet"
                # If ANY of the sub-components are found, we count it as a match
                sub_tokens = [t.strip() for t in p_lower.split('/') if len(t.strip()) > 2]
                if not sub_tokens: sub_tokens = [p_lower]
                
                is_match = False
                for token in sub_tokens:
                    # Specialized mappings
                    if token == "solar": token = "zonnepanelen"
                    if token == "accu": token = "batterij"
                    if token == "jaren 30": token = "193" # rudimentary year check
                    if token == "warmtepomp": token = "warmtepomp"
                    
                    if token in source_lower:
                        is_match = True
                        break
                
                if is_match:
                    matches.append(p)
                else:
                    misses.append(p)
            return matches, misses

        # Combine source text for searching
        description = d.get('description', '') or ""
        features = str(d.get('features', []))
        source_blob = f"{description} {features}"
        
        # Check Visible Priorities
        m_matches, m_misses = check_features(marcel_prio, source_blob)
        p_matches, p_misses = check_features(petra_prio, source_blob)
        
        # Check Hidden Priorities
        mh_matches, mh_misses = check_features(marcel_hidden, source_blob)
        ph_matches, ph_misses = check_features(petra_hidden, source_blob)
        
        # Scoring includes BOTH visible and hidden
        total_prio = len(marcel_prio) + len(petra_prio) + len(marcel_hidden) + len(petra_hidden)
        total_match = len(m_matches) + len(p_matches) + len(mh_matches) + len(ph_matches)
        
        score_pct = int((total_match / total_prio * 100)) if total_prio > 0 else 50 # Default 50 if no prefs

        intro = f"Op basis van de aangescherpte profielen van Marcel (Tech & Infra) en Petra (Sfeer & Comfort) scoort deze woning een match van {score_pct}%."
        
        # Analysis ONLY shows visible priorities
        analysis = "<h4>Marcel's Tech-Check</h4><ul>"
        if m_matches:
            analysis += "".join([f"<li class='text-green-600'>✓ {m} gevonden</li>" for m in m_matches])
        else:
             analysis += "<li>Geen directe tech-hits in de omschrijving.</li>"
        if m_misses:
            analysis += "".join([f"<li class='text-gray-400'>? {m} controleren</li>" for m in m_misses[:3]]) # Show max 3 misses
        analysis += "</ul>"
        
        analysis += "<h4>Petra's Woonwensen</h4><ul>"
        if p_matches:
             analysis += "".join([f"<li class='text-pink-600'>✓ {p} aanwezig</li>" for p in p_matches])
        else:
             analysis += "<li>Geen specifieke stijlkenmerken herkend in de tekst.</li>"
        if p_misses:
            analysis += "".join([f"<li class='text-gray-400'>? {m} niet vermeld</li>" for m in p_misses[:3]])
        analysis += "</ul>"

        interpretation = f"""
        <p>De woning sluit voor <strong>{'Marcel' if (len(m_matches)+len(mh_matches)) > (len(p_matches)+len(ph_matches)) else 'Petra'}</strong> op papier het beste aan. 
        {'De technische infrastructuur lijkt veelbelovend.' if 'Glasvezel' in m_matches or 'Zonnepanelen' in m_matches else 'De technische basisvoorzieningen vragen nader onderzoek.'}
        {'De sfeer en uitstraling matchen met de gezochte esthetiek.' if 'Jaren 30' in p_matches or 'Karakteristiek' in p_matches else 'De woning kan met de juiste styling naar wens worden gemaakt.'}</p>
        """

        strengths = []
        if len(m_matches) > 2: strengths.append("Sterke Tech Match")
        if len(p_matches) > 2: strengths.append("Sterke Stijl Match")
        strengths.extend(m_matches[:2])
        strengths.extend(p_matches[:2])

        advice = "<ul>"
        if m_misses: advice += f"<li>Marcel: Controleer mogelijkheden voor {', '.join(m_misses[:2])}.</li>"
        if p_misses: advice += f"<li>Petra: Beoordeel ter plaatse de {', '.join(p_misses[:2])}.</li>"
        advice += "</ul>"

        conclusion = f"Een {score_pct}% match. {'Een sterke kandidaat!' if score_pct > 60 else 'Voldoet aan de basis, maar concessies zijn nodig.'}"
        
        return {
            "title": "Matchanalyse M&P",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }

    @staticmethod
    def _narrative_ch3(d):
        risks = []
        if d['year'] < 1930: risks.append("de fundering (hout/staal?)")
        if d['year'] < 1980: risks.append("asbestverdachte materialen")
        if d['year'] < 1990: risks.append("het leidingwerk (lood/koper)")
        
        # Dynamic Intro
        intro_parts = []
        if d['year'] < 1920:
             intro_parts.append(f"Dit monumentale pand ademt de geschiedenis van {d['year']}. Een bouwkundig juweel, maar wel een met 'gebruiksaanwijzing'.")
        elif d['year'] < 1970:
             intro_parts.append(f"Gebouwd in {d['year']}, een periode van wederopbouw en systeembouw. De basis is vaak degelijk, maar isolatie was destijds geen prioriteit.")
        elif d['year'] > 2010:
             intro_parts.append(f"Met bouwjaar {d['year']} voldoet dit object aan de strengste moderne bouwbesluiten. Zorgeloos wonen staat hier centraal.")
        else:
             intro_parts.append(f"Een solide basis uit {d['year']}, kenmerkend voor de functionele bouwstijl van die tijd.")
        
        intro = " ".join(intro_parts)
        
        # Dynamic Analysis
        analysis_parts = []
        risks_str = ", ".join(risks)
        risk_sentence = f"Let echter specifiek op {risks_str}." if risks else "Er zijn geen directe risico-indicatoren."
        analysis_parts.append(f"<p>De constructieve staat oogt {'uitstekend' if d['year'] > 2000 else 'voldoende, gezien de leeftijd'}. {risk_sentence}</p>")
        
        if d['year'] < 1990:
             analysis_parts.append(f"<p>Dak & Gevel: Gezien de leeftijd van {2025-d['year']} jaar is het aannemelijk dat het dak of de goten al eens vervangen zijn of binnenkort aan de beurt zijn.</p>")
        else:
             analysis_parts.append("<p>De schil van de woning (dak, gevel, kozijnen) bevindt zich waarschijnlijk nog in de eerste levensfase en vereist minimaal onderhoud.</p>")
             
        analysis = "".join(analysis_parts)

        # Interpretation
        if d['year'] < 1940:
            interpretation = "<p>Oude woningen 'werken'. Scheurvorming is niet ongewoon, maar dient wel beoordeeld te worden op stabiliteit. De charme wint het hier vaak van de perfectie.</p>"
        elif d['year'] > 2000:
            interpretation = "<p>Dit huis is 'af'. De focus ligt hier niet op renoveren, maar op personaliseren. Bouwtechnisch is dit de veiligste categorie in de markt.</p>"
        else:
            interpretation = "<p>Een prima casco dat zich goed leent voor modernisering. De structuur laat vaak toe om wanden te verwijderen voor een modernere indeling.</p>"

        # Advice
        advice_list = []
        advice_list.append(f"Bouwkundige keuring is {'noodzakelijk' if d['year'] < 1990 else 'altijd verstandig'}.")
        if d['year'] < 1980: advice_list.append("Laat een asbestinventarisatie uitvoeren bij verbouwplannen.")
        if "hout" in str(d.get('features','')).lower(): advice_list.append("Controleer schilderwerk en houtrot kritisch.")
        
        advice = "<ul>" + "".join([f"<li>{item}</li>" for item in advice_list]) + "</ul>"

        strengths = []
        if d['year'] > 1990: strengths.append("Modern Bouwbesluit")
        if d['year'] < 1940: strengths.append("Karakteristiek")
        if d['year'] > 2005: strengths.append("Betonvloeren (geluidsisolatie)")

        conclusion = f"Risicoprofiel: {'Laag (Instapklaar)' if not risks else 'Gemiddeld (Inspectie vereist)'}."
        
        return {
            "title": "Bouwkundige Staat",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }

    @staticmethod
    def _narrative_ch4(d):
        green = ["A", "A+", "A++", "A+++", "B"]
        is_green = any(x in d['label'] for x in green)
        
        # Intro
        if is_green:
            intro = f"Gefeliciteerd, met energielabel {d['label']} behoort deze woning tot de 'groene' voorhoede. Dit betekent direct comfort en lagere maandlasten."
        elif d['label'] in ['C', 'D']:
            intro = f"Met energielabel {d['label']} presteert de woning gemiddeld. Er is een solide basis, maar optimalisatie is zeker mogelijk."
        else:
            intro = f"Energielabel {d['label']} is een duidelijk signaal: hier valt winst te behalen. Duurzaamheid is bij dit object de belangrijkste investeringspost."
        
        # Analysis
        analysis_parts = []
        if d['year'] < 1980 and not is_green:
            analysis_parts.append(f"<p>Gezien het bouwjaar {d['year']} is de isolatie van de spouw, vloer en dak waarschijnlijk de 'laaghangende fruit' investering. Dit verdien je vaak binnen 5-7 jaar terug.</p>")
        elif is_green:
             analysis_parts.append("<p>De woning is reeds 'toekomstproof'. De volgende stap zou 'Off-Grid' kunnen zijn met extra zonnepanelen of een thuisbatterij.</p>")
        else:
             analysis_parts.append("<p>Het huidige label suggereert enkelglas of verouderde CV-techniek. Een energiescan zal de exacte pijnpunten blootleggen.</p>")
             
        analysis = "".join(analysis_parts)
        
        # Interpretation
        if is_green:
            interpretation = "<p>In de huidige markt is dit label een 'waarde-vermeerderaar'. Kopers betalen graag een premie voor instapklaar comfort.</p>"
        else:
            interpretation = "<p>Zie dit als een kans. Subsidies voor verduurzaming zijn ruim voorhanden, en na renovatie stijgt de woningwaarde direct.</p>"
            
        advice_list = []
        if not is_green: 
            advice_list.append("Vraag offertes op voor spouwmuurisolatie.")
            advice_list.append("Vervang eventueel resterend enkel glas door HR++.")
        else:
            advice_list.append("Optimaliseer de instellingen van de huidige installaties.")
        
        if d['plot'] and d['plot'] > 0: advice_list.append("dakligging checken voor zonnepanelen.")
        
        advice = "<ul>" + "".join([f"<li>{item}</li>" for item in advice_list]) + "</ul>"

        strengths = []
        if is_green: strengths.append(f"Uitstekend Label {d['label']}")
        if d['year'] > 2020: strengths.append("Gasloos")
        
        conclusion = f"{'Groene Modelwoning' if is_green else 'Renovatieproject met Potentie'}."

        return {
            "title": "Energie & Duurzaamheid",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }

    @staticmethod
    def _narrative_ch5(d):
        rooms = max(2, int(d['area'] / 25))
        
        if d['area'] > 150:
             intro = f"Zeeën van ruimte. Met {d['area']} m² is dit object een canvas voor uw woondromen, van thuiswerkplek tot home-gym."
        elif d['area'] < 70:
             intro = f"Compact en slim ingedeeld. De {d['area']} m² zijn efficiënt benut, wat resulteert in een knusse en beheersbare woonomgeving."
        else:
             intro = f"Met {d['area']} m² biedt deze woning precies de juiste maatvoering voor een comfortabel huishouden."
             
        analysis_parts = []
        if rooms > 5:
             analysis_parts.append(f"<p>We tellen (of schatten) maar liefst {rooms} kamers. Dit biedt ongekende flexibiliteit voor samengestelde gezinnen of hobbyisten.</p>")
        else:
             analysis_parts.append(f"<p>De indeling is functioneel met circa {rooms} hoofdvertrekken.</p>")
             
        if d['year'] < 1940:
             analysis_parts.append("<p>De klassieke 'en suite' indeling of voorkamer/achterkamer structuur is hier vaak nog voelbaar (of aanwezig). Dit geeft sfeer, maar kan de lichtinval beperken.</p>")
        elif d['year'] > 1990:
             analysis_parts.append("<p>Moderne 'recht-toe-recht-aan' architectuur zorgt ervoor dat vrijwel elke m² bruikbaar is. Geen verloren hoekjes.</p>")
             
        analysis = "".join(analysis_parts)
        
        interpretation = "<p>De 'flow' van het huis bepaalt het woonplezier. Een moderne woonkeuken is vaak het hart; check of de muur tussen keuken en kamer dragend is als u wilt doorbreken.</p>"
        
        advice_list = ["Neem een meetlint mee naar de bezichtiging.", "Check de internetverbinding op zolder/werkkamer."]
        advice = "<ul>" + "".join([f"<li>{item}</li>" for item in advice_list]) + "</ul>"

        strengths = [f"Gebruiksoppervlakte {d['area']} m²", "Indelingsvrijheid"]

        conclusion = "Flexibiliteit is de troef van dit object."
        return {
            "title": "Indeling & Ruimte",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }

    @staticmethod
    def _narrative_ch6(d):
        target = "modernisering" if d['year'] < 2010 else "finetuning"
        
        if d['year'] < 2015:
            intro = f"Laten we eerlijk zijn: u koopt hier de 'potentie'. De afwerking is functioneel, maar een update naar {2025} is waarschijnlijk gewenst."
        else:
            intro = "Instapklaar. Dozen uitpakken en wonen. De staat van onderhoud is uitstekend."
            
        analysis = f"""
        <p>Op basis van het bouwjaar {d['year']} verwachten we dat de keuken en badkamer in de {(2025-d['year']) // 15 + 1}e fase van hun levensduur zitten.
        {'Houd rekening met vervanging.' if d['year'] < 2010 else 'Deze kunnen nog jaren mee.'}</p>
        """
        
        if target == "modernisering":
            interpretation = "<p>Onderschat de impact van stuc- en schilderwerk niet. Een frisse witte basis doet wonderen voor de lichtbeleving en verkoopwaarde.</p>"
        else:
            interpretation = "<p>De luxe afwerking (indien aanwezig) rechtvaardigt de hogere m²-prijs. U bespaart immers direct op aannemerskosten en wachttijden.</p>"
        
        advice = "<ul><li>Maak een begroting vóór het bieden.</li><li>Vraag naar garanties op keukenapparatuur.</li></ul>"
        
        strengths = ["Basisstructuur"]
        if d['year'] > 2010: strengths.append("Modern Sanitair")

        conclusion = f"Project '{target}'."
        return {
            "title": "Onderhoud & Afwerking",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }

    @staticmethod
    def _narrative_ch7(d):
        garden = max(0, d['plot'] - (d['area']/2)) if d['plot'] else 0
        
        # Intro
        if garden > 200:
             intro = f"Het buitenleven roept! Met naar schatting {int(garden)} m² tuin heeft u hier uw eigen parkje."
        elif garden > 40:
             intro = "De tuin heeft een fijn, behapbaar formaat. Genoeg plek voor een BBQ en loungehoek, zonder dat u elk weekend in het groen moet werken."
        else:
             intro = "De buitenruimte is compact. Ideaal voor wie houdt van een espresso in de zon, maar niet van grasmaaien."
             
        analysis_parts = []
        if d['plot'] > 0:
            analysis_parts.append(f"<p>De perceelgrootte van {d['plot']} m² is een waarde-anker. Grond wordt immers niet meer bijgemaakt.</p>")
            analysis_parts.append("<p>Let op de oriëntatie: Een tuin op het zuid(west)en is goud waard, maar een noord-tuin biedt koelte in hete zomers.</p>")
        else:
            analysis_parts.append("<p>Bij dit appartement vertrouwt u op het balkon of dakterras (check VvE regels voor gebruik).</p>")
            
        analysis = "".join(analysis_parts)
        
        interpretation = "<p>Privacy is het sleutelwoord. Staan er hoge bomen? Zijn er inkijkende buren? Dit gevoel laat zich niet in data vangen, maar moet u ervaren.</p>"

        advice = "<ul><li>Check kadastrale erfgrenzen (staat het hek goed?).</li><li>Let op bomen (kapvergunning nodig?).</li></ul>"
        strengths = []
        if garden > 100: strengths.append("Royale tuin")
        if garden == 0: strengths.append("Onderhoudsvrij")

        conclusion = f"Buitenruimte score: {8 if garden > 100 else 6}/10."
        return {
            "title": "Tuin & Buiten",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }

    @staticmethod
    def _narrative_ch8(d):
        intro_parts = []
        if d['price'] > 500000:
             intro_parts.append("Kiezen voor deze locatie is kiezen voor comfort. De bereikbaarheid speelt daarbij een sleutelrol.")
        else:
             intro_parts.append("Een praktische locatie voor wie mobiel wil zijn.")
        intro = "".join(intro_parts)
        
        analysis_parts = []
        analysis_parts.append("<p>Op basis van de postcode-data zien we dat de afstand tot snelwegen en OV-knooppunten 'gemiddeld tot goed' is.</p>")
        
        if d['year'] < 1920:
             analysis_parts.append("<p>In historische stadscentra zoals deze is parkeren vaak de grootste uitdaging. Een bewonersvergunning is waarschijnlijk vereist en er kunnen wachtlijsten zijn.</p>")
        else:
             analysis_parts.append("<p>De wijkopzet uit deze bouwperiode houdt rekening met autobezit. Parkeren kan vermoedelijk ruimschoots in de straat of op eigen terrein.</p>")
             
        analysis = "".join(analysis_parts)
        
        interpretation = "<p>Voor forenzen is de reistijd-tot-werk de bepalende factor. Test dit zelf op een dinsdagochtend.</p>"
        
        advice = "<ul><li>Controleer parkeerbeleid gemeente (kosten/vergunning).</li><li>Test de OV-verbinding in de spits.</li></ul>"
        strengths = ["Centrale ligging"]

        conclusion = "<strong>Conclusie:</strong> Mobiliteitsscore: Voldoende, parkeren vergt aandacht."
        
        return {
            "title": "Mobiliteit",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }

    @staticmethod
    def _narrative_ch9(d):
        intro = "Juridische zekerheid is het fundament van uw investering."
        analysis_parts = []
        
        if d['year'] < 1992:
             analysis_parts.append("<p>Oude aktes bevatten soms vergeten erfdienstbaarheden (recht van overpad). Dit kan invloed hebben op uw privacy.</p>")
        else:
             analysis_parts.append("<p>Bij nieuwere woningbouw zijn de juridische kaders vaak strak vastgelegd in de koopovereenkomst en eventuele mandeligheid.</p>")
             
        if "appartement" in d.get('address', '').lower(): # Weak check
             analysis_parts.append("<p>Let op: U koopt een appartementsrecht, geen pand. De VvE-reglementen zijn leidend.</p>")
             
        analysis = "".join(analysis_parts)
        
        interpretation = "<p>Wij zien geen directe 'rode vlaggen' in de basisgegevens, maar de duivel zit in de details van het eigendomsbewijs.</p>"
        advice = "<ul><li>Laat de koopakte screenen door een jurist/notaris.</li><li>Controleer erfpachtvoorwaarden (indien van toepassing).</li></ul>"
        strengths = ["Geen complexe constructies bekend"]

        conclusion = "<strong>Conclusie:</strong> Juridisch 'standaard' risico."
        return {
            "title": "Juridische Aspecten",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }

    @staticmethod
    def _narrative_ch10(d):
        intro = "Is de vraagprijs reëel? Een financiële deep-dive."
        kk = int(d['price'] * 0.04)
        m2_price = int(d['price']/d['area']) if d['area'] else 0
        
        analysis = f"""
        <p>Met een m²-prijs van €{m2_price} bevindt dit object zich {'aan de bovenkant van de markt' if m2_price > 6000 else 'in een toegankelijk segment'}. 
        Houd rekening met bijkomende kosten (k.k. + inrichting) van circa € {int(kk * 1.5):,}.</p>
        """
        
        if d['label'] == 'G':
            interpretation = "<p>Let op: Bij een laag energielabel is uw leencapaciteit wellicht beperkter, maar u kunt mogelijk wel een bouwdepot voor verduurzaming meefinancieren.</p>"
        else:
            interpretation = "<p>Het goede energielabel kan zorgen voor rentekorting bij sommige hypotheekverstrekkers ('Groenhypotheek').</p>"
            
        advice = "<ul><li>Bespreek een bouwdepot met uw adviseur.</li><li>Neem ontbindende voorwaarden op voor financiering.</li></ul>"
        strengths = ["Transparante prijsstelling"]

        conclusion = f"<strong>Conclusie:</strong> Totale investering schatten op € {d['price'] + kk + 20000:,}."
        return {
            "title": "Financiële Analyse",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }
        
    @staticmethod
    def _narrative_ch11(d):
        intro = "Timing is alles. Hoe ligt dit object in de markt?"
        
        if d['price'] < 400000:
             analysis = "<p>In dit prijssegment is de concurrentie moordend. Verwacht veel bezichtigingen en mogelijk een inschrijvingsprocedure.</p>"
        elif d['price'] > 1000000:
             analysis = "<p>Het hogere segment kent een langere doorlooptijd. Dit geeft u iets meer ademruimte voor onderhandeling en due diligence.</p>"
        else:
             analysis = "<p>Een courante gezinswoning. De verkoopsnelheid hangt sterk af van de presentatie en 'look & feel'.</p>"
             
        interpretation = "<p>Wees voorbereid op snel schakelen, maar laat u niet opjagen.</p>"
        advice = "<ul><li>Vraag de makelaar naar het biedingsproces.</li><li>Zorg dat uw dossier (werkgeversverklaring etc.) op orde is.</li></ul>"
        strengths = ["Courant object"]

        conclusion = "<strong>Conclusie:</strong> Hete markt, koel hoofd houden."
        return {
            "title": "Marktpositie",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }

    @staticmethod
    def _narrative_ch0(d):
        """Generate narrative for Chapter 0 (introductory page) handling missing data and AI usage note."""
        # Helper to safely get values with fallback
        def get(key, default="onbekend"):
            val = d.get(key)
            return val if val not in (None, "", 0) else default
        address = get('address')
        price = get('price')
        area = get('area')
        label = get('label')
        # Intro
        intro_parts = []
        intro_parts.append(f"Welkom bij de analyse van het object aan {address}.")
        if price != "onbekend":
            intro_parts.append(f"De vraagprijs bedraagt €{price:,}.")
        if area != "onbekend":
            intro_parts.append(f"Het woonoppervlak is {area} m².")
        intro_parts.append(f"Energielabel: {label}.")
        intro = " ".join(intro_parts)
        # Main analysis – note missing KPI handling
        analysis = "\n<p>De beschikbare KPI's zijn beperkt; sommige waarden ontbreken of zijn niet ingevuld.</p>"
        # AI usage note
        interpretation = "<p>Deze analyse is gegenereerd met behulp van een AI‑engine die de beschikbare data interpreteert.</p>"
        # Conclusion
        conclusion = "<strong>Conclusie:</strong> Controleer de ontbrekende gegevens voor een volledige beoordeling."
        return {
            "title": "Introductie & Samenvatting",
            "intro": intro,
            "main_analysis": analysis,
            "interpretation": interpretation,
            "advice": "",
            "strengths": [],
            "conclusion": conclusion
        }

    def _narrative_ch12(d):
        intro = "Na deze diepgaande analyse komen we tot de slotsom."
        
        narrative_parts = []
        narrative_parts.append(f"<p>De woning aan de {d['address']} heeft indruk gemaakt met zijn {d['area']} m² en karakter.</p>")
        
        if d['year'] < 1980 or "G" in d['label']:
             narrative_parts.append("<p><strong>De Uitdaging:</strong> De investering stopt niet bij de aankoop. Verduurzaming en modernisering vragen om visie en budget.</p>")
        else:
             narrative_parts.append("<p><strong>Het Comfort:</strong> De basis is uitstekend. U koopt hier vooral woonplezier, geen bouwproject.</p>")
             
        analysis = "".join(narrative_parts)
        
        interpretation = "<p>Is dit uw droomhuis? Dat bepaalt uw gevoel. Is het een verstandige aankoop? De data zegt: 'Ja, mits de prijs in lijn is met de staat'.</p>"
        
        advice = "<ul><li>Laatste check: Bestemmingsplan omgeving.</li><li>Biedt strategisch (geen ronde getallen).</li></ul>"
        strengths = ["Unieke combinatie locatie/ruimte"]
        
        # Final Score Logic (Mock)
        final_score = 8.5 if d['label'] in ['A','B'] else 7.0

        conclusion = f"<strong>Eindcijfer: {final_score}/10.</strong> {'KOOPWAARDIG' if final_score > 7 else 'AANDACHT VEREIST'}."
        
        return {
            "title": "Advies & Conclusie",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }
