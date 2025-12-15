import random
import re
from typing import Dict, Any

class IntelligenceEngine:
    """
    Simulates a sophisticated AI analyst that generates dynamic narratives 
    based on property data. In a full production version, this would 
    interface with an LLM (e.g., OpenAI API).
    """

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
            "address": ctx.get('adres', 'het object')
        }

        if chapter_id == 1:
            return IntelligenceEngine._narrative_ch1(data)
        elif chapter_id == 2:
            return IntelligenceEngine._narrative_ch2(data)
        elif chapter_id == 3:
            return IntelligenceEngine._narrative_ch3(data)
        elif chapter_id == 4:
            return IntelligenceEngine._narrative_ch4(data)
        elif chapter_id == 5:
            return IntelligenceEngine._narrative_ch5(data)
        elif chapter_id == 6:
            return IntelligenceEngine._narrative_ch6(data)
        elif chapter_id == 7:
            return IntelligenceEngine._narrative_ch7(data)
        elif chapter_id == 8:
            return IntelligenceEngine._narrative_ch8(data)
        elif chapter_id == 9:
            return IntelligenceEngine._narrative_ch9(data)
        elif chapter_id == 10:
            return IntelligenceEngine._narrative_ch10(data)
        elif chapter_id == 11:
            return IntelligenceEngine._narrative_ch11(data)
        elif chapter_id == 12:
            return IntelligenceEngine._narrative_ch12(data)
        else:
            return {"title": "Analyse", "intro": "Generieke analyse.", "main_analysis": "Geen data.", "conclusion": "N.v.t."}

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

    # --- NARRATIVES ---

    @staticmethod
    def _narrative_ch1(d):
        ratio = int(d['area'] / d['plot'] * 100) if d['plot'] else 100
        rooms_est = max(3, int(d['area']/25))
        
        # 1. Intro
        intro = f"Voor de woning aan de {d['address']} hebben we een diepgaande analyse uitgevoerd van de fysieke eigenschappen. " \
                f"Met een woonoppervlakte van {d['area']} m² en een perceel van {d['plot']} m² spreken we van een " \
                f"{'royaal' if d['area'] > 150 else 'courant'} object."

        # 2. Main Analysis (Legacy support)
        analysis = f"""
        <p>De verhouding tussen wonen en perceel bedraagt circa {ratio}%. 
        {'Dit duidt op een stedelijke dichtheid met maximale benutting van de kavel.' if ratio > 60 else 'Dit geeft aan dat de woning vrij gelegen is met veel ruimte rondom.'}
        Het bouwjaar {d['year']} plaatst het object in een periode waarin {'isolatie nog geen standaard was' if d['year'] < 1980 else 'moderne bouwtechnieken hun intrede deden'}.</p>
        
        <p>Op basis van het volume schatten we een inhoud van circa {d['area']*3} m³, wat mogelijkheden biedt voor {rooms_est} { 'royale' if d['area'] > 180 else 'functionele'} kamers.</p>
        """

        # 3. Rich AI Interpretation (New)
        interpretation = f"""
        <p>Dit betreft een {'zeer ruim bemeten' if d['area'] > 200 else 'marktconform'} woning die duidelijk positie kiest in het {'hogere' if d['price'] > 750000 else 'midden'}segment. 
        De combinatie van {d['area']} m² woonoppervlakte op een perceel van {d['plot']} m² is {'uniek' if d['plot'] > d['area']*3 else 'in balans'}. 
        Het volume en de indeling suggereren een gebruik als {'luxe gezinswoning' if d['area'] > 150 else 'praktische eengezinswoning'} met {'multifunctionele mogelijkheden' if d['area'] > 250 else 'voldoende ruimte'}.</p>
        """

        # 4. Advice / Attention Points
        advice = []
        if d['year'] < 1980:
            advice.append("Controleer de isolatiestandaard (dak/vloer/glas) gezien het bouwjaar.")
            advice.append("Houd rekening met modernisering van installaties.")
        if d['label'] in ['E', 'F', 'G']:
            advice.append("Verduurzaming is noodzakelijk voor toekomstbestendigheid.")
        if not advice:
            advice.append("Geen directe bouwkundige aandachtspunten op basis van deze data.")
        
        advice_html = "<ul>" + "".join([f"<li>{point}</li>" for point in advice]) + "</ul>"

        # 5. Strengths (Sterktes)
        strengths = []
        if d['area'] > 150: strengths.append(f"Royaal woonoppervlak ({d['area']} m²)")
        if d['plot'] > 500: strengths.append(f"Groot perceel ({d['plot']} m²)")
        if "A" in d['label']: strengths.append("Energiezuinig label")
        
        # 6. Conclusion
        score = "Marktconform" if d['area'] > 100 else "Compact"
        conclusion = f"<strong>Conclusie:</strong> Een {score.lower()} object met {'veel' if d['plot'] > d['area']*2 else 'voldoende'} ontwikkelpotentie."
        
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
        marcel_prio = prefs.get('marcel', {}).get('priorities', [])
        petra_prio = prefs.get('petra', {}).get('priorities', [])
        
        # Simple keyword matching helper
        def check_features(priorities, source_text):
            matches = []
            misses = []
            source_lower = source_text.lower()
            for p in priorities:
                # Naive matching: property feature descriptions often contain these words
                # In a real system, we'd map 'Solar' to 'Zonnepanelen', 'Warmtepomp' to 'Warmtepomp', etc.
                keyword = p.lower()
                if keyword == "solar": keyword = "zonnepanelen"
                if keyword == "accu": keyword = "batterij"
                if keyword == "jaren 30": keyword = "193" # rudimentary year check
                
                if keyword in source_lower:
                    matches.append(p)
                else:
                    misses.append(p)
            return matches, misses

        # Combine source text for searching
        description = d.get('description', '') or ""
        features = str(d.get('features', []))
        source_blob = f"{description} {features}"
        
        m_matches, m_misses = check_features(marcel_prio, source_blob)
        p_matches, p_misses = check_features(petra_prio, source_blob)
        
        total_prio = len(marcel_prio) + len(petra_prio)
        total_match = len(m_matches) + len(p_matches)
        score_pct = int((total_match / total_prio * 100)) if total_prio > 0 else 50 # Default 50 if no prefs

        intro = f"Op basis van de aangescherpte profielen van Marcel (Tech & Infra) en Petra (Sfeer & Comfort) scoort deze woning een match van {score_pct}%."
        
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
        <p>De woning sluit voor <strong>{'Marcel' if len(m_matches) > len(p_matches) else 'Petra'}</strong> op papier het beste aan. 
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

        conclusion = f"<strong>Conclusie:</strong> Een {score_pct}% match. {'Een sterke kandidaat!' if score_pct > 60 else 'Voldoet aan de basis, maar concessies zijn nodig.'}"
        
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
        if d['year'] < 1980: risks.append("de aanwezigheid van asbest")
        if d['year'] < 1990: risks.append("de staat van het leidingwerk")
        
        risk_text = f"Gezien het bouwjaar {d['year']} adviseren wij specifiek te letten op {', '.join(risks)}." if risks else "Gezien het recente bouwjaar verwachten we geen structurele gebreken."

        intro = f"Met een oorsprong in {d['year']} draagt dit pand een specifieke bouwkundige signatuur."
        
        analysis = f"""
        <p>De constructieve staat oogt op basis van de kerngegevens {'solide' if d['year'] > 1990 else 'aandachtbehoevend'}. 
        {risk_text}</p>
        <p>Dak & Gevel: De levensduur van dakpannen is ca. 40-50 jaar. Bij dit object is {(2025-d['year']) % 50} jaar geleden theoretisch vervanging/groot onderhoud nodig geweest.</p>
        """

        interpretation = f"""
        <p>Het pand is gebouwd met de kwaliteitsnormen van {d['year']}. Dit betekent dat modernisering naar huidige maatstaven {'een optie' if d['year'] > 2000 else 'een noodzaak'} is.
        De bouwkundige structuur lijkt {'standaard' if d['year'] > 1980 else 'traditioneel'}.</p>
        """

        advice = "<ul>"
        advice += f"<li>Bouwkundige keuring is {'essentieel' if risks else 'aanbevolen'}.</li>"
        if d['year'] < 1980: advice += "<li>Inventariseer risico op asbest.</li>"
        advice += "</ul>"

        strengths = []
        if d['year'] > 1990: strengths.append("Modern bouwbesluit (bouwtechnisch veilig)")
        if d['year'] < 1940: strengths.append("Karakteristieke bouwstijl")

        conclusion = f"<strong>Conclusie:</strong> Bouwtechnisch beoordelen we het risico als {'Laag' if not risks else 'Gemiddeld tot Hoog'}."
        
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
        
        intro = f"Duurzaamheid is key voor waardebehoud. Met energielabel {d['label']} scoort deze woning {'boven' if is_green else 'onder'} de moderne standaard."
        
        analysis = f"""
        <p>Het huidige label impliceert dat er {'reeds flink geïnvesteerd is' if is_green else 'nog winst te behalen valt'}. 
        Voor een woning uit {d['year']} is dit label {'een knappe prestatie' if is_green else 'volgens verwachting'}.</p>
        <p>Besparingspotentieel: {'Optimalisatie van installaties' if is_green else 'Het isoleren van schil (dak/vloer/gevel) is de eerste stap naar lagere lasten'}.</p>
        """
        
        interpretation = f"""
        <p>De woning { 'voldoet aan' if is_green else 'blijft achter bij' } de huidige duurzaamheidseisen.
        Met het oog op de gasloze toekomst is een investeringsplan {'raadzaam' if is_green else 'noodzakelijk'}.</p>
        """

        advice = "<ul>"
        if not is_green: advice += "<li>Overweeg na-isolatie van spouw en dak.</li>"
        advice += "<li>Onderzoek mogelijkheden voor warmtepomp/zonnepanelen.</li></ul>"

        strengths = []
        if is_green: strengths.append(f"Energielabel {d['label']}")
        strengths.append("Dakligging geschikt voor zonnepanelen (check oriëntatie)")

        conclusion = f"<strong>Conclusie:</strong> {d['label']}-label geeft een {'solide basis' if is_green else 'duidelijke renovatieopgave'}."
        
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
        intro = f"Met {d['area']} m² gebruiksoppervlakte biedt deze woning ruimte aan diverse leefscenario's."
        
        analysis = f"""
        <p>De indeling faciliteren naar schatting {rooms} leefruimtes. 
        {'Dit is ideaal voor een gezin' if rooms > 3 else 'Dit past perfect bij een starter of stel'}. 
        De flow van de woning kan bij oudere won ({d['year']}) soms hokkerig zijn; overweeg het doorbreken van een wand voor een open concept.</p>
        """

        interpretation = f"<p>De m² zijn {'ruim' if d['area'] > 120 else 'compact'} verdeeld. De woning biedt {'veel' if rooms > 4 else 'beperkte'} flexibiliteit voor thuiswerken of gezinsuitbreiding.</p>"

        advice = "<ul><li>Beoordeel de dragende wanden bij herindeling.</li><li>Kijk naar mogelijkheden voor open keuken.</li></ul>"

        strengths = [f"Woonoppervlakte {d['area']} m²", f"Potentieel {rooms} kamers"]

        conclusion = "<strong>Conclusie:</strong> Functioneel en flexibel in te delen."
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
        intro = "De staat van onderhoud en het afwerkingsniveau bepalen direct uw verhuisbudget."
        analysis = f"""
        <p>Op de foto's (indien geanalyseerd) en data baseren we dat u rekening moet houden met {target}. 
        Keukens en badkamers gaan gemiddeld 15 jaar mee. Bij bouwjaar {d['year']} zit u nu in de {(2025-d['year']) // 15 + 1}e levenscyclus van het sanitair.</p>
        """

        interpretation = f"<p>Het afwerkingsniveau lijkt {'basis' if d['year'] < 2015 else 'luxe'}. Houd rekening met een budget voor {'vloeren en wanden' if target=='modernisering' else 'klein onderhoud'}.</p>"
        
        advice = "<ul><li>Maak een kostenraming voor direct noodzakelijk onderhoud.</li><li>Check leeftijd CV-ketel en apparatuur.</li></ul>"
        
        strengths = ["Basis lijkt solide"] # Generic

        conclusion = f"<strong>Conclusie:</strong> Reserveer budget voor {target}."
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
        garden = max(0, d['plot'] - (d['area']/2))
        intro = "Een eigen buitenruimte is een verlengstuk van de woonkamer."
        analysis = f"""
        <p>Met circa {int(garden)} m² aan onbebouwde grond (schatting) is er {'volop ruimte voor tuinieren en recratie' if garden > 50 else 'sprake van een onderhoudsvriendelijke buitenruimte'}.
        De privacy en zonligging moeten ter plaatse geverifieerd worden, maar de perceelgrootte is veelbelovend.</p>
        """

        interpretation = f"<p>De tuin biedt {'veel' if garden > 100 else 'beperkte'} privacy. De verhouding steen/groen is {'gunstig' if garden > 50 else 'stedelijk'}.</p>"

        advice = "<ul><li>Controleer de zonnestand op uw favoriete momenten.</li><li>Let op inkijk van buren.</li></ul>"
        strengths = []
        if garden > 100: strengths.append("Royale tuin")

        conclusion = "<strong>Conclusie:</strong> Buitenruimte is een sterke asset bij dit object."
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
        intro = "Bereikbaarheid en mobiliteit zijn cruciaal voor dagelijks comfort."
        analysis = """
        <p>De parkeersituatie in deze wijktype vereist vaak een check op vergunningen. 
        De nabijheid van uitvalswegen en OV lijkt volgens onze kaartanalyse in orde.</p>
        """
        interpretation = "<p>De locatie is goed ontsloten. Voor forenzen is dit een strategische plek.</p>"
        advice = "<ul><li>Controleer parkeerbeleid gemeente.</li><li>Test reistijd in de spits.</li></ul>"
        strengths = ["Goede bereikbaarheid"]

        conclusion = "<strong>Conclusie:</strong> Mobiliteitsscore: Voldoende."
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
        intro = "Juridische verrassingen wilt u te allen tijde voorkomen."
        analysis = """
        <p>Controleer altijd het eigendomsbewijs op erfdienstbaarheden. 
        Is er sprake van eigen grond of erfpacht? Gezien de regio is dit een belangrijk controlepunt.</p>
        """
        interpretation = "<p>Juridisch lijkt dit een standaard object (volle eigendom aangenomen), maar check de kleine lettertjes.</p>"
        advice = "<ul><li>Vraag eigendomsbewijs op.</li><li>Check kadastrale kaart op grenzen.</li></ul>"
        strengths = ["Waarschijnlijk volle eigendom (te verifiëren)"]

        conclusion = "<strong>Conclusie:</strong> Juridische status vergt nader onderzoek bij het kadaster."
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
        intro = "Een nuchtere kijk op de financiën."
        kk = int(d['price'] * 0.04) # approx
        analysis = f"""
        <p>Met een vraagprijs van € {d['price']:,} komt het totaalplaatje inclusief kosten koper op circa € {d['price']+kk:,}.
        De vierkantemeterprijs van € {int(d['price']/d['area']) if d['area'] else '?'} ligt in lijn met de huidige markttrends.</p>
        """
        interpretation = "<p>De vraagprijs lijkt {'scherp' if d['price'] < 500000 else 'marktconform'} gezien de m². De TCO (Total Cost of Ownership) zal hoger liggen door energie/onderhoud.</p>"
        advice = "<ul><li>Maak een sluitende financieringsopzet.</li><li>Houd rekening met overbieden in deze markt.</li></ul>"
        strengths = ["Courante prijsklasse"]

        conclusion = "<strong>Conclusie:</strong> Financieel haalbaar indien passend binnen leencapaciteit."
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
        intro = "Hoe ligt dit object in de huidige woningmarkt?"
        analysis = """
        <p>De marktkoeling lijkt te stabiliseren, wat kansen biedt voor kopers. 
        Dergelijke objecten hebben doorgaans een looptijd van 2-4 weken.</p>
        """
        interpretation = "<p>De gewildheid van dit type woningen is hoog. Snel handelen is geboden.</p>"
        advice = "<ul><li>Plan direct een bezichtiging.</li><li>Zorg dat uw dossier compleet is.</li></ul>"
        strengths = ["Hoge verkoopbaarheid"]

        conclusion = "<strong>Conclusie:</strong> Courante woning met goede verkoopbaarheid."
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
    def _narrative_ch12(d):
        intro = "Alles samenvattend komen we tot het volgende advies."
        analysis = f"""
        <p>De woning aan de {d['address']} scoort solide op ruimte en locatie. De aandachtspunten op gebied van {'duurzaamheid' if "G" in d['label'] else 'onderhoud'} wegen wij mee.</p>
        """
        interpretation = "<p>Dit object is een {'buitenkans' if d['plot'] > 500 else 'degelijke aankoop'} voor wie zoekt naar kwaliteit en ruimte.</p>"
        advice = "<ul><li>Doe een openingsbod gebaseerd op feiten.</li><li>Laat u niet gek maken door emotie.</li></ul>"
        strengths = [f"Locatie {d['address']}", "Potentie"]

        conclusion = "<strong>Conclusie: KOOPWAARDIG (onder voorbehoud keuring).</strong>"
        return {
            "title": "Advies & Conclusie",
            "intro": intro, 
            "main_analysis": analysis, 
            "interpretation": interpretation,
            "advice": advice,
            "strengths": strengths,
            "conclusion": conclusion
        }
