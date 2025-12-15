import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import os

titles = {
    1: "Algemene Woningkenmerken",
    2: "Locatie & Omgeving",
    3: "Bouwkundige Staat",
    4: "Energie & Duurzaamheid",
    5: "Indeling & Ruimtegebruik",
    6: "Onderhoud & Afwerking",
    7: "Tuin & Buitenruimte",
    8: "Parkeren & Bereikbaarheid",
    9: "Juridische Aspecten",
    10: "Financiële Analyse",
    11: "Marktpositie",
    12: "Advies & Conclusie"
}

base_dir = os.path.dirname(__file__)
rapport_dir = os.path.join(base_dir, "rapport")
os.makedirs(rapport_dir, exist_ok=True)

content_template = """# [{title}]

**Betreft:** [Adres]
**Datum:** 2024

### Inleiding
Dit hoofdstuk analyseert de {lowertitle} van het object aan de [Adres]. We kijken specifiek naar de impact hiervan op de marktwaarde en woongenot.

### Analyse
Gegevens uit de advertentie tonen de volgende kernpunten:
*   **Vraagprijs:** [Prijs]
*   **Woonoppervlakte:** [Oppervlakte]
*   **Perceel:** [Perceel]
*   **Bouwjaar:** [Bouwjaar]

[IF Label matches A]
**Duurzaamheids-check:** De woning heeft een uitstekend energielabel ([Label]). Dit suggereert recente isolatiemaatregelen en lagere maandlasten.
[ELSE]
**Duurzaamheids-check:** Met energielabel [Label] is er waarschijnlijk ruimte voor verduurzaming.
[ENDIF]

### Conclusie voor {lowertitle}
Op basis van de beschikbare data beoordelen wij dit aspect als **[IF Price > 0]marktconform[ELSE]nader te onderzoeken[ENDIF]**.

---
*Gegenereerd door AI Woning Rapport voor [Adres]*
"""

for i, title in titles.items():
    filename = f"hoofdstuk{i}.txt"
    path = os.path.join(rapport_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        # Custom logic for some chapters
        text = content_template.format(title=title, lowertitle=title.lower())
        f.write(text)
    print(f"Generated {filename}")
