# 4-PLANE REPORT — CHAPTERS 5-8

---

# CHAPTER 5: INDELING & POTENTIE

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Room Allocation
```
┌─────────────────────────────────────────┐
│   KAMERVERDELING (6 kamers totaal)      │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │      BEGANE GROND (geschat)     │   │
│   │  ┌──────────┬──────────────────┐│   │
│   │  │ Hal/     │    Woonkamer     ││   │
│   │  │ Entree   │    (~40-50 m²)   ││   │
│   │  ├──────────┼─────────┬────────┤│   │
│   │  │ WC │ Keuken      │ Bijkeuken││   │
│   │  └────┴─────────────┴──────────┘│   │
│   └─────────────────────────────────┘   │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │      EERSTE VERDIEPING          │   │
│   │  ┌────────┬────────┬───────────┐│   │
│   │  │ Slaap1 │ Slaap2 │ Badkamer  ││   │
│   │  ├────────┼────────┼───────────┤│   │
│   │  │ Slaap3 │ Slaap4 │ Overloop  ││   │
│   │  └────────┴────────┴───────────┘│   │
│   └─────────────────────────────────┘   │
│                                         │
│   ⚠️ LET OP: Plattegrond is SPECULATIEF │
│      Geen indeling data in registry     │
└─────────────────────────────────────────┘
```
**Data Source**: `rooms`, `bedrooms` — layout is INFERRED

### Chart 2: Space Per Person Ratio
```
┌─────────────────────────────────────────┐
│   M² PER BEWONER (4-persoons gezin)     │
│                                         │
│   Haakakker 7:  35.5 m²/persoon         │
│   ██████████████████████████████████░   │
│                                         │
│   Gemiddeld NL: 30.0 m²/persoon         │
│   █████████████████████████████░░░░░░   │
│                                         │
│   Minimum norm: 20.0 m²/persoon         │
│   ████████████████████░░░░░░░░░░░░░░░   │
│                                         │
│   Status: RUIM (+18% vs gemiddeld)      │
└─────────────────────────────────────────┘
```
**Data Source**: `living_area_m2` ÷ aangenomen gezinsgrootte

### Chart 3: Bedroom Size Estimate
```
┌─────────────────────────────────────────┐
│   GESCHATTE SLAAPKAMERGROOTTES          │
│   (142 m² - 60 m² leefruimte) ÷ 4       │
│                                         │
│   Beschikbaar voor slaapkamers: ~55 m²  │
│   Gemiddeld per slaapkamer:     ~14 m²  │
│                                         │
│   ┌───────────┬───────────────────────┐ │
│   │ <10 m²    │ Krap    ░░░░░░░░░░░░ │ │
│   │ 10-12 m²  │ Basis   ████░░░░░░░░ │ │
│   │ 12-15 m²  │ Goed    ███████▲░░░░ │ │
│   │ 15-20 m²  │ Ruim    ██████████░░ │ │
│   │ >20 m²    │ Groot   ████████████ │ │
│   └───────────┴───────────────────────┘ │
│                                         │
│   ⚠️ Schatting — bezichtiging vereist   │
└─────────────────────────────────────────┘
```
**Data Source**: Derived estimates only

### Visuals NOT Applicable

| Visual | Reason |
|--------|--------|
| Accurate floor plan | No `floor_plan` in registry |
| Room dimensions | No per-room data |
| Circulation diagram | No spatial relationships |

---

## 🟩 PLANE B — NARRATIVE REASONING (318 words)

De indeling van Haakakker 7 blijft grotendeels een raadsel op basis van de beschikbare data. Met 6 kamers waarvan 4 slaapkamers weten we wat er is, maar niet hoe het georganiseerd is. Dit hoofdstuk moet daarom opereren in een modus van geïnformeerde speculatie, met nadrukkelijke disclaimers over de onzekerheden.

**Ruimtelijke Logica van een Vrijstaande Jaren-'70 Woning**

Woningen uit 1978 volgden typisch een conservatieve indeling: hal, afgesloten woonkamer, separate keuken, en een ruime trap naar de bovenverdieping met vier slaapkamers rondom een overloop. De open keuken was nog niet mainstream; doorbraken tussen keuken en woonkamer waren een latere renovatie die veel huiseigenaren hebben uitgevoerd. Of dit bij Haakakker 7 is gebeurd, is onbekend.

**Potentie Analyse**

De 142 m² biedt significant potentieel voor herinrichting mocht de huidige indeling niet optimaal zijn. Mogelijke scenario's:

1. **Creëren van master bedroom suite**: Samenvoegen van twee slaapkamers tot een suite met en-suite badkamer
2. **Thuiswerkruimte**: Eén slaapkamer transformeren tot permanent kantoor
3. **Open woonkeuken**: Doorbraak tussen keuken en woonkamer (als niet reeds gedaan)
4. **Uitbouw begane grond**: Perceelruimte (37% bebouwd) laat uitbreiding toe

**De Bezichtiging als Cruciale Informatiebronn**

Geen enkel algoritme of databestand kan vervangen wat een fysieke bezichtiging oplevert: de lichtval door de ramen, de doorkijk tussen ruimtes, de hoogte van het plafond, de geluiden van buiten. De registry verschaft het skelet; de bezichtiging onthult het leven in de ruimte.

**Praktische Overwegingen**

Voor een gezin met jonge kinderen is de vraag of de slaapkamers op één etage liggen (praktisch) of verspreid (onpraktisch). Voor thuiswerkers is de vraag of er een afgesloten ruimte is die als kantoor kan dienen. Voor gastvrijheid-georiënteerde bewoners is de vraag of de woonkamer gracious gastvrij is. Deze vragen kan alleen de bezichtiging beantwoorden.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Known Layout Data

| KPI | Value | Source | Status |
|-----|-------|--------|--------|
| Totaal kamers | 6 | `rooms` | ✅ PRESENT |
| Slaapkamers | 4 | `bedrooms` | ✅ PRESENT |
| Overige kamers | 2 | derived | ✅ DERIVED |
| Woonoppervlak | 142 m² | `living_area_m2` | ✅ PRESENT |
| Perceeloppervlak | 380 m² | `plot_area_m2` | ✅ PRESENT |

### Unknown Layout Data

| Field | Status | Impact |
|-------|--------|--------|
| Verdiepingen | ❌ UNKNOWN | Accessibility assessment |
| Kamergroottes | ❌ UNKNOWN | Functionality assessment |
| Plattegrond | ❌ UNKNOWN | Flow assessment |
| Badkamers | ❌ UNKNOWN | Comfort level |
| Toiletten | ❌ UNKNOWN | Practicality |
| Bergruimte | ❌ UNKNOWN | Storage capacity |
| Garage | ❌ UNKNOWN | Parking/workshop potential |
| Kelder | ❌ UNKNOWN | Additional space |
| Zolder | ❌ UNKNOWN | Expansion potential |

### Estimated Space Allocation (Speculatief)

| Zone | Estimated m² | Percentage |
|------|-------------|------------|
| Leefruimte (woon/keuken) | ~60 m² | 42% |
| Slaapkamers (4x) | ~55 m² | 39% |
| Badkamer(s) | ~15 m² | 11% |
| Hal/trap/overloop | ~12 m² | 8% |

### Uitbreidingspotentieel

| Option | Feasibility | Estimated Cost |
|--------|-------------|----------------|
| Uitbouw begane grond | ✅ Mogelijk (63% onbebouwd) | €1.500-€2.500/m² |
| Dakopbouw/-kapverhoging | ⚠️ Vergunningafhankelijk | €2.000-€3.000/m² |
| Aanbouw serre | ✅ Waarschijnlijk mogelijk | €800-€1.500/m² |
| Garage conversie | ❓ Onbekend of garage aanwezig | Variable |

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Perspective

**Layout Satisfaction**: ⚠️ UNCERTAIN (cannot assess)

**Key Questions**:
1. Is er een geschikte thuiswerkplek? (belangrijk post-COVID)
2. Hoeveelheid natuurlijk licht? (energiebesparing, welbevinden)
3. Slaapkamers groot genoeg voor dubbelbedden + kasten?
4. Bergruimte voor gereedschap, fietsen, seizoensartikelen?

**Must-Haves**:
- Minimaal één werkruimte die afsluitbaar is
- Adequate bergruimte (zolder of garage of schuur)
- Logische verkeersstroom (geen doorkamers)

**Assessment**: "Kan niet beoordelen zonder bezichtiging. Dit is hét hoofdstuk waar de registry volledig tekortschiet."

### Petra's Perspective

**Layout Satisfaction**: 🌟 OPTIMISTIC (based on numbers)

**Key Questions**:
1. Kan de keuken open naar tuin/buiten? (binnen-buiten connectie)
2. Sfeer van de woonkamer? (licht, hoogte, gezelligheid)
3. Is master bedroom ruim genoeg voor hotelgevoel?
4. Hoe voelt de entree? (eerste indruk, welkom)

**Must-Haves**:
- Lichte, ruime leefruimte
- Visuele verbinding met tuin
- Slaapkamer die rustgevend aanvoelt
- Badkamer met daglicht

**Assessment**: "142 m² met 4 slaapkamers klinkt als droomwoning. De indeling kunnen we aanpassen; de ruimte en het perceel zijn gegeven."

### Comparison

| Aspect | Marcel | Petra | Status |
|--------|--------|-------|--------|
| Kamergrootte | Functioneel | Ruimtegevoel | ↔️ DIFFERENT LENS |
| Indeling | Praktisch | Sfeer | ↔️ COMPLEMENTARY |
| Thuiswerk | Kritisch | Secundair | ⚡ TENSION |
| Verbouwpotentie | Kost geld | Kans | ↔️ COMPLEMENTARY |

### Joint Assessment

Beiden kunnen dit hoofdstuk niet volledig beoordelen zonder bezichtiging. De consensus is dat de kwantitatieve basis (142 m², 6 kamers) veelbelovend is, maar kwalitatieve beoordeling essentieel is. Dit moet een primair focusgebied zijn bij bezichtiging.

---

# CHAPTER 6: AFWERKING & ONDERHOUD

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Maintenance Lifecycle Position
```
┌─────────────────────────────────────────┐
│   ONDERHOUDSCYCLUS POSITIE              │
│                                         │
│   Bouwjaar: 1978    Leeftijd: 47 jaar   │
│                                         │
│   COMPONENT LEVENSDUUR (gemiddeld)      │
│   ─────────────────────────────────     │
│   Dak          30-50 jr  ████████▒▒     │
│   Kozijnen     25-40 jr  ██████████     │
│   Keuken       15-25 jr  ██████████     │
│   Badkamer     15-25 jr  ██████████     │
│   CV-ketel     15-20 jr  ██████████     │
│   Schilderwerk  5-8 jr   ██████████     │
│                                         │
│   ▒ = Einde levensduur bereikt/nabij    │
│   (aannemend geen vervanging sinds '78) │
│                                         │
│   ⚠️ MEESTE COMPONENTEN OVER CYCLUS     │
└─────────────────────────────────────────┘
```
**Data Source**: `build_year` + standaard levensduurcycli

### Chart 2: Unknown Interior Status
```
┌─────────────────────────────────────────┐
│   INTERIEUR STATUS — VOLLEDIGE BLINDVLEK│
│                                         │
│   Keuken staat     ░░░░░░░░░░ ONBEKEND  │
│   Badkamer staat   ░░░░░░░░░░ ONBEKEND  │
│   Vloeren          ░░░░░░░░░░ ONBEKEND  │
│   Muur afwerking   ░░░░░░░░░░ ONBEKEND  │
│   Trappenhuis      ░░░░░░░░░░ ONBEKEND  │
│   Schilderwerk     ░░░░░░░░░░ ONBEKEND  │
│                                         │
│   Data beschikbaar: 0%                  │
│                                         │
│   Alle interieur-oordelen vereisen      │
│   fysieke bezichtiging                  │
└─────────────────────────────────────────┘
```
**Data Source**: Registry completeness check

### Visuals NOT Applicable

| Visual | Reason |
|--------|--------|
| Photo gallery | No media in registry |
| Condition scoring | No inspection data |
| Renovation timeline | No historical data |

---

## 🟩 PLANE B — NARRATIVE REASONING (302 words)

Afwerking en onderhoudsstaat zijn de meest tastbare aspecten van een woning — en tegelijkertijd de aspecten waar de registry volledig zwijgt. Dit creëert een paradoxale situatie: het hoofdstuk dat de meest directe impact heeft op woonbeleving en korte-termijn kosten kan niet op basis van data worden geschreven.

**Wat de Leeftijd Impliceert**

Een woning van 47 jaar heeft meerdere onderhoudscycli doorlopen. Keuken, badkamer, CV-installatie hebben typisch levensduren van 15-25 jaar, wat betekent dat deze componenten idealiter 2-3 keer vervangen hadden moeten zijn. De kwaliteit van deze vervangingen — en of ze überhaupt hebben plaatsgevonden — bepaalt de huidige staat.

**Scenario's**

1. **Best case**: Eigenaren hebben regelmatig geïnvesteerd, recente keuken, moderne badkamer, nieuwe CV. Woning is instapklaar.
2. **Gemiddeld case**: Sommige updates (keuken ooit vernieuwd, badkamer gedateerd maar functioneel). Geleidelijke modernisering nodig.
3. **Worst case**: Tijd-capsule uit 1978. Alles origineel, alles aan vervanging toe. Investering €50.000+ nodig voor moderne staat.

**De Funda Foto's als Informatiebronn**

De Funda-advertentie bevat waarschijnlijk foto's die de basisconditie tonen. Deze zijn niet in de registry opgenomen maar zijn essentieel voor eerste indrukvorming. Echter: Funda-foto's zijn professioneel gestaged en tonen de woning op zijn best. Bezichtiging blijft nodig voor realistisch beeld.

**Financiële Buffer Noodzaak**

Gegeven de volledige onzekerheid rond afwerkingsstaat, is een financiële buffer essentieel. Vuistregel bij woningen van deze leeftijd zonder duidelijke moderniseringshistorie: reken op €10.000-€30.000 aan noodzakelijke of gewenste upgrades in de eerste jaren. Dit is geen pessimisme maar realisme.

**Bezichtiging Focuspunten**

Bij bezichtiging specifiek letten op: staat keukenapparatuur, waterleidinggeluid (oud leidingwerk?), vochtplekken (daklekkage, opstijgend vocht?), schilderwerkconditie, deurenkwaliteit, en algehele "opgeruimdheid" die eigenaarstrots indiceert.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Known Data

| KPI | Value | Source | Status |
|-----|-------|--------|--------|
| Bouwjaar | 1978 | `build_year` | ✅ PRESENT |
| Leeftijd | 47 jaar | derived | ✅ DERIVED |

### Unknown Interior/Finish Data

| Field | Status | Typical Cost if Replace |
|-------|--------|-------------------------|
| Keuken type | ❌ UNKNOWN | €8.000-€25.000 |
| Keuken leeftijd | ❌ UNKNOWN | — |
| Badkamer type | ❌ UNKNOWN | €5.000-€15.000 |
| Badkamer leeftijd | ❌ UNKNOWN | — |
| Vloertype | ❌ UNKNOWN | €50-€150/m² |
| Vloerconditie | ❌ UNKNOWN | — |
| Binnenschilderwerk | ❌ UNKNOWN | €3.000-€8.000 |
| Wandafwerking | ❌ UNKNOWN | Variable |
| Trapconditie | ❌ UNKNOWN | €2.000-€5.000 |
| Binnendeuren | ❌ UNKNOWN | €200-€500/stuk |
| Stopcontacten/schakelaars | ❌ UNKNOWN | €500-€2.000 |

### Onderhoudscyclus Referenties

| Component | Typische Levensduur | Status bij 47jr |
|-----------|--------------------|--------------------|
| Dak (pannen) | 40-60 jaar | ⚠️ Mogelijk over cyclus |
| Dak (bitumen) | 20-30 jaar | 🔴 Over cyclus |
| Kozijnen (hout) | 30-50 jaar | ⚠️ Mogelijk over cyclus |
| Kozijnen (kunststof) | 40-50 jaar | ✅ Als vervangen OK |
| Keuken | 15-25 jaar | 🔴 2-3x cyclus verstreken |
| Badkamer | 20-30 jaar | 🔴 1-2x cyclus verstreken |
| CV-ketel | 15-20 jaar | 🔴 2-3x cyclus verstreken |
| Elektra | 30-40 jaar | ⚠️ Mogelijk aan vervanging toe |

### Geschat Renovatiebudget Scenario's

| Scenario | Keuken | Bad | Vloer | Overig | Totaal |
|----------|--------|-----|-------|--------|--------|
| Instapklaar | €0 | €0 | €0 | €0 | €0 |
| Minimaal | €0 | €0 | €5k | €3k | €8k |
| Gemiddeld | €15k | €8k | €8k | €5k | €36k |
| Volledig | €25k | €15k | €15k | €15k | €70k |

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Perspective

**Finish Priority**: ⚠️ HIGH (cost control focus)

**Key Concerns**:
1. Verborgen gebreken kunnen budget ontregelen
2. Gedateerde elektra = vervangingsnoodzaak
3. Oude badkamer/keuken = onvermijdelijke kosten
4. Schilderwerkstaat = eigenaarsverzorging indicator

**Approach**:
"Ik wil precies weten wat de staat is vóór we een bod doen. Elke verassing na aankoop is te voorkomen met grondige inspectie nu."

**Budget Reserve**: Wil €20.000-€30.000 apart houden voor "verrassingen"

### Petra's Perspective

**Finish Priority**: 🟢 MODERATE (cosmetic focus)

**Key Observations**:
1. Ziet renovatie als kans om eigen stempel te drukken
2. Gedateerde keuken = excuus voor droomkeuken
3. Oude badkamer = wellness-project
4. Afwerking is veranderbaar; locatie en ruimte niet

**Approach**:
"Als de basis goed is (constructie, locatie, ruimte), dan maken we de afwerking naar eigen smaak. Dat is deel van het avontuur."

**Budget View**: Wil gefaseerd investeren over meerdere jaren

### Tension Analysis

| Topic | Marcel | Petra | Resolution |
|-------|--------|-------|------------|
| Onbekende staat | Risico | Avontuur | Keuring geeft zekerheid |
| Renovatiebudget | Nu reserveren | Later faseren | Hybrid: kern nu, cosmetisch later |
| Prioriteiten | Noodzakelijk | Gewenst | Eerst functie, dan vorm |

### Joint Position

Beiden erkennen dat afwerkingsstaat alleen via bezichtiging te beoordelen is. Afspraak: bij bezichtiging systematisch elke ruimte beoordelen op staat, foto's maken, en schatting maken van noodzakelijke vs gewenste investeringen. Bouwkundige keuring vult dit aan met professionele blik.

---

# CHAPTER 7: TUIN & BUITENRUIMTE

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Plot Utilization
```
┌─────────────────────────────────────────┐
│   PERCEELVERDELING 380 m²               │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│   │
│   │░░░░░░░░░░┌───────────┐░░░░░░░░░░│   │
│   │░░░TUIN░░░│           │░░░TUIN░░░│   │
│   │░░░░░░░░░░│  WONING   │░░░░░░░░░░│   │
│   │░░~240 m²░│  ~140 m²  │░░░░░░░░░░│   │
│   │░░░░░░░░░░│           │░░░░░░░░░░│   │
│   │░░░░░░░░░░└───────────┘░░░░░░░░░░│   │
│   │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│   │
│   └─────────────────────────────────┘   │
│                                         │
│   Bebouwd: 37% │ Onbebouwd: 63%         │
│                                         │
│   ⚠️ Layout is SPECULATIEF              │
└─────────────────────────────────────────┘
```
**Data Source**: `plot_area_m2`, `living_area_m2`

### Chart 2: Garden Size Comparison
```
┌─────────────────────────────────────────┐
│   TUINGROOTTE VERGELIJKING              │
│                                         │
│   Haakakker 7:  ~240 m²                 │
│   ████████████████████████████████████  │
│                                         │
│   Gem. vrijstaand NL: ~200 m²           │
│   █████████████████████████████░░░░░░   │
│                                         │
│   Gem. rijtjeswoning NL: ~60 m²         │
│   █████████████░░░░░░░░░░░░░░░░░░░░░░   │
│                                         │
│   Status: 20% GROTER dan gem. vrijstaand│
└─────────────────────────────────────────┘
```
**Data Source**: `plot_area_m2` - estimated building footprint

### Chart 3: Orientation Unknown
```
┌─────────────────────────────────────────┐
│   TUIN ORIËNTATIE                       │
│                                         │
│              N                          │
│              ▲                          │
│              │                          │
│      W ◄─────┼─────► O                  │
│              │                          │
│              ▼                          │
│              Z                          │
│                                         │
│   Achtertuin oriëntatie: ❓ ONBEKEND    │
│                                         │
│   • Zuid = optimale zon                 │
│   • West = avondzon                     │
│   • Noord = schaduw (koel zomer)        │
│   • Oost = ochtendzon                   │
│                                         │
│   ⚠️ Oriëntatie niet in registry        │
└─────────────────────────────────────────┘
```
**Data Source**: NOT AVAILABLE

### Visuals NOT Applicable

| Visual | Reason |
|--------|--------|
| Satellite view | No geo data |
| Garden layout | No plan in registry |
| Planting plan | No vegetation data |

---

## 🟩 PLANE B — NARRATIVE REASONING (311 words)

De buitenruimte van Haakakker 7 is potentieel een van de sterkste troeven van deze woning. Met een geschatte 240 m² tuinoppervlak — afgeleid van het 380 m² perceel minus bebouwing — behoort deze tuin tot het bovengemiddelde segment. In een era waarin buitenruimte een premium commodity is geworden, is dit geen triviale eigenschap.

**Kwantiteit versus Kwaliteit**

De registry verschaft de kwantiteit (vierkante meters) maar zwijgt over kwaliteit. Een tuin van 240 m² kan variëren van een verwilderde jungle die duizenden euro's snoeiwerk vraagt, tot een professioneel aangelegde oase die direct bruikbaar is. De oriëntatie — wellicht de meest cruciale tuinkwaliteit — is onbekend. Een noordtuin van 240 m² is minder waard dan een zuidtuin van 150 m².

**Mogelijkheden**

De omvang biedt significante mogelijkheden:
- **Terras**: Ruimte voor substantieel terras (30-50 m²) met behoud van groen
- **Gazon**: Speelruimte voor kinderen, sports, recreatie
- **Moestuin**: Trend in stijgende lijn; ruimte voor substantieel project
- **Berging/schuur**: Als niet aanwezig, ruimte voor toevoeging
- **Zwembad/jacuzzi**: Fysiek mogelijk bij deze perceelgrootte

**Onderhoudslast**

Keerzijde: een tuin van 240 m² vraagt onderhoud. Rekening houden met:
- Grasmaaien: wekelijks in seizoen
- Snoeien: jaarlijks voor hagen en struiken
- Bladruimen: herfst
- Onkruidbestrijding: doorlopend

Dit is arbeid of kosten (hovenier €30-€50/uur). Voor wie geen tuinliefhebber is, kan een grote tuin een last worden.

**Privacy-Overwegingen**

Een vrijstaande woning met ruime tuin suggereert goede privacy, maar dit is afhankelijk van beplanting, schuttingen, en hoogte naburige bebouwing. De advertentiefoto's en bezichtiging moeten dit verduidelijken.

**Bezichtiging Checklist voor Tuin**
- Oriëntatie achtertuin bepalen (kompas-app)
- Staat verharding en terras
- Leeftijd en conditie beplanting
- Privacy van buren
- Drainage/waterafvoer bij regen

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Known Outdoor Data

| KPI | Value | Source | Status |
|-----|-------|--------|--------|
| Perceeloppervlak | 380 m² | `plot_area_m2` | ✅ PRESENT |
| Geschat buitenruimte | ~240 m² | derived | ✅ DERIVED |
| Bebouwingspercentage | 37% | derived | ✅ DERIVED |
| Onbebouwd percentage | 63% | derived | ✅ DERIVED |

### Unknown Outdoor Data

| Field | Status | Impact |
|-------|--------|--------|
| Tuin oriëntatie | ❌ UNKNOWN | Zonlicht, bruikbaarheid |
| Tuin voor/achter verdeling | ❌ UNKNOWN | Privacy, functie |
| Verharding m² | ❌ UNKNOWN | Onderhoud, waterafvoer |
| Berging/schuur | ❌ UNKNOWN | Opslag, praktisch |
| Garage | ❌ UNKNOWN | Parkeren, werkplaats |
| Oprit | ❌ UNKNOWN | Parkeren, toegang |
| Erfafscheiding | ❌ UNKNOWN | Privacy, onderhoudslast |
| staat beplanting | ❌ UNKNOWN | Onderhoudskosten |
| Zwembad/vijver | ❌ UNKNOWN | Onderhoud, waarde |

### Tuinoppervlak Referenties

| Type woning | Gemiddeld perceel | Gem. tuin |
|-------------|-------------------|-----------|
| Appartement | 0 m² | 0 m² |
| Tussenwoning | 150 m² | 50-80 m² |
| Hoekwoning | 200 m² | 80-120 m² |
| Twee-onder-één-kap | 300 m² | 150-200 m² |
| **Vrijstaand** | **400 m²** | **200-250 m²** |
| **Haakakker 7** | **380 m²** | **~240 m² (est.)** |

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Perspective

**Outdoor Priority**: 🟢 MODERATE

**Key Observations**:
- Tuin is ruim voldoende voor gezinsgebruik
- Vraagt wel onderhoudscommitment
- Bergruimte voor gereedschap/fietsen belangrijk
- Privacy van belang voor thuisgevoel

**Practical Questions**:
1. Is er een schuur/berging voor gereedschap en fietsen?
2. Hoe is de erfafscheiding (privacy, onderhoud)?
3. Is er ruimte voor werkplaats of hobbyruimte?
4. Hoe is de drainage bij harde regenval?

**Assessment**: "Grote tuin is mooi, maar niet mijn primaire drijfveer. Belangrijker dat de praktische zaken kloppen."

### Petra's Perspective

**Outdoor Priority**: 🌟 HIGH

**Key Observations**:
- Droom: buiten ontbijten, tuinieren, kinderen laten spelen
- 240 m² is meer dan gehoopt
- Oriëntatie bepaalt sfeer — moet zuidwest of west zijn voor avondzon
- Wil sfeervolle tuin, niet sportveldje

**Emotional Questions**:
1. Voelt de tuin als een verlengde van het huis?
2. Is er plek voor buiten-eethoek met privacy?
3. Hoe is het uitzicht vanuit de woonkamer naar de tuin?
4. Zijn er volwassen bomen (schaduw, karakter)?

**Assessment**: "De tuin kan de dealmaker zijn. Als de tuin klopt, klopt het huis."

### Tension Points

| Aspect | Marcel | Petra | Resolution |
|--------|--------|-------|------------|
| Tuingrootte | Functioneel | Enthousiast | Aligned (groot is goed) |
| Onderhoud | Wie doet het? | Deel van leefplezier | Te bespreken |
| Investering tuin | Beperken | Sfeer creëren | Gefaseerd |
| Prioriteit | Secundair | Primair | ⚡ TENSION |

### Joint Assessment

Petra's enthousiasme voor de tuin moet gebalanceerd worden door Marcels praktische blik. Tijdens bezichtiging: beiden beoordelen, Petra op sfeer en potentie, Marcel op onderhoud en praktijk. Als tuin aan beider criteria voldoet, is dit een sterk pluspunt.

---

# CHAPTER 8: LOCATIE & BEREIKBAARHEID

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Location Context
```
┌─────────────────────────────────────────┐
│   MIERLO — GEOGRAFISCHE CONTEXT         │
│                                         │
│   Noord-Brabant, Gemeente Geldrop-Mierlo│
│                                         │
│           ┌─────────────────────┐       │
│           │    EINDHOVEN        │       │
│           │    (15 km →)        │       │
│           │         ↑           │       │
│           │         │           │       │
│           │    GELDROP          │       │
│           │      (3 km →)       │       │
│           │         ↑           │       │
│           │         │           │       │
│           │  ★ MIERLO           │       │
│           │    Haakakker        │       │
│           │                     │       │
│           └─────────────────────┘       │
│                                         │
│   Karakter: Dorps, rustig, groen        │
└─────────────────────────────────────────┘
```
**Data Source**: `address` (parsed location)

### Chart 2: Estimated Distances
```
┌─────────────────────────────────────────┐
│   GESCHATTE AFSTANDEN (indicatief)      │
│                                         │
│   Centrum Mierlo      ~1-2 km           │
│   ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                         │
│   NS Station Geldrop  ~5 km             │
│   █████████████░░░░░░░░░░░░░░░░░░░░░░░  │
│                                         │
│   Centrum Eindhoven   ~15 km            │
│   ████████████████████████████████████  │
│                                         │
│   A67 Afrit           ~3-5 km           │
│   ██████████████░░░░░░░░░░░░░░░░░░░░░░  │
│                                         │
│   ⚠️ Afstanden zijn schattingen         │
│      Geen exacte data in registry       │
└─────────────────────────────────────────┘
```
**Data Source**: Derived from `address` + algemene kennis

### Chart 3: Location Attribute Matrix
```
┌─────────────────────────────────────────┐
│   LOCATIE KENMERKEN MATRIX              │
│                                         │
│                    Gunstig → Ongunstig  │
│   Rust             ████████████░░ ++++  │
│   Ruimte           ████████████░░ ++++  │
│   Groen            ███████████░░░ +++   │
│   Winkels nabij    ██████░░░░░░░░ ++    │
│   OV bereikbaar    █████░░░░░░░░░ +     │
│   Grote stad nabij ███████████░░░ +++   │
│   Snelweg nabij    ████████░░░░░░ ++    │
│                                         │
│   Profiel: Dorps wonen met stad bereik  │
└─────────────────────────────────────────┘
```
**Data Source**: General knowledge (not in registry)

### Visuals NOT Applicable

| Visual | Reason |
|--------|--------|
| Detailed map | No geo-coordinates |
| Walk score | No API data |
| Transit score | No OV data |
| Crime statistics | No veiligheidsdata |

---

## 🟩 PLANE B — NARRATIVE REASONING (329 words)

Mierlo is een dorp met circa 11.000 inwoners, gelegen in de gemeente Geldrop-Mierlo in Noord-Brabant. De locatie vertegenwoordigt een klassiek "best of both worlds" scenario: dorpse rust en ruimte, met stedelijke voorzieningen van Eindhoven op acceptabele afstand. Of deze combinatie optimaal is, hangt af van lifestyle en prioriteiten.

**Het Dorpsprofiel**

Mierlo biedt wat kleinere kernen typisch bieden: sociale cohesie, veiligheidsgevoel, ruimte voor kinderen om buiten te spelen, en lagere grondprijzen dan stedelijk gebied. De keerzijde: beperkte lokale voorzieningen, auto-afhankelijkheid voor veel activiteiten, en potentieel minder cultureel aanbod.

**Connectiviteit naar Eindhoven**

De nabijheid van Eindhoven (15 km) is een strategisch voordeel. De Brainport-regio is economisch sterk, met voorzieningen, werkgelegenheid, en cultureel aanbod van een stad. Per auto is Eindhoven in 15-25 minuten bereikbaar; per OV (bus via Geldrop naar trein) is de reis langer en minder frequent. Voor wie afhankelijk is van OV, is Mierlo geen ideale locatie.

**De A67 Factor**

De nabijheid van de A67 biedt snelle verbindingen naar de rest van Brabant en richting Venlo/Duitsland. Dit is positief voor forenzen met flexibele werklocaties, maar introduceert ook potentieel geluids- of luchtkwaliteitoverwegingen afhankelijk van de exacte afstand tot de snelweg.

**Buurtspecifieke Overwegingen**

"Haakakker" als straatnaam klinkt als een rustige woonwijk — geen doorgaande weg of winkelstrip. De exacte positie binnen Mierlo is echter niet uit de registry af te leiden. Bij bezichtiging letten op: verkeersintensiteit, aanwezigheid scholen in de buurt (verkeerspiek schooltijden), ligging ten opzichte van industrieterreinen, en algehele buurtkarakter.

**Toekomstscenario's**

Mierlo profiteert van de regionale groei rond Eindhoven. Woningwaardestijging in Brainport-gemeenten overtreft het landelijk gemiddelde. Dit maakt de locatie interessant vanuit investeringsperspectief, zij het met de kanttekening dat binnenstedelijke locaties doorgaans sneller appreciëren dan dorpskernen.

**Wat Ontbreekt**

De registry bevat geen voorzieningen-data (scholen, winkels, zorg), geen bereikbaarheidsscores, en geen buurtstatistieken. Dit moet via bezichtiging en aanvullend onderzoek worden ingevuld.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Known Location Data

| KPI | Value | Source | Status |
|-----|-------|--------|--------|
| Adres | Haakakker 7 | `address` | ✅ PRESENT |
| Plaats | Mierlo | `address` | ✅ PRESENT |
| Gemeente | Geldrop-Mierlo | derived | ⚠️ INFERRED |
| Provincie | Noord-Brabant | derived | ⚠️ INFERRED |

### Unknown Location Data

| Field | Status | Typical Sources |
|-------|--------|-----------------|
| Exacte coördinaten | ❌ UNKNOWN | Kadaster, Maps |
| Afstand centrum | ❌ UNKNOWN | Maps |
| Afstand OV | ❌ UNKNOWN | 9292.nl |
| Afstand snelweg | ❌ UNKNOWN | Maps |
| Afstand basisschool | ❌ UNKNOWN | Scholenopdekaart.nl |
| Afstand supermarkt | ❌ UNKNOWN | Maps |
| Afstand huisarts | ❌ UNKNOWN | Zorgkaart |
| Geluidsbelasting | ❌ UNKNOWN | RIVM, Atlas LG |
| Luchtkwaliteit | ❌ UNKNOWN | RIVM |
| Overstromingsrisico | ❌ UNKNOWN | Klimaateffectatlas |

### Mierlo Algemene Statistieken (Externe Referentie)

| Metric | Value | Bron |
|--------|-------|------|
| Inwoners | ~11.000 | CBS 2023 |
| Gemeente | Geldrop-Mierlo | |
| Afstand Eindhoven | ~15 km | |
| Karakter | Forensendorp | |
| Woningmarkt druk | Hoog | Brainport-effect |

### Bereikbaarheid Indicaties (Schattingen)

| Bestemming | Afstand | Auto | OV |
|------------|---------|------|-----|
| Centrum Mierlo | ~1-2 km | 3-5 min | 5-10 min (fiets) |
| Station Geldrop | ~5 km | 8-10 min | 15-20 min (bus) |
| Eindhoven CS | ~15 km | 15-25 min | 35-45 min |
| Eindhoven Airport | ~10 km | 10-15 min | 30-40 min |
| A67 afrit | ~3-5 km | 5-8 min | N/A |

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Perspective

**Location Priority**: 🟢 MODERATE-POSITIVE

**Key Observations**:
- Mierlo is acceptabel als woonplaats
- Afstand tot werk/activiteiten te evalueren
- Auto vereist — geen issue gegeven leefstijl
- Snelwegbereikbaarheid positief voor flexibiliteit

**Practical Concerns**:
1. Wat is de woon-werk afstand concreet?
2. Zijn er technische beroepsvoorzieningen in de regio?
3. Hoe is de internetconnectiviteit (glasvezel)?
4. Parkeerdruk in de straat?

**Assessment**: "Locatie is geen dealbreaker, geen dealmaker. Functioneel acceptabel indien praktische zaken kloppen."

### Petra's Perspective

**Location Priority**: 🌟 HIGH-POSITIVE

**Key Observations**:
- Dorpse sfeer is ideaal voor gezinsopbouw
- Minder stress dan stedelijk wonen
- Natuur en groen voor kinderen
- Brabantse gezelligheid

**Emotional Concerns**:
1. Voelt het dorp levendig of uitgestorven?
2. Zijn er speeltuinen, parken, wandelmogelijkheden?
3. Hoe is het sociaal weefsel — buren, verenigingsleven?
4. Zijn er jonge gezinnen in de buurt?

**Assessment**: "Mierlo past perfect bij het leven dat ik voor me zie. Rustig opgroeien, ruimte, maar Eindhoven voor cultuur als ik wil."

### Alignment Analysis

| Aspect | Marcel | Petra | Status |
|--------|--------|-------|--------|
| Dorpskarakter | Neutraal | Positief | ↔️ COMPLEMENTARY |
| Auto-afhankelijk | Geen probleem | Geen probleem | ✅ ALIGNED |
| Eindhoven nabij | Praktisch | Cultureel | ✅ ALIGNED |
| Voorzieningen | Functioneel | Sfeer | ↔️ DIFFERENT LENS |

### Joint Position

Locatie is acceptabel tot positief voor beiden. Geen dealbreakers geïdentificeerd op basis van algemene buurtkennis. Bezichtiging moet bevestigen:
- Directe straat-beleving (rust vs. doorgaand)
- Buurkarakter (verzorgd, sociaal, veilig)
- Bereikbaarheid van dagelijkse voorzieningen

Dit is een hoofdstuk waar aanvullend (online) onderzoek zinvol is: Google Maps verkenning, Funda-buurtprofiel, lokale forumberichten.
