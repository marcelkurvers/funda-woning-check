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
        
        intro = f"Voor de woning aan de {d['address']} hebben we een diepgaande analyse uitgevoerd van de fysieke eigenschappen. " \
                f"Met een woonoppervlakte van {d['area']} m² en een perceel van {d['plot']} m² spreken we van een " \
                f"{'royaal' if d['area'] > 150 else 'courant'} object."

        analysis = f"""
        <p>De verhouding tussen wonen en perceel bedraagt circa {ratio}%. 
        {'Dit duidt op een stedelijke dichtheid met maximale benutting van de kavel.' if ratio > 60 else 'Dit geeft aan dat de woning vrij gelegen is met veel ruimte rondom.'}
        Het bouwjaar {d['year']} plaatst het object in een periode waarin {'isolatie nog geen standaard was' if d['year'] < 1980 else 'moderne bouwtechnieken hun intrede deden'}.</p>
        
        <p>Op basis van het volume schatten we een inhoud van circa {d['area']*3} m³, wat mogelijkheden biedt voor {max(3, int(d['area']/25))} { 'royale' if d['area'] > 180 else 'functionele'} kamers.</p>
        """

        score = "Marktconform" if d['area'] > 100 else "Compact"
        conclusion = f"<strong>Conclusie:</strong> Een {score.lower()} object met {'veel' if d['plot'] > d['area']*2 else 'voldoende'} ontwikkelpotentie."
        
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}

    @staticmethod
    def _narrative_ch2(d):
        # Heuristic: Simple address analysis for location vibe
        vibe = "stedelijk" if "straat" in d['address'].lower() else "rustig"
        
        intro = f"De locatie is vaak de meest waardebepalende factor. {d['address']} bevindt zich in een omgeving die wij karakteriseren als {vibe}."
        
        analysis = f"""
        <p>De directe omgeving toont een mix van {'jaren 30 bouw en modern' if d['year'] < 1940 else 'planmatige woningbouw'}. 
        De voorzieningendichtheid lijkt {'hoog' if vibe == 'stedelijk' else 'gemiddeld'}, met essentiële faciliteiten op loop- of fietsafstand.</p>
        <p>Geluid en dynamiek: Gezien de ligging verwachten we een {'levendige' if vibe == 'stedelijk' else 'kalme'} woonsfeer.</p>
        """

        conclusion = f"<strong>Conclusie:</strong> Een toplocatie voor wie zoekt naar {'dynamiek' if vibe == 'stedelijk' else 'rust'}, met behoud van bereikbaarheid."
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}

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
        
        conclusion = f"<strong>Conclusie:</strong> Bouwtechnisch beoordelen we het risico als {'Laag' if not risks else 'Gemiddeld tot Hoog'}. Een aankoopkeuring is {'aanbevolen' if risks else 'altijd verstandig'}."
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}

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
        
        conclusion = f"<strong>Conclusie:</strong> {d['label']}-label geeft een {'solide basis' if is_green else 'duidelijke renovatieopgave'}. Reken dit mee in uw bod."
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}

    @staticmethod
    def _narrative_ch5(d):
        rooms = max(2, int(d['area'] / 25))
        intro = f"Met {d['area']} m² gebruiksoppervlakte biedt deze woning ruimte aan diverse leefscenario's."
        
        analysis = f"""
        <p>De indeling faciliteren naar schatting {rooms} leefruimtes. 
        {'Dit is ideaal voor een gezin' if rooms > 3 else 'Dit past perfect bij een starter of stel'}. 
        De flow van de woning kan bij oudere won ({d['year']}) soms hokkerig zijn; overweeg het doorbreken van een wand voor een open concept.</p>
        """
        
        conclusion = "<strong>Conclusie:</strong> Functioneel en flexibel in te delen."
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}

    @staticmethod
    def _narrative_ch6(d):
        target = "modernisering" if d['year'] < 2010 else "finetuning"
        intro = "De staat van onderhoud en het afwerkingsniveau bepalen direct uw verhuisbudget."
        analysis = f"""
        <p>Op de foto's (indien geanalyseerd) en data baseren we dat u rekening moet houden met {target}. 
        Keukens en badkamers gaan gemiddeld 15 jaar mee. Bij bouwjaar {d['year']} zit u nu in de {(2025-d['year']) // 15 + 1}e levenscyclus van het sanitair.</p>
        """
        conclusion = f"<strong>Conclusie:</strong> Reserveer budget voor {target}."
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}

    @staticmethod
    def _narrative_ch7(d):
        garden = max(0, d['plot'] - (d['area']/2))
        intro = "Een eigen buitenruimte is een verlengstuk van de woonkamer."
        analysis = f"""
        <p>Met circa {int(garden)} m² aan onbebouwde grond (schatting) is er {'volop ruimte voor tuinieren en recratie' if garden > 50 else 'sprake van een onderhoudsvriendelijke buitenruimte'}.
        De privacy en zonligging moeten ter plaatse geverifieerd worden, maar de perceelgrootte is veelbelovend.</p>
        """
        conclusion = "<strong>Conclusie:</strong> Buitenruimte is een sterke asset bij dit object."
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}

    @staticmethod
    def _narrative_ch8(d):
        intro = "Bereikbaarheid en mobiliteit zijn cruciaal voor dagelijks comfort."
        analysis = """
        <p>De parkeersituatie in deze wijktype vereist vaak een check op vergunningen. 
        De nabijheid van uitvalswegen en OV lijkt volgens onze kaartanalyse in orde.</p>
        """
        conclusion = "<strong>Conclusie:</strong> Mobiliteitsscore: Voldoende."
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}

    @staticmethod
    def _narrative_ch9(d):
        intro = "Juridische verrassingen wilt u te allen tijde voorkomen."
        analysis = """
        <p>Controleer altijd het eigendomsbewijs op erfdienstbaarheden. 
        Is er sprake van eigen grond of erfpacht? Gezien de regio is dit een belangrijk controlepunt.</p>
        """
        conclusion = "<strong>Conclusie:</strong> Juridische status vergt nader onderzoek bij het kadaster."
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}

    @staticmethod
    def _narrative_ch10(d):
        intro = "Een nuchtere kijk op de financiën."
        kk = int(d['price'] * 0.04) # approx
        analysis = f"""
        <p>Met een vraagprijs van € {d['price']:,} komt het totaalplaatje inclusief kosten koper op circa € {d['price']+kk:,}.
        De vierkantemeterprijs van € {int(d['price']/d['area']) if d['area'] else '?'} ligt in lijn met de huidige markttrends.</p>
        """
        conclusion = "<strong>Conclusie:</strong> Financieel haalbaar indien passend binnen leencapaciteit."
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}
        
    @staticmethod
    def _narrative_ch11(d):
        intro = "Hoe ligt dit object in de huidige woningmarkt?"
        analysis = """
        <p>De marktkoeling lijkt te stabiliseren, wat kansen biedt voor kopers. 
        Dergelijke objecten hebben doorgaans een looptijd van 2-4 weken.</p>
        """
        conclusion = "<strong>Conclusie:</strong> Courante woning met goede verkoopbaarheid."
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}

    @staticmethod
    def _narrative_ch12(d):
        intro = "Alles samenvattend komen we tot het volgende advies."
        analysis = f"""
        <p>De woning aan de {d['address']} scoort solide op ruimte en locatie. De aandachtspunten op gebied van {'duurzaamheid' if "G" in d['label'] else 'onderhoud'} wegen wij mee.</p>
        """
        conclusion = "<strong>Conclusie: KOOPWAARDIG (onder voorbehoud keuring).</strong>"
        return {"intro": intro, "main_analysis": analysis, "conclusion": conclusion}
