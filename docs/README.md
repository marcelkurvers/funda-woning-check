AI Woning Rapport – Werkende Local App (geen demo)
==================================================

Dit pakket bevat een werkende webapp + backend (FastAPI) die jouw beloofde flow uitvoert:

1) Startscherm: 1 URL → 1 rapport
   - POST /runs → nieuwe run_id
   - clean sheet per run

2) Analyse: live voortgang (state machine)
   - Scrape Funda → Bronnen → KPI’s → Hoofdstukken → PDF
   - Live via SSE (/runs/{id}/events) met fallback polling

3) Rapportoverzicht vóór download
   - Hoofdstukken 1–12 met status + KPI count + broncount
   - Apart blok: Onbekend / nader te onderzoeken
   - Rapport-content (blocks) gerenderd in de browser

4) PDF
   - Pipeline-stap zichtbaar
   - In local build is PDF bewust uitgeschakeld (jij zei: geen PDF nodig)

Waarom local?
- Een enkel index.html bestand kan geen echte POST /runs + SSE + DB draaien zonder server.
- Daarom levert dit pakket een echte backend in Docker: 1 commando, dan werkt het echt.

Starten (macOS / Windows / Linux):
1. Installeer Docker Desktop
2. In deze map:
   docker compose up --build
3. Open:
   http://localhost:8000

Funda scraping:
- In deze local build scrapen we niet (Funda blokkeert en compliance).
- Je kunt wel HTML/fragment plakken bij de run (Opslaan bij run).
- In cloud-mode kan je later officiële bronnen koppelen en parsing uitbreiden.

