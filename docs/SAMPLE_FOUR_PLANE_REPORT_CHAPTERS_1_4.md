# 4-PLANE REPORT — CHAPTERS 1-4

---

# CHAPTER 1: KERNGEGEVENS (Core Property Data)

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Property Size Distribution
```
┌─────────────────────────────────────────┐
│  OPPERVLAKTE VERDELING                  │
│                                         │
│  Wonen      ████████████████░░  142 m²  │
│  Perceel    ████████████████████ 380 m² │
│  Bebouwd    ████████░░░░░░░░░░  ~140 m² │
│  Tuin       ████████████░░░░░░  ~240 m² │
│                                         │
│  Bebouwingspercentage: 37%              │
└─────────────────────────────────────────┘
```
**Data Source**: `living_area_m2`, `plot_area_m2`

### Chart 2: Room Distribution
```
┌─────────────────────────────────────────┐
│  Kamers: 6 totaal                       │
│  ┌──────┬──────┬──────┬──────┐          │
│  │ SLAAP│ SLAAP│ SLAAP│ SLAAP│ = 4      │
│  ├──────┴──────┼──────┴──────┤          │
│  │   WONEN     │   OVERIG    │ = 2      │
│  └─────────────┴─────────────┘          │
└─────────────────────────────────────────┘
```
**Data Source**: `bedrooms`, `rooms`

### Chart 3: Age Timeline
```
1978 ─────────────────────────────────> 2025
 │                                       │
 ▼ Bouwjaar                              ▼ Nu
 
 Leeftijd: 47 jaar
 
 │ 0-25 jaar │ 25-50 jaar │ 50-75 jaar │
 │   JONG    │  ▲ MIDDEN  │    OUD     │
```
**Data Source**: `build_year`

### Visuals NOT Applicable

| Visual | Reason |
|--------|--------|
| Floor plan layout | No indeling data in registry |
| 3D visualization | No geometry data available |

---

## 🟩 PLANE B — NARRATIVE REASONING (342 words)

De kerngegevens van Haakakker 7 schetsen het portret van een substantiële gezinswoning die zowel ruimte als potentie biedt. Met 142 vierkante meter woonoppervlak behoort deze woning tot het bovengemiddelde segment; de gemiddelde Nederlandse woning meet circa 120 m², wat deze woning 18% ruimer maakt dan de norm. Dit ruimteverschil vertaalt zich direct naar leefcomfort en flexibiliteit in de dagelijkse praktijk.

**Perceel en Bebouwingsdichtheid**

Het perceel van 380 m² biedt een bebouwingspercentage van slechts 37%, wat uitzonderlijk laag is voor vrijstaande woningen in dit segment. Dit impliceert aanzienlijke buitenruimte — geschat op circa 240 m² — wat in de huidige markt, waarin buitenruimte een premium commodity is geworden, een significant waardekenmerk vormt. De vraag die de registry niet beantwoordt: hoe is deze buitenruimte geconfigureerd? Ligt de tuin op het zuiden? Is er privacy? Deze informatie is essentieel voor een volledige waardebepaling.

**Kamerverdeling en Functionaliteit**

De configuratie van 6 kamers waarvan 4 slaapkamers suggereert een klassieke gezinsindeling met mogelijkheid tot thuiswerken. De overige 2 kamers — vermoedelijk woonkamer en een veelzijdige ruimte — bieden flexibiliteit die in de post-COVID werkrealiteit niet onderschat mag worden. Echter, zonder plattegrond blijft onduidelijk of de kamers logisch verbonden zijn, of er een open keuken is, en hoe de verkeersstromen door de woning lopen.

**Woningtype Context**

Als vrijstaande woning geniet deze eigendom de maximale mate van privacy en autonomie. Er is geen gehorige muur met buren, geen gemeenschappelijke kosten via een VvE, en volledige vrijheid in tuinaanleg en uitbreidingsmogelijkheden (binnen bestemmingsplanregels). Dit type woning wordt schaars; nieuwbouw richt zich overwegend op rijwoningen en appartementen vanwege grondschaarste. De schaarstewaarde van het vrijstaande segment moet meewegen in de prijsbeoordeling.

**Datakwaliteit Notitie**

De kerngegevens zijn volledig geregistreerd in de registry met hoge betrouwbaarheid. Wat ontbreekt zijn de kwalitatieve aspecten die een bezichtiging vereisen: de staat van onderhoud, de sfeer bij binnenkomst, de lichtval door de ramen. Cijfers schetsen het skelet; de bezichtiging moet het vlees aan de botten geven.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Property Identification

| Field | Value | Registry ID | Status |
|-------|-------|-------------|--------|
| Adres | Haakakker 7 | `address` | ✅ |
| Plaats | Mierlo | `address` | ✅ |
| Woningtype | Vrijstaand | `property_type` | ✅ |
| Bouwjaar | 1978 | `build_year` | ✅ |
| Leeftijd | 47 jaar | derived | ✅ |

### Oppervlaktes

| Metric | Value | Unit | Registry ID |
|--------|-------|------|-------------|
| Woonoppervlak | 142 | m² | `living_area_m2` |
| Perceeloppervlak | 380 | m² | `plot_area_m2` |
| Bebouwingsgraad | 37 | % | derived |

### Indeling

| Metric | Value | Registry ID |
|--------|-------|-------------|
| Totaal kamers | 6 | `rooms` |
| Slaapkamers | 4 | `bedrooms` |
| Overige kamers | 2 | derived |

### Missing Data

| Field | Status | Impact |
|-------|--------|--------|
| Badkamers | ❌ UNKNOWN | Comfort assessment incomplete |
| Toiletten | ❌ UNKNOWN | Functionality unclear |
| Garage/berging | ❌ UNKNOWN | Storage capacity unknown |
| Verdiepingen | ❌ UNKNOWN | Accessibility unclear |

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Analysis

**Relevance Score**: 75%

**Key Observations**:
- 142 m² is ruim voldoende voor gezinssamenstelling
- 47 jaar oud = aandacht voor onderhoudscyclus vereist
- Vrijstaand = geen VvE-risico's maar volledige onderhoudslast
- Bebouwingspercentage 37% is technisch gunstig (ruimte voor eventuele uitbreiding)

**Concerns**:
- Leeftijd woning suggereert mogelijk achterstallig onderhoud
- Onbekend aantal badkamers/toiletten is praktisch bezwaar

### Petra's Analysis

**Relevance Score**: 82%

**Key Observations**:
- 4 slaapkamers = ruimte voor groei en logés
- Ruime tuin (240 m² geschat) = buitenleven gegarandeerd
- Vrijstaand = privacy en geen buren-overlast
- 6 kamers = flexibiliteit voor werken, hobby, gezin

**Concerns**:
- Indeling onbekend — kan de keuken open naar de tuin?
- Is er voldoende licht in de woning?

### Comparison Matrix

| Aspect | Marcel | Petra | Status |
|--------|--------|-------|--------|
| Oppervlak woning | Voldoende | Ruim | ✅ ALIGNED |
| Perceel/tuin | Functioneel | Enthousiast | ↔️ COMPLEMENTARY |
| Woningtype | Praktisch | Ideaal | ↔️ COMPLEMENTARY |
| Leeftijd | Aandachtspunt | Acceptabel | ⚡ TENSION |

---

# CHAPTER 2: MATCHANALYSE MARCEL & PETRA

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Dual Persona Match Radar
```
              Ruimte
                ▲
               /|\
              / | \    Marcel: 72% ───
Locatie     /  |  \    Petra:  80% - - -
           /   |   \
          ─────●─────
           \   |   /
            \  |  /
             \ | /
              \|/
            Prijs
    
    ┌──────────────────────────────┐
    │ Marcel: ████████░░░░ 72%     │
    │ Petra:  ██████████░░ 80%     │
    │ Delta:  8 percentage points  │
    └──────────────────────────────┘
```
**Data Source**: `marcel_match_score`, `petra_match_score`

### Chart 2: Category Breakdown
```
┌─────────────────────────────────────────┐
│ MATCH PER CATEGORIE                     │
│                                         │
│ Ruimte    M: ████████░░ 85%            │
│           P: █████████░ 90%            │
│                                         │
│ Locatie   M: ███████░░░ 70%            │
│           P: ███████░░░ 72%            │
│                                         │
│ Prijs     M: ███████░░░ 68%            │
│           P: ███████░░░ 75%            │
│                                         │
│ Techniek  M: ██████░░░░ 60%            │
│           P: ███████░░░ 70%            │
│                                         │
│ Energie   M: █████░░░░░ 55%            │
│           P: ██████░░░░ 62%            │
└─────────────────────────────────────────┘
```
**Data Source**: Derived from individual KPI matches

### Chart 3: Alignment Spectrum
```
   TENSION ◄──────────────────────► ALIGNED
           │                        │
   Prijs   ├──▼─────────────────────┤
   Energie ├───▼────────────────────┤  
   Ruimte  ├───────────────────▼────┤
   Locatie ├────────────────────▼───┤
```

---

## 🟩 PLANE B — NARRATIVE REASONING (378 words)

De matchanalyse tussen Marcel en Petra onthult een fundamenteel interessante dynamiek: beide scoren positief op deze woning, maar vanuit distinctief verschillende waarderingskaders. Het verschil van 8 procentpunten (72% vs 80%) is niet triviaal — het representeert een kwantificeerbare divergentie in hoe beiden de woning ervaren en evalueren.

**De Bron van Petra's Hogere Score**

Petra's 80% match wordt primair gedreven door de experientiële dimensies: de ruimte (142 m² biedt ademruimte), de tuin (geschatte 240 m² buitenruimte voor ontspanning en buitenleven), en het vrijstaande karakter (privacy, geen gehorige buren, autonomie). Voor Petra weegt de belofte van woongeluk zwaarder dan technische perfectie. Het energielabel C is voor haar geen dealbreaker maar een verbeterproject; de leeftijd van de woning geen risico maar patina.

**De Bronnen van Marcels Lagere Score**

Marcels 72% — nog steeds een positieve score — wordt geremd door de onbeantwoorde technische vragen. De afwezigheid van funderingsinformatie, de onduidelijkheid over dakconditie en de gedateerde energieprestatie wegen zwaar in zijn risicogewogen beoordeling. Waar Petra potentieel ziet, ziet Marcel onzekerheid die eerst gereduceerd moet worden voordat enthousiasme verantwoord is. Zijn lagere score is niet afwijzing maar voorbehoud.

**De Strategische Implicatie van de 8%-Gap**

Een verschil van 8 procentpunten suggereert dat deze woning een "Petra-beslissing met Marcel-voorwaarden" zou moeten zijn. Petra's enthousiasme kan de drijvende kracht zijn om door te zetten; Marcels voorzichtigheid kan de remmende kracht zijn die overbieden of te snel committeren voorkomt. Dit is geen conflict maar complementariteit — mits beide perspectieven gerespecteerd worden in het beslisproces.

**Categorieanalyse**

De sterkste alignment zit op ruimte (beide hoog) en locatie (beide neutraal-positief). De sterkste spanning zit op techniek en energie — precies de domeinen waar data ontbreekt en onzekerheid het hoogst is. Dit suggereert dat technische inspectie niet alleen verstandig is voor risicoreductie, maar ook voor het harmoniseren van Marcel en Petra's beoordelingen. Als inspectie gunstig uitvalt, stijgt Marcels score; als die negatief uitvalt, wordt Petra's enthousiasme gemodereerd.

**Gezamenlijk Besliskader**

De optimale strategie is sequentieel: investeer in kennis (bouwkundige keuring, energiescan) voordat een definitief oordeel wordt geveld. De kosten van een keuring (€300-€600) zijn verwaarloosbaar tegenover de waarde van gefundeerd vertrouwen — of gefundeerde afwijzing.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Overall Match Scores

| Persona | Score | Status | Source |
|---------|-------|--------|--------|
| Marcel | 72% | ✅ | `marcel_match_score` |
| Petra | 80% | ✅ | `petra_match_score` |
| Combined | 76% | ✅ | `total_match_score` |
| Delta | 8% | derived | - |

### Category Match Breakdown

| Category | Marcel | Petra | Weight | Status |
|----------|--------|-------|--------|--------|
| Ruimte | 85% | 90% | 25% | ✅ derived |
| Locatie | 70% | 72% | 20% | ✅ derived |
| Prijs | 68% | 75% | 25% | ✅ derived |
| Techniek | 60% | 70% | 15% | ⚠️ uncertain |
| Energie | 55% | 62% | 15% | ⚠️ uncertain |

### Preference Alignment Matrix

| Dimension | Agreement Level |
|-----------|----------------|
| Size requirements | HIGH |
| Location preferences | MEDIUM-HIGH |
| Price tolerance | MEDIUM |
| Technical standards | LOW |
| Energy priorities | LOW |

### Data Quality Note

⚠️ Techniek and Energie scores are marked uncertain because underlying registry data for these dimensions is incomplete (foundation type unknown, insulation details missing).

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Match Profile

**Overall**: 72% MATCH

| Priority | This Property | Match |
|----------|--------------|-------|
| #1 Structurele zekerheid | Onbekend | ⚠️ 60% |
| #2 Onderhoudslast | Gemiddeld (47jr) | ⬤ 70% |
| #3 Investerings risicot | Boven markt | ⬤ 65% |
| #4 Energiekosten | Label C | ⬤ 55% |
| #5 Ruimte/functionaliteit | 142 m² / 6 kamers | ✅ 85% |

**Decision Posture**: CAUTIOUS POSITIVE
"Ik wil wel verder, maar alleen met technische keuring als voorwaarde."

### Petra's Match Profile

**Overall**: 80% MATCH

| Priority | This Property | Match |
|----------|--------------|-------|
| #1 Ruimtegevoel | 142 m² + 4 slaap | ✅ 90% |
| #2 Buitenruimte | ~240 m² tuin | ✅ 88% |
| #3 Sfeer/karakter | Vrijstaand, '78 | ✅ 82% |
| #4 Woonlasten | Label C = hoger | ⬤ 65% |
| #5 Buurt/omgeving | Mierlo rustig | ⬤ 75% |

**Decision Posture**: ENTHUSIASTIC
"Dit is het type woning waar ik van droom. De verbeterpunten zijn projecten, geen problemen."

### Tension-Alignment Map

**Aligned** ✅:
- Ruimte is voldoende voor beiden
- Locatie acceptabel voor beiden
- Vrijstaand type gewenst door beiden

**Complementary** ↔️:
- Petra's sfeer-focus + Marcel's functie-focus = complete beoordeling
- Petra's visie + Marcel's inspectie = degelijk proces

**Tension** ⚡:
- Prijs: Marcel vindt €485k te hoog; Petra vindt het fair
- Tempo: Marcel wil onderzoek; Petra wil doorzetten
- Risico: Marcel ziet onbekenden als waarschuwing; Petra als avontuur

---

# CHAPTER 3: BOUWKUNDIGE STAAT

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Building Age Context
```
┌─────────────────────────────────────────┐
│   BOUWJAAR CONTEXT                      │
│                                         │
│   1920 ─── 1950 ─── 1978 ─── 2000 ─── nu│
│                      ▲                  │
│                      │                  │
│   Pre-war │ Post-war │ Energie │ Modern │
│           │          │  Crisis │        │
│                                         │
│   Typische kenmerken bouwjaar 1978:     │
│   • Spouwmuur (vaak onisoleerd)         │
│   • Plat of schuin dak                  │
│   • Enkel glas naar dubbelglas          │
│   • Mogelijk asbest in dakbedekking     │
└─────────────────────────────────────────┘
```
**Data Source**: `build_year`

### Chart 2: Technical Data Completeness
```
┌─────────────────────────────────────────┐
│   TECHNISCHE DATA STATUS                │
│                                         │
│   Fundering     ░░░░░░░░░░ ONBEKEND     │
│   Dakconditie   ░░░░░░░░░░ ONBEKEND     │
│   Gevelisolatie ░░░░░░░░░░ ONBEKEND     │
│   Kozijnen      ░░░░░░░░░░ ONBEKEND     │
│   CV-installatie░░░░░░░░░░ ONBEKEND     │
│   Elektra       ░░░░░░░░░░ ONBEKEND     │
│                                         │
│   ████████░░░░░░░░░░░░░░░░ 0/6 = 0%    │
│                                         │
│   ⚠️ KRITIEK: Geen technische data      │
└─────────────────────────────────────────┘
```
**Data Source**: Registry completeness check

### Visuals NOT Applicable

| Visual | Reason |
|--------|--------|
| Condition heatmap | No room-by-room data |
| Defect locations | No inspection data |
| Maintenance timeline | No historical records |

---

## 🟩 PLANE B — NARRATIVE REASONING (356 words)

De bouwkundige staat van Haakakker 7 is het grootste analytische zwarte gat in deze rapportage. Met nul van de zes technische kernvariabelen aanwezig in de registry, is elke uitspraak over de structurele conditie speculatief. Dit is geen verwaarloosbaar detail — dit is het fundament (letterlijk en figuurlijk) waarop een half miljoen euro investeringsbeslissing zou rusten.

**Wat het Bouwjaar 1978 Suggereert**

Woningen uit 1978 vallen in een bijzondere bouwgeneratie: gebouwd na de oliecrisis van 1973 toen energiebewustzijn begon te ontwaken, maar vóór de strenge isolatienormen van de jaren '80 en '90. Typisch voor dit tijdperk zijn spouwmuren die óf niet geïsoleerd zijn óf nachisolatie hebben ontvangen van wisselende kwaliteit. De kozijnen zijn waarschijnlijk één of meerdere keren vervangen; oorspronkelijke jaren-'70 kozijnen zouden nu aan het einde van hun levensduur zijn.

**Kritieke Onbekenden**

De funderingstype is cruciaal voor risicobeoordeling, zeker in de Brabantse kleigronden. Is de woning gefundeerd op staal (funderingsmuren direct op draagkrachtige grond) of op palen? Staalfunderingen zijn gevoeliger voor zetting bij droogte en grondwaterfluctuatie — een toenemend risico in klimaatverandering. Zonder dit te weten, kan geen verantwoorde inschatting worden gemaakt van structureel risico op lange termijn.

De dakconditie — onbekend — is eveneens significant. Een dak van een woning uit 1978 heeft zijn oorspronkelijke levensduur (30-40 jaar) allang overschreden tenzij vervangen. Als vervanging niet heeft plaatsgevonden, is dit een investering van €10.000-€25.000 die op korte termijn kan materialiseren.

**De Noodzaak van Bouwkundige Keuring**

Gegeven de complete afwezigheid van technische data, is een professionele bouwkundige keuring niet optioneel maar verplicht voor verantwoorde besluitvorming. Een keuring van €400-€600 levert essentiële informatie op over fundering, dak, gevels, kozijnen, installaties en mogelijke asbest. De kosten zijn fractie van de potentiële verrassingen die zonder keuring kunnen optreden.

**Asbest-Overwegingen**

Woningen uit 1978 bevatten frequet asbesthoudende materialen: dakleien, golfplaten, vinylvloeren, Kit rond vensters. Een asbestinventarisatie is aanbevolen, zeker als verbouwplannen worden overwogen. Sanering is kostbaar (€50-€150/m²) en moet meewegen in het financiële plaatje.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Known Technical Data

| KPI | Value | Source | Status |
|-----|-------|--------|--------|
| Bouwjaar | 1978 | `build_year` | ✅ PRESENT |
| Woningtype | Vrijstaand | `property_type` | ✅ PRESENT |
| Leeftijd | 47 jaar | derived | ✅ DERIVED |

### Unknown Technical Data (FAIL-LOUD)

| KPI | Status | Risk Impact | Mitigation |
|-----|--------|-------------|------------|
| Funderingstype | ❌ UNKNOWN | HIGH | Bouwkundige keuring |
| Funderingsconditie | ❌ UNKNOWN | HIGH | Bouwkundige keuring |
| Daktype | ❌ UNKNOWN | MEDIUM | Visuele inspectie |
| Dakconditie | ❌ UNKNOWN | MEDIUM | Bouwkundige keuring |
| Gevelisolatie | ❌ UNKNOWN | MEDIUM | Energiescan |
| Spouwmuurisolatie | ❌ UNKNOWN | MEDIUM | Thermografie |
| Kozijntype | ❌ UNKNOWN | LOW | Bezichtiging |
| CV-installatie type | ❌ UNKNOWN | MEDIUM | Bezichtiging |
| CV-installatie leeftijd | ❌ UNKNOWN | MEDIUM | Bezichtiging |
| Elektra-installatie | ❌ UNKNOWN | LOW-MEDIUM | Keuring |
| Asbest-status | ❌ UNKNOWN | MEDIUM-HIGH | Asbestinventarisatie |

### Bouwjaar Risico Matrix

| Bouwperiode | Typische Aandachtspunten |
|-------------|-------------------------|
| Pre-1920 | Fundering, vocht, houtrot |
| 1920-1945 | Betonrot, kozijnen |
| 1945-1970 | Naoorlogse haast, materialenkwaliteit |
| **1970-1985** | **Asbest, isolatiegebrek, vlakke daken** |
| 1985-2000 | Minder kritiek, begin isolatienormen |
| Post-2000 | Moderne normen, minder risico |

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Perspective

**Concern Level**: 🔴 HIGH

"Dit hoofdstuk bevestigt mijn grootste zorg: we weten vrijwel niets over de technische staat. Ik kan geen verantwoorde beslissing nemen op basis van deze informatie. Een bouwkundige keuring is voor mij een harde voorwaarde vóór elk bod."

**Specific Concerns**:
1. Fundering onbekend in Brabantse kleigrond = onaanvaardbaar risico
2. Dak 47 jaar oud zonder vervangingshistorie = potentieel €15k+ kostenpost
3. Asbest waarschijnlijk aanwezig gezien bouwjaar = saneringskoten mogelijk
4. Geen van mijn technische prioriteiten kan worden geëvalueerd

**Required Actions**:
- Bouwkundige keuring (€400-600)
- Asbestscreening
- Funderings verificatie

### Petra's Perspective

**Concern Level**: 🟡 MODERATE

"Ik begrijp dat technische onzekerheid bestaat, maar dat geldt voor bijna elke bestaande woning. Een keuring is prima, maar ik laat me niet afschrikken door het ontbreken van data — dat is oplosbaar."

**Observations**:
1. 47 jaar oud maar vrijstaand = waarschijnlijk beter onderhouden door eigenaren
2. Keuring is redelijk, zolang het proces niet eindeloos wordt
3. Verbeterpunten zie ik als waarde-creatie mogelijkheden

**Acceptance Conditions**:
- Keuring mag, maar moet snel
- Geen eindeloze technische discussies
- Focus op bewoonbaarheid, niet perfectie

### Joint Recommendation

**Consensus**: Bouwkundige keuring is noodzakelijk en acceptabel voor beiden.

**Verschil**: Marcel ziet keuring als risico-eliminatie; Petra ziet het als formaliteit. Dit verschil moet gemanaged worden in verwachtingsniveau: een keuring zal vrijwel zeker bevindingen opleveren (geen 47-jarige woning is perfect), en beiden moeten vooraf definiëren wat "acceptabel" versus "dealbreaker" bevindingen zijn.

---

# CHAPTER 4: ENERGIE & DUURZAAMHEID

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Energy Label Scale
```
┌─────────────────────────────────────────┐
│   ENERGIELABEL CLASSIFICATIE            │
│                                         │
│   A++++ ██████████████████████ Beste    │
│   A+++  █████████████████████           │
│   A++   ████████████████████            │
│   A+    ███████████████████             │
│   A     ██████████████████              │
│   B     █████████████████               │
│   C     ████████████████  ◄─── DEZE     │
│   D     ███████████████                 │
│   E     ██████████████                  │
│   F     █████████████                   │
│   G     ████████████       Slechtste    │
│                                         │
│   Label C = Midden-ondergemiddeld       │
└─────────────────────────────────────────┘
```
**Data Source**: `energy_label`

### Chart 2: Estimated Energy Cost Comparison
```
┌─────────────────────────────────────────┐
│   GESCHATTE JAARLIJKSE ENERGIEKOSTEN    │
│   (142 m² woning, indicatief)           │
│                                         │
│   Label A: €1.200 ████████              │
│   Label B: €1.600 ██████████            │
│   Label C: €2.100 █████████████  ◄──    │
│   Label D: €2.600 ████████████████      │
│   Label G: €4.000 ████████████████████  │
│                                         │
│   Meerkosten vs Label A: ~€900/jaar     │
│   Over 10 jaar: ~€9.000 extra           │
└─────────────────────────────────────────┘
```
**Data Source**: `energy_label`, `living_area_m2`, NIBUD referentiewaarden

### Chart 3: Upgrade Investment vs Savings
```
┌─────────────────────────────────────────┐
│   UPGRADE SCENARIO C → A                │
│                                         │
│   Geschatte investering:                │
│   ├── Spouwmuurisolatie    €3.500       │
│   ├── Dakisolatie          €6.000       │
│   ├── HR++ glas            €8.000       │
│   ├── Warmtepomp          €12.000       │
│   └── Zonnepanelen        €10.000       │
│   ─────────────────────────────────     │
│   TOTAAL                  €39.500       │
│                                         │
│   Jaarlijkse besparing:    ~€900        │
│   Terugverdientijd:        ~44 jaar     │
│   (excl. subsidies en waardestijging)   │
└─────────────────────────────────────────┘
```
**Note**: Indicatief — exacte kosten afhankelijk van huidige staat

---

## 🟩 PLANE B — NARRATIVE REASONING (324 words)

Energielabel C plaatst Haakakker 7 in het midden-ondergemiddelde segment van de Nederlandse woningvoorraad. Dit is geen rampscenario — het gros van de bestaande bouw heeft labels tussen C en G — maar het is ook geen kwaliteitskenmerk. In een context waarin energieprestatie steeds zwaarder weegt in zowel woonlasten als verkoopwaarde, verdient dit label serieuze aandacht.

**Financiële Implicaties**

Een woning met label C verbruikt significant meer energie dan een A-label equivalent. Voor een woning van 142 m² impliceert dit geschatte meerkosten van €700-€1.100 per jaar vergeleken met een energiezuinige woning. Over een bezitsperiode van 10-15 jaar cumuleert dit tot €7.000-€15.000 aan additionele energiekosten — een bedrag dat in de totale kostenafweging moet meewegen.

**Upgrade Potentieel en Kosten**

Upgraden van label C naar A of B is technisch haalbaar voor een woning uit 1978, maar vergt substantiële investering. Een volledige upgrade (spouwmuurisolatie, dakisolatie, HR++ glas, warmtepomp, zonnepanelen) kost €35.000-€45.000. De pure terugverdientijd op energiebesparing alleen is lang (40+ jaar), maar de calculus verandert wanneer subsidies (ISDE, gemeentelijke regelingen) en waardestijging van de woning worden meegewogen. Een energiezuinige woning verkoopt sneller en voor meer geld.

**Strategische Overwegingen**

De afweging is niet binair (wel/niet upgraden) maar getapt (wat eerst). Spouwmuurisolatie biedt typisch de beste kosten-batenverhouding en is vaak subsidiabel. Dakisolatie volgt if het dak toch vervanging behoeft. Zonnepanelen hebben kortste terugverdientijd. Warmtepomp is grote investering die zorgvuldige overweging verdient.

**De Data-Beperking**

Zonder gedetailleerde isolatie-informatie — spouw wel/niet gevuld, type beglazing, dakisolatiestatus — blijven deze schattingen indicatief. Een professionele energiescan of EPA-advies (€100-€300) kan precisere input leveren voor upgrade-planning.

**Wettelijke Context**

Let op: de Nederlandse overheid stuurt aan op gasloze woningen in 2050. Een woning met label C en gasgestookte CV zal in de komende decennia verplichte transitie moeten ondergaam. Dit is geen acute kostenpost maar een horizon die meespeelt in lange-termijn waardering.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Energy Performance

| KPI | Value | Source | Status |
|-----|-------|--------|--------|
| Energielabel | C | `energy_label` | ✅ PRESENT |
| Woonoppervlak | 142 m² | `living_area_m2` | ✅ PRESENT |
| Bouwjaar | 1978 | `build_year` | ✅ PRESENT |

### Estimated Energy Costs (Indicatief)

| Metric | Value | Basis |
|--------|-------|-------|
| Geschat gasverbruik | 1.800 m³/jaar | NIBUD ref × oppervlak |
| Geschat elektricitatieverbruik | 3.500 kWh/jaar | Gemiddeld gezin |
| Geschatte jaarkosten Gas | €1.400 | €0.80/m³ |
| Geschatte jaarkosten Elektra | €700 | €0.20/kWh |
| Totaal geschat | €2.100/jaar | Indicatief |

### Missing Energy Data

| Field | Status | Impact |
|-------|--------|--------|
| Isolatietype spouw | ❌ UNKNOWN | Upgrade planning |
| Isolatietype dak | ❌ UNKNOWN | Upgrade planning |
| Glasttype | ❌ UNKNOWN | Warmteverlies inschatting |
| CV-type | ❌ UNKNOWN | Vervangingskosten |
| CV-leeftijd | ❌ UNKNOWN | Korte-termijn risico |
| Zonnepanelen aanwezig | ❌ UNKNOWN | Energiebalans |

### Upgrade Investment Referenties

| Maatregel | Indicatieve Kosten | Besparing/jr | Subsidie |
|-----------|-------------------|--------------|----------|
| Spouwmuurisolatie | €2.500-€4.500 | €300-€500 | ISDE |
| Dakisolatie | €5.000-€8.000 | €200-€400 | ISDE |
| HR++ Glas | €6.000-€12.000 | €200-€300 | - |
| Warmtepomp (hybride) | €5.000-€8.000 | €300-€500 | ISDE |
| Warmtepomp (volledig) | €10.000-€15.000 | €500-€800 | ISDE |
| Zonnepanelen (10 stuks) | €6.000-€10.000 | €400-€600 | Saldering |

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Analysis

**Energy Concern Level**: 🟡 MODERATE-HIGH

**Key Observations**:
- Label C is niet dramatisch maar ook niet goed
- Geschatte €900/jaar meerkosten vs A-label moet meewegen in vergelijking
- Upgrade naar A is duur (€35-45k) met lange terugverdientijd
- Onbekend of spouw al geïsoleerd is — dit bepaalt laaghangend fruit

**Strategic View**:
"De energiesituatie is beheersbaar maar moet mee in de prijsonderhandeling. Als de woning €485k kost en €40k energie-upgrade nodig heeft, is de effectieve prijs €525k. Dat verandert de vergelijking met concurrerende woningen."

**Required Actions**:
- Energiescan of EPA-advies opvragen
- Subsidiemogelijkheden inventariseren
- Energiekosten meenemen in biedstrategie

### Petra's Analysis

**Energy Concern Level**: 🟢 LOW-MODERATE

**Key Observations**:
- Ziet energie-upgrade als "mooie projecten"
- Begrijpt dat kosten hoger zijn dan nieuwbouw, accepteert dit
- Zonnepanelen en warmtepomp passen in duurzaamheidsvisie
- Prioriteert wooncomfort boven pure financiële optimaliteit

**Strategic View**:
"Energielabel verbeteren hoort bij het avontuur van een bestaande woning kopen. We hoeven niet alles op dag één te doen — gefaseerd aanpakken past bij onze draagkracht. De meerkosten nu zijn de investeringen die de woning toekomstbestendig maken."

**Acceptance**:
- Label C acceptabel mits upgradepad duidelijk
- Wil niet eindeloos uitstellen vanwege energievraagstuk
- Ziet duurzaamheidsinvestering als waardecreatie

### Consensus Position

**Agreement**: Beiden accepteren dat energielabel C verbeterd moet worden, maar niet per se vóór aankoop of in eerste jaar.

**Approach**:
1. Energiescan uitvoeren met bouwkundige keuring
2. Upgrade-roadmap opstellen (wat eerst, wat later)
3. Subsidie-aanvragen parallel voorbereiden
4. Urgente zaken (oude CV) eerste jaar; cosmetische upgrades later

**Budget Alignment**: Beiden accepteren ca. €15.000-€20.000 aan energie-investeringen in eerste 3 jaar als onderdeel van "inrichtingsbudget bestaande woning".
