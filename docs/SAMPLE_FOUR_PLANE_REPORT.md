# 4-PLANE ENFORCED ANALYTICAL REPORT
## Sample Property Analysis: Haakakker 7, Mierlo

**Report Generated**: 2025-12-25T09:12:08+01:00  
**Report Version**: 9.0.0  
**Enforcement Mode**: FAIL-CLOSED  

---

# REGISTRY STATUS

## Available Data (Simulated Sample)

| Registry Key | Value | Status | Source |
|-------------|-------|--------|--------|
| `asking_price_eur` | €485,000 | ✅ PRESENT | funda_parse |
| `living_area_m2` | 142 m² | ✅ PRESENT | funda_parse |
| `plot_area_m2` | 380 m² | ✅ PRESENT | funda_parse |
| `build_year` | 1978 | ✅ PRESENT | funda_parse |
| `energy_label` | C | ✅ PRESENT | funda_parse |
| `bedrooms` | 4 | ✅ PRESENT | funda_parse |
| `rooms` | 6 | ✅ PRESENT | funda_parse |
| `property_type` | Vrijstaande woning | ✅ PRESENT | funda_parse |
| `address` | Haakakker 7, Mierlo | ✅ PRESENT | funda_parse |
| `price_per_m2` | €3,415 | ✅ DERIVED | calculated |
| `total_match_score` | 76% | ✅ DERIVED | preference_engine |
| `marcel_match_score` | 72% | ✅ DERIVED | preference_engine |
| `petra_match_score` | 80% | ✅ DERIVED | preference_engine |

## Missing Data (FAIL-LOUD)

| Registry Key | Impact | Mitigation |
|-------------|--------|------------|
| `woz_value` | ❌ UNKNOWN | Market valuation uncertainty increases |
| `foundation_type` | ❌ UNKNOWN | Structural risk cannot be assessed |
| `roof_condition` | ❌ UNKNOWN | Maintenance forecast incomplete |
| `insulation_details` | ❌ UNKNOWN | Energy upgrade costs uncertain |
| `vve_costs` | ❌ N/A | Not applicable (vrijstaand) |

**Completeness Score**: 72% (13/18 core fields present)

---

# CHAPTER 0: EXECUTIVE DASHBOARD

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Overall Match Score Gauge
```
┌─────────────────────────────────────────┐
│            MATCH SCORE                  │
│                                         │
│              ████████░░                 │
│                 76%                     │
│                                         │
│   Marcel: 72% ■■■■■■■░░░                │
│   Petra:  80% ■■■■■■■■░░                │
└─────────────────────────────────────────┘
```
**Data Source**: `total_match_score`, `marcel_match_score`, `petra_match_score`

### Chart 2: Price vs Area Positioning
```
Price/m²: €3,415
┌─────────────────────────────────────────┐
│ Budget  │  Average  │  Premium  │ Luxury│
│         │     ▲     │           │       │
│         │  €3,415   │           │       │
└─────────────────────────────────────────┘
Regional Average: €3,200/m²
```
**Data Source**: `price_per_m2`, `asking_price_eur`, `living_area_m2`

### Chart 3: Property Profile Radar
```
          Ruimte (85)
              ▲
             /|\
Locatie    / | \    Energie
  (70)    /  |  \     (55)
         /   |   \
        ─────●─────
         \   |   /
          \  |  /
           \ | /
            \|/
         Prijs (72)
```
**Data Source**: Derived from registry values per dimension

### Visuals NOT Applicable

| Visual Type | Reason |
|------------|--------|
| Trend over time | No historical data in registry |
| Neighborhood heatmap | Geo data not available |
| Comparable sales | No market data in registry |

---

## 🟩 PLANE B — NARRATIVE REASONING

### Executive Synthesis (557 words)

De woning aan de Haakakker 7 in Mierlo presenteert zich als een substantiële vrijstaande woning uit 1978 die zowel kansen als aandachtspunten biedt voor potentiële kopers. Met een vraagprijs van €485.000 voor 142 m² woonoppervlak op een perceel van 380 m², positioneert deze woning zich in het midden-plus segment van de regionale markt. De prijs per vierkante meter van €3.415 ligt circa 7% boven het regionale gemiddelde, wat een kritische beoordeling van de geboden waarde rechtvaardigt.

**Strategische Context en Marktpositie**

Het bouwjaar 1978 plaatst deze woning in een interessante categorie: oud genoeg om potentieel asbesthoudende materialen en gedateerde bouwpraktijken te bevatten, maar jong genoeg om waarschijnlijk een solide constructieve basis te hebben. De afwezigheid van fundamentinformatie in de registry is een significante blinde vlek die technische due diligence vereist vóór elk bindend bod. In de Brabantse kleigronden waar Mierlo zich bevindt, is kennis van de paalfundering of het ontbreken daarvan essentieel voor risicobeoordeling.

Het energielabel C is een tweesnijdend zwaard. Enerzijds voldoet de woning niet aan hedendaagse duurzaamheidsnormen, wat investeringen in isolatie, mogelijk een warmtepomp, en zonnepanelen suggereert. Anderzijds biedt dit verbeterpotentieel: een upgrade naar label A of B is realistisch haalbaar en zou zowel de woonlasten als de toekomstige verkoopwaarde positief beïnvloeden. De afwezigheid van gedetailleerde isolatiegegevens maakt een accurate kostenraming voor dergelijke upgrades onmogelijk op basis van de huidige data.

**Ruimtelijke Analyse en Leefbaarheid**

Met 6 kamers waarvan 4 slaapkamers biedt de woning aanzienlijke flexibiliteit voor gezinsuitbreiding, thuiswerken, of andere ruimtevragende levenspatronen. De verhouding woon- tot perceeloppervlak (37%) suggereert substantiële buitenruimte, wat in een post-COVID context waarin thuisblijven en tuingebruik een renaissance beleeft, een strategisch voordeel vormt. De exacte indeling en oriëntatie van deze buitenruimte ontbreekt echter in de registry, waardoor conclusies over zonligging en privacy speculatief blijven.

**Risico's en Onzekerheden**

De 72% completeness score van de registry data signaleert dat bijna een derde van de relevante informatie ontbreekt. Dit is geen verwaarloosbaar gegeven. De afwezige WOZ-waarde maakt externe waardeverificatie onmogelijk; de onbekende dakconditie en funderingstype introduceren potentieel kostbare verrassingen. Een bouwtechnische keuring vóór finale besluitvorming is niet slechts aanbevolen, maar essentieel.

**Match Score Interpretatie**

De gecombineerde match score van 76% weerspiegelt een woning die voor beide kopers substantiële, maar niet optimale aansluiting biedt. Petras hogere score (80%) versus Marcels lagere score (72%) duidt op een fundamentele spanning: de woning scoort waarschijnlijk hoger op leefbaarheid, sfeer en ruimtebeleving dan op technische staat, onderhoudsprognose en investeringsrisico. Dit is een cruciaal inzicht voor de gezamenlijke besluitvorming.

**Strategische Aanbeveling**

Deze woning verdient serieuze overweging, maar niet zonder kritisch onderzoek. De combinatie van locatie in Mierlo (rust versus bereikbaarheid), ruimte, en verbeterpotentieel maakt haar aantrekkelijk. De technische onzekerheden en bovengemiddelde vierkante-meterprijs vereisen echter een onderhandelingsstrategie die ruimte laat voor eventuele bevindingen uit nadere inspectie. Een bod van €460.000-€475.000 met voorwaarden voor technisch onderzoek zou een verstandig vertrekpunt zijn.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Core KPIs

| KPI | Value | Unit | Provenance | Registry ID | Completeness |
|-----|-------|------|------------|-------------|--------------|
| Vraagprijs | €485.000 | EUR | fact | `asking_price_eur` | ✅ |
| Woonoppervlak | 142 | m² | fact | `living_area_m2` | ✅ |
| Perceeloppervlak | 380 | m² | fact | `plot_area_m2` | ✅ |
| Prijs/m² | €3.415 | EUR/m² | derived | `price_per_m2` | ✅ |
| Bouwjaar | 1978 | jaar | fact | `build_year` | ✅ |
| Energielabel | C | - | fact | `energy_label` | ✅ |
| Slaapkamers | 4 | stuks | fact | `bedrooms` | ✅ |
| Kamers | 6 | stuks | fact | `rooms` | ✅ |
| Type | Vrijstaand | - | fact | `property_type` | ✅ |
| Locatie | Mierlo | - | fact | `address` | ✅ |

### Match Scores

| Metric | Value | Source |
|--------|-------|--------|
| Totaal Match | 76% | `total_match_score` |
| Marcel Match | 72% | `marcel_match_score` |
| Petra Match | 80% | `petra_match_score` |

### Missing Critical Data

| Field | Impact Level | Required For |
|-------|-------------|--------------|
| WOZ-waarde | HIGH | Marktwaarde verificatie |
| Funderingstype | HIGH | Structurele risico-inschatting |
| Dakconditie | MEDIUM | Onderhoudsraming |
| Isolatiedetails | MEDIUM | Energie-upgrade planning |
| CV-ketel leeftijd | LOW | Korte-termijn kosten |

### Parameters

```json
{
  "report_version": "9.0.0",
  "registry_locked": true,
  "completeness_score": 0.72,
  "registry_entry_count": 13,
  "validation_passed": true
}
```

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Perspective (Technical/Risk-Focused)

**Match Score**: 72%  
**Mood**: ⚠️ CAUTIOUS

**Key Values**:
- Structurele integriteit en onderhoudshistorie
- Technische staat van installaties
- Investerings- en waardebehoud risico
- Energie-efficiëntie en toekomstbestendigheid

**Concerns**:
1. Onbekend funderingstype is een rode vlag voor 1978-bouw in Brabant
2. Energielabel C impliceert significante upgrade-investering
3. Prijs boven marktgemiddelde zonder compenserend technisch voordeel
4. Afwezigheid van bouwkundige details maakt risicobeoordeling onvolledig

**Summary**: "De woning vraagt om grondige technische inspectie voordat ik me comfortabel voel bij dit prijsniveau. De onbekende factoren wegen zwaarder dan de zichtbare kwaliteiten."

---

### Petra's Perspective (Comfort/Experiential)

**Match Score**: 80%  
**Mood**: 🌟 POSITIEF

**Key Values**:
- Ruimtegevoel en leefbaarheid
- Tuin en buitenruimte voor ontspanning
- Sfeer en woonbeleving
- Buurtkarakter en omgeving

**Concerns**:
1. Modernisering nodig voor hedendaags wooncomfort
2. Energiekosten mogelijk hoger dan gewenst
3. Onbekend of tuin op zon ligt

**Summary**: "De combinatie van vrijstaand wonen met ruime tuin in een rustige omgeving spreekt enorm aan. De investeringen in sfeer en comfort zie ik als kans, niet als probleem."

---

### Preference Comparison

| Aspect | Marcel | Petra | Alignment |
|--------|--------|-------|-----------|
| Prijs/Waarde | Kritisch | Acceptabel | ⚡ TENSION |
| Technische staat | Onzeker | Secundair | ⚡ TENSION |
| Ruimte/Indeling | Voldoende | Uitstekend | ↔️ COMPLEMENTARY |
| Energielabel | Bezorgd | Verbeterkans | ↔️ COMPLEMENTARY |
| Locatie | Functioneel | Aantrekkelijk | ✅ ALIGNED |

### Overlap Points
- Beide waarderen de vrijstaande ligging en privacy
- Beide zien verbeterpotentieel in de woning
- Beide erkennen dat dit type woning schaars is op de markt

### Tension Points
- Marcel wil technische zekerheid vóór commitment; Petra wil niet door risico-analyse vertraagd worden
- Marcel ziet energielabel C als kostenpost; Petra ziet het als verbeterproject
- Marcel vindt prijs te hoog gegeven onzekerheden; Petra vindt prijs redelijk voor gebodene

### Joint Synthesis

Marcel en Petra benaderen deze woning vanuit complementaire maar soms conflicterende perspectieven. De sleutel tot gezamenlijke besluitvorming ligt in een getrapte aanpak: eerst investeren in technische zekerheid (bouwkundige keuring) om Marcels zorgen te adresseren, waarna Petra's enthousiasme de onderhandelingsstrategie kan informeren. Een voorwaardelijk bod dat ruimte laat voor inspectieresultaten is het optimale compromis.

---
