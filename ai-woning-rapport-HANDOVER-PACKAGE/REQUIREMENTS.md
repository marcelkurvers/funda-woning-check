# REQUIREMENTS – AI Woning Rapport Web App

## Functional (must)
1. Startscherm: 1 URL → 1 rapport (clean sheet)
2. Analyse scherm: live state machine (SSE/polling)
3. Scrape-test Funda → bij fail automatisch copy‑paste flow
4. Rapportoverzicht vóór download:
   - H1–H12
   - status compleet/deels/onbekend
   - KPI’s + broncount
   - “Onbekend / nader te onderzoeken”
5. Alleen openbare bronnen (best-effort) + bronvermelding per hoofdstuk
6. Browser-first rendering (PDF optioneel)

## Non-functional (must)
- Single-user local
- 1 command start (docker compose)
- Geen data gokken; missing = “onbekend / nader te onderzoeken”
- Modulaire code (parsers/sources/generator/pipeline)
- Traceability: sources + timestamps

## Constraints
- Geen bot-omzeiling / agressieve scraping van Funda.
- Copy-paste is het primaire inputpad.
