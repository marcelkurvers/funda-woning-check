# 4-PLANE REPORT — CHAPTERS 9-12

---

# CHAPTER 9: JURIDISCH & KADASTER

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Ownership Structure
```
┌─────────────────────────────────────────┐
│   EIGENDOMSSTRUCTUUR                    │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │                                 │   │
│   │   ┌───────────────────────────┐ │   │
│   │   │                           │ │   │
│   │   │   EIGENDOM 100%           │ │   │
│   │   │   (Vrijstaande woning)    │ │   │
│   │   │                           │ │   │
│   │   │   • Geen VvE              │ │   │
│   │   │   • Geen erfpacht (aann.) │ │   │
│   │   │   • Geen opstalrecht      │ │   │
│   │   │                           │ │   │
│   │   └───────────────────────────┘ │   │
│   │                                 │   │
│   └─────────────────────────────────┘   │
│                                         │
│   ⚠️ Erfpachtstatus niet bevestigd     │
└─────────────────────────────────────────┘
```
**Data Source**: `property_type` (vrijstaand = geen VvE)

### Chart 2: Legal Data Completeness
```
┌─────────────────────────────────────────┐
│   JURIDISCHE DATA STATUS                │
│                                         │
│   Kadaster info    ░░░░░░░░░ ONBEKEND   │
│   Erfpachtstatus   ░░░░░░░░░ ONBEKEND   │
│   Bestemmingsplan  ░░░░░░░░░ ONBEKEND   │
│   Servituten       ░░░░░░░░░ ONBEKEND   │
│   Erfdienstbaarhdn ░░░░░░░░░ ONBEKEND   │
│   Bodemkwaliteit   ░░░░░░░░░ ONBEKEND   │
│   Monumentstatus   ░░░░░░░░░ ONBEKEND   │
│                                         │
│   ████░░░░░░░░░░░░░░░░░░░░ 0/7 bekend  │
│                                         │
│   ⚠️ KRITIEK: Geen juridische data     │
└─────────────────────────────────────────┘
```
**Data Source**: Registry completeness check

### Chart 3: Risk Matrix
```
┌─────────────────────────────────────────┐
│   JURIDISCHE RISICO MATRIX              │
│                                         │
│        Kans onbekend │ Impact als waar  │
│   ─────────────────────────────────     │
│   Erfpacht       ❓   │ HOOG (kosten)   │
│   Servituut      ❓   │ MEDIUM (beperk) │
│   Bodemvervuil   ❓   │ HOOG (sanering) │
│   Monument       ❓   │ LOW (onwaarsch) │
│   Beslaglegging  ❓   │ HOOG (blokkade) │
│                                         │
│   Alle risico's vereisen notaris-check  │
└─────────────────────────────────────────┘
```

---

## 🟩 PLANE B — NARRATIVE REASONING (318 words)

De juridische en kadastrale aspecten van Haakakker 7 zijn een complete blinde vlek in de huidige dataset. Dit is niet ongebruikelijk — Funda-advertenties bevatten zelden deze informatie, en de registry is afhankelijk van wat geparsed kan worden. Desalniettemin zijn dit cruciale aspecten die vóór aankoop onderzocht moeten worden.

**Eigendomsvorm**

Als vrijstaande woning is Haakakker 7 vrijwel zeker volle eigendom zonder VvE-structuur. Dit elimineert de complexiteiten van appartementsrecht, reservefonds-zorgen, en mede-eigenaarschap. Echter, andere juridische constructies zijn niet uitgesloten.

**Erfpacht Risico**

In sommige gemeenten zijn woningen gebouwd op erfpachtgrond, met periodieke canon-herzieningen die kosten significant kunnen verhogen. Hoewel erfpacht in Noord-Brabant minder prevalent is dan in bijvoorbeeld Amsterdam, is uitsluiting vereist. Een kadasteruittreksel (€3-€10 online) bevestigt dit definitief.

**Servituten en Erfdienstbaarheden**

Oudere woningen kunnen belast zijn met rechten die derden hebben, zoals recht van overpad (buren mogen over uw tuin lopen), kabels en leidingen, of beperkingen op bebouwing. Het kadaster en de eigendomsakte onthullen deze, de notaris in het koopproces verifieert volledigheid.

**Bodemkwaliteit**

Bouwjaar 1978 betekent dat de woning vóór strenge milieuwetgeving is gebouwd. Historisch gebruik van het perceel (was het landbouw? industrie? stortplaats?) bepaalt bodemsaneringsrisico. De gemeente heeft vaak een bodemloket met historische informatie; de provinciale bodematlas (bodemloket.nl) biedt eerste inzicht.

**Bestemmingsplan**

Het vigerende bestemmingsplan bepaalt wat u mag bouwen, verbouwen, en exploiteren. Plannen voor dakopbouw, aan- of uitbouw, of anderssoortig gebruik vereisen verificatie tegen het bestemmingsplan. De gemeente Geldrop-Mierlo heeft waarschijnlijk een online ruimtelijk plan-viewer.

**Notaris Due Diligence**

Bij aankoop voert de notaris standaard een kadaster-check, beslaglegging-check, en eigendomsverificatie uit. Dit is geen vervanging voor eigen vooronderzoek. Het is verstandig vóór bod al basisinformatie te verzamelen om verrassingen in de notarisfase te voorkomen.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Known Legal Data

| KPI | Value | Source | Status |
|-----|-------|--------|--------|
| Woningtype | Vrijstaand | `property_type` | ✅ PRESENT |
| VvE | Niet van toepassing | derived | ✅ DERIVED |
| Adres | Haakakker 7, Mierlo | `address` | ✅ PRESENT |
| Gemeente | Geldrop-Mierlo | derived | ⚠️ INFERRED |

### Unknown Legal/Cadastral Data

| Field | Status | Where to Find |
|-------|--------|---------------|
| Kadastraal perceel | ❌ UNKNOWN | Kadaster uittreksel |
| Eigendomsvorm | ❌ UNKNOWN | Kadaster |
| Erfpacht | ❌ UNKNOWN | Kadaster |
| Canon (indien erfpacht) | ❌ UNKNOWN | Erfpachtakte |
| Servituten | ❌ UNKNOWN | Eigendomsakte |
| Erfdienstbaarheden | ❌ UNKNOWN | Eigendomsakte |
| Hypotheek huidig | ❌ UNKNOWN | Kadaster |
| Beslaglegging | ❌ UNKNOWN | Kadaster, notaris |
| Bestemmingsplan | ❌ UNKNOWN | Ruimtelijkeplannnen.nl |
| Monumentstatus | ❌ UNKNOWN | Monumentenregister |
| Bodemkwaliteit | ❌ UNKNOWN | Bodemloket.nl |
| Energieprestatiecertificaat | Ja (Label C) | `energy_label` | ✅ PRESENT |

### Verificatie Checklist

| Item | Actie | Kosten | Wanneer |
|------|-------|--------|---------|
| Kadaster uittreksel | Online opvragen | €3-€10 | Vóór bod |
| Bestemmingsplan bekijken | Gemeente viewer | Gratis | Vóór bod |
| Bodemloket checken | Online | Gratis | Vóór bod |
| Monument check | Monumentenregister | Gratis | Vóór bod |
| Volledige eigendomsakte | Via notaris | In kosten | Na akkoord |
| Erfpacht-detailering | Via notaris | In kosten | Na akkoord |

### Aankoop Juridische Kosten (Indicatief)

| Kostenpost | Bedrag | Toelichting |
|------------|--------|-------------|
| Overdrachtsbelasting | €9.700 | 2% van €485.000 |
| Notariskosten | €1.000-€1.500 | Leveringsakte |
| Inschrijving kadaster | €150-€200 | |
| Hypotheekakte | €500-€1.000 | Indien hypotheek |
| Taxatie | €400-€600 | Voor hypotheek |
| Bouwkundige keuring | €400-€600 | Aanbevolen |
| **Totaal bijkomend** | **~€12.000-€14.000** | |

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Perspective

**Legal Concern Level**: 🟡 MODERATE

**Key Observations**:
- Vrijstaand = geen VvE-zorgen = positief
- Erfpacht-uitsluiting is essentieel — moet gecheckt worden
- Bestemmingsplan relevant als uitbouwplannen bestaan
- Bodemkwaliteit moet geverifieerd, zeker bij bouwjaar 1978

**Required Actions**:
1. Kadasteruittreksel opvragen (€10, 5 minuten)
2. Bodemloket.nl checken (gratis, 2 minuten)
3. Ruimtelijkeplannen.nl checken (gratis, 10 minuten)
4. Monumentenregister checken (gratis, 2 minuten)

**Risk Tolerance**: "Ik wil zekerheid op papier. Geen bod zonder kadaster-check."

### Petra's Perspective

**Legal Concern Level**: 🟢 LOW

**Key Observations**:
- Vertrouwt op notaris om problemen te signaleren
- Geen uitgebreide verbouwplannen, dus bestemmingsplan minder urgent
- Erfpacht zou vervelend zijn maar is waarschijnlijk niet het geval

**Comfort Level**:
- Laat juridische details aan Marcel/notaris over
- Wil niet vertraagd worden door paperwork
- Vertrouwt dat "er wel niets aan de hand zal zijn"

### Tension Resolution

Marcel's behoefte aan juridische zekerheid is legitiem en kost weinig tijd/geld. Petra's vertrouwen in proces is ook valid. Compromis: Marcel doet de 30 minuten online checks vóór bezichtiging; indien clean, gaat proces door zonder vertraging. Indien issues, vroege detectie is beter dan late.

### Joint Checklist

- [ ] Kadaster uittreksel (Marcel verantwoordelijk)
- [ ] Bodemloket check (Marcel verantwoordelijk)
- [ ] Bestemmingsplan bekijken (Marcel verantwoordelijk)
- [ ] Resultaten delen met Petra (samen bespreken)
- [ ] Notaris informeren over bevindingen (bij koopproces)

---

# CHAPTER 10: FINANCIËLE ANALYSE

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Price Position Analysis
```
┌─────────────────────────────────────────┐
│   PRIJSPOSITIONERING                    │
│                                         │
│   Vraagprijs:       €485.000            │
│   ══════════════════════════════════    │
│                                         │
│   Prijs/m²:         €3.415              │
│   ████████████████████████████░░░░░░    │
│                                         │
│   Regionaal gem:    €3.200 /m²          │
│   █████████████████████████░░░░░░░░░    │
│                                         │
│   Verschil:         +€215 /m² (+7%)     │
│                                         │
│   Status: BOVEN MARKT                   │
└─────────────────────────────────────────┘
```
**Data Source**: `asking_price_eur`, `living_area_m2`, `price_per_m2`

### Chart 2: Total Cost of Ownership (Jaar 1)
```
┌─────────────────────────────────────────┐
│   TOTALE EIGENDOMSKOSTEN (JAAR 1)       │
│                                         │
│   Aanschaf                              │
│   ├── Koopsom               €485.000    │
│   ├── Overdrachtsbelasting   €9.700     │
│   ├── Notaris/kadaster       €2.000     │
│   ├── Taxatie/keuring          €900     │
│   └── Subtotaal             €497.600    │
│                                         │
│   Geschatte renovatie (basis)            │
│   ├── Noodzakelijk           €10.000    │
│   ├── Gewenst                €15.000    │
│   └── Subtotaal              €25.000    │
│                                         │
│   ═══════════════════════════════════   │
│   TOTAAL JAAR 1:            €522.600    │
└─────────────────────────────────────────┘
```
**Data Source**: Derived calculations + estimates

### Chart 3: Monthly Cost Projection
```
┌─────────────────────────────────────────┐
│   GESCHATTE MAANDLASTEN                 │
│   (Hypotheek €400k, 4%, 30 jaar)        │
│                                         │
│   Hypotheek (bruto)    €1.910           │
│   ████████████████████████████████░░    │
│                                         │
│   Energie (Label C)      €175           │
│   ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│                                         │
│   Onderhoud (1%/jr)      €400           │
│   █████████████░░░░░░░░░░░░░░░░░░░░░    │
│                                         │
│   Verzekeringen           €75           │
│   ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│                                         │
│   Gemeentebelastingenest €100           │
│   ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│                                         │
│   ═══════════════════════════════════   │
│   TOTAAL BRUTO:         ~€2.660/maand   │
└─────────────────────────────────────────┘
```
**Note**: Indicatief — persoonlijke situatie varieert

---

## 🟩 PLANE B — NARRATIVE REASONING (341 words)

De financiële analyse van Haakakker 7 onthult een woning die boven het regionale marktgemiddelde geprijsd is, maar waar die premium door karakteristieken kan worden gerechtvaardigd — of niet. De vraagprijs van €485.000 voor 142 m² resulteert in €3.415 per vierkante meter, circa 7% boven het Brabantse gemiddelde. Dit verschil moet kritisch worden gewogen.

**Wat de Premium Rechtvaardigt**

Het vrijstaande karakter is een schaarste-eigenschap; nieuwbouw vrijstaand is zeldzaam geworden. Het ruime perceel (380 m²) met substantiële tuin is eveneens premium-waardig. De locatie in Brainport-regio met waardeappreciatie-potentieel voegt strategische waarde toe. Deze factoren samen kunnen een bovengemiddelde prijs verdienen.

**Wat de Premium Ondermijnt**

Energielabel C impliceert hogere woonlasten en noodzakelijke investering voor toekomstbestendigheid. De leeftijd (47 jaar) zonder duidelijke moderniseringshistorie introduceert onzekerheid over korte-termijn investeringsnoodzaak. De afwezigheid van WOZ-waarde verhindert objectieve waardetoetsing. Zonder deze referenties is de vraagprijs een "seller's ask" zonder externe validatie.

**Total Cost of Ownership**

De werkelijke kosten van deze woning zijn niet €485.000 maar significant hoger. Kosten koper (k.k.), overdrachtsbelasting, notaris, en inrichtingskosten tillen de initiële investering naar €500.000+. Als renovatie €25.000-€50.000 bedraagt (reëel voor 47-jarige woning), nadert de totale investering €550.000 in het eerste jaar. Dit moet de basis zijn voor vergelijking met alternatieven.

**Maandlasten Realiteit**

Bij een hypotheek van €400.000 (aannemend €85.000-€100.000 eigen middelen), resulteren bruto maandlasten van circa €1.900 voor hypotheek alleen. Met energie (Label C = ~€175/maand), onderhoud reserve (1% van woningwaarde/jaar = €400/maand), verzekeringen, en belastingen, bedragen totale woonlasten €2.500-€2.800 per maand bruto. Dit vereist een proportioneel inkomen.

**Onderhandelingsruimte**

De 7% premium boven markt, gecombineerd met onbekende technische staat, creëert onderhandelingsruimte. Een openingsbod van €450.000-€460.000 (5-7% onder vraagprijs) is verdedigbaar, met verhoging mogelijk na gunstige bouwkundige keuring. Bereidheid om snel te handelen kan compenseren voor prijskorting.

**Investeringswaarde**

Brainport-woningen appreciëren historisch boven landelijk gemiddelde. Echter, dit is geen garantie, en korte-termijn prijsontwikkeling is onvoorspelbaar. Koop voor woonwaarde, niet speculatie.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Price Analysis

| KPI | Value | Source | Status |
|-----|-------|--------|--------|
| Vraagprijs | €485.000 | `asking_price_eur` | ✅ PRESENT |
| Woonoppervlak | 142 m² | `living_area_m2` | ✅ PRESENT |
| Prijs per m² | €3.415 | `price_per_m2` | ✅ DERIVED |
| WOZ-waarde | ❌ UNKNOWN | - | ❌ MISSING |
| Oorspronkelijke aankoopprijs | ❌ UNKNOWN | - | ❌ MISSING |
| Tijd op markt | ❌ UNKNOWN | - | ❌ MISSING |

### Acquisition Costs

| Kostenpost | Bedrag | Basis |
|------------|--------|-------|
| Koopsom | €485.000 | Vraagprijs |
| Overdrachtsbelasting | €9.700 | 2% |
| Notaris + kadaster | €1.500-€2.000 | Gemiddeld |
| Taxatie | €400-€600 | Hypotheek vereiste |
| Bouwkundige keuring | €400-€600 | Aanbevolen |
| **Kosten Koper Totaal** | **~€12.000-€14.000** | |
| **Totaal Verwerving** | **~€497.000-€499.000** | |

### Hypotheek Scenario's

| Scenario | Hypotheeksom | Rente | Looptijd | Bruto/maand |
|----------|--------------|-------|----------|-------------|
| 100% financiering | €485.000 | 4.0% | 30 jaar | €2.315 |
| 90% financiering | €436.500 | 4.0% | 30 jaar | €2.084 |
| 80% financiering | €388.000 | 3.8% | 30 jaar | €1.808 |

### Monthly Ownership Costs (Indicatief)

| Kostenpost | Bedrag/maand | Basis |
|------------|--------------|-------|
| Hypotheek (bruto) | €1.900-€2.300 | Afhankelijk van scenario |
| Energie | €150-€200 | Label C, 142 m² |
| Onderhoudsreserve | €400 | 1% woningwaarde/jaar |
| Opstalverzekering | €40-€60 | 142 m²  |
| Inboedelverzekering | €25-€40 | Gemiddeld |
| OZB | €50-€100 | Gemeente afhankelijk |
| Waterschapsbelasting | €30-€50 | |
| **Totaal bruto** | **€2.600-€3.150** | |

### Unknown Financial Data

| Field | Status | Impact |
|-------|--------|--------|
| WOZ-waarde | ❌ UNKNOWN | Can't validate market price |
| Grondwaarde | ❌ UNKNOWN | Erfpacht calculus |
| Historische prijsontwikkeling | ❌ UNKNOWN | Trend analysis |
| Vergelijkbare verkopen | ❌ UNKNOWN | Market positioning |

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Financial Assessment

**Comfort Level**: ⚠️ MODERATE CONCERN

**Key Calculations**:
- €485k is significant; wil zekerheid over waarde
- 7% boven markt zonder WOZ-referentie is risico
- Moet renovatiebudget (€25-50k) meefinancieren of cash
- Maandlasten €2.600+ vereist stabiel inkomen

**Financial Priorities**:
1. WOZ-waarde achterhalen ter validatie
2. Onderhandelingsruimte identificeren (target: €460k)
3. Renovatiebudget apart houden, niet in hypotheek
4. Reserve voor onvoorzien behouden

**Quote**: "De woning is niet goedkoop. Bij deze prijs wil ik zekerheden. Elk onbekend technisch probleem is extra geld."

### Petra's Financial Assessment

**Comfort Level**: 🟢 ACCEPTABLE

**Key Perspective**:
- €485k is veel, maar past binnen verwachting voor dit type
- Ziet woning als lange-termijn thuis, niet als investering
- Renovatie is normaal bij bestaande bouw
- Maandlasten zijn hoog maar draagbaar

**Financial Priorities**:
1. Bevestigen dat hypotheek rond komt
2. Eerste jaar basisrenovatie, daarna gefaseerd
3. Niet te conservatief; dit is woning voor 15+ jaar
4. Kwaliteit van leven belangrijker dan spreadsheet

**Quote**: "Ja, het is veel geld. Maar we betalen ook voor tuin, ruimte, vrijheid. Dat heeft waarde die niet in euro's past."

### Joint Financial Framework

| Topic | Marcel Position | Petra Position | Resolution |
|-------|-----------------|----------------|------------|
| Max bod | €460.000 | €480.000 | Starten €455k, max €475k |
| Renovatiebudget | €20.000 cash | €30.000 gefaseerd | €25.000 beschikbaar, rest later |
| Onderhandeling | Hard op prijs | Flexibel | Marcel leidt onderhandeling |
| Risicopremie | Eisen korting voor onzekerheid | Accepteren | Bij slechte keuring: heronderhandelen |

### Financial Recommendation

**Opening Bod**: €455.000 (-6% van vraagprijs)
**Maximum Bod**: €475.000 (-2% van vraagprijs), alleen na positieve bouwkundige keuring
**Voorbehouden**: Bouwkundige keuring, financieringsvoorbehoud, NHG indien mogelijk

---

# CHAPTER 11: MARKTPOSITIE

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Market Segment Position
```
┌─────────────────────────────────────────┐
│   MARKTSEGMENT POSITIONERING            │
│                                         │
│   Prijs                                 │
│   ^                                     │
│   │                                     │
│   │  €600k+ ·  ·  ·  ·  ·  Premium      │
│   │                                     │
│   │  €500k  ·  ·  X  ·  ·  Boven-       │
│   │        ★ DEZE                gemid. │
│   │  €400k  ·  ·  ·  ·  ·  Gemiddeld    │
│   │                                     │
│   │  €300k  ·  ·  ·  ·  ·  Starter     │
│   │                                     │
│   └────────────────────────────> m²     │
│       80   100   120   140   160        │
│                  ▲                      │
│                  │                      │
│              142 m²                     │
│                                         │
│   Segment: Upper-Middle Vrijstaand      │
└─────────────────────────────────────────┘
```
**Data Source**: `asking_price_eur`, `living_area_m2`

### Chart 2: Regional Context
```
┌─────────────────────────────────────────┐
│   BRAINPORT REGIO MARKTCONTEXT          │
│                                         │
│   Prijsontwikkeling (indicatief)        │
│   2020 ████████████░░░░░░░░ Basis       │
│   2021 ██████████████████░░ +15%        │
│   2022 ████████████████████ +20%        │
│   2023 █████████████████░░░ +10%        │
│   2024 ██████████████████░░ +12%        │
│                                         │
│   Brainport > Landelijk gemiddelde      │
│   Mierlo < Eindhoven centrum            │
│                                         │
│   ⚠️ Data is indicatief, niet exacte   │
│      marktcijfers                       │
└─────────────────────────────────────────┘
```

### Chart 3: Competitive Landscape (Conceptueel)
```
┌─────────────────────────────────────────┐
│   CONCURRERENDE WONINGEN                │
│   (Hypothetisch - geen data)            │
│                                         │
│   Haakakker 7      €485k  142 m²  1978  │
│   ════════════════════════════════════  │
│                                         │
│   Alternatief A?   €???k  ??? m²  ????  │
│   Alternatief B?   €???k  ??? m²  ????  │
│   Alternatief C?   €???k  ??? m²  ????  │
│                                         │
│   ❌ Geen vergelijkingsdata in registry │
│      Handmatig Funda-onderzoek vereist  │
└─────────────────────────────────────────┘
```
**Note**: Competitive analysis requires external data

---

## 🟩 PLANE B — NARRATIVE REASONING (336 words)

De marktpositie van Haakakker 7 moet worden begrepen binnen de dynamiek van de Brainport-regio, een van de meest competitieve woningmarkten van Nederland. De vraagprijs van €485.000 voor een vrijstaande woning van 142 m² in Mierlo reflecteert zowel lokale factoren als regionale marktkrachten.

**Regionale Marktdynamiek**

De Brainport-regio (Eindhoven e.o.) ervaart aanhoudende vraagdruk door economische groei, ASML-effect, en kenniswerker-instroom. Dit drijft prijzen omhoog, ook in omliggende gemeenten zoals Geldrop-Mierlo. Vrijstaande woningen zijn bijzonder gewild door gezinnen die ruimte zoeken buiten de stad maar Eindhoven-bereikbaarheid willen behouden.

**Segment Positionering**

Haakakker 7 bevindt zich in het upper-middle segment: substantieel maar niet luxe, ruim maar niet uitgestrekt. Dit segment heeft relatief gestabiliseerde vraag; het is te duur voor starters, te bescheiden voor premium-zoekers. De typische koper is een doorstromer — gezin met jonge kinderen dat uit appartement of rijtjeshuis komt.

**Concurrentie Analyse (Niet Beschikbaar)**

Een kritieke leemte in de analyse is het ontbreken van vergelijkingsdata. Hoeveel soortgelijke woningen (vrijstaand, 130-160 m², Mierlo/Geldrop) staan te koop? Tegen welke prijzen? Hoe lang staan ze al te koop? Deze vragen vereisen handmatig Funda-onderzoek, dat niet in de registry is opgenomen.

**Tijd op Markt**

Onbekend is hoe lang Haakakker 7 al te koop staat. Een woning die al 3+ maanden staat, heeft mogelijk een te hoge vraagprijs; een woning die net is geplaatst, test de markt. Dit beïnvloedt onderhandelingsdynamiek significant.

**Waardeontwikkeling Vooruitzicht**

Gegeven de Brainport-dynamiek is waardeappreciatie op middellange termijn (5-10 jaar) waarschijnlijk. Echter, korte-termijn fluctuaties zijn onvoorspelbaar, en de recente rentestijging heeft koopkracht gedrukt. Koop deze woning als thuis, niet als speculatie-object.

**Strategische Aanbeveling**

De marktpositie rechtvaardigt een bod onder vraagprijs, ondersteund door (a) 47-jarige leeftijd, (b) onbekende technische staat, (c) energielabel C. Een korting van 5-10% ten opzichte van vraagprijs is verdedigbaar. Echter, wees voorbereid op competitie indien andere geïnteresseerden zijn.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Market Position Data

| KPI | Value | Source | Status |
|-----|-------|--------|--------|
| Vraagprijs | €485.000 | `asking_price_eur` | ✅ PRESENT |
| Prijs/m² | €3.415 | `price_per_m2` | ✅ DERIVED |
| Regionaal gem. €/m² | ~€3.200 | Algemene ref. | ⚠️ ESTIMATED |
| Premium vs markt | +7% | Derived | ⚠️ ESTIMATED |

### Missing Market Data

| Field | Status | Source Needed |
|-------|--------|---------------|
| Tijd op markt (DOM) | ❌ UNKNOWN | Funda history |
| Oorspronkelijke vraagprijs | ❌ UNKNOWN | Funda history |
| Prijswijzigingen | ❌ UNKNOWN | Funda history |
| Vergelijkbare verkopen buurt | ❌ UNKNOWN | Kadaster, NVM |
| Aanbod soortgelijke woningen | ❌ UNKNOWN | Funda zoek |
| Transactieprijzen gebied | ❌ UNKNOWN | NVM, Kadaster |
| Overbieden percentage regio | ❌ UNKNOWN | Makelaarsdata |
| Gemiddelde verkooptijd regio | ❌ UNKNOWN | NVM stats |

### Indicatieve Marktbenchmarks (Externe Referentie)

| Metric | Brainport | NL Gemiddeld |
|--------|-----------|--------------|
| Prijsstijging YoY | +8-12% | +5-8% |
| Gem. verkooptijd | 30-45 dagen | 45-60 dagen |
| Overbieden % | 2-5% | 1-3% |
| Vraag/aanbod ratio | Krap | Krap |

### Price Scenario Analysis

| Scenario | Bod | Argumentatie |
|----------|-----|--------------|
| Agressief | €445.000 | -8%, maximale onderhandeling |
| Redelijk | €455.000-€465.000 | -4 tot -6%, technische onzekerheid |
| Marktconform | €475.000 | -2%, snelle deal |
| Overbieden | €490.000+ | Niet aanbevolen |

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Market Assessment

**Urgency Level**: 🟡 MODERATE

**Key Observations**:
- Markt is competitief maar niet hysterisch
- Geen data over hoe lang woning te koop staat
- 7% boven marktgemiddelde is risico
- Wil niet overbieden voor onzekerheden

**Strategy Preference**:
- Starten onder vraagprijs (-6 tot -8%)
- Ruimte voor verhoging na keuring
- Geen emotionele beslissingen
- Bereid te verliezen aan hogere bieder

**Quote**: "Als iemand anders €500k wil betalen voor onbekende risico's, laat ze gaan. Er zijn altijd andere woningen."

### Petra's Market Assessment

**Urgency Level**: 🟠 MODERATE-HIGH

**Key Observations**:
- Dit type woning (vrijstaand, ruime tuin, Mierlo) is schaars
- Te lang wachten = mislopen
- Markt kan harder worden
- Past in levensfase nu

**Strategy Preference**:
- Serieus bod (-3 tot -5%)
- Niet onderaan beginnen (toont desinteresse)
- Snelheid als concurrentievoordeel
- Bereid iets boven taxatie te gaan voor zekerheid

**Quote**: "Ik wil niet over 2 jaar terugkijken en wensen dat we doorgezet hadden. Het perfecte moment bestaat niet."

### Market Strategy Negotiation

| Element | Marcel | Petra | Compromis |
|---------|--------|-------|-----------|
| Opening bod | €445k | €465k | €455k |
| Max bod | €465k | €485k | €475k |
| Onderhandelingsstijl | Hard | Flexibel | Stappen |
| Reactiesnelheid | Rustig | Snel | 24 uur beslisruimte |
| Walk-away punt | €470k | €490k | €475k |

### Joint Bidding Strategy

**Fase 1**: Opening bod €455.000, voorbehoud keuring/financiering
**Fase 2**: Indien tegenvoorstel, verhogen naar €465.000 met versnelde keuring
**Fase 3**: Maximum €475.000, alleen na akkoord op keuringsvoorwaarden
**Walk Away**: Boven €475.000 of indien verkoper geen voorbehouden accepteert

---

# CHAPTER 12: CONCLUSIE & ADVIES

## 🟦 PLANE A — VISUAL INTELLIGENCE

### Chart 1: Decision Matrix Summary
```
┌─────────────────────────────────────────┐
│   BESLISMATRIX HAAKAKKER 7              │
│                                         │
│   POSITIEF (+)                          │
│   ──────────────────                    │
│   ├── Ruimte (142 m²)        ████████   │
│   ├── Tuin (~240 m²)         █████████  │
│   ├── Vrijstaand             █████████  │
│   ├── Locatie Mierlo         ███████    │
│   └── Brainport-potentieel   ████████   │
│                                         │
│   NEGATIEF (-)                          │
│   ──────────────────                    │
│   ├── Prijs (+7% markt)      ██████     │
│   ├── Energielabel C         █████      │
│   ├── Leeftijd 47 jr         ████       │
│   ├── Techniek onbekend      ████████   │
│   └── Renovatiekosten (est.) ██████     │
│                                         │
│   ONBEKEND (?)                          │
│   ──────────────────                    │
│   ├── Afwerking/onderhoud    ░░░░░░░░░  │
│   ├── Indeling/kwaliteit     ░░░░░░░░░  │
│   └── Juridisch/kadaster     ░░░░░░░░░  │
└─────────────────────────────────────────┘
```

### Chart 2: Match Score Final
```
┌─────────────────────────────────────────┐
│   FINAL MATCH ASSESSMENT                │
│                                         │
│   Marcel         ████████████░░░░ 72%   │
│   Petra          ████████████████░ 80%  │
│   Combined       ██████████████░░░ 76%  │
│                                         │
│   ▲                                     │
│   │                                     │
│   │  Alignment zones:                   │
│   │  <60%  = Walk away                  │
│   │  60-70 = With concerns              │
│   │  70-80 = Good fit ◄─── BOTH HERE    │
│   │  80-90 = Strong fit                 │
│   │  >90%  = Exceptional                │
│   │                                     │
│   Verdict: PROCEED WITH CONDITIONS      │
└─────────────────────────────────────────┘
```

### Chart 3: Next Steps Flow
```
┌─────────────────────────────────────────┐
│   AANBEVOLEN VERVOLGSTAPPEN             │
│                                         │
│   [NU]                                  │
│     │                                   │
│     ▼                                   │
│   [1. Online checks]───────────────────┐│
│   (Kadaster, bodem, bestemmingsplan)   ││
│     │                                  ││
│     ▼                                  ││
│   [2. Bezichtiging]                    ││
│     │                                  ││
│     ├── Positief ──▶ [3. Bod]         ││
│     │                    │            ││
│     │                    ▼            ││
│     │         [4. Bouwkundige keuring]││
│     │                    │            ││
│     │           ┌───────┴───────┐     ││
│     │           ▼               ▼     ││
│     │       [Positief]    [Negatief]  ││
│     │           │               │     ││
│     │           ▼               ▼     ││
│     │    [5. Definitief] [Heronderh.] ││
│     │                          of     ││
│     │                      [AFZIEN]   ││
│     │                                 ││
│     └── Negatief ──▶ [AFZIEN] ◄───────┘│
│                                         │
└─────────────────────────────────────────┘
```

---

## 🟩 PLANE B — NARRATIVE REASONING (523 words)

Haakakker 7 in Mierlo presenteert zich als een woning met substantieel potentieel, significante onzekerheden, en een vraagprijs die kritische evaluatie verdient. Na analyse van alle beschikbare dimensies — van kerngegevens tot financiën, van techniek tot preferenties — concluderen we dat deze woning serieuze overweging waard is, maar alleen onder strikte voorwaarden.

**De Centrale Spanning**

De fundamentele spanning in deze woning is die tussen belofte en zekerheid. De belofte is aanzienlijk: 142 m² woonruimte, 380 m² perceel met ruime tuin, vrijstaand karakter, Mierlo als rustige woonplek met Eindhoven-bereikbaarheid. Voor een gezin dat ruimte, privacy, en buitenleven zoekt, zijn dit krachtige aantrekkingsfactoren. De zekerheid ontbreekt echter op cruciale punten: technische staat onbekend, onderhoudsbehoefte niet te kwantificeren, en afwerkingskwaliteit niet te beoordelen. De registry bevat slechts 72% van de kernvelden die een volledig gefundeerde beslissing zouden ondersteunen.

**Wat We Weten versus Wat We Moeten Weten**

We weten: prijs, oppervlaktes, kamers, bouwjaar, energielabel, locatie. We weten niet: fundering, dakconditie, isolatiestaat, CV-installatie, keuken/badkamer leeftijd, afwerkingsniveau, juridische bijzonderheden. Deze asymmetrie is typisch voor woningaankoop — de advertentie verkoopt de droom, niet de details — maar moet actief worden opgelost door bezichtiging, inspectie, en due diligence.

**De Match Score Interpretatie**

Met een gecombineerde match van 76%, een score van 72% voor Marcel en 80% voor Petra, bevindt deze woning zich in de "goede fit" zone. Het is geen droomwoning die alle twijfels wegvaagt, maar het is ook geen compromis dat acceptatie afdwingt bij gebrek aan beter. De 8-punten divergentie tussen Marcel en Petra reflecteert hun verschillende waarderingskaders: Marcel wordt geremd door technische onzekerheden, Petra wordt aangetrokken door leefkwaliteit-potentieel. Beide perspectieven zijn valide en vullen elkaar aan.

**Financiële Realiteit**

De vraagprijs van €485.000 is boven marktgemiddelde zonder compenserende technische kwaliteitsbewijzen. De effectieve totale investering — inclusief kosten koper, geschatte renovatie, en energie-upgrades — benadert €550.000 in een realistisch scenario. Dit vereist solide financiering en reserves. De maandlasten zullen €2.500-€3.000 bruto bedragen, afhankelijk van hypotheekconstructie. Dit is aanzienlijk maar niet onhaalbaar bij tweeverdieners-inkomen passend bij dit prijssegment.

**Aanbeveling**

Wij adviseren door te gaan naar de volgende fase: online vooronderzoek (kadaster, bodem, bestemmingsplan) gevolgd door bezichtiging. Bij positieve indruk tijdens bezichtiging, een bod onder vraagprijs (€455.000-€465.000) met voorbehoud voor bouwkundige keuring. De keuring bepaalt het eindoordeel: bij gunstige resultaten is deze woning een waardige aankoop; bij significante bevindingen is heronderhandeling of afzien aangewezen.

**Beslissingscriterium**

De ultieme vraag is: biedt deze woning meer leefwaarde per geïnvesteerde euro dan de alternatieven? Zonder vergelijking met concrete alternatieven is dit niet volledig te beantwoorden. Maar de combinatie van vrijstaand karakter, ruimte, tuin, en Brainport-locatie is objectief schaars. Als de bezichtiging de potentie bevestigt en de keuring geen dealbreakers onthult, is Haakakker 7 een verantwoorde keuze voor gezinsvestiging op lange termijn.

---

## 🟨 PLANE C — FACTUAL ANCHOR

### Summary Statistics

| Category | Score | Status |
|----------|-------|--------|
| Data completeness | 72% | ⚠️ Suboptimal |
| Overall match | 76% | ✅ Good fit |
| Marcel match | 72% | ✅ Acceptable |
| Petra match | 80% | ✅ Good fit |
| Price vs market | +7% | ⚠️ Above average |

### Property Summary

| Attribute | Value | Assessment |
|-----------|-------|------------|
| Vraagprijs | €485.000 | Boven markt |
| Woonoppervlak | 142 m² | Ruim |
| Perceel | 380 m² | Ruim |
| Tuin (geschat) | ~240 m² | Groot |
| Slaapkamers | 4 | Voldoende |
| Kamers | 6 | Ruim |
| Bouwjaar | 1978 | Aandachtspunt |
| Leeftijd | 47 jaar | Onderhoudsfocus |
| Energielabel | C | Verbeteren |
| Type | Vrijstaand | Premium |
| Locatie | Mierlo | Dorps + Brainport |

### Cost Projections

| Category | Low Est. | High Est. |
|----------|----------|-----------|
| Koopsom | €455.000 | €485.000 |
| Kosten koper | €12.000 | €14.000 |
| Renovatie noodzak. | €10.000 | €30.000 |
| Renovatie gewenst | €15.000 | €40.000 |
| Energie-upgrade | €15.000 | €40.000 |
| **Totaal 5-jaar** | **€507.000** | **€609.000** |

### Decision Criteria Checklist

| Criterium | Status | Action |
|-----------|--------|--------|
| Online checks (kadaster, bodem) | ⬜ TODO | Vóór bezichtiging |
| Bezichtiging | ⬜ TODO | Plannen |
| Eerste indruk positief | ⬜ TBD | Bezichtiging bepaalt |
| Bod uitbrengen | ⬜ TBD | Na positieve bezichtiging |
| Bouwkundige keuring | ⬜ TBD | Na geaccepteerd bod |
| Keuring positief | ⬜ TBD | Keuring bepaalt |
| Financiering rond | ⬜ TBD | Parallel aan bod |
| Definitief akkoord | ⬜ TBD | Na alle voorbehouden |

### Go/No-Go Matrix

| Scenario | Recommendation |
|----------|----------------|
| Keuring OK + Prijs €475k | ✅ GO |
| Keuring OK + Prijs €485k | ⚠️ CONSIDER (grens) |
| Keuring issues €5-10k + Prijs €460k | ✅ GO (heronderhandeld) |
| Keuring issues €20k+ + Any price | ⚠️ HERONDERHANDEL of NO-GO |
| Bezichtiging negatief | ❌ NO-GO |

---

## 🟥 PLANE D — HUMAN PREFERENCE

### Marcel's Final Assessment

**Verdict**: ✅ PROCEED WITH CONDITIONS

**Summary Statement**:
"Deze woning verdient serieuze overweging, maar ik ga niet blindelings in. Mijn voorwaarden zijn helder: (1) online checks clean, (2) bezichtiging bevestigt potentieel, (3) keuring zonder grote verrassingen, (4) prijs onderhandeld naar acceptabel niveau. Als aan alle voorwaarden voldaan is, steun ik aankoop van harte. Als niet, walk away."

**Non-Negotiables**:
- Bouwkundige keuring verplicht
- Maximum bod €475.000
- €25.000 renovatiereserve beschikbaar
- Geen haastbeslissingen

**Emotional State**: Cautiously optimistic. De woning past kwantitatief; de kwalitatieve bevestiging moet nog komen.

### Petra's Final Assessment

**Verdict**: ✅ ENTHUSIASTIC PROCEED

**Summary Statement**:
"Dit is precies het type woning waar ik van droom: ruimte, tuin, vrijstaand, een dorp met karakter. De onzekerheden zijn normaal voor elke bestaande woning. Ik geloof dat we hier een thuis kunnen bouwen. Laten we doorzetten."

**Priorities**:
- Bezichtiging plannen zo snel mogelijk
- Niet te zuinig bieden (toont commitment)
- Open staan voor de sfeer, niet alleen de checklist
- Besluitvaardig zijn als het klopt

**Emotional State**: Excited but grounded. Begrijpt dat enthousiasme moet worden gebalanceerd door Marcels analytische blik.

### Joint Final Decision Framework

**Alignment Statement**:
Marcel en Petra benaderen Haakakker 7 vanuit complementaire perspectieven die samen een volledig beeld vormen. Petra brengt visie en enthousiasme; Marcel brengt analyse en risico-bewustzijn. De woning met 76% gezamenlijke match en positieve scores voor beiden is het waard om verder te onderzoeken.

**Action Plan**:

1. **Week 1**: 
   - Marcel: Online checks (kadaster, bodemloket, bestemmingsplan)
   - Petra: Bezichtiging regelen via makelaar
   
2. **Week 2**: 
   - Samen: Bezichtiging
   - Beiden: Onafhankelijke eerste impressie noteren
   - Samen: Debriefing dezelfde avond
   
3. **Week 2-3** (indien positief):
   - Marcel: Bod voorbereiden (opening €455k)
   - Samen: Biedstrategie finaliseren
   - Bod uitbrengen
   
4. **Na bod-acceptatie**:
   - Bouwkundige keuring inplannen
   - Financieringsaanvraag starten
   - Resultaten afwachten
   
5. **Finale beslissing**:
   - Keuring positief + financiering rond → PROCEED
   - Keuring negatief → HERONDERHANDEL of AFZIEN
   - Financiering niet rond → AFZIEN (noodgedwongen)

**Final Word**:
Haakakker 7 is geen perfecte woning — geen woning is dat. Het is een woning met substantieel potentieel, aanvaardbare maar niet verwaarloosbare risico's, en een vraagprijs die ruimte laat voor onderhandeling. Voor Marcel en Petra, met hun gecombineerde perspectief van analyse en visie, is dit een verantwoorde woning om serieus te verkennen. De komende weken zullen de nog ontbrekende informatie opleveren die een definitief oordeel mogelijk maakt.

**Recommendation**: DOORGAAN NAAR BEZICHTIGING.

---

# REPORT COMPLETE

## Meta-Information

| Field | Value |
|-------|-------|
| Report Version | 9.0.0 |
| Generated | 2025-12-25T09:12:08+01:00 |
| Chapters | 13 (0-12) |
| Planes per Chapter | 4 (A, B, C, D) |
| Enforcement Mode | FAIL-CLOSED |
| Registry Completeness | 72% |
| Overall Match Score | 76% |
| Recommendation | PROCEED WITH CONDITIONS |

## Appendix: Missing Data Summary

| Category | Missing Fields | Impact |
|----------|---------------|--------|
| Technical | Foundation, roof, insulation, CV | HIGH |
| Interior | Kitchen age, bathroom, floors | MEDIUM |
| Legal | Kadaster, erfpacht, servitudes | MEDIUM |
| Market | Comparables, time on market | LOW-MEDIUM |
| Energy | Insulation details, panel status | MEDIUM |

## Appendix: Action Items

1. ☐ Kadaster uittreksel opvragen
2. ☐ Bodemloket checken
3. ☐ Bestemmingsplan bekijken
4. ☐ Bezichtiging inplannen
5. ☐ Funda-vergelijkingsonderzoek
6. ☐ Hypotheekverkenning starten
7. ☐ Bouwkundig keurder selecteren
8. ☐ Biedstrategie documenteren

---

*Einde rapport. Gegenereerd door 4-Plane Enforced Analytical System.*
